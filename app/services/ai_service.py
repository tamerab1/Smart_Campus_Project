# app/services/ai_service.py
import os
from google import genai
from google.genai import types

# Fetch API key securely from .env
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from the environment variables.")

# Initialize the new standard client
client = genai.Client(api_key=api_key)

async def generate_campus_response(question: str, db_context: str) -> str:
    """
    Constructs a prompt with the campus context and sends it to Gemini using the new SDK.
    """
    system_instruction = f"""
    You are the 'Smart Campus Assistant', a helpful and concise AI for students.
    Answer the student's question using ONLY the provided Database Context.
    If the answer is not in the context, politely state that you do not have that information.
    Keep the answer friendly and short.

    Database Context:
    {db_context}
    """
    
    try:
        # Non-blocking async call using the updated fast model
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash', # Updated to the current available model
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"AI Service Error: {e}")
        # Graceful fallback if API fails
        return "The AI service is currently unavailable. Please try again later."