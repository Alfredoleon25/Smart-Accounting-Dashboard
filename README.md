# Smart Accounting Dashboard

The **Smart Accounting Dashboard** is a simple, powerful app for uploading and processing files like CSV, Excel, and JSON. It uses **OpenAI’s GPT** to provide AI-powered insights, helping you explore your data effortlessly.

## 🚀 Get Started

### 1. Clone the Repo
```bash
git clone https://github.com/Alfredoleon25/Smart-Accounting-Dashboard.git
cd Smart-Accounting-Dashboard

2. Install Dependencies
Install all required packages:
pip install -r requirements.txt

3. Set Up Environment Variables
Create a .env file with your keys and credentials:
OPENAI_API_KEY=your_openai_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
JWT_SECRET=your_jwt_secret_key

POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_HOST=your_postgres_host
POSTGRES_PORT=your_postgres_port
POSTGRES_DB=your_postgres_db

🏃‍♂️ Run the App
Backend (FastAPI)
Start the backend server:
fastapi dev main.py
The backend will run at: http://127.0.0.1:8000

Frontend (Streamlit)
Run the frontend dashboard:
streamlit run frontend/Dashboard.py
The dashboard will be available at: http://localhost:8501

🔑 Authentication
Log in using Google OAuth. You’ll receive a JWT token for secure access.

📂 File Management
Upload Files: Supports CSV, Excel, JSON, and more.
Process Files: Send a file and ask AI-powered questions.
Manage Files: View, update, and delete your files.

🧠 AI Insights
Get quick insights on your data with OpenAI's GPT, such as:
"What are the average sales for each region?"
"Can you summarize this data for me?"

📦 Database
Stores user-uploaded files and metadata in PostgreSQL.

📄 License
MIT License

