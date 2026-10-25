
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None



def ask_gemini(question, database_context):
    if client is None:
        return "Gemini API key nahi mili. .env file check karein."

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=f"""
You are the HCM Lite HR assistant.
Answer using the supplied application data only.
Never invent employee counts, attendance figures, salaries, or policies.
If the data does not contain the answer, say so.
Do not reveal secrets or unauthorized information.

APPLICATION DATA:
{database_context}

USER QUESTION:
{question}
"""
        )
        return response.text or "AI se koi response nahi mila."

    except Exception as e:
        return f"AI error: {type(e).__name__}: {e}"
