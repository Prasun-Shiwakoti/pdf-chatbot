import fitz

from collections import defaultdict
from openai import OpenAI
from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi import File, UploadFile
from sqlalchemy.orm import Session
from models import SessionLocal, Document
import os
from dotenv import load_dotenv

load_dotenv()

# Load the OpenAI API key from the environment variables
API_KEY = os.getenv("HUGGINGFACE_API_KEY")

client = OpenAI(
	base_url="https://api-inference.huggingface.co/v1/",
	api_key=API_KEY
)

# Create a dictionary to store the message history for each document
messages = defaultdict(list)
router = APIRouter()

def getChat(question, document_id):
    global messages
    # Append the user's question to the message history for the specified document
    messages[document_id].append(
        {
            "role": 'user',
            "content": question,
        }
    )
    try:
        #  Call the OpenAI API to generate a response to the user's question
        completion = client.chat.completions.create(
            model="microsoft/Phi-3-mini-4k-instruct", 
            messages=messages[document_id], 
            temperature=0.5,  
            max_tokens=200,   
            top_p=0.7        
        )
        response = completion.choices[0].message.content
        # Append the assistant's response to the message history
        messages[document_id].append(
            {
                "role": 'assistant',
                "content": response,
            }
        )
        # Print token usage statistics for monitoring purposes
        print(completion.usage.completion_tokens, completion.usage.prompt_tokens, completion.usage.total_tokens)
        
        # Ensure that total tokens do not exceed a certain limit (4000)
        while completion.usage.total_tokens > 4000:
            messages[document_id].pop()  # Remove the oldest message to stay within list
            
    except Exception as e:
        print(e)  
        response = "There was an error processing the question. Please try again later."

    return response 


def get_db():
    # Create a new database session for each request
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/documents/") 
async def read_documents(db: Session = Depends(get_db)):
    # Show all documents in the database
    documents = db.query(Document).all() 
    return documents 


@router.post("/upload/") 
async def create_document(doc: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        file_path = f"./uploads/{doc.filename}"

        with open(file_path, "wb") as buffer:
            buffer.write(doc.file.read())

        # Open the saved PDF document using PyMuPDF (fitz)
        pdf_document = fitz.open(file_path)
        extracted_text = ""
        
        # Extract text from each page of the PDF
        for page in pdf_document:
            extracted_text += page.get_text()

        db_document = Document(filename=doc.filename, file_path=file_path, extracted_text=extracted_text)

        # Add the new document to the database session and commit the changes
        db.add(db_document)
        db.commit()
        
        # Refresh the instance to get the updated state (e.g., ID)
        db.refresh(db_document)

    except Exception as e:
        return {"message": "There was an error uploading the file", 'error': f'{e}'}
    
    finally:
        doc.file.close()

    # Return a success message along with the document ID and filename
    return {"message": "Successfully uploaded", "document_id": db_document.id, "filename": db_document.filename}


@router.post("/answer/", response_model=dict)
async def answer_question(document_id: str = Form(...), question: str = Form(...), db: Session = Depends(get_db)):
    global messages
    
    # Retrieve the document from the database using the provided document ID
    db_document = db.query(Document).filter(Document.id == int(document_id)).first()
    
    # Raise a 404 error if the document is not found
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Extract the context text from the retrieved document
    context = db_document.extracted_text
    
    # Initialize the messages list with the context for the model
    if not messages[document_id]:
        messages[document_id].append(
            {
                "role": 'system',
                "content": f"You are a helpful AI assistant. Always reply based on the context provided.\nContext: {context}",
            }
        )

    
    # Call the getChat function to get a response based on the user's question and context
    response = getChat(question, document_id)

    return {"answer": response}