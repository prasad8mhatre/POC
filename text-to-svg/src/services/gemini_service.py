"""Service for interacting with Google's Gemini AI model."""
import json
import re
from typing import List, Dict, Optional

import google.generativeai as genai
import streamlit as st

from src.config.settings import GOOGLE_API_KEY, GEMINI_MODEL_NAME
from src.utils.prompt_loader import PromptLoader
from src.utils.logger import get_logger

logger = get_logger("gemini_service")

class GeminiService:
    """Service class for handling Gemini AI model interactions."""
    
    def __init__(self):
        """Initialize the Gemini service."""
        logger.info("Initializing GeminiService")
        self._configure_api()
        self.model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        self.prompt_loader = PromptLoader()
        logger.debug(f"Using model: {GEMINI_MODEL_NAME}")
    
    @staticmethod
    def _configure_api():
        """Configure the Gemini API with credentials."""
        logger.debug("Configuring Gemini API")
        genai.configure(api_key=GOOGLE_API_KEY)
    
    def _create_visualization_prompt(self, text: str) -> str:
        """Create the prompt for generating visualizations.
        
        Args:
            text: The text to create visualizations for.
            
        Returns:
            str: The formatted prompt for the model.
        """
        logger.debug("Creating visualization prompt")
        return self.prompt_loader.format_prompt(
            'visualization_generation',
            text=text
        )

    def _parse_response(self, response_text: str) -> List[Dict[str, str]]:
        """Parse the model's response to extract visualizations.
        
        Args:
            response_text: The raw response text from the model.
            
        Returns:
            List[Dict[str, str]]: List of visualization dictionaries.
        """
        logger.debug("Parsing model response")
        try:
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                visualizations = json.loads(json_match.group())
                logger.info(f"Successfully parsed {len(visualizations)} visualizations")
                return visualizations
            logger.warning("No JSON array found in response")
            return []
        except Exception as e:
            logger.error(f"Error parsing visualizations: {str(e)}", exc_info=True)
            st.error(f"Error parsing visualizations: {str(e)}")
            return []

    def generate_visualizations(self, text: str) -> List[Dict[str, str]]:
        """Generate SVG visualizations for the given text.
        
        Args:
            text: The text to create visualizations for.
            
        Returns:
            List[Dict[str, str]]: List of dictionaries containing visualization data.
        """
        if not text.strip():
            logger.warning("Empty text provided for visualization generation")
            return []
            
        try:
            logger.info("Generating visualizations for text")
            prompt = self._create_visualization_prompt(text)
            logger.debug(f"Prompt length: {len(prompt)} characters")
            
            response = self.model.generate_content(prompt)
            logger.debug("Received response from model")
            
            return self._parse_response(response.text)
        except Exception as e:
            logger.error(f"Error generating visualizations: {str(e)}", exc_info=True)
            st.error(f"Error generating visualizations: {str(e)}")
            return [] 