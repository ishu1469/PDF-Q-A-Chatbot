import streamlit as st
import requests
import websocket
import json

# Initialize Streamlit UI
st.title('Langchain Demo with Llama2 API')
pdf_file = st.file_uploader("Upload a PDF file", type="pdf")

# URL of the backend server
BACKEND_URL = "http://localhost:8000"

# Upload the PDF file
if pdf_file is not None:
    files = {'file': pdf_file}
    response = requests.post(f"{BACKEND_URL}/upload", files=files)
    if response.status_code == 200:
        st.success("File uploaded and processed successfully.")
    else:
        st.error("File upload failed.")

# WebSocket connection using session state
if "ws" not in st.session_state:
    try:
        ws = websocket.WebSocket()
        ws.connect("ws://localhost:8000/ws")
        st.session_state["ws"] = ws  # Save the WebSocket in session state
        st.success("Connected to WebSocket successfully.")
    except Exception as e:
        st.error(f"Could not connect to WebSocket: {e}")

# Function to send query via WebSocket and get response
def send_query(query):
    ws = st.session_state.get("ws")  # Get the WebSocket from session state
    if ws is None or not ws.connected:
        # Reconnect if needed
        try:
            ws = websocket.WebSocket()
            ws.connect("ws://localhost:8000/ws")
            st.session_state["ws"] = ws
        except Exception as e:
            st.error(f"WebSocket connection error: {e}")
            return None
    try:
        ws.send(query)  # Send the query to the WebSocket server
        response = ws.recv()  # Receive the response
        return response
    except Exception as e:
        st.error(f"An error occurred while sending the query: {e}")
        return None

# Allow user to input a query and display response
input_text = st.text_input("Search the topic you want")
if input_text:
    response = send_query(input_text)
    if response:
        st.write("Response:", response)
    else:
        st.error("No response received from the server.")
