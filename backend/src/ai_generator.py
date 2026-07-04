import os
import json
import random
import re
import google.generativeai as genai
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Configure the API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def generate_challenge_with_ai(difficulty: str, language: str, topic: str) -> Dict[str, Any]:
    """
    Generate a coding challenge with a specific question body, topic, and language.
    """
    prompt = f"""You are a senior software engineering interviewer.
    STRICT CONSTRAINT: Create a technical challenge about {topic} in {language} ({difficulty.upper()}).
    The question MUST include a specific code snippet or a deep technical scenario.

    Return ONLY a valid JSON object matching this structure:
    {{
      "title": "Technical Title",
      "question": "The technical problem or code snippet.",
      "options": ["Op 1", "Op 2", "Op 3", "Op 4"],
      "correct_answer_id": 0,
      "explanation": "Detailed breakdown."
    }}
    Do not use markdown formatting. Seed: {random.randint(1, 1000000)}
    """

    try:
        print(f"\n=== ATTEMPTING AI GENERATION ===")
        print(f"Difficulty: {difficulty}, Language: {language}, Topic: {topic}")

        # Check if API key exists
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        print(f"API Key found: {api_key[:10]}... (truncated)")

        # Use the correct Gemini API call
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        print("Model initialized successfully")

        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                response_mime_type="application/json",
            )
        )

        print("API call successful, processing response...")

        # Get the text from response
        raw_text = response.text.strip()
        print(f"Raw response length: {len(raw_text)} characters")
        print(f"First 200 chars: {raw_text[:200]}")

        # Clean any markdown formatting
        clean_text = re.sub(r'```json|```', '', raw_text).strip()

        # Extract JSON object
        start_index = clean_text.find('{')
        end_index = clean_text.rfind('}')

        if start_index == -1 or end_index == -1:
            raise ValueError(f"No JSON object found in response. Raw text: {raw_text}")

        clean_text = clean_text[start_index:end_index + 1]
        print(f"Extracted JSON: {clean_text[:200]}...")

        data = json.loads(clean_text)
        print("JSON parsed successfully")

        # Validate required keys
        required_keys = ["title", "question", "options", "correct_answer_id", "explanation"]
        for key in required_keys:
            if key not in data:
                raise KeyError(f"Missing required key: {key}")

        print("=== AI GENERATION SUCCESS ===\n")
        return data

    except Exception as e:
        print(f"\n=== AI GENERATION FAILED ===")
        print(f"ERROR TYPE: {type(e).__name__}")
        print(f"ERROR MESSAGE: {e}")

        if 'response' in locals():
            try:
                print(f"RAW AI RESPONSE: {response.text}")
            except:
                print("Could not access response.text")

        if 'raw_text' in locals():
            print(f"RAW TEXT CAPTURED: {raw_text}")

        print(f"=== END DEBUG INFO ===\n")

        # Re-raise the exception so we can see it in the API
        raise Exception(f"AI Generation failed: {type(e).__name__} - {str(e)}")