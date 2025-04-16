import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.GOOGLE_API_KEY)

def generate_with_gemini(prompt, max_tokens=300, chat_history=None):
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    try:
        if chat_history:
            # Start a chat with history if context exists
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": max_tokens,
                }
            )
        else:
            
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": max_tokens,
                }
            )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"