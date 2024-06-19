import os
import openai
import google.generativeai as genai

gemini_safety_settings = [
    {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

class AskLLM:
    def __init__(
        self, 
        llm_model, 
        gpt_organization=None, 
        google_api_key=None
    ) -> None:
        self.llm_model = llm_model
        if self.llm_model.startswith('gpt'):

            if gpt_organization is not None:
                self.client = openai.OpenAI(organization=gpt_organization)
            else:
                self.client = openai.OpenAI()

            self.model_name = self.get_openai_model_name()
            
        elif self.llm_model.startswith('gemini'):

            self.google_api_key = google_api_key if google_api_key is not None else os.environ.get('GOOGLE_API_KEY')

            if self.google_api_key is None:
                raise ValueError('Please provide a valid Google API key.')
            
            genai.configure(api_key=self.google_api_key)
            self.model_name = self.get_gemini_model_name()
        else:
            raise ValueError('Supported models are GPT and Gemini LLM models.')
        
    def get_openai_model_name(self):
        if self.llm_model == 'gpt-4':
            return "gpt-4-0125-preview"
        elif self.llm_model == 'gpt-4o':
            return "gpt-4o"
        elif self.llm_model == 'gpt-3.5':
            return "gpt-3.5-turbo-0125"
        else:
            raise ValueError('Supported OpenAI models are GPT-3.5 and GPT-4.')
    
    def get_gemini_model_name(self):
        if self.llm_model == 'gemini-1.0-pro':
            return "gemini-1.0-pro"
        else:
            raise ValueError('Supported Gemini models: Gemini-1.0-pro.')

    def ask(self, prompt):
        if self.llm_model.startswith('gpt'):
            return self.ask_openai(prompt)
        elif self.llm_model.startswith('gemini'):
            return self.ask_google(prompt)
        else:
            raise ValueError('Supported models are GPT and Gemini LLM models.')
    
    def ask_openai(self, prompt):
        prompt_chat = [{"role": "user", "content": prompt.strip()}]
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=prompt_chat,
            temperature=0,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        return response.choices[0].message.content.strip()
        
    def ask_google(self, prompt):
        model = genai.GenerativeModel(self.model_name)
        response = model.generate_content(prompt, safety_settings=gemini_safety_settings)
        return response.text.strip()
