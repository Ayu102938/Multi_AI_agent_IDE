import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load env
base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, ".env")
load_dotenv(env_path, override=True)

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found.")
    exit(1)

genai.configure(api_key=api_key)

print("Listing available models...")
try:
    with open("available_models.txt", "w", encoding="utf-8") as f:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
                f.write(m.name + "\n")
except Exception as e:
    print(f"Error listing models: {e}")
    with open("available_models.txt", "w", encoding="utf-8") as f:
        f.write(f"Error: {e}")
