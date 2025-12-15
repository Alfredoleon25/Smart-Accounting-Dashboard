# Smart Accounting Dashboard

Welcome to the **Smart Accounting Dashboard**! This app allows users to upload files (CSV, Excel, JSON, etc.), get AI-powered insights, and interact with the data. It combines **FastAPI** for the backend, **Streamlit** for the frontend, and **PostgreSQL** for data storage. Plus, you can use **Google OAuth** for authentication and interact with **OpenAI’s GPT model** for file analysis.

## 🗂 Project Overview

Here’s a quick look at the project:

### Backend (FastAPI)
- **Handles file uploads, data processing, and AI insights** using the OpenAI API.
- Manages **authentication** via Google OAuth and **JWT tokens** for secure user sessions.
- Connects to **PostgreSQL** to store uploaded files and user data.

### Frontend (Streamlit)
- **User-friendly interface** for uploading files, viewing results, and interacting with the AI-powered model.
- Supports data preview, file processing, and generating charts.

### Key Files:
- `AI.py`: Where the magic happens—sending files to OpenAI and getting responses.
- `auth.py`: Manages user authentication and session management.
- `main.py`: The entry point to the FastAPI app, including routes for uploading and processing files.
- `Dashboard.py`: The Streamlit frontend where users can upload files, chat with the AI, and view results.

## ⚡ Quick Start Guide

### 1. Clone the Repo

Start by cloning the repository to your local machine:

```bash
git clone https://github.com/Alfredoleon25/Smart-Accounting-Dashboard.git
cd Smart-Accounting-Dashboard
2. Set Up Your Environment
Create a virtual environment and activate it:
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
3. Install Dependencies
Install the required Python packages:
pip install -r requirements.txt
4. Configure Environment Variables
Create a .env file in the root directory with the following:
OPENAI_API_KEY=your_openai_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
JWT_SECRET=your_jwt_secret_key

POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_HOST=your_postgres_host
POSTGRES_PORT=your_postgres_port
POSTGRES_DB=your_postgres_db
Replace the placeholders (your_openai_api_key, etc.) with your actual credentials.
🚀 Running the App
Backend (FastAPI)
Start the FastAPI backend by running this command:
fastapi dev main.py
This will start the backend server at http://127.0.0.1:8000.
Frontend (Streamlit)
To run the frontend dashboard, use:
streamlit run frontend/Dashboard.py
This will launch the frontend at http://localhost:8501.
🔑 Authentication
This app uses Google OAuth for authentication. After logging in with your Google account, you’ll receive a JWT token, which is used to secure the API requests.
📂 File Management
Endpoints to Know:
Upload Files: You can upload CSV, Excel, JSON, Parquet, and image files.
Process Files: Send a file along with a query to get AI-powered insights. You can ask questions about the data, and the app will respond using OpenAI’s GPT model.
View Files: You can list, view, update, or delete your uploaded files.
🧠 AI-Powered File Processing
The app leverages OpenAI’s GPT to process files and answer queries based on the data. For example, you can upload a CSV and ask questions like:
“What are the average sales for each region?”
“Can you summarize this data for me?”
🗄 Database
We use PostgreSQL to store user-uploaded files and their metadata. Here’s an example of the UploadedFile model:
class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    content_type = Column(String)
    data = Column(LargeBinary)
    ai_summary = Column(Text)
    user_email = Column(String, index=True)
📑 Notes
The .env file is excluded from version control (via .gitignore) to protect sensitive information like API keys and database credentials.
JWT tokens are stored securely using encrypted cookies in the frontend.
🤝 Contribution
We’d love to have your help! If you want to contribute to this project:
Fork the repo.
Create a new branch: git checkout -b feature/my-feature.
Make your changes and commit them: git commit -am 'Add new feature'.
Push your branch: git push origin feature/my-feature.
Open a Pull Request.
📝 License
This project is licensed under the MIT License.

