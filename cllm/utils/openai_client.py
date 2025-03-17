import os
import httpx
from typing import Dict, Any, Optional
from rich.console import Console

console = Console()

class OpenAIClient:
    """OpenAi Client"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set the OPENAI_API_KEY environment variable or provide the key when initializing the client.")
        
        self.base_url = "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def chat_completion(
        self, 
        prompt: str, 
        model: str = "gpt-3.5-turbo", 
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Sends a prompt to the OpenAI chat model and returns the response.
        
        Args:
            prompt: The text of the prompt
            model: The model to be used
            max_tokens: Maximum number of tokens in the response
            temperature: Temperature for text generation (0.0 to 1.0)
            
        Returns:
            Dictionary with the API response
        """
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, json=payload, timeout=30.0)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            error_response = e.response.json()
            if error_response.get("error", {}).get("code") == "model_not_found":
                console.print(f"[bold red]The model `{model}` does not exist or you do not have access to it.[/bold red]")
                return {"error": f"The model `{model}` does not exist or you do not have access to it."}
            console.print(f"[bold red]API error ({e.response.status_code}): {e.response.text}[/bold red]")
            return {"error": e.response.text}
        except httpx.RequestError as e:
            console.print(f"[bold red]Connection error: {str(e)}[/bold red]")
            return {"error": str(e)}
    
    def extract_text_response(self, response: Dict[str, Any]) -> str:
        """Extracts the text from the API response."""
        if "error" in response:
            return f"Error: {response['error']}"
        
        try:
            return response["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as e:
            return f"Error extracting a response: {str(e)}"