import os
import openai
from dotenv import load_dotenv

load_dotenv()

# Load API key from environment variable or directly (for now, you can hardcode for testing)
openai.api_key = os.getenv("OPENAI_API_KEY")  # Replace with your key during testing

def score_resume(jd_text: str, resume_text: str) -> tuple:
    prompt = f"""
You are a hiring assistant. Compare the following Job Description (JD) and Resume.

JD:
{jd_text}

Resume:
{resume_text}

Give a score from 0 to 10 based on how well the resume matches the JD.
Also give a one-line reason for your score.

Respond in this format:
Score: X
Reason: <reason>
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        content = response['choices'][0]['message']['content']
        score_line = next((line for line in content.splitlines() if "Score:" in line), None)
        reason_line = next((line for line in content.splitlines() if "Reason:" in line), "")

        score = int(score_line.split(":")[1].strip()) if score_line else 0
        reason = reason_line.split(":", 1)[1].strip() if "Reason:" in reason_line else "No reason provided."

        return score, reason

    except Exception as e:
        return 0, f"Error: {str(e)}"
