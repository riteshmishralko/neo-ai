import os

# ABSOLUTELY FORCE CPU USAGE
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "0"
os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0"
os.environ["PYTORCH_NO_MPS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"


import torch

if hasattr(torch.backends, "mps"):
    torch.backends.mps.is_available = lambda: False
    
import requests
# import numpy as np
from datasets import Dataset, Audio
from transformers import (
    CsmForConditionalGeneration,
    CsmProcessor,
    TrainingArguments,
    Trainer
)

print("torch.cuda.is_available():", torch.cuda.is_available())
print("torch.backends.mps.is_available():", hasattr(torch.backends, "mps") and torch.backends.mps.is_available())
print("torch.get_default_dtype():", torch.get_default_dtype())

class CSMVoiceDatasetBuilder:
    def __init__(self, json_data, audio_dir="audio", sampling_rate=24000):
        self.data = json_data
        self.audio_dir = audio_dir
        self.sampling_rate = sampling_rate
        os.makedirs(self.audio_dir, exist_ok=True)

    def download_and_build(self):
        dataset_list = []
        for row in self.data['rows']:
            entry = row['row']
            audio_url = entry['audio'][0]['src']
            audio_id = entry['id']
            text = entry['text']
            speaker_id = entry['speaker_id']
            style = entry.get('style', '')
            local_audio_path = os.path.join(self.audio_dir, f"{audio_id}.wav")
            if not os.path.exists(local_audio_path):
                print(f"Downloading: {local_audio_path}")
                try:
                    r = requests.get(audio_url)
                    with open(local_audio_path, "wb") as f:
                        f.write(r.content)
                except Exception as e:
                    print(f"Failed to download {audio_url}: {e}")
                    continue
            dataset_list.append({
                "audio": local_audio_path,
                "text": text,
                "speaker_id": speaker_id,
                "style": style,
                "id": audio_id
            })
        return dataset_list

    def build_hf_dataset(self):
        dataset_list = self.download_and_build()
        ds = Dataset.from_list(dataset_list)
        ds = ds.cast_column("audio", Audio(sampling_rate=self.sampling_rate))
        print(ds)
        return ds

class CSMCustomVoiceTrainer:
    def __init__(
        self,
        model_id="sesame/csm-1b",
        speaker_id=2,
        exp_dir="csm-finetuned-custom-voice",
    ):
        self.model_id = model_id
        self.speaker_id = speaker_id
        self.exp_dir = exp_dir

        # --- ABSOLUTELY FORCE CPU ---
        self.device = "cpu"
        print(f"USING DEVICE: {self.device}")

        self.processor = CsmProcessor.from_pretrained(self.model_id)
        self.model = CsmForConditionalGeneration.from_pretrained(self.model_id).to(self.device)
        self.model.train()
        self.model.codec_model.eval()

    def data_collator(self, samples):
        conversations = []
        for sample in samples:
            arr = sample["audio"]["array"]
            conversation = [{
                "role": str(self.speaker_id),
                "content": [
                    {"type": "text", "text": sample["text"]},
                    {"type": "audio", "audio": arr}
                ]
            }]
            conversations.append(conversation)
        return self.processor.apply_chat_template(
            conversations,
            tokenize=True,
            return_dict=True,
            output_labels=True,
        )

    def train(self, dataset, epochs=1, batch_size=1, lr=2e-5):
        print("Starting training...")
        training_args = TrainingArguments(
            self.exp_dir,
            remove_unused_columns=False,
            gradient_checkpointing=True,
            per_device_train_batch_size=batch_size,
            learning_rate=lr,
            num_train_epochs=epochs,
            logging_steps=1,
            save_steps=10,
            report_to="none",
            save_total_limit=3,
        )
        trainer = Trainer(
            self.model,
            training_args,
            train_dataset=dataset,
            data_collator=self.data_collator,
        )
        trainer.train()
        print("Training complete!")
        self.processor.save_pretrained(self.exp_dir)
        self.model.save_pretrained(self.exp_dir)
        print(f"Saved model and processor to {self.exp_dir}")

def train_csm():
    HF_URL = "https://datasets-server.huggingface.co/rows?dataset=ylacombe%2Fexpresso&config=read&split=train&offset=0&length=100"
    print("Downloading metadata JSON...")
    resp = requests.get(HF_URL)
    json_data = resp.json()

    builder = CSMVoiceDatasetBuilder(json_data, audio_dir="audio")
    ds = builder.build_hf_dataset()

    trainer = CSMCustomVoiceTrainer(
        model_id="sesame/csm-1b",
        speaker_id=2,
        exp_dir="csm-finetuned-custom-voice"
    )
    trainer.train(ds, epochs=3, batch_size=1)

# if __name__ == "__main__":
#     train_csm()
