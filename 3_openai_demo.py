from openai import OpenAI
import os

# Load environment variables from a .env file
from dotenv import load_dotenv

# Load all environment variables from the .env file
load_dotenv()

# Get the OpenAI API key from the environment variables
# api_key = os.getenv('OPENAI_API_KEY')

# Initialize the OpenAI client
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-3.5-turbo",  # Specify the model to use,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."}
    ],
)

print(response[0].message['content'])