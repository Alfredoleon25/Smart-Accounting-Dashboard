# Smart Accounting Dashboard

A full-stack application using **FastAPI** for the backend and **Streamlit** for the frontend. It allows authenticated users to upload files, explore data, and get AI-powered insights via OpenAI’s API.

## 📁 Project Structure

**Backend (FastAPI)**  
- `main.py`: FastAPI server with endpoints for file upload, processing, and CRUD.  
- `AI.py`: `/process_chat` endpoint — sends files + query to OpenAI.  
- `auth.py`: Google OAuth authentication & JWT token creation.  
- `database.py`: SQLAlchemy database setup.  
- `models.py`: Database models (e.g., `UploadedFile`).  

**Frontend (Streamlit)**  
- `Dashboard.py`: Main dashboard for upload, preview, project listing, and AI chat UI.

**Other**  
- `.env`: Environment variables (excluded via `.gitignore`).  
- `requirements.txt`: All Python dependencies.

## 🚀 Quick Start

### 1. Clone the Repo
```bash
git clone https://github.com/Alfredoleon25/Smart-Accounting-Dashboard.git
cd Smart-Accounting-Dashboard
2. Create & Activate Virtual Environment
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
3. Install Dependencies
pip install -r requirements.txt
4. Create a .env file
Add the following in .env:
OPENAI_API_KEY=your_openai_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
JWT_SECRET=your_jwt_secret_key

POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_HOST=your_postgres_host
POSTGRES_PORT=your_postgres_port
POSTGRES_DB=your_postgres_db
🛠️ Running the App
Backend (FastAPI)
Start the backend:
fastapi dev main.py
The backend runs at:
⬢ http://127.0.0.1:8000
Frontend (Streamlit)
Start the dashboard:
streamlit run frontend/Dashboard.py
The frontend runs at:
➡️ http://localhost:8501
🔐 Authentication
Users log in with Google OAuth.
After login, a JWT token is returned and stored in the dashboard for API calls.
📂 File Management Endpoints
Endpoint	Description
POST /process	Get type & basic info of uploaded file
POST /upload	Save the uploaded file to DB
GET /files	List user’s uploaded files
GET /file/{id}	Get full preview & metadata
GET /file_bytes/{id}	Download raw file bytes
PUT /file/{id}	Update a stored file
DELETE /file/{id}	Remove a file
🧠 AI Chat Endpoint
POST /process_chat
Send a file and a query — receive a GPT response.
Works with CSV, Excel, JSON, text, images, and more.
🗄 Database
PostgreSQL with SQLAlchemy.
Example model:
class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    content_type = Column(String)
    data = Column(LargeBinary)
    ai_summary = Column(Text)
    user_email = Column(String, index=True)
📌 Notes
Your .env is included in .gitignore to protect sensitive data.
The dashboard persists JWT in encrypted cookies.
🤝 Contribution
Fork the repo
Create a branch (git checkout -b feature/my-feature)
Commit your changes (git commit -m "Add feature")
Push (git push origin feature/my-feature)
Open a Pull Request

