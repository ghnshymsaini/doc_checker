from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import os
import shutil
import uuid
import fitz # PyMuPDF for PDF processing
import spacy

# Initialize FastAPI app
app = FastAPI(title="AI Python Developer Assessment (checks compliance against English guidelines)")

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# "uploaded_files" will temporarily hold the incoming PDF
UPLOAD_DIR = "uploaded_files"
# "processed_texts" will store the extracted plain text for compliance checks and modifications
PROCESSED_TEXT_DIR = "processed_texts" 

# Creating directories assuming they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_TEXT_DIR, exist_ok=True)

# PDF Text Extraction
def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text() + "\n" 
        doc.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing error: {e}. "
                                                     "Please ensure it's a valid, unencrypted PDF.")
    return text.strip()

# Pydantic Models for API Data Structure
class ComplianceReport(BaseModel):
    status: str
    summary: str
    issues: list[dict] # A list of dictionaries, each describing a specific issue
    original_filename: str
    processed_text_id: str

class ModificationRequest(BaseModel):
    processed_text_id: str
    phrase_to_find: str
    replacement_phrase: str

# FastAPI Endpoints
@app.post("/upload_and_check/", response_model=ComplianceReport)
async def upload_and_check_document(file: UploadFile = File(...)):
    
    # Validate file type: Ensure it's a PDF
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail=f"Unsupported file type. "
                                                     f"Please upload a PDF file. Received: {file.content_type}")

    # Save the uploaded PDF temporarily
    unique_file_id = str(uuid.uuid4()) 
    # Store the PDF with its unique ID in the UPLOAD_DIR
    temp_pdf_path = os.path.join(UPLOAD_DIR, f"{unique_file_id}.pdf")

    try:
        with open(temp_pdf_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded PDF file: {e}")

    # Extract text from the temporary PDF
    extracted_text = extract_text_from_pdf(temp_pdf_path)

    # Basic AI Agent (SpaCy) Checks
    compliance_issues = []
    doc = nlp(extracted_text)

    # Rule 1: Flag sentences longer than 20 words as a clarity concern
    for i, sent in enumerate(doc.sents):
        if len(sent.text.split()) > 20: 
            compliance_issues.append({
                "type": "Clarity/Length",
                "sentence_index": i, 
                "original_text": sent.text,
                "suggestion": "Very long sentence. Consider shorten it for better clarity."
            })

    # Rule 2: Flag the adjective "English" as vague, suggesting alternatives
    for token in doc: 
        # Check if the token is an adjective and specifically the word "good"
        if token.lower_ == "English" and token.pos_ == "ADJ":
            compliance_issues.append({
                "type": "Vocabulary/Vagueness",
                "word": token.text, 
                "suggestion": f"'{token.text}' is vague. Consider stronger alternatives like 'ENGLISH', 'ENGlish'."
            })

    # Generate a summary of findings
    summary = f"After Analyzing PDF: '{file.filename}'. Observed {len(compliance_issues)} compliance issues."
    if not compliance_issues:
        summary = "PDF seems compliant with basic checks and no issues found."

    # Save the extracted plain text to a .txt file
    text_file_name = f"{unique_file_id}.txt"
    processed_text_file_path = os.path.join(PROCESSED_TEXT_DIR, text_file_name)
    try:
        with open(processed_text_file_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)
    except Exception as e:
        print(f"Warning: Not able to save processed text to '{processed_text_file_path}': {e}")

    # Delete the temporarily stored uploaded PDF file
    try:
        os.remove(temp_pdf_path)
    except OSError as e:
        print(f"Error removing temporary uploaded PDF file '{temp_pdf_path}': {e}")

    # Return the compliance report
    return ComplianceReport(
        status="success",
        summary=summary,
        issues=compliance_issues,
        original_filename=file.filename,
        processed_text_id=unique_file_id
    )

@app.post("/modify_document_text/")
async def modify_document_text(request: ModificationRequest):

    # Construct the path to the previously saved extracted text file
    text_file_path = os.path.join(PROCESSED_TEXT_DIR, f"{request.processed_text_id}.txt")

    # Verify if the text file exists
    if not os.path.exists(text_file_path):
        raise HTTPException(status_code=404, detail=f"Processed text with ID '{request.processed_text_id}' not found. "
                                                     "Please ensure you've uploaded a document successfully and used a valid ID.")

    # Read the original extracted text content
    try:
        with open(text_file_path, "r", encoding="utf-8") as f:
            original_text = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read original text for modification: {e}")

    # Apply the simple find-and-replace modification
    modified_text = original_text.replace(request.phrase_to_find, request.replacement_phrase)

    # Save the modified text to a new .txt file
    modified_file_name = f"modified_{request.processed_text_id}.txt"
    modified_file_path = os.path.join(PROCESSED_TEXT_DIR, modified_file_name)
    try:
        with open(modified_file_path, "w", encoding="utf-8") as f:
            f.write(modified_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save modified text to file: {e}")

    # Return the modified text file for download
    return FileResponse(
        path=modified_file_path,
        filename=modified_file_name,
        media_type="text/plain" 
    )