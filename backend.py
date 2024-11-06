from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
import os
import PyPDF2
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
from dotenv import load_dotenv
import asyncio
from collections import deque
from datetime import datetime, timedelta

app = FastAPI()

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

# Initialize LangChain components
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert assistant with access to a PDF file uploaded by the user. Answer only based on the content of this PDF. Provide detailed, direct answers and cite relevant parts of the document where applicable. If the answer is not clearly found in the document, respond by indicating that it is not explicitly covered in the file."),
        ("user", "Question: {question}")
    ]
)

llm = Ollama(model="llama2")
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# Store uploaded PDF content in memory
pdf_content = ""

# Rate limit settings
MAX_MESSAGES = 1  # Max messages allowed
TIME_WINDOW = 120  # Time window in seconds

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global pdf_content
    # Save file temporarily
    file_path = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Read and process PDF content
    pdf_reader = PyPDF2.PdfReader(file_path)
    pdf_text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        pdf_text += page.extract_text()
    
    # Use BeautifulSoup for cleaner text extraction
    soup = BeautifulSoup(pdf_text, 'html.parser')
    pdf_content = soup.get_text()
    
    return {"message": "File uploaded and processed successfully"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Create a deque to store timestamps of recent messages
    message_timestamps = deque()
    
    try:
        while True:
            # Check if the client has disconnected
            try:
                data = await websocket.receive_text()
            except WebSocketDisconnect:
                print("Client disconnected")
                break
            
            # Keep track of message rate
            current_time = datetime.now()
            while message_timestamps and (current_time - message_timestamps[0]).total_seconds() > TIME_WINDOW:
                message_timestamps.popleft()
            
            # If rate limit exceeded, inform the client
            if len(message_timestamps) >= MAX_MESSAGES:
                await websocket.send_text("Rate limit exceeded. Please wait before sending more messages.")
                await asyncio.sleep(TIME_WINDOW - (current_time - message_timestamps[0]).total_seconds())
                continue
            
            # Log the time of this message
            message_timestamps.append(current_time)
            
            # Process the query and send the response
            try:
                response = chain.invoke({"question": data, "context": pdf_content})
                await websocket.send_text(response)
            except Exception as e:
                # Catch any processing errors and send an error message
                if not websocket.client_state.closed:
                    await websocket.send_text(f"An error occurred: {str(e)}")
            
    except WebSocketDisconnect:
        print("WebSocket disconnected")

    except Exception as e:
        print(f"Unexpected error: {e}")
