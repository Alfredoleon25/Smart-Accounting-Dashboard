# Smart Accounting Dashboard

A web application for uploading, managing, and analyzing files with AI assistance.  
Backend is built with **FastAPI**, frontend with **Streamlit**.

---

## Features

- User authentication with Google and JWT tokens
- Upload and preview files (CSV, Excel, JSON, TXT, Parquet, Images)
- Analyze tabular data and draw charts
- AI chat assistant to query uploaded files
- Update or delete files

---

## Installation

1. Clone the repository:

```bash
git clone <repository_url>
cd <repository_folder>

Install dependencies:
pip install -r requirements.txt

Create .env file in backend/:
JWT_SECRET=supersecretkey
DATABASE_URL=postgresql://username:password@localhost:5432/dbname

Running the App:
Backend
cd backend
fastapi dev main.py
API runs at http://127.0.0.1:8000.
Frontend
cd frontend
streamlit run Dashboard.py
Dashboard runs at http://localhost:8501.

Usage
Open the Streamlit dashboard.
Login with Google or your token.
Upload files, preview, and analyze data.
Use AI assistant to ask questions about your files.

Supported File Types
CSV, Excel, JSON, TXT, Parquet
PNG, JPG, JPEG (image preview)
