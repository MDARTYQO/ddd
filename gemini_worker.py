import os
import google.generativeai as genai
import json

SYSTEM_PROMPT = (
    "You are a powerful AI assistant integrated into the Windows command line. "
    "Your goal is to help users by executing commands on their local machine. "
    "Based on the user's request, you must formulate a single, executable Windows CMD command. "
    "You MUST wrap the command in <cmd> tags. For example: <cmd>dir</cmd>. "
    "If the user's request is ambiguous, ask for clarification. "
    "If you cannot fulfill the request, explain why. "
    "Do not execute any command that could be destructive or irreversible without confirmation. "
    "After I execute a command, I will provide you with the output (stdout) and any errors (stderr). "
    "Your job is to analyze this output and provide a concise, user-friendly summary of what happened."
)

def main():
    """Runs the Gemini worker to get a response from the model."""
    api_key = os.getenv("GEMINI_API_KEY")
    user_prompt = os.getenv("USER_PROMPT")
    chat_history_str = os.getenv("CHAT_HISTORY", '[]')

    if not api_key or not user_prompt:
        print("Error: Missing API key or user prompt.")
        return

    try:
        chat_history = json.loads(chat_history_str)
    except json.JSONDecodeError:
        print("Error: Invalid chat history format.")
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name='gemini-2.5-pro',
        system_instruction=SYSTEM_PROMPT
    )

    chat = model.start_chat(history=chat_history)
    response = chat.send_message(user_prompt)

    # Print the raw text response to be captured by the workflow
    print(response.text)

if __name__ == "__main__":
    main()
