# PDF Q&A Application

This is a full-stack application that allows users to upload PDF documents and ask questions about the content. The application extracts text from the uploaded PDFs and uses Natural Language Processing (NLP) to answer user queries. The backend is built using FastAPI, and the frontend is built using React.js.

---

## **Table of Contents**
- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [API Documentation](#api-documentation)
- [Usage](#usage)
- [Technologies Used](#technologies-used)

---

## **Features**
- Upload PDF files and store them locally.
- Ask questions related to the content of the PDF.
- Retrieve answers based on text extraction from the uploaded PDF.
- Friendly and intuitive user interface.

---

## **Architecture Overview**

The application follows a typical full-stack architecture:

1. **Frontend**:
   - Built using React.js.
   - Contains components for PDF uploads, question input, and answer display.
   - Makes API calls to the FastAPI backend for processing.
   
2. **Backend**:
   - Built using FastAPI.
   - Handles PDF uploads, text extraction, and question-answering logic.
   - Uses a pre-trained model (Phi-3-mini-4k-instruct) for processing text-based queries.
   
3. **Database**:
   - SQLite (for storing metadata about uploaded PDFs).
   
4. **File Storage**:
   - PDF files are stored on the local filesystem.

---

## **Prerequisites**
- Python 3.8+
- Node.js and npm (for the React frontend)
- FastAPI (backend)
- SQLite or PostgreSQL (for database, optional)
- HuggingFase API key

---

## **Installation**

### 1. Clone the repository:

```bash
git clone https://github.com/Prasun-Shiwakoti/pdf-chatbot
cd pdf-chatbot
```

### 2. Backend Setup (FastAPI)
1. Navigate into app directory.
    ```bash
    cd app
    ```
2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```

3. Install required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file and add your Hugging Face API key:
    ```makefile
    HUGGINGFACE_API_KEY=your_huggingface_api_key_here
    ```
5. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
     By default, the FastAPI server will run on `http://127.0.0.1:8000`.

### 3. Frontend Setup (React)

1. Open another terminal inside `frontend` folder:
   ```bash
   cd frontend
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   ```

3. Run the React app:
   ```bash
   npm start
   ```
      The React app will run on `http://localhost:3000`. 
---

## **API Documentation**

### 1. **Upload PDF**

- **URL**: `/upload/`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Request Body**: PDF file
- **Response**: JSON object with document ID and filename.
  
  Example:
  ```json
  {
    "message": "Successfully uploaded", "document_id": "1", 
    "filename": "sample_document.pdf"
  }
  ```

### 2. **Ask a Question**

- **URL**: `/answer/`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "document_id": "1",
    "question": "What is the price of the car?"
  }
  ```
- **Response**: JSON object with the answer.

  Example:
  ```json
  {
    "answer": "The price of the car is $20,000."
  }
  ```

---

## **Usage**
    
1. **Upload PDF**: 
   - Open the React app in the browser (http://localhost:3000/)
   - Use the file upload interface to select and upload a PDF.
   
2. **Ask Questions**: 
   - After uploading the PDF, use the question input to type in your questions.
   - The application will process the question and display the answer.

---

## **Technologies Used**

- **Frontend**: React.js, Axios
- **Backend**: FastAPI, PyMuPDF (for text extraction), OpenAI (for NLP), Hugging Face Transformers
- **Database**: SQLite
- **File Storage**: Local filesystem 

---