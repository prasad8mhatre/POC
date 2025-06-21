# Text-to-SVG Document Editor

An interactive document editor that generates SVG visualizations from selected text using Google's Gemini AI model.

## Project Structure

```
text-to-svg/
├── src/
│   ├── components/         # UI components
│   │   ├── document_editor.py
│   │   └── visualization_panel.py
│   ├── config/            # Configuration settings
│   │   └── settings.py
│   ├── services/          # External service integrations
│   │   └── gemini_service.py
│   ├── utils/             # Utility functions and classes
│   │   └── state_manager.py
│   └── app.py            # Main application entry point
├── requirements.txt      # Project dependencies
└── README.md            # Project documentation
```

## Features

- Google Docs-like text editor interface
- Text selection for visualization generation
- AI-powered SVG visualization generation
- Multiple visualization options
- Ability to insert visualizations into the document

## Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd text-to-svg
```

2. Install uv (if not already installed):
```bash
pip install uv
```

3. Create a virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
uv pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

5. Run the Streamlit app:
```bash
streamlit run src/app.py
```

## Usage

1. Write or paste your content in the document editor on the left side
2. Select the text you want to visualize
3. Copy the selected text to the "Selected Text" box
4. Click "Generate Visualizations" to get AI-generated visualization options
5. Choose your preferred visualization to insert it into the document

## Project Organization

- `components/`: Contains reusable UI components
- `config/`: Application configuration and settings
- `services/`: External service integrations (e.g., Gemini AI)
- `utils/`: Utility functions and helper classes
- `app.py`: Main application entry point

## Requirements

- Python 3.7+
- Streamlit
- Google Generative AI
- Python-dotenv
- SVGwrite

## Note

Make sure you have a valid Google API key with access to the Gemini model. You can obtain one from the Google AI Studio. 