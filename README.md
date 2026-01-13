# MultiRag Chat

MultiRag Chat is a Retrieval-Augmented Generation (RAG) chatbot application built with Streamlit and LangChain. It allows users to upload documents (PDF, TXT), creates a knowledge base, and lets users chat with an AI assistant that can retrieve information from these documents as well as perform web searches.

## Features

- **Document Ingestion**: Upload PDF and TXT files to create a local knowledge base.
- **RAG Capabilities**: The chatbot uses a retrieval pipeline to answer questions based on uploaded documents.
- **Web Search**: Integrated DuckDuckGo search for answering questions beyond the uploaded context.
- **Conversation History**: Persistent chat history using SQLite, with support for multiple conversation threads.
- **Modern UI**: A clean, ChatGPT-like interface built with Streamlit.

## Tech Stack

- **Frontend**: Streamlit
- **LLM Orchestration**: LangChain, LangGraph
- **LLM Provider**: Groq (Llama 3.1)
- **Database**: SQLite (for conversation history)
- **Search**: DuckDuckGo

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd multiRag
    ```

2.  **Create and activate a virtual environment (optional but recommended):**

    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install streamlit langchain langchain-core langchain-community langchain-groq langgraph langchain-aws python-dotenv pydantic requests duckduckgo-search
    ```

    _(Note: You may need to install other dependencies found in the code, such as `vconsoleprint` if it's a valid package, or remove it if unused.)_

4.  **Set up Environment Variables:**

    Create a `.env` file in the root directory and add your API keys:

    ```env
    GROQ_API_KEY=your_groq_api_key
    # Add other necessary keys (e.g., AWS keys if using Bedrock, though Groq is currently used in main.py)
    ```

## Usage

1.  **Run the application:**

    ```bash
    streamlit run frontend.py
    ```

2.  **Interact with the Chatbot:**
    - Open the provided local URL in your browser.
    - Use the sidebar to upload documents to the Knowledge Base.
    - Start a new conversation or switch between existing threads.
    - Chat with the assistant!

## Project Structure

- `frontend.py`: Main Streamlit application file handling the UI.
- `main.py`: Core logic for the LangGraph agent, tools, and LLM interaction.
- `ingestion_pipeline.py`: Script/module for processing uploaded documents.
- `retreiver_pipeline.py`: Module for retrieving relevant documents.
- `docs/`: Directory where uploaded documents are stored.
- `db/`: Directory for the vector database (created upon ingestion).
- `chatbot.db`: SQLite database for storing chat history.
