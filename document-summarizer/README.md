# Document Summarizer

A Streamlit-based application for processing, indexing, and querying multiple document types with a chat-like interface. The application uses FAISS for efficient document indexing and Google's Gemini model for generating responses.

## Features

- Multi-format document support (PDF, Excel, PowerPoint, Word, Text)
- Document parsing and chunking
- FAISS-based document indexing
- Chat interface with Google Gemini integration
- Document visualization capabilities

## Project Structure

```
document-summariser/
├── src/
│   ├── parsers/        # Document parsing modules
│   ├── embeddings/     # Text embedding generation
│   ├── indexing/       # FAISS index management
│   ├── ui/            # Streamlit UI components
│   └── utils/         # Utility functions
├── tests/             # Test files
├── docs/              # Documentation
├── app.py            # Main entry point
├── requirements.txt   # Project dependencies
└── README.md         # This file
```

## Setup Instructions

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # or
   .\venv\Scripts\activate  # On Windows
   ```

2. Install the package in development mode:
   ```bash
   pip install -e .
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory with:
   ```
   GOOGLE_API_KEY=your_google_api_key
   ```

4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Development

- The application is built without using frameworks like LangChain
- Uses FAISS for efficient similarity search
- Implements custom document processing pipeline
- Integrates Google Gemini for response generation

## License

MIT License 