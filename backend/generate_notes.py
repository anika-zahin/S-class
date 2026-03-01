import os
from groq import Groq

# 1. Setup your "Brain" (Paste your Groq API Key below!)
client = Groq(api_key="GROQ_API_KEY")

def process_lecture_notes(raw_text):
    # This is the "Prompt" - we are telling the AI exactly how to behave
    prompt = f"""
    I am a student. I have OCR text from a whiteboard: "{raw_text}"
    
    Please do the following:
    1. Identify the main Subject/Title.
    2. Extract key headings/topics.
    3. For each heading, write a clear, 3-sentence definition.
    4. Create 3 Multiple Choice Questions (MCQs) for a quiz.
    5. Create a 3-bullet point 'Cheat Sheet' summary.
    
    Format the response clearly with titles like 'TITLE:', 'DEFINITIONS:', 'QUIZ:', and 'CHEATSHEET:'.
    """

    print("Sending text to the AI Professor...")
    
    # 2. Ask the AI
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile", # Using Llama 3 for speed and intelligence
        messages=[{"role": "user", "content": prompt}],
    )

    return completion.choices[0].message.content

# --- TEST IT OUT ---
# Let's pretend this is what your OCR read from the board
sample_ocr_text = "Photosynthesis. Plants use sunlight. Chlorophyll. Oxygen is released. Glucose production."

structured_notes = process_lecture_notes(sample_ocr_text)
print("\n--- YOUR SMART NOTES ---")

print(structured_notes)
