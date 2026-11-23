# LLM API integration

from groq import Groq
from config.settings import settings

class GroqLLMClient:
    def __init__(self) -> None:
        if not settings.groq_api_key:
            raise ValueError("Groq API key is required.")
        self._client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model

   

    def generate_json_response(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2500,
    ) -> str:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content

        if not content:
            raise ValueError("LLM returned an empty response.")

        return content.strip()
    