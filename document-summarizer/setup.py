from setuptools import setup, find_packages

setup(
    name="document-summarizer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.32.0",
        "python-docx>=1.1.0",
        "python-pptx>=0.6.21",
        "PyPDF2>=3.0.0",
        "pandas>=2.2.0",
        "openpyxl>=3.1.2",
        "faiss-cpu>=1.7.4",
        "google-generativeai>=0.3.2",
        "numpy>=1.24.0",
        "python-dotenv>=1.0.0",
        "sentence-transformers>=2.5.0",
        "plotly>=5.18.0"
    ],
    python_requires=">=3.8",
) 