# Document RAG - Setup Guide

## Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd DocumentRAG
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```
   
2. Edit the `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

3. Get your OpenAI API key from: https://platform.openai.com/api-keys

### 4. Run the Application
```bash
streamlit run main.py
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key for accessing GPT models |
| `OPENAI_ORG_ID` | No | Organization ID (if you belong to multiple orgs) |
| `OPENAI_PROJECT_ID` | No | Project ID for usage tracking |

## Features

- 📄 Upload and preview PDF documents
- 🤖 Chat with your PDF using OpenAI's GPT-4
- 🔍 File search capabilities for accurate document-based responses
- 💬 Interactive Streamlit interface

## Troubleshooting

- Make sure your OpenAI API key is valid and has sufficient credits
- Ensure all dependencies are installed correctly
- Check that your PDF file is not corrupted or password-protected
