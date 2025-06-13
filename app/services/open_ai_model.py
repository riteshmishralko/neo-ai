import os
from openai import OpenAI

class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set in environment variables.")
        self.openai = OpenAI(api_key=self.api_key)

    def create_chat_completion(self, model, messages, temperature, response_format=None):
        if response_format is not None:
            return self.openai.chat.completions.create(
                model=model, 
                messages=messages, 
                temperature=temperature,
                response_format={'type': response_format}
            )
        else:
            return self.openai.chat.completions.create(
                model=model, 
                messages=messages, 
                temperature=temperature
            )

class PromptSender:
    open_ai_model = {
        'model_4o': 'gpt-4o',
        'model_4o_mini': 'gpt-4o-mini',
        'model_4_1_nano': 'gpt-4.1-nano',
        'model_4_1_mini': 'gpt-4.1-mini',
        'model_4_1': 'gpt-4.1'
    }
    openai_client = OpenAIClient()
    models = open_ai_model

    @classmethod
    def send_prompt_by4o(cls, prompt_list, response_format=None, temperature=0.2):
        """Send a prompt to the OpenAI API using the 'model_4o' configuration."""
        completion = cls.openai_client.create_chat_completion(
            model=cls.models['model_4o'],
            messages=prompt_list,
            temperature=temperature,
            response_format=response_format
        )
        return completion.choices[0].message.content

    @classmethod
    def send_prompt_by4o_mini(cls, prompt_list, response_format=None, temperature=0.2):
        """Send a prompt to the OpenAI API using the 'model_4o_mini' configuration."""
        completion = cls.openai_client.create_chat_completion(
            model=cls.models['model_4o_mini'],
            messages=prompt_list,
            temperature=temperature,
            response_format=response_format
        )
        return completion.choices[0].message.content

    @classmethod
    def send_prompt_by4_1(cls, prompt_list, response_format=None, temperature=0.2):
        """Send a prompt to the OpenAI API using the 'model_4_1' configuration."""
        completion = cls.openai_client.create_chat_completion(
            model=cls.models['model_4_1'],
            messages=prompt_list,
            temperature=temperature,
            response_format=response_format
        )
        return completion.choices[0].message.content

    @classmethod
    def send_prompt_by4_1_nano(cls, prompt_list, response_format=None, temperature=0.2):
        """Send a prompt to the OpenAI API using the 'model_4_1_nano' configuration."""
        completion = cls.openai_client.create_chat_completion(
            model=cls.models['model_4_1_nano'],
            messages=prompt_list,
            temperature=temperature,
            response_format=response_format
        )
        return completion.choices[0].message.content

    @classmethod
    def send_prompt_by4(cls, prompt_list, response_format=None):
        """Send a prompt to the OpenAI API using the 'model_4' configuration."""
        completion = cls.openai_client.create_chat_completion(
            model=cls.models['model_4'],
            messages=prompt_list,
            temperature=0.2,
            response_format=response_format
        )
        return completion.choices[0].message.content