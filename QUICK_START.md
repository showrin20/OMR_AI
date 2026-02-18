# OMR Sheet Generator - Quick Start

Simple API to generate OMR (Answer) sheets and download as PDF.

## 🚀 Quick Install

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload

# Open browser
open http://localhost:8000
```

## 📋 How It Works

1. **Configure**: Set number of questions, options, and columns
2. **Generate**: Click button to generate OMR sheet as PDF
3. **Download**: PDF is ready to print
4. **Print & Use**: Students fill bubbles with pen

## 🔌 API Endpoint

**POST** `/generate-and-download-pdf`

### Parameters
- `questions` (int): Number of questions (1-200, default 50)
- `options` (int): Options per question (2-6, default 4)
- `columns` (int): Grid columns (1-3, default 2)

### Example
```bash
curl -X POST http://localhost:8000/generate-and-download-pdf \
  -d "questions=50&options=4&columns=2" \
  -o omr.pdf
```

## 📦 What You Get

✅ Fixed-layout PDF (exact bubble positions)
✅ Print-ready format (A4 size)
✅ Configurable questions/options
✅ Professional appearance
✅ No external dependencies needed

## 🛠️ Installation Issues?

If `pip install -r requirements.txt` fails:

```bash
# Update pip first
pip install --upgrade pip

# Then install dependencies
pip install reportlab fastapi uvicorn python-multipart jinja2 opencv-python numpy aiofiles
```

## 📖 Usage

1. Open http://localhost:8000
2. Enter configuration:
   - Total Questions: 50
   - Options: A, B, C, D (4 options)
   - Columns: 2
3. Click "Generate & Download PDF"
4. Print the PDF
5. Students fill with pen
6. Scan completed sheets

## ⚙️ Configuration

Edit HTML form in `main.py` to customize:
- Default values
- Min/max limits
- Form styling

## 📝 Notes

- Uses ReportLab (pure Python, no external dependencies)
- PDFs are A4 size by default
- Bubbles are 10pt circles
- Works on macOS, Linux, Windows

## 🔧 Development

```bash
# Run with auto-reload
uvicorn main:app --reload

# Run in production
gunicorn main:app -w 4

# Check health
curl http://localhost:8000/health
```

---

**Version**: 1.0.0
**Dependencies**: ReportLab only
**Status**: Ready to use
