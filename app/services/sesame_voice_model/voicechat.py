import torch
from transformers import CsmForConditionalGeneration, AutoProcessor
import openai
import speech_recognition as sr
import tempfile
import os
import subprocess
import platform

os.environ["TOKENIZERS_PARALLELISM"] = "false"

openai.api_key = os.getenv("OPENAI_API_KEY")
model_dir = "sesame/csm-1b"
# model_dir = "eustlb/csm-1b"

# model_dir = "csm-finetuned-custom-voice" 

if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

print(f"Using device: {device}")

# # Load models once (on the right device)
# processor = AutoProcessor.from_pretrained(model_id)
# model = CsmForConditionalGeneration.from_pretrained(model_id).to(device)



# model_dir = "csm-finetuned-custom-voice"  # or whatever you set in your training
processor = AutoProcessor.from_pretrained(model_dir)
model = CsmForConditionalGeneration.from_pretrained(model_dir).to(device)


# Enable CSM static cache for fast repeated inference (if supported)
try:
    model.generation_config.cache_implementation = "static"
    model.depth_decoder.generation_config.cache_implementation = "static"
    print("CSM static cache enabled for fast inference.")
except Exception as e:
    print("Could not enable static cache:", e)

def openai_gpt_conversation(conversation, model="gpt-4.1-nano"):
    response = openai.chat.completions.create(
        model=model,
        messages=conversation
    )
    return response.choices[0].message.content

def convert_audio_to_wav(input_bytes, input_format="webm"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{input_format}") as input_file:
        input_file.write(input_bytes)
        input_fname = input_file.name
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as output_file:
        output_fname = output_file.name
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", input_fname,
            "-ar", "16000", "-ac", "1", output_fname
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        os.remove(input_fname)
        os.remove(output_fname)
        raise RuntimeError(f"ffmpeg conversion failed: {e.stderr.decode()}") from e
    os.remove(input_fname)
    return output_fname

async def handle_voice_ws(websocket):
    audio_bytes = b""
    conversation = [
        {"role": "system", "content": "You are a helpful AI speaking assistant."}
    ]
    while True:
        data = await websocket.receive_bytes()
        if data == b"END":
            print("Received audio bytes:", len(audio_bytes))
            wav_path = convert_audio_to_wav(audio_bytes, input_format="webm")

            print("WAV path for STT:", wav_path, type(wav_path))
            recognizer = sr.Recognizer()
            user_text = None
            try:
                with sr.AudioFile(wav_path) as source:
                    audio = recognizer.record(source)
                user_text = recognizer.recognize_google(audio)
                print(f"You said: {user_text}")
                await websocket.send_json({"type": "transcript", "text": user_text})
                conversation.append({"role": "user", "content": user_text})
            except sr.UnknownValueError:
                print("Sorry, could not understand audio.")
                await websocket.send_json({"type": "transcript", "text": "(Sorry, I could not understand your speech. Please try again.)"})
                os.remove(wav_path)
                continue
            except sr.RequestError as e:
                print(f"Speech recognition service error: {e}")
                await websocket.send_json({"type": "transcript", "text": "(Speech recognition service error. Please try again later.)"})
                os.remove(wav_path)
                continue
            finally:
                if os.path.exists(wav_path):
                    os.remove(wav_path)

            # Only continue if user_text was recognized
            response_text = openai_gpt_conversation(conversation)
            conversation.append({"role": "assistant", "content": response_text})
            print(f"Bot: {response_text}")
            await websocket.send_json({"type": "bot_text", "text": response_text})

            # TTS (CSM), stream audio as it's synthesized
            csm_conversation = [
                {"role": "1", "content": [{"type": "text", "text": response_text}]}
            ]
            inputs = processor.apply_chat_template(
                csm_conversation,
                tokenize=True,
                return_dict=True
            ).to(device)
            with torch.no_grad():
                audio = model.generate(**inputs, output_audio=True)

            # Save and stream TTS audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as bot_wav:
                processor.save_audio(audio, bot_wav.name)
                bot_wav_path = bot_wav.name
            try:
                # Use a larger chunk for more efficient streaming (32k)
                with open(bot_wav_path, "rb") as f:
                    chunk = f.read(32768)
                    while chunk:
                        await websocket.send_bytes(chunk)
                        chunk = f.read(32768)
                await websocket.send_bytes(b"END_AUDIO")
            finally:
                if os.path.exists(bot_wav_path):
                    os.remove(bot_wav_path)
            # break
        else:
            audio_bytes += data