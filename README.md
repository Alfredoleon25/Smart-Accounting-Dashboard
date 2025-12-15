# Smart Accounting Dashboard

A full-stack application using **FastAPI** for the backend and **Streamlit** for the frontend. Upload files, get AI insights, and interact with data using **OpenAI's GPT**.

## 🗂 Project Overview

### Backend (FastAPI)
- File upload, processing, and AI insights via OpenAI API.
- Google OAuth for authentication with JWT for secure sessions.
- Stores data in **PostgreSQL**.

### Frontend (Streamlit)
- Simple UI for uploading files, viewing data, and interacting with AI-powered processing.

## ⚡ Quick Start

### 1. Clone the Repo
```bash
git clone https://github.com/Alfredoleon25/Smart-Accounting-Dashboard.git
cd Smart-Accounting-Dashboard
2. Set Up Your Environment
Create and activate a virtual environment:
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
3. Install Dependencies
pip install -r requirements.txt
4. Configure Environment Variables
Create a .env file with:
OPENAI_API_KEY=your_openai_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
JWT_SECRET=your_jwt_secret_key

POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_HOST=your_postgres_host
POSTGRES_PORT=your_postgres_port
POSTGRES_DB=your_postgres_db
🚀 Running the App
Backend (FastAPI)
Run the backend server:
fastapi dev main.py
It will be available at http://127.0.0.1:8000.
Frontend (Streamlit)
Run the frontend dashboard:
streamlit run frontend/Dashboard.py
It will be available at http://localhost:8501.
🔐 Authentication
Users log in via Google OAuth. After login, they get a JWT token for secure access.
📂 File Management
Upload files: CSV, Excel, JSON, etc.
Process files: Send files with a query to get AI insights.
View, update, delete files.
🧠 AI Processing
AI uses OpenAI’s GPT to process your files and answer questions like:
“What are the average sales for each region?”
“Can you summarize this data for me?”
🗄 Database
PostgreSQL is used to store uploaded files and metadata. The UploadedFile model stores details such as the filename, content type, data, and AI summary.
🤝 Contribution
Fork the repo
Create a new branch: git checkout -b feature/my-feature
Commit changes: git commit -am 'Add new feature'
Push: git push origin feature/my-feature
Open a Pull Request
📄 License
This project is licensed under the MIT License.
