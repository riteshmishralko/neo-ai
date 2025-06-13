import torch
from transformers import CsmForConditionalGeneration, AutoProcessor
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import tempfile
import os
import openai
# --- SETUP ---
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

model_id = "sesame/csm-1b"
device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Loading model ({model_id}) on {device}...")
processor = AutoProcessor.from_pretrained(model_id)
model = CsmForConditionalGeneration.from_pretrained(model_id).to(device)
print("Model loaded.")

recognizer = sr.Recognizer()
mic = sr.Microphone()

openai_conversation = [
    {"role": "system", "content": "You are a helpful AI speaking assistant."}
]

conversation = []

def record_and_transcribe():
    with mic as source:
        print("You: (speak now)")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I could not understand your speech. Please try again.")
        return None
    except sr.RequestError:
        print("Sorry, there was an error reaching the speech recognition service.")
        return None



def openai_gpt_conversation(conversation, model="gpt-4.1-nano"):
    """
    conversation: list of dicts [{'role': 'user/assistant/system', 'content': ...}]
    returns: assistant reply (string)
    """
    response = openai.chat.completions.create(
        model=model,
        messages=conversation
    )
    return response.choices[0].message.content
    # return response['choices'][0]['message']['content']




def bot_generate_and_speak(response_text):
    # Use [1] as the bot speaker
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
    # Save and play audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
        processor.save_audio(audio, tmp_wav.name)
        data, samplerate = sf.read(tmp_wav.name)
        print("Bot: (speaking...)")
        sd.play(data, samplerate)
        sd.wait()
        os.unlink(tmp_wav.name)

print("\n--- OpenAI GPT + CSM Voice Chatbot ---")
print("Press Ctrl+C to exit.\n")

# Initial greeting
bot_greeting = "Hello! How can I help you today?"
print(f"Bot: {bot_greeting}")
bot_generate_and_speak(bot_greeting)
openai_conversation.append({"role": "assistant", "content": bot_greeting})

# --- MAIN LOOP ---
try:
    while True:
        user_text = record_and_transcribe()
        if not user_text:
            print("Please try speaking again.\n")
            continue
        openai_conversation.append({"role": "user", "content": user_text})
        response_text = openai_gpt_conversation(openai_conversation)
        print(f"Bot: {response_text}")
        openai_conversation.append({"role": "assistant", "content": response_text})
        bot_generate_and_speak(response_text)
except KeyboardInterrupt:
    print("\nExiting. Goodbye!")