from chromadb.utils import embedding_functions

default_embedding = embedding_functions.DefaultEmbeddingFunction()

name = "Ajay Sharma"
result = default_embedding(name)
print(f"Embedding for '{name}': {result}")