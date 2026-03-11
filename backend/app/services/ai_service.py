# app/services/ai_service.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Using the standard model for text generation
model = genai.GenerativeModel('gemini-2.5-flash')

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
async def generate_campus_response_combined(question: str, db_context: str, history: list = None):
    history_prompt = ""
    if history:
        history_prompt = "Previous Conversation Context:\n" + "\n".join([f"{msg.role.capitalize()}: {msg.content}" for msg in history[-4:]])

    # הנחיה משולבת: גם סיווג וגם תשובה
    prompt = f"""You are a Smart Campus Assistant.
    Your task:
    1. Classify the student's question into one of these: 'Schedule', 'Technical Issue', 'Staff Info', 'General Info', 'Out of Scope'.
    2. Provide a natural answer.
    
    Database Information:
    {db_context}
    
    {history_prompt}
    Student Question: {question}
    
    Format your response EXACTLY like this (start with Category, then a newline, then Answer):
    Category: [The Category]
    Answer: [The Answer]
    """
    
    response = model.generate_content(prompt)
    text = response.text
    
    try:
        category_part = text.split("Category:")[1].split("Answer:")[0].strip()
        answer_part = text.split("Answer:")[1].strip()
        return category_part, answer_part
    except:
        return "General Info", text
    
# app/services/ai_service.py
async def get_ai_category_and_answer(question: str, db_context: str, history: list = None):
    history_prompt = ""
    if history:
        history_prompt = "Previous Conversation:\n" + "\n".join([f"{msg.role.capitalize()}: {msg.content}" for msg in history[-4:]])

    prompt = f"""You are a professional, accurate, and helpful Smart Campus Assistant.

    YOUR OPERATIONAL RULES:
    1. LANGUAGE: Detect the language of the student's question (Hebrew or English). ALWAYS respond in the SAME language as the question.
    2. COMPREHENSIVE SCANNING (MANDATORY): You are provided with lists of data. NEVER stop at the first item. You MUST scan the ENTIRE provided list (Exams, Facilities, Staff, FAQs) to find all relevant matches.
    3. CONTEXT AWARENESS: Use the 'Previous Conversation' history to resolve pronouns (e.g., if the user asks 'What is her email?', identify 'her' from the previous turns in history).
    4. QUESTION PRIORITIZATION: Focus exclusively on the user's current intent. If they ask for a lecturer, provide lecturer details. Do NOT inject unrelated info (like exam dates) unless asked.
    5. HELPFUL FALLBACK: If the answer is NOT in the provided Database Information, DO NOT give up. Suggest logical next steps (e.g., "I don't have this in my records, I suggest checking the campus IT website or visiting the admin office.").
    6. SMART INFERENCE: You are allowed to use common sense. 
       - If a user asks for 'Wi-Fi' and you don't see a specific Wi-Fi entry, but you see 'Active' rooms or facilities, 
       DO NOT say 'I don't know'.
       - Instead, say: 'I don't have a specific status for Wi-Fi in other areas, but Room 205 and Room 102 
       are currently listed as active, so you might want to try there.'

    Database Information:
    {db_context}

    Previous Conversation:
    {history_prompt}

    User Question: "{question}"

    Format your response STRICTLY as follows (do not add conversational filler like 'Sure'):
    CATEGORY: [Schedule / Technical Issue / Staff Info / General Info / Out of Scope]
    ANSWER: [Your helpful response]
    """
    
    response = model.generate_content(prompt)
    raw_text = response.text
    
    try:
        category = raw_text.split("CATEGORY:")[1].split("ANSWER:")[0].strip()
        answer = raw_text.split("ANSWER:")[1].strip()
        return category, answer
    except:
        return "General Info", raw_text