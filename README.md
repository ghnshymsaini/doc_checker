# PDF Compliance Checker (AI Developer Assessment)

## Key Features

* **PDF Document Upload:** Accepts PDF files via a FastAPI endpoint.
* **Text Extraction:** Extracts plain text content from uploaded PDFs using PyMuPDF.
* **Compliance Checks:** Utilizes SpaCy library to perform foundational checks against English guidelines:
    * **Used 2 self complied rules these are**
    * **Sentence Length Analysis:** Flags sentences exceeding 20 words as a clarity concern.
    * **Vocabulary Assessment:** Identifies vague adjectives like "English" and suggests stronger alternatives.
* **Modified Text Download:** Returns the modified text content as a new plain `.txt` file.

## Technologies Used

* **Python:**
* **FastAPI:** A modern, fast (high-performance) web framework for building APIs with Python.
* **Uvicorn:** An ASGI server, used to run the FastAPI application.
* **Pydantic:** Used for data validation and settings management with Python type hints.
* **PyMuPDF :** A highly efficient library for working with PDF documents, used here for robust text extraction.
* **SpaCy:** A Natural Language Processing (NLP) library, utilized for tokenization, sentence segmentation, and Part-of-Speech (POS) tagging to implement basic AI compliance rules.

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


## Setup Instructions

Follow these steps to get the project running locally:

1.  **Clone the Repository:**
    ```
    git clone [https://github.com/ghnshymsaini/doc_checker.git](https://github.com/ghnshymsaini/doc_checker.git)
    cd doc_checker
    ```

2.  **Create a Virtual Environment:**
    ```
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:**
    * **Windows:**
        ```
        .\venv\Scripts\Activate
        ```
   
4.  **Install Dependencies:**
    ```
    pip install -r requirements.txt
    ```
    
5.  **Download SpaCy Language Model:**
    ```
    python -m spacy download en_core_web_sm
    ```

## How to Run the Application

1.  **Start the FastAPI Server:**
    Ensure your virtual environment is activated, then run:
    ```
    uvicorn main:app --reload
    ```
    The server will typically run on `http://127.0.0.1:8000`. Keep this terminal open.

## API Endpoints & Usage (with Postman)

### 1. Upload Document for Compliance Check

* **Endpoint:** `POST /upload_and_check/`
* **URL:** `http://127.0.0.1:8000/upload_and_check/`
* **Headers:**
    * `Accept: application/json`
* **Body:**
    * Select `form-data`.
    * Add a `Key`: `file` (Type: `File`).
    * Select `sample.pdf` file.

* **Response:** A JSON object containing `status`, `summary`, `issues` (a list of detected compliance problems), `original_filename`, and a `processed_text_id`. **Copy this `processed_text_id` for the next step.**
    

### 2. Request Document Text Modification

* **Endpoint:** `POST /modify_document_text/`
* **URL:** `http://127.0.0.1:8000/modify_document_text/`
* **Headers:**
    * `Content-Type: application/json`
* **Body:**
    * Select `raw` and choose `JSON`.
    * Provide the `processed_text_id` obtained from the previous step, along with the `phrase_to_find` and `replacement_phrase`.

    ```json
    {
      "processed_text_id": "YOUR_COPIED_ID_HERE",
      "phrase_to_find": "good",
      "replacement_phrase": "excellent"
    }
    ```
* **Response:** The plain text content of the modified document (a `.txt` file) will be returned directly.
    

---

## Testing

Basic tests are included to ensure core API functionality.

**Run tests:**
    ```terminal
    pytest
    ```

This project is a time constrained for assessment purposes, So, it has intentional assumptions as below:

* **PDF-Only Input:** The system currently supports only PDF file uploads.
* **Plain Text Output for Modification:** Modified content is provided as a plain `.txt` file.
* **Basic AI Rules:** Currently implements only two illustrative rules (sentence length, vague vocabulary).
