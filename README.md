# PDF Q&A System with Llama2 and LangChain

A real-time PDF question-answering system built with FastAPI, Streamlit, and Llama2. The system allows users to upload PDF documents and ask questions about their content, receiving instant responses through WebSocket communication.

## 🌟 Features

- Real-time PDF document processing
- Interactive Q&A through WebSocket communication
- Rate limiting for system stability
- Clean text extraction using Beautiful Soup
- Error handling and connection management
- Streamlit-based user interface

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **WebSocket**: For real-time communication
- **AI Model**: Llama2 via Ollama
- **PDF Processing**: PyPDF2
- **Text Processing**: Beautiful Soup
- **AI Framework**: LangChain

## 📋 Prerequisites

- Python 3.8+
- Ollama installed and running locally
- LangChain API key (if using LangChain cloud features)

## 🏃‍♂️ Running the Application

1. Start the backend server:
```bash
uvicorn backend:app --reload
```

2. In a new terminal, start the frontend:
```bash
streamlit run frontend.py
```

## 📝 Usage

1. Upload a PDF file using the file upload button
2. Wait for the confirmation message
3. Type your question in the input field
4. Receive real-time responses about the PDF content

## ⚙️ Configuration

The system can be configured through environment variables:

- `LANGCHAIN_API_KEY`: Your LangChain API key
- `MAX_MESSAGES`: Maximum number of messages allowed in the time window (default: 2)
- `TIME_WINDOW`: Time window for rate limiting in seconds (default: 60)

## 🔒 Rate Limiting

The system implements rate limiting with:
- Maximum 2 messages per minute by default
- Configurable time window
- Graceful handling of limit exceeded cases

## 🛑 Error Handling

The system handles various error cases:
- PDF processing errors
- WebSocket disconnections
- Rate limit exceeded
- Invalid queries
- Model response errors
