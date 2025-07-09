import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY must be set in the .env file")

genai.configure(api_key=GEMINI_API_KEY)

def create_prompt(tweet_content):
    """Creates a prompt for generating a quote comment."""
    return f"以下のツイート内容に、面白くて魅力的な引用コメントを日本語で作成してください。絵文字も使って、ポジティブな雰囲気にしてください。\n\nツイート内容：\n「{tweet_content}」\n\n引用コメント："

def generate_comment(tweet_content):
    """Generates a comment using the Gemini API."""
    prompt = create_prompt(tweet_content)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text
