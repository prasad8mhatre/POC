import os
import google.generativeai as genai
from typing import List, Dict, Any
import json

from src.utils.logger import setup_logger

class GeminiManager:
    """Manages interactions with Google's Gemini model."""
    
    def __init__(self):
        """Initialize the Gemini manager."""
        self.logger = setup_logger(__name__)
        self.logger.info("Initializing GeminiManager")
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            self.logger.error("GOOGLE_API_KEY not found in environment variables")
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        self.logger.debug("Successfully initialized Gemini API client")
    
    def generate_response(self, 
                         query: str,
                         context_chunks: List[Dict],
                         chat_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Generate a response using the Gemini model.
        
        Args:
            query (str): User's question
            context_chunks (List[Dict]): Relevant document chunks with metadata
            chat_history (List[Dict]): Previous chat messages
            
        Returns:
            dict: Response with text and structured data
        """
        try:
            self.logger.info(f"Generating response for query: {query}")
            
            # Prepare context from relevant chunks
            context = "\n\n".join([
                f"Document: {chunk['metadata']['filename']}\n{chunk['text']}"
                for chunk in context_chunks
            ])
            
            # Prepare chat history context
            history_context = ""
            if chat_history:
                self.logger.debug(f"Including {len(chat_history)} previous messages")
                history_context = "Previous conversation:\n" + "\n".join([
                    f"User: {msg['content']}" if msg['role'] == 'user'
                    else f"Assistant: {msg['content']['text']}"
                    for msg in chat_history[-3:]  # Include last 3 messages
                ])
            
            # Prepare prompt
            prompt = f"""You are a helpful AI assistant analyzing documents. Please help answer the following question based on the provided document excerpts.

Context from documents:
{context}

{history_context}

User's question: {query}

Please provide a response in the following JSON format:
{{
    "text": "Your detailed response here",
    "structured_data": {{
        "key_points": ["List of key points"],
        "statistics": {{"key": "value"}},  // Any relevant numerical data
        "categories": ["Relevant categories"],
        "sentiment": "positive/negative/neutral"
    }}
}}

Ensure the response is comprehensive and directly addresses the user's question using the provided context."""
            
            self.logger.debug("Sending request to Gemini API")
            response = self.model.generate_content(prompt)
            
            try:
                # Parse JSON response

                #self.logger.info(f"Response: {response.text}")
                response_text = response.text.replace("```json", "").replace("```", "")
                response_data = json.loads(response_text)
                self.logger.debug("Successfully parsed response JSON")
                return response_data
                
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse JSON response, returning raw text")
                return {
                    "text": response.text,
                    "structured_data": {
                        "key_points": [],
                        "statistics": {},
                        "categories": [],
                        "sentiment": "neutral"
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            raise 