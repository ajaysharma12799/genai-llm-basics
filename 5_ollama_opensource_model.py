# Ollama Intro
from ollama import chat, list
from ollama import ChatResponse

# Get List of available models
models = list()
# Print the list of models
print("Available models:", models)

# Without Streaming

# Define the model to use
model = "gemma3:1b"
# Define the prompt
prompt = "What is the capital of France?"
# Call the model with the prompt
response: ChatResponse = chat(model=model, messages=[{"role": "user", "content": prompt}])

# Print the response
print(response.message.content)

# With Streaming
streamResponse:ChatResponse = chat(model=model, messages=[{"role": "user", "content": prompt}], stream=True)
# Print the response as it streams
for chunk in streamResponse:
    print(chunk.message.content, end="", flush=True)