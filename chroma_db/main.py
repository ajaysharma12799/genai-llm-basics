"""
Interactive Document Processing System with ChromaDB

This script provides an interactive interface for processing and querying documents
using ChromaDB vector database. It supports both PDF and TXT files, allowing users
to upload documents, store them as embeddings, and perform semantic search queries.

Features:
- Interactive document type selection (PDF/TXT)
- Automatic text extraction from different file formats
- Vector storage in ChromaDB cloud database
- Semantic search with relevance scoring
- User-friendly interface with progress indicators

Requirements:
- chromadb: For vector database operations
- PyPDF2: For PDF text extraction
- python-dotenv: For environment variable management
- Valid ChromaDB cloud credentials in .env file

Author: [Ajay Sharma]
Version: 1.0
"""

import chromadb
import os
import pathlib
from dotenv import load_dotenv
import PyPDF2

# Load environment variables from .env file
# This should contain CHROMADB_API_KEY and CHROMADB_TENANT
load_dotenv()


def get_user_choice():
    """
    Present document type options to user and get their selection.

    This function displays a menu for document type selection and validates
    user input to ensure only valid options (1 for PDF, 2 for TXT) are accepted.

    Returns:
        str: User's choice ('1' for PDF, '2' for TXT)

    Example:
        choice = get_user_choice()
        if choice == '1':
            # Process PDF file
    """
    print("\n" + "=" * 50)
    print("Document Processing System")
    print("=" * 50)
    print("Please select the type of document you want to process:")
    print("1. PDF file")
    print("2. TXT file")
    print("=" * 50)

    # Input validation loop - continues until valid choice is made
    while True:
        choice = input("Enter your choice (1 or 2): ").strip()
        if choice in ['1', '2']:
            return choice
        else:
            print("Invalid choice! Please enter 1 for PDF or 2 for TXT.")


def get_file_path():
    """
    Get file path from user with validation and default option.

    This function prompts the user for a file path and validates that the file exists.
    If no path is provided, it returns a default sample file path.

    Returns:
        pathlib.Path: Valid file path object

    Example:
        file_path = get_file_path()
        print(f"Processing file: {file_path}")
    """
    while True:
        file_path = input("\nEnter the file path (or press Enter for default sample file): ").strip()

        # Use default sample file if no path provided
        if not file_path:
            default_path = pathlib.Path(__file__).parent.parent / 'sample_data/article-1.pdf'
            print(f"Using default file: {default_path}")
            return default_path

        # Validate that the provided file exists
        path = pathlib.Path(file_path)
        if path.exists():
            return path
        else:
            print(f"File not found: {file_path}")
            print("Please enter a valid file path.")


def get_user_query():
    """
    Get user's search query with input validation.

    This function prompts the user to enter their question about the document
    and ensures that a non-empty query is provided.

    Returns:
        str: User's search query/question

    Example:
        query = get_user_query()
        # Query can be used for semantic search: "What are the main topics?"
    """
    print("\n" + "-" * 50)
    print("Query Section")
    print("-" * 50)

    # Input validation loop - ensures non-empty query
    while True:
        query = input("What would you like to know about the document? ").strip()
        if query:
            return query
        else:
            print("Please enter a valid question.")


def extract_text_from_pdf(pdf_path):
    """
    Extract text content from PDF file using PyPDF2.

    This function opens a PDF file in binary mode, reads all pages,
    and extracts text content. It handles potential errors and provides
    progress feedback to the user.

    Args:
        pdf_path (pathlib.Path): Path to the PDF file

    Returns:
        str or None: Extracted text content, or None if extraction fails

    Example:
        text = extract_text_from_pdf(Path("document.pdf"))
        if text:
            print("Text extracted successfully")
    """
    print(f"\nProcessing PDF file: {pdf_path}")
    text_content = ""

    try:
        # Open PDF file in binary mode (required for PyPDF2)
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            print(f"Found {total_pages} pages in the PDF")

            # Extract text from each page
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()

                # Only add pages that contain actual text content
                if page_text.strip():
                    text_content += f"Page {page_num + 1}:\n{page_text}\n\n"

    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

    # Validate that we extracted some content
    if not text_content:
        print("Warning: No text could be extracted from the PDF")
        print("The PDF might be image-based or corrupted")
        return None

    print("✓ PDF text extraction completed successfully")
    return text_content


def extract_text_from_txt(txt_path):
    """
    Extract text content from TXT file with multiple encoding support.

    This function attempts to read a text file using various character encodings
    to handle different file formats and international characters properly.

    Args:
        txt_path (pathlib.Path): Path to the text file

    Returns:
        str or None: File content as string, or None if reading fails

    Example:
        content = extract_text_from_txt(Path("document.txt"))
        if content:
            print(f"Read {len(content)} characters")
    """
    print(f"\nProcessing TXT file: {txt_path}")

    # List of encodings to try (most common first)
    # UTF-8: Standard Unicode encoding
    # Latin-1: Western European characters
    # CP1252: Windows Western European
    # ISO-8859-1: International standard
    encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

    # Try each encoding until one works
    for encoding in encodings_to_try:
        try:
            with open(txt_path, 'r', encoding=encoding) as file:
                content = file.read()
                print(f"✓ Successfully read file with {encoding} encoding")
                return content
        except UnicodeDecodeError:
            # This encoding didn't work, try the next one
            continue

    # If we get here, none of the encodings worked
    print("Error: Could not read the file with any supported encoding")
    print("The file might be corrupted or in an unsupported format")
    return None


def process_and_store_content(collection, content, file_type):
    """
    Process extracted content and store it in ChromaDB collection.

    This function takes the extracted text content, splits it into meaningful
    chunks based on the file type, and stores each chunk as a separate document
    in the ChromaDB collection for vector search.

    Args:
        collection: ChromaDB collection object
        content (str): Extracted text content from the document
        file_type (str): Type of file ("PDF" or "TXT")

    Returns:
        int: Number of document sections successfully stored

    Example:
        count = process_and_store_content(collection, text_content, "PDF")
        print(f"Stored {count} document sections")
    """
    print(f"\nStoring {file_type} content in ChromaDB...")

    # Split content differently based on file type
    if file_type == "PDF":
        # For PDFs, split by pages (already formatted with "Page X:" markers)
        sections = content.split("Page ")
        sections = [section.strip() for section in sections if section.strip()]
    else:
        # For TXT files, split by double line breaks (paragraphs)
        sections = [p.strip() for p in content.split('\n\n') if p.strip()]

    documents_added = 0

    # Process each section and add to ChromaDB
    for idx, section in enumerate(sections):
        # Only process substantial content (more than 10 characters)
        if section and len(section) > 10:
            # Create unique ID for each document section
            doc_id = f"{file_type.lower()}_doc_{idx + 1}"

            try:
                # Add document to ChromaDB collection
                # ChromaDB will automatically generate embeddings for semantic search
                collection.add(
                    ids=[doc_id],  # Unique identifier
                    documents=[section]  # Text content to be embedded
                )
                documents_added += 1
                print(f"✓ Added document {doc_id}")
            except Exception as e:
                print(f"✗ Error adding document {doc_id}: {e}")

    print(f"\n✓ Successfully stored {documents_added} document sections")
    return documents_added


def main():
    """
    Main function that orchestrates the entire document processing workflow.

    This function coordinates all the steps:
    1. Connect to ChromaDB
    2. Get user preferences (file type, file path, query)
    3. Extract text from the selected document
    4. Store content in vector database
    5. Perform semantic search based on user query
    6. Display results with relevance scores

    The function includes comprehensive error handling and user feedback
    throughout the process.
    """
    try:
        # Step 1: Initialize ChromaDB connection
        print("Connecting to ChromaDB...")

        # Create cloud client using credentials from environment variables
        client = chromadb.CloudClient(
            api_key=os.getenv("CHROMADB_API_KEY"),  # API key for authentication
            tenant=os.getenv("CHROMADB_TENANT"),  # Tenant identifier
            database='Test'  # Database name
        )
        print("✓ Connected to ChromaDB successfully")

        # Get or create a collection for storing document embeddings
        # Collections in ChromaDB are like tables in traditional databases
        collection = client.get_or_create_collection(name='interactive_collection')

        # Step 2: Get user preferences
        choice = get_user_choice()

        # Determine file type based on user choice
        if choice == '1':
            print("\nYou selected: PDF file")
            file_type = "PDF"
        else:
            print("\nYou selected: TXT file")
            file_type = "TXT"

        # Get the file path from user
        file_path = get_file_path()
        print(f"Selected file: {file_path}")

        # Step 3: Extract text content based on file type
        if file_type == "PDF":
            content = extract_text_from_pdf(file_path)
        else:
            content = extract_text_from_txt(file_path)

        # Validate that content extraction was successful
        if not content:
            print("Failed to extract content from the file. Exiting...")
            return

        # Step 4: Store content in ChromaDB for vector search
        docs_count = process_and_store_content(collection, content, file_type)

        # Ensure we have documents to search
        if docs_count == 0:
            print("No documents were stored. Exiting...")
            return

        # Step 5: Get user's search query
        user_query = get_user_query()

        # Step 6: Perform semantic search
        print(f"\nSearching for: '{user_query}'")
        print("Processing your query...")

        try:
            # Perform vector similarity search
            # ChromaDB will find documents most similar to the query
            results = collection.query(
                query_texts=[user_query],  # Search query
                n_results=min(5, docs_count)  # Limit results (max 5 or total docs)
            )

            # Step 7: Display search results
            print(f"\n{'=' * 60}")
            print("SEARCH RESULTS")
            print("=" * 60)

            # Check if we got any results
            if results['documents'] and results['documents'][0]:
                # Display each result with relevance score
                for i, (doc, distance) in enumerate(zip(results['documents'][0], results['distances'][0])):
                    # Convert distance to relevance score (lower distance = higher relevance)
                    relevance_score = 1 - distance

                    print(f"\nResult {i + 1} (Relevance Score: {relevance_score:.3f}):")
                    print("-" * 40)

                    # Show preview of document content (first 500 characters)
                    preview = doc[:500] + ("..." if len(doc) > 500 else "")
                    print(preview)
                    print()
            else:
                # No results found
                print("No relevant results found for your query.")
                print("Try rephrasing your question or check if the document contains related content.")

        except Exception as e:
            print(f"Error during query: {e}")

        # Step 8: Session completion
        print("\n" + "=" * 60)
        print("Session completed successfully!")
        print("=" * 60)

    except Exception as e:
        # Handle any unexpected errors
        print(f"An error occurred: {e}")
        print("Please check your ChromaDB configuration and try again.")
        print("Ensure your .env file contains valid CHROMADB_API_KEY and CHROMADB_TENANT")


# Entry point of the script
# This ensures the main function only runs when the script is executed directly
# (not when imported as a module)
if __name__ == "__main__":
    main()