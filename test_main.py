from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)

os.makedirs("uploaded_files", exist_ok=True)
os.makedirs("processed_texts", exist_ok=True)

def test_upload_and_check_pdf_success():
    # Test case: Lets upload a non-PDF file
    response = client.post(
        "/upload_and_check/",
        files={"file": ("test.txt", b"This is not a PDF file.", "text/plain")}
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]

def test_modify_document_text_not_found():
    # Test case: Requesting modification for a non-existent ID
    response = client.post(
        "/modify_document_text/",
        json={
            "processed_text_id": "non-existent-id",
            "phrase_to_find": "abc",
            "replacement_phrase": "xyz"
        }
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]