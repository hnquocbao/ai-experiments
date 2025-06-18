from agno.models.groq import Groq
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.models.google import Gemini


def get_model(model_id:str,api_key:str):
    # Handle None or empty model_id by using a default
    if not model_id:
        model_id = "llama-3.3-70b-versatile"  # Default Groq model
    
    if 'gpt' in  model_id.lower():
        return OpenAIChat(id=model_id,api_key=api_key)
    if 'claude' in  model_id.lower():
        return Claude(id=model_id,api_key=api_key)
    if 'gemini' in  model_id.lower():
        return Gemini(id=model_id,api_key=api_key)
    
    return Groq(id=model_id,api_key=api_key)
    
    