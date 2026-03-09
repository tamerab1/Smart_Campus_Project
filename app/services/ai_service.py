# app/services/ai_service.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Using the standard model for text generation
model = genai.GenerativeModel('gemini-2.5-pro')

async def generate_campus_response(question: str, db_context: str, history: list = None):
    # Format the history into the prompt if it exists
    history_prompt = ""
    if history:
        history_prompt = "Previous Conversation Context:\n"
        # Keep only the last 4 messages so the prompt doesn't get too long
        for msg in history[-4:]:
            history_prompt += f"{msg.role.capitalize()}: {msg.content}\n"

    prompt = f"""You are a helpful Smart Campus Assistant.
    Answer the student's question naturally based ONLY on the provided Database Information.
    If the database context is missing, use the Previous Conversation Context to understand what the user is referring to.

    {history_prompt}
    
    Database Information:
    {db_context}
    
    Student Question: {question}
    """
    
    response = model.generate_content(prompt)
    return response.text

async def get_ai_category(question: str) -> str:
    prompt = f"""You are a smart router. Classify the user question into ONE of these categories:
    'Schedule', 'Technical Issue', 'Staff Info', 'General Info'.
    If the question is irrelevant, return 'Out of Scope'.
    
    Question: "{question}"
    Respond with ONLY the category name. No quotes, no extra text."""
    
    response = model.generate_content(prompt)
    return response.text.strip()