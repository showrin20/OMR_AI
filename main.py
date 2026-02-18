"""
OMR Service - Generate OMR Sheets as PDF
"""

import logging
import os
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from omr.pdf_converter import generate_omr_pdf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
TMP_DIR = BASE_DIR / "tmp"
TMP_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="OMR Service",
    description="Generate OMR sheets and download as PDF",
    version="1.0.0"
)

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────
# Main Endpoint
# ─────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def index():
    """Serve the form to generate OMR sheet"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OMR Sheet Generator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; }
            .form-group { margin: 20px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input { padding: 10px; width: 100%; max-width: 300px; }
            button { padding: 10px 30px; background: #007bff; color: white; border: none; cursor: pointer; border-radius: 5px; font-size: 16px; }
            button:hover { background: #0056b3; }
            .info { background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>📋 OMR Sheet Generator</h1>
        
        <div class="info">
            <p><strong>Generate a custom OMR (Answer) sheet and download as PDF</strong></p>
            <p>Configure the number of questions and options, then download as a ready-to-print PDF.</p>
        </div>

        <form action="/generate-and-download-pdf" method="POST">
            <div class="form-group">
                <label for="questions">Total Questions:</label>
                <input type="number" id="questions" name="questions" value="50" min="1" max="200" required>
            </div>

            <div class="form-group">
                <label for="options">Options per Question:</label>
                <select id="options" name="options" style="padding: 10px; width: 100%; max-width: 300px;">
                    <option value="2">2 (A, B)</option>
                    <option value="3">3 (A, B, C)</option>
                    <option value="4" selected>4 (A, B, C, D)</option>
                    <option value="5">5 (A, B, C, D, E)</option>
                    <option value="6">6 (A, B, C, D, E, F)</option>
                </select>
            </div>

            <div class="form-group">
                <label for="columns">Grid Columns:</label>
                <select id="columns" name="columns" style="padding: 10px; width: 100%; max-width: 300px;">
                    <option value="1">1 Column</option>
                    <option value="2" selected>2 Columns</option>
                    <option value="3">3 Columns</option>
                </select>
            </div>

            <button type="submit">📥 Generate & Download PDF</button>
        </form>

        <div class="info" style="margin-top: 40px;">
            <h3>How to use:</h3>
            <ol>
                <li>Set the number of questions (e.g., 50)</li>
                <li>Choose options per question (e.g., A, B, C, D)</li>
                <li>Select grid layout (1, 2, or 3 columns)</li>
                <li>Click "Generate & Download PDF"</li>
                <li>Print the PDF</li>
                <li>Students fill the bubbles with pen</li>
                <li>Scan the completed sheet</li>
                <li>Upload for automatic evaluation</li>
            </ol>
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
    Main Endpoint: Generate OMR HTML and return as PDF download
    
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
        
        # Generate HTML from template
        options_list = ["A", "B", "C", "D", "E", "F"][:options]
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Answer Sheet</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Bebas+Neue&display=swap');

    :root {{
      --bg: #f5f0e8;
      --ink: #1a1a1a;
      --border: #1a1a1a;
      --bubble-size: 28px;
      --row-gap: 10px;
      --accent: #c0392b;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      background: var(--bg);
      font-family: 'DM Mono', monospace;
      color: var(--ink);
      padding: 30px;
      min-height: 100vh;
    }}

    .sheet-wrapper {{
      max-width: 860px;
      margin: 0 auto;
      background: #fff;
      border: 2px solid var(--border);
      padding: 36px 40px 40px;
      box-shadow: 6px 6px 0 var(--ink);
    }}

    .sheet-header {{
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      border-bottom: 3px solid var(--ink);
      padding-bottom: 16px;
      margin-bottom: 28px;
      gap: 20px;
    }}

    .sheet-title {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: 2.6rem;
      letter-spacing: 0.06em;
      line-height: 1;
    }}

    .sheet-meta {{
      display: flex;
      flex-direction: column;
      gap: 8px;
      font-size: 0.78rem;
      letter-spacing: 0.04em;
    }}

    .meta-field {{
      display: flex;
      gap: 8px;
      align-items: center;
    }}

    .meta-label {{
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      opacity: 0.55;
      white-space: nowrap;
    }}

    .meta-line {{
      width: 140px;
      border-bottom: 1.5px solid var(--ink);
      height: 18px;
    }}

    .instructions {{
      font-size: 0.72rem;
      letter-spacing: 0.03em;
      line-height: 1.7;
      opacity: 0.6;
      margin-bottom: 28px;
      border-left: 3px solid var(--accent);
      padding-left: 12px;
    }}

    .questions-grid {{
      display: grid;
      gap: var(--row-gap) 32px;
    }}

    .q-row {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .q-num {{
      font-size: 0.72rem;
      letter-spacing: 0.05em;
      width: 28px;
      text-align: right;
      opacity: 0.5;
      flex-shrink: 0;
    }}

    .bubbles {{
      display: flex;
      gap: 7px;
    }}

    .bubble {{
      width: var(--bubble-size);
      height: var(--bubble-size);
      border-radius: 50%;
      border: 2px solid var(--ink);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.65rem;
      font-weight: 500;
      letter-spacing: 0.05em;
      cursor: pointer;
      transition: background 0.15s, color 0.15s;
      user-select: none;
      position: relative;
    }}

    .bubble:hover {{
      background: #eee;
    }}

    .bubble.filled {{
      background: var(--ink);
      color: #fff;
    }}

    .sheet-footer {{
      margin-top: 32px;
      border-top: 2px solid var(--ink);
      padding-top: 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.68rem;
      letter-spacing: 0.06em;
      opacity: 0.45;
    }}

    @media print {{
      body {{ background: #fff; padding: 0; }}
      .sheet-wrapper {{ box-shadow: none; border: 1px solid #000; }}
      .bubble {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
      .bubble.filled {{ background: #000 !important; color: #fff !important; }}
    }}

    @media (min-width: 560px) {{
      .questions-grid {{ grid-template-columns: repeat(var(--cols, {columns}), 1fr); }}
    }}
    @media (max-width: 559px) {{
      .questions-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>

<div class="sheet-wrapper" id="sheet">

  <div class="sheet-header">
    <div class="sheet-title">Answer<br>Sheet</div>
    <div class="sheet-meta">
      <div class="meta-field"><span class="meta-label">Name</span><div class="meta-line"></div></div>
      <div class="meta-field"><span class="meta-label">Date</span><div class="meta-line"></div></div>
      <div class="meta-field"><span class="meta-label">Score</span><div class="meta-line"></div></div>
    </div>
  </div>

  <p class="instructions">
    Use a dark pen or pencil. Fill the bubble completely for your chosen answer.<br>
    To change an answer, cross out the old bubble and fill the correct one.
  </p>

  <div class="questions-grid" id="questionsGrid"></div>

  <div class="sheet-footer">
    <span id="footerTotal"></span>
    <span>© Answer Sheet Template</span>
  </div>

</div>

<script>
  const TOTAL_QUESTIONS = {questions};
  const OPTIONS = {repr(options_list)};
  const COLUMNS = {columns};

  document.documentElement.style.setProperty('--cols', COLUMNS);

  const bubbleSize = TOTAL_QUESTIONS <= 20 ? 32
                   : TOTAL_QUESTIONS <= 50 ? 28
                   : TOTAL_QUESTIONS <= 80 ? 24
                   : 20;

  const rowGap = TOTAL_QUESTIONS <= 30 ? 13
               : TOTAL_QUESTIONS <= 60 ? 10
               : 8;

  document.documentElement.style.setProperty('--bubble-size', bubbleSize + 'px');
  document.documentElement.style.setProperty('--row-gap', rowGap + 'px');

  const grid = document.getElementById('questionsGrid');
  const footer = document.getElementById('footerTotal');

  for (let i = 1; i <= TOTAL_QUESTIONS; i++) {{
    const row = document.createElement('div');
    row.className = 'q-row';
    row.innerHTML = `<span class="q-num">${{i}}</span><div class="bubbles" data-q="${{i}}"></div>`;
    const bubblesDiv = row.querySelector('.bubbles');

    OPTIONS.forEach(opt => {{
      const b = document.createElement('div');
      b.className = 'bubble';
      b.textContent = opt;
      b.dataset.opt = opt;
      b.addEventListener('click', () => {{
        bubblesDiv.querySelectorAll('.bubble').forEach(x => x.classList.remove('filled'));
        b.classList.toggle('filled');
      }});
      bubblesDiv.appendChild(b);
    }});

    grid.appendChild(row);
  }}

  footer.textContent = `Total Questions: ${{TOTAL_QUESTIONS}}`;
</script>

</body>
</html>"""
        
        # Generate PDF from HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = str(TMP_DIR / f"omr_{timestamp}.pdf")
        
        logger.info(f"Converting to PDF: {pdf_path}")
        
        if not REPORTLAB_AVAILABLE:
            logger.error("ReportLab not available")
            return {
                "error": "PDF generation not available",
                "message": "Install ReportLab: pip install reportlab"
            }
        
        # Create PDF with reportlab
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import mm
            
            # Calculate dimensions
            page_width, page_height = A4
            
            # Create canvas
            c = canvas.Canvas(pdf_path, pagesize=A4)
            
            # Draw circles for bubbles and lines for questions
            bubble_radius = 10  # points
            bubble_spacing = 30
            question_x = 50
            start_y = page_height - 50
            
            # Draw title
            c.setFont("Helvetica-Bold", 24)
            c.drawString(50, start_y + 20, "ANSWER SHEET")
            
            # Draw header info
            c.setFont("Helvetica", 9)
            c.drawString(50, start_y - 20, "Name: _____________________")
            c.drawString(350, start_y - 20, "Date: _____________________")
            c.drawString(50, start_y - 40, "Roll No: _____________________")
            
            # Draw instructions
            c.setFont("Helvetica", 8)
            c.drawString(50, start_y - 60, "Fill the bubble completely with a dark pen or pencil. Do not make any extra marks.")
            
            # Draw bubbles for questions
            c.setFont("Helvetica", 8)
            y_pos = start_y - 100
            col_count = columns
            
            for q_num in range(1, questions + 1):
                if q_num > 1 and (q_num - 1) % col_count == 0:
                    y_pos -= 60
                
                col_offset = ((q_num - 1) % col_count) * 200
                x_base = question_x + col_offset
                
                # Question number
                c.drawString(x_base, y_pos, f"Q{q_num}:")
                
                # Option bubbles
                for opt_idx, opt in enumerate(["A", "B", "C", "D", "E", "F"][:options]):
                    bubble_x = x_base + 40 + (opt_idx * bubble_spacing)
                    # Draw circle
                    c.circle(bubble_x, y_pos + 2, bubble_radius / 2, fill=0)
                    # Draw option letter
                    c.drawString(bubble_x - 2, y_pos - 2, opt)
            
            c.save()
            logger.info(f"PDF created successfully: {pdf_path}")
            
        except Exception as e:
            logger.error(f"Error creating PDF: {e}", exc_info=True)
            return {
                "error": f"PDF creation failed: {str(e)}",
                "message": "An error occurred while creating the PDF"
            }
        
        # Verify PDF was created
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file was not created: {pdf_path}")
            return {
                "error": "PDF generation failed",
                "message": "PDF file was not created"
            }
        
        # Return PDF as download
        logger.info(f"Returning PDF file for download: {pdf_path}")
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"omr_sheet_{questions}q_{options}opt_{timestamp}.pdf"
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF: {e}", exc_info=True)
        return {
            "error": str(e),
            "message": "Failed to generate PDF. Make sure Playwright is installed: playwright install chromium"
        }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == '__main__':
    print("Run with: uvicorn main:app --reload")
    print("Then open: http://localhost:8000")
