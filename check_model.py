import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)

print("🔍 Checking available models for your key...")
try:
    # This asks Google: "What works?"
    for model in client.models.list():
        print(f"✅ Found: {model.name}")
except Exception as e:
    print(f"❌ Error listing models: {e}")