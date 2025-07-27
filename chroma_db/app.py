import chromadb
chroma_client = chromadb.Client()

collection_name = "test_collection"
collection = chroma_client.get_or_create_collection(collection_name)

# Define text documents
documents = [
    { "id": "doc1", "text": "This is the first document." },
    { "id": "doc2", "text": "This is the second document." },
    { "id": "doc3", "text": "This is the third document." },
    { "id": "doc4", "text": "This is the fourth document." },
    { "id": "doc5", "text": "This is the fifth document." },
    { "id": "doc6", "text": "This is the sixth document." },
]

# Loop over the documents and add them to the collection
for doc in documents:
    collection.upsert(ids=[doc["id"]], documents=[doc["text"]])

# Define a query text
query_text = "This is the first document."

# Query the collection for similar documents
results = collection.query(query_texts=[query_text], n_results=3)

# Print the results
for idx, doc in enumerate(results["documents"][0]):
    doc_id = results["ids"][0][idx]
    distance = results["distances"][0][idx]
    print(f"Document ID: {doc_id}, Text: {doc}, Distance: {distance}")
print("Query completed successfully.")
print(f"Total documents in collection: {len(collection.get()['ids'])}")