import json
from typing import Dict, List
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def initialize_client(use_ollama: bool = False) -> OpenAI:
    """Initialize the OpenAI client for either OpenAI or OLLAMA."""
    if use_ollama:
        return OpenAI(base_url="http://localhost:11434/v1", api_key="gemma3:1b")
    return OpenAI()


def create_initial_messages() -> List[Dict[str, str]]:
    """Create the initial messages for the context memory."""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
    ]


def chat(
    user_input: str, messages: List[Dict[str, str]], client: OpenAI, model_name: str
) -> str:
    """Handle user input and generate responses"""
    # Append user message to the conversation
    messages.append({"role": "user", "content": user_input})

    try:
        # Generate a response using the API
        response = client.chat.completions.create(model=model_name, messages=messages)

        # Append assistant's response to the conversation
        assistant_response = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_response})

        return assistant_response
    except Exception as e:
        return f"Error with API: {str(e)}"


def summarize_messages(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Summarize older messages to save tokens"""
    summary = "Previous conversation summarized: " + " ".join(
        [m["content"][:50] + "..." for m in messages[-5:]]
    )
    return [{"role": "system", "content": summary}] + messages[-5:]


def save_conversation(
    messages: List[Dict[str, str]], filename: str = "conversation.json"
):
    """Save conversation to a file"""
    with open(filename, "w") as f:
        json.dump(messages, f)


def load_conversation(filename: str = "conversation.json") -> List[Dict[str, str]]:
    """Load conversation from a file"""
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"No conversation file found at {filename}")
        return create_initial_messages()


def main():
    # Model selection
    print("Select model type:")
    print("1. OpenAI GPT-4")
    print("2. Ollama (Local)")

    choice = input("Enter choice (1 or 2): ")
    use_ollama = choice == "2"

    # Initialize client and model name
    client = initialize_client(use_ollama)
    model_name = "gemma3:1b" if use_ollama else "gpt-4o-mini"

    # Initialize or load conversation
    messages = create_initial_messages()

    print(f"\nUsing {'Gemma3:1b' if use_ollama else 'OpenAI'} model. Type 'quit' to exit.")
    print("Available commands:")
    print("- 'save': Save conversation")
    print("- 'load': Load conversation")
    print("- 'summary': Summarize conversation")

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() == "quit":
            break
        elif user_input.lower() == "save":
            save_conversation(messages)
            print("Conversation saved!")
            continue
        elif user_input.lower() == "load":
            messages = load_conversation()
            print("Conversation loaded!")
            continue
        elif user_input.lower() == "summary":
            messages = summarize_messages(messages)
            print("Conversation summarized!")
            continue

        response = chat(user_input, messages, client, model_name)
        print(f"\nAssistant: {response}")

        # Automatically summarize if conversation gets too long
        if len(messages) > 10:
            messages = summarize_messages(messages)
            print("\n(Conversation automatically summarized)")


# Example usage
if __name__ == "__main__":
    main()

# Flow Chart for this code:
# 1. Start
# 2. Load environment variables
# 3. Initialize OpenAI client based on user choice (Ollama or OpenAI)
# 4. Create initial messages
# 5. Display model selection options
# 6. Get user choice for model
# 7. Enter chat loop
# 8. Get user input
# 9. Check for special commands (save, load, summary, quit)
# 10. If 'save', save conversation to file
# 11. If 'load', load conversation from file
# 12. If 'summary', summarize conversation
# 13. If 'quit', exit loop
# 14. If normal input, call chat function to get response
# 15. Print assistant's response
# 16. Check if conversation length exceeds threshold
# 17. If yes, summarize conversation
# 18. Loop back to step 8
# 19. End
# 20. End
# 21. Save conversation to file
# 22. Load conversation from file
# 23. Summarize conversation
# 24. End
# 25. End

# Context and Memory Management (Simple Explanation):
# - "Context" means remembering what has happened in the conversation so far.
# - The program keeps a list of messages (from user and assistant) to know the history.
# - "Memory management" is about saving, loading, and summarizing these messages.
# - Saving lets you keep the conversation for later.
# - Loading brings back a saved conversation.
# - Summarizing shortens old messages so the assistant doesn't forget important things but uses fewer resources.
# - This helps the assistant give better answers by knowing what you talked about before.
