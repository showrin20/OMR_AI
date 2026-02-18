#!/usr/bin/env python3
"""
OMR Sheet Generator - FastAPI Application
Simplified version: PDF generation endpoint only
"""

import logging
import os
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from omr.pdf_converter import generate_omr_pdf
from omr.detector_enhanced import detect_omr_answers

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup paths
BASE_DIR = Path(__file__).parent
TMP_DIR = BASE_DIR / "tmp"
TMP_DIR.mkdir(exist_ok=True)

# Setup FastAPI app
app = FastAPI(
    title="OMR Sheet Generator",
    description="Generate customizable OMR sheets as PDF",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def index():
    """Serve the form to generate OMR sheet"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OMR Sheet Generator</title>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 600px; 
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            h1 { color: #333; margin-top: 0; }
            .form-group { 
                margin: 20px 0;
                display: flex;
                flex-direction: column;
            }
            label { 
                display: block; 
                margin-bottom: 8px; 
                font-weight: 600;
                color: #333;
            }
            input, select { 
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 16px;
                font-family: inherit;
            }
            button { 
                padding: 12px 30px; 
                background: #007bff; 
                color: white; 
                border: none; 
                cursor: pointer; 
                border-radius: 4px; 
                font-size: 16px;
                font-weight: 600;
                margin-top: 20px;
                transition: background 0.3s;
            }
            button:hover { 
                background: #0056b3; 
            }
            .info { 
                background: #e7f3ff;
                border-left: 4px solid #007bff;
                padding: 15px;
                border-radius: 4px;
                margin: 20px 0;
                font-size: 14px;
            }
            .steps {
                background: #f9f9f9;
                padding: 15px;
                border-radius: 4px;
                margin-top: 30px;
            }
            .steps h3 { margin-top: 0; }
            .steps ol { margin: 10px 0; padding-left: 20px; }
            .steps li { margin: 8px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📋 OMR Sheet Generator</h1>
            
            <div class="info">
                <strong>Generate a custom OMR (Answer) sheet and download as PDF</strong><br>
                Configure the number of questions and options, then download a ready-to-print PDF.
            </div>

            <form action="/generate-and-download-pdf" method="POST">
                <div class="form-group">
                    <label for="questions">Total Questions:</label>
                    <input type="number" id="questions" name="questions" value="50" min="1" max="200" required>
                </div>

                <div class="form-group">
                    <label for="options">Options per Question:</label>
                    <select id="options" name="options">
                        <option value="2">2 Options (A, B)</option>
                        <option value="3">3 Options (A, B, C)</option>
                        <option value="4" selected>4 Options (A, B, C, D)</option>
                        <option value="5">5 Options (A, B, C, D, E)</option>
                        <option value="6">6 Options (A, B, C, D, E, F)</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="columns">Grid Columns:</label>
                    <select id="columns" name="columns">
                        <option value="1">1 Column</option>
                        <option value="2" selected>2 Columns</option>
                        <option value="3">3 Columns</option>
                    </select>
                </div>

                <button type="submit">📥 Generate & Download PDF</button>
            </form>

            <div class="steps">
                <h3>How to use:</h3>
                <ol>
                    <li>Set the number of questions</li>
                    <li>Choose options per question</li>
                    <li>Select grid layout</li>
                    <li>Click "Generate & Download PDF"</li>
                    <li>Print the PDF</li>
                    <li>Students fill the bubbles with pen</li>
                </ol>
            </div>

            <hr style="margin: 40px 0; border: none; border-top: 1px solid #ddd;">
            
            <h2>📸 Scan & Detect Answers</h2>
            <p>Upload a filled OMR sheet to automatically detect answers.</p>
            
            <form id="scanForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="omrFile">Upload OMR Sheet (Image or PDF):</label>
                    <input type="file" id="omrFile" name="file" accept=".jpg,.jpeg,.png,.pdf" required>
                </div>

                <div class="form-group">
                    <label for="scanOptions">Options per Question:</label>
                    <select id="scanOptions" name="expected_options">
                        <option value="2">2 Options</option>
                        <option value="3">3 Options</option>
                        <option value="4" selected>4 Options</option>
                        <option value="5">5 Options</option>
                        <option value="6">6 Options</option>
                    </select>
                </div>

                <button type="submit" onclick="scanOMR(event)">🔍 Scan & Detect Answers</button>
            </form>

            <div id="scanResult" style="margin-top: 30px; display: none;"></div>
        </div>

        <script>
        async function scanOMR(event) {
            event.preventDefault();
            
            const fileInput = document.getElementById('omrFile');
            const optionsInput = document.getElementById('scanOptions');
            const resultDiv = document.getElementById('scanResult');
            
            if (!fileInput.files[0]) {
                alert('Please select a file');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('expected_options', optionsInput.value);
            
            try {
                resultDiv.innerHTML = '<p>⏳ Scanning OMR sheet...</p>';
                resultDiv.style.display = 'block';
                
                const response = await fetch('/scan-omr', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    let answersHTML = '<h3>✅ Detection Successful</h3>';
                    answersHTML += '<p><strong>Total Questions Detected:</strong> ' + data.total_questions + '</p>';
                    answersHTML += '<p><strong>Marked Answers:</strong> ' + data.detected_bubbles + '</p>';
                    answersHTML += '<h4>Answers Detected:</h4>';
                    answersHTML += '<div style="background: #f0f8ff; padding: 15px; border-radius: 4px; max-height: 300px; overflow-y: auto;"><pre>';
                    
                    const answers = data.detected_answers;
                    let answerText = '';
                    for (const [qnum, answer] of Object.entries(answers)) {
                        answerText += qnum + '.' + answer + '  ';
                        if (qnum % 5 === 0) answerText += '\n';
                    }
                    answersHTML += answerText;
                    answersHTML += '</pre></div>';
                    
                    resultDiv.innerHTML = answersHTML;
                } else {
                    resultDiv.innerHTML = '<div style="background: #ffe0e0; padding: 15px; border-radius: 4px; color: #c00;">';
                    resultDiv.innerHTML += '<strong>❌ Error:</strong> ' + (data.error || data.message) + '</div>';
                }
            } catch (error) {
                resultDiv.innerHTML = '<div style="background: #ffe0e0; padding: 15px; border-radius: 4px; color: #c00;">';
                resultDiv.innerHTML += '<strong>❌ Error:</strong> ' + error.message + '</div>';
            }
        }
        </script>
    </div>
    </body>
    </html>
    """


@app.post("/generate-and-download-pdf")
async def generate_and_download_pdf(
    questions: int = Form(50),
    options: int = Form(4),
    columns: int = Form(2)
):
    """
    Endpoint: Generate OMR PDF and return as downloadable file
    
    Parameters:
        - questions: Number of questions (1-200)
        - options: Options per question (2-6)
        - columns: Grid columns (1-3)
    
    Returns: PDF file download
    """
    try:
        # Validate inputs
        questions = max(1, min(questions, 200))
        options = max(2, min(options, 6))
        columns = max(1, min(columns, 3))
        
        logger.info(f"Generating OMR: {questions} questions, {options} options, {columns} columns")
        
        # Create temporary PDF file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = str(TMP_DIR / f"omr_{timestamp}.pdf")
        
        # Generate PDF using pdf_converter module
        logger.info(f"Generating PDF: {pdf_path}")
        generate_omr_pdf(
            output_path=pdf_path,
            questions=questions,
            options=options,
            columns=columns
        )
        
        # Verify PDF was created
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file was not created: {pdf_path}")
            raise FileNotFoundError(f"PDF generation failed for {pdf_path}")
        
        logger.info(f"Returning PDF for download: {pdf_path}")
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"omr_sheet_{questions}q_{options}opt_{timestamp}.pdf"
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF: {e}", exc_info=True)
        return {
            "error": str(e),
            "message": "Failed to generate PDF"
        }


@app.post("/scan-omr")
async def scan_omr(
    file: UploadFile = File(...),
    expected_options: int = Form(4)
):
    """
    Endpoint: Scan a filled OMR sheet and detect answers
    
    Parameters:
        - file: OMR sheet image/PDF (JPEG, PNG, or PDF)
        - expected_options: Expected number of options per question (2-6)
    
    Returns: JSON with detected answers in format:
    {
        "status": "success",
        "student_id": "2130",
        "answers": {
            "1": "A",
            "2": "B",
            "3": "C",
            ...
        },
        "total_questions": 50,
        "detected_bubbles": 50
    }
    """
    try:
        # Validate inputs
        expected_options = max(2, min(expected_options, 6))
        
        logger.info(f"Scanning OMR sheet with {expected_options} expected options")
        
        # Save uploaded file temporarily
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = Path(file.filename).suffix.lower()
        temp_path = str(TMP_DIR / f"scan_{timestamp}{file_ext}")
        
        # Save file to disk
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Saved uploaded file: {temp_path}")
        
        # If PDF, convert to image first
        if file_ext == ".pdf":
            try:
                from pdf2image import convert_from_path
                images = convert_from_path(temp_path, first_page=1, last_page=1)
                if images:
                    import tempfile
                    png_path = str(TMP_DIR / f"scan_{timestamp}_page1.png")
                    images[0].save(png_path, "PNG")
                    temp_path = png_path
                    logger.info(f"Converted PDF to image: {png_path}")
            except ImportError:
                logger.error("pdf2image not installed, please install it: pip install pdf2image pillow")
                return JSONResponse(
                    status_code=400,
                    content={"error": "PDF processing not available", "message": "Please upload an image (PNG/JPEG) instead"}
                )
        
        # Detect OMR answers
        logger.info(f"Detecting answers from: {temp_path}")
        result = detect_omr_answers(temp_path, expected_options=expected_options)
        
        logger.info(f"Detection result: {result}")
        
        return {
            "status": "success",
            "detected_answers": result.get("detected_answers", {}),
            "total_questions": result.get("total_questions", 0),
            "detected_bubbles": len(result.get("detected_answers", {})),
            "raw_result": result
        }
        
    except Exception as e:
        logger.error(f"Error scanning OMR: {e}", exc_info=True)
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "error": str(e),
                "message": "Failed to scan OMR sheet"
            }
        )


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "service": "OMR Sheet Generator", "version": "1.0.0"}


@app.get("/info")
async def info():
    """Service information endpoint"""
    return {
        "name": "OMR Sheet Generator & Scanner",
        "version": "2.0.0",
        "description": "Generate customizable OMR sheets and scan filled sheets to detect answers",
        "endpoints": {
            "GET /": "HTML interface for OMR generation and scanning",
            "POST /generate-and-download-pdf": "Generate and download OMR PDF sheet",
            "POST /scan-omr": "Scan and detect answers from filled OMR sheet",
            "GET /health": "Health check",
            "GET /info": "Service information"
        }
    }


if __name__ == "__main__":
    print("Start the server with:")
    print("  uvicorn main:app --reload")
    print("\nThen open:")
    print("  http://localhost:8000")
