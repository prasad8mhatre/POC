"""Configuration settings for the application."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

# Model Configuration
GEMINI_MODEL_NAME = 'gemini-2.0-flash'

# App Configuration
APP_TITLE = "StoryViz AI - Visual Business Storytelling"
APP_DESCRIPTION = """Transform your business narratives into compelling visual stories. 
Write your content, select key points, and let AI create professional visualizations that enhance your message."""

# UI Configuration
EDITOR_HEIGHT = 400
SELECTION_HEIGHT = 100
DEFAULT_COLUMN_RATIO = [2, 1]  # Left column : Right column ratio

# Styling
THEME_COLOR = "#1E88E5"  # Professional blue
SECONDARY_COLOR = "#FFC107"  # Accent color for highlights 