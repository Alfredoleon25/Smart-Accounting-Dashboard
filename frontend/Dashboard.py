import streamlit as st
import pandas as pd
import json
from PIL import Image
import requests
from io import BytesIO
import base64
import time
import urllib.parse
from jose import jwt
import os 
from streamlit_cookies_manager import EncryptedCookieManager

JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60

API_URL = "http://127.0.0.1:8000"
# ---------------- Cookies ----------------
cookies = EncryptedCookieManager(
    prefix="myapp_",
    password="supersecretpassword123",
)
if not cookies.ready():
    st.stop()
# ------------------ Authentication ------------------
# Initialize session_state.token from cookie if not present
cookie_token = cookies.get("token")

if "token" not in st.session_state:
    st.session_state.token = cookie_token or st.session_state.get("token")

token = st.query_params.get("token", None)

if token:
    st.session_state.token = token
    cookies["token"] = token
    cookies.save()
    st.query_params.clear()
    st.rerun() 

if st.session_state.token is None: 
    login_url = f"{API_URL}/login"

    st.markdown(
        f"""
        <style>
        /* Lock page scrolling and match Streamlit dark theme exactly */
        html, body, #root, .appview-container, .main, .block-container {{
            overflow: hidden !important;
            height: 100vh !important;
            margin: 0 !important;
            padding: 0 !important;
            background-color: #0E1117 !important;  /* Streamlit dark background */
        }}

        /* Center login box, match background */
        .login-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            background-color: #0E1117;  /* same as page for perfect match */
            padding: 0; 
            border-radius: 0;
            box-shadow: none;
        }}

        /* Google login button style */
        .google-btn {{
            display: flex;
            align-items: center;
            gap: 12px;
            background-color: #2b2b2b;
            color: #ffffff;
            padding: 12px 20px;
            border-radius: 8px;
            border: 1px solid #444;
            font-size: 16px;
            font-weight: 500;
            text-decoration: none;
            transition: 0.2s;
        }}
        .google-btn:hover {{
            background-color: #3c3c3c;
        }}
        .google-logo {{
            width: 22px;
            height: 22px;
        }}

        h1 {{
            font-family: 'Helvetica', sans-serif;
            margin-bottom: 30px;
            color: #ffffff;
        }}
        </style>

        <div class="login-container">
            <h1>Welcome</h1>
            <a class="google-btn" href="{login_url}" target="_self">
                <img class="google-logo" src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"/>
                Continue with Google
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


    # st.title("Login")
    # login_url = f"{API_URL}/login"
    # st.markdown(f'<a href="{login_url}" target="_self">Login with Google</a>', unsafe_allow_html=True)
    # st.stop()

headers = {"Authorization": f"Bearer {st.session_state.token}"}

# ---------------- SESSION STATE ---------------- #
if "current_page" not in st.session_state:
    st.session_state.current_page = "main"
if "selected_project_id" not in st.session_state:
    st.session_state.selected_project_id = None
if "uploaded_file_bytes" not in st.session_state:
    st.session_state.uploaded_file_bytes = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None
if "uploaded_file_type" not in st.session_state:
    st.session_state.uploaded_file_type = None
if "is_uploaded_preview" not in st.session_state:
    st.session_state.is_uploaded_preview = False

col1, col2 = st.columns([7, 1])
if st.session_state.token:
    decoded = jwt.decode(st.session_state.token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    username = decoded.get("name")
if st.session_state.current_page == "main":
    with col1:
        if st.session_state.get('token'):
            st.markdown(f"#### Hello! {username}")

    with col2:
        if st.session_state.get('token'):
            if st.button("Logout"):
                st.session_state.token = None
                cookies["token"] = ""
                cookies.save()
                st.rerun()


# ---------------- MAIN PAGE ---------------- #
def show_main():
    st.set_page_config( layout="wide",  )
    st.title("Smart Accounting Dashboard ")

    # ---------------- UPLOAD ----------------
    uploaded_file = st.file_uploader(
        "Upload any file",
        type=["csv", "xlsx", "json", "txt", "png", "jpg", "jpeg", "parquet"]
    )

    if uploaded_file:
        st.session_state.uploaded_file_bytes = uploaded_file.getvalue()
        st.session_state.uploaded_file_name = uploaded_file.name
        st.session_state.uploaded_file_type = uploaded_file.type
        st.session_state.is_uploaded_preview = True
        st.session_state.current_page = "view_uploaded"
        st.rerun()

    # ---------------- LIST PROJECTS ----------------
    st.subheader("All Projects")
    response = requests.get(f"{API_URL}/files",headers=headers)
    projects = response.json()
    # Sort projects newest first
    projects = sorted(projects, key=lambda x: x['id'], reverse=True)

    if projects:
        for project in projects:
            st.write(f"**Name:** {project['filename']} | **Type:** {project['content_type']}")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("View", key=f"project_button{project['id']}"):
                    st.session_state.selected_project_id = project['id']
                    st.session_state.current_page = "view_project"
                    st.rerun()

            with col2:
                # Initialize toggle state for this project
                toggle_key = f"show_uploader_{project['id']}"
                if toggle_key not in st.session_state:
                    st.session_state[toggle_key] = False

                # Toggle button
                if st.button("Update", key=f"update_{project['id']}"):
                    st.session_state[toggle_key] = not st.session_state[toggle_key]

                # Conditionally show the file uploader
                if st.session_state[toggle_key]:
                    new_file = st.file_uploader("", key=f"update_file_{project['id']}", label_visibility="collapsed")
                    if new_file is not None:
                        new_bytes = new_file.read()
                        upd_response = requests.put(
                            f"{API_URL}/file/{project['id']}",
                            files={"new_file": (new_file.name, new_bytes, new_file.type)},
                            headers=headers
                        )
                        st.success(upd_response.json()["status"])
                        # Hide uploader after upload
                        st.session_state[toggle_key] = False
                        time.sleep(1)
                        st.rerun()
            with col3:
                if st.button("Delete", key=f"delete_{project['id']}"):
                    del_response = requests.delete(f"{API_URL}/file/{project['id']}",headers=headers)
                    st.success(del_response.json()["status"])
                    time.sleep(0.1)
                    st.rerun()
# ---------------- VIEW UPLOADED PAGE ---------------- #
def show_view_uploaded():
    st.set_page_config(layout="wide")
    
    # Lock page scrolling only
    st.markdown("""
        <style>
        /* Completely lock page scrolling */
        html {
            overflow: hidden !important;
            height: 100vh !important;
        }
        body {
            overflow: hidden !important;
            height: 100vh !important;
            position: fixed !important;
            width: 100% !important;
        }
        section[data-testid="stAppViewContainer"] {
            overflow: hidden !important;
            height: 100vh !important;
        }
        section[data-testid="stAppViewContainer"] > div {
            overflow: hidden !important;
        }
        .main {
            overflow: hidden !important;
            height: 100vh !important;
        }
        .block-container {
            overflow: hidden !important;
            padding-top: 0rem !important;
            padding-bottom: 1rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        if st.button("Back to Dashboard", use_container_width=True):
            st.session_state.current_page = "main"
            st.session_state.is_uploaded_preview = False
            st.rerun()
    
    with col_btn2:
        if st.button("Save it for later", use_container_width=True):
            response = requests.post(
                f"{API_URL}/upload",
                files={"file": (st.session_state.uploaded_file_name, st.session_state.uploaded_file_bytes, st.session_state.uploaded_file_type)}
            ,headers=headers)
            result = response.json()
            st.success(result["status"])
            time.sleep(0.1)
            # After saving, switch to the saved file view
            new_id = result.get("id")
            if new_id:
                st.session_state.selected_project_id = new_id
                st.session_state.current_page = "view_project"
                st.session_state.is_uploaded_preview = False
                st.rerun()

    col1, col2 = st.columns([2, 1])

    with col1:
        with st.container(height=500, border=True):
            st.title(f"Preview — {st.session_state.uploaded_file_name}")
            file_bytes = st.session_state.uploaded_file_bytes
            filename = st.session_state.uploaded_file_name.lower()

            # ---------- CSV ----------
            if filename.endswith(".csv"):
                df = pd.read_csv(BytesIO(file_bytes))
                st.subheader("Preview")
                st.dataframe(df.head())
                st.subheader("Description")
                st.write(df.describe())

                # Filtering & Chart
                columns = df.columns.tolist()
                st.subheader("Filter Data")
                sel_col = st.selectbox("Select Column", columns)
                sel_val = st.selectbox("Select Value", df[sel_col].unique())
                filtered = df[df[sel_col] == sel_val]
                st.write(filtered)

                st.subheader("Draw a Chart")
                x_axis = st.selectbox("X-axis", columns)
                y_axis = st.selectbox("Y-axis", columns)
                if st.button("Generate Chart"):
                    try:
                        st.line_chart(df.set_index(x_axis)[y_axis])
                    except:
                        st.error("Cannot generate chart with selected columns")

            # ---------- Excel ----------
            elif filename.endswith(".xlsx"):
                df = pd.read_excel(BytesIO(file_bytes))
                st.dataframe(df.head())

            # ---------- JSON ----------
            elif filename.endswith(".json"):
                try:
                    df = pd.read_json(BytesIO(file_bytes))
                    st.dataframe(df.head())
                except ValueError:
                    st.json(json.loads(file_bytes))

            # ---------- Text ----------
            elif filename.endswith(".txt"):
                text = file_bytes.decode("utf-8")
                st.text(text)

            # ---------- Parquet ----------
            elif filename.endswith(".parquet"):
                df = pd.read_parquet(BytesIO(file_bytes))
                st.dataframe(df.head())

            # ---------- Images ----------
            elif filename.endswith((".png", ".jpg", ".jpeg")):
                img = Image.open(BytesIO(file_bytes))
                st.image(img)

            else:
                st.error("Unsupported file type")
                return
            
    with col2:
        with st.container(height=500, border=True):
            st.markdown("""
                **NEED SOME HELP!!!**
                <style>         
                /* Hide Streamlit form border */
                div[data-testid="stForm"] {
                    border: none !important;
                    padding: 0 !important;
                }
                
                /* Style the submit button */
                div[data-testid="stForm"] button {
                    background-color: #4a90e2 !important;
                    border: none !important;
                    border-radius: 50% !important;
                    width: 40px !important;
                    height: 40px !important;
                    padding: 0 !important;
                    color: white !important;
                    font-size: 20px !important;
                }          
                </style>
            """, unsafe_allow_html=True)
            if "current_response_viewed" not in st.session_state:
                st.session_state.current_response_viewed = None

            # Display only the response
            with st.container(height=370):
                if st.session_state.current_response_viewed:
                    st.markdown(
                        st.session_state.current_response_viewed,
                        unsafe_allow_html=True
                    )

            # Input form at bottom
            with st.form(key="chat_box", clear_on_submit=True):
                col_input, col_button = st.columns([6, 1])
                with col_input:
                    user_input = st.text_input(
                        "Message",
                        key="user_input",
                        label_visibility="collapsed",
                    )
                with col_button:
                    submit_button = st.form_submit_button("↑")
            
            if submit_button and user_input.strip():
                filename = st.session_state.uploaded_file_name.lower() 
                file_bytes = st.session_state.uploaded_file_bytes 
                ftype = None

                if filename.endswith((".csv", ".xlsx", ".json", ".txt", ".parquet")):
                    # For text/tabular files, send raw bytes
                    # files = {"file": (filename, file_bytes)}
                    # payload = {"query": user_input}
                    files = {"file": (filename, file_bytes)}
                    payload = {"query": user_input}
                    response = requests.post(
                        f"{API_URL}/process_chat",
                        files=files,
                        data=payload,
                        headers=headers
                    )

                elif filename.endswith((".png", ".jpg", ".jpeg")):
                    # For images, extract metadata and optional OCR text
                    img = Image.open(BytesIO(file_bytes))
                    # metadata = f"Image: {filename}, Size: {img.size}, Mode: {img.mode}"

                    # try:
                    #     text_from_image = pytesseract.image_to_string(img)
                    #     if text_from_image.strip():
                    #         metadata += f"\nExtracted Text: {text_from_image}"
                    # except Exception:
                    #     pass  # OCR optional

                    # files = None  # No need to send raw bytes to a text AI
                    # payload = {"query": user_input, "metadata": metadata}
                    files = {"file":(filename,file_bytes)}
                    metadata = f"""
                    Image Name: {filename}
                    Size: {img.size}
                    Mode: {img.mode}
                    Format: {img.format}
                    """

                    payload = {
                        "query": user_input,
                        "metadata": metadata
                    }

                    response = requests.post(
                        f"{API_URL}/process_chat",
                        data=payload,
                        files=files,
                        headers=headers
                    )

                else:
                    st.error("Unsupported file type for AI processing")
                    st.stop()

                # Send request to AI endpoint
                    # if files:
                    #     response = requests.post(f"{API_URL}/process_chat", files=files, data=payload, headers=headers)
                    # else:
                    #     response = requests.post(f"{API_URL}/process_chat", data=payload, headers=headers)

                try:
                    result = response.json()
                    st.session_state.current_response_viewed = result["response"]
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to get AI response: {e}")


# ---------------- VIEW EXISTING PROJECT ---------------- #
def show_view_project(project_id):
    st.set_page_config(layout="wide")
    st.markdown("""
        <style>
        /* Completely lock page scrolling */
        html {
            overflow: hidden !important;
            height: 100vh !important;
        }
        body {
            overflow: hidden !important;
            height: 100vh !important;
            position: fixed !important;
            width: 100% !important;
        }
        section[data-testid="stAppViewContainer"] {
            overflow: hidden !important;
            height: 100vh !important;
        }
        section[data-testid="stAppViewContainer"] > div {
            overflow: hidden !important;
        }
        .main {
            overflow: hidden !important;
            height: 100vh !important;
        }
        .block-container {
            overflow: hidden !important;
            padding-top: 0rem !important;
            padding-bottom: 1rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

    file_response = requests.get(f"{API_URL}/file/{project_id}",headers=headers)
    if file_response.status_code != 200:
        st.error("Failed to fetch project details")
        return
    data = file_response.json()
    ftype = data.get("type")

    if st.button("Back to main dashboard"):
        st.session_state.current_page = "main"
        st.session_state.selected_project_id = None
        st.rerun()
    col1, col2 = st.columns([5, 3])
    with col1:
        with st.container(height=500, border=True):
            st.title(f"Dashboard — {data['filename']}")

            # Tabular
            if ftype == "tabular":
                st.subheader("Preview")
                try:
                    df = pd.DataFrame(data["preview"])
                    st.dataframe(df,use_container_width=True, height=250)
                except Exception:
                    st.json(data["preview"])

                st.subheader("Description")
                try:
                    desc_df = pd.DataFrame(data["description"])
                    st.dataframe(desc_df)
                except:
                    st.json(data["description"])

                # Chart Builder
                columns = data["columns"]
                x_axis = st.selectbox("X-axis", columns)
                y_axis = st.selectbox("Y-axis", columns)
                if st.button("Generate Chart"):
                    try:
                        st.line_chart(df.set_index(x_axis)[y_axis])
                    except:
                        st.error("Columns are not numeric or cannot be charted.")

            # JSON
            elif ftype == "json":
                st.subheader("JSON Preview")
                st.json(data["preview"])

            # Text
            elif ftype == "text":
                st.subheader("Text Preview")
                st.text(data["preview"])
                st.write(f"Characters: {data['char_count']}")
                st.write(f"Words: {data['word_count']}")
                st.write(f"Lines: {data['line_count']}")
                st.write("Top Words:", data["top_words"])

            # Image
            elif ftype == "image":
                st.subheader("Image Info")
                st.write(f"Size: {data['image_size']}")
                st.write(f"Mode: {data['color_mode']}")
                img_bytes = base64.b64decode(data["image_base64"])
                img = Image.open(BytesIO(img_bytes))
                st.image(img, caption=data["filename"])

            else:
                st.warning("Unsupported file type")
    with col2:
        with st.container(height=500, border=True):
            st.markdown("""
                **NEED SOME HELP!!!**
                <style>         
                /* Hide Streamlit form border */
                div[data-testid="stForm"] {
                    border: none !important;
                    padding: 0 !important;
                }
                
                /* Style the submit button */
                div[data-testid="stForm"] button {
                    background-color: #4a90e2 !important;
                    border: none !important;
                    border-radius: 50% !important;
                    width: 40px !important;
                    height: 40px !important;
                    padding: 0 !important;
                    color: white !important;
                    font-size: 20px !important;
                }          
                </style>
            """, unsafe_allow_html=True)

            # Initialize response in session state
            if "current_response" not in st.session_state:
                st.session_state.current_response = None

            # Display only the response
            with st.container(height=370):
                if st.session_state.current_response:
                    st.markdown(
                        st.session_state.current_response,
                        unsafe_allow_html=True
                    )

            # Input form at bottom
            with st.form(key="chat_box", clear_on_submit=True):
                col_input, col_button = st.columns([6, 1])
                with col_input:
                    user_input = st.text_input(
                        "Message",
                        key="user_input",
                        label_visibility="collapsed",
                    )
                with col_button:
                    submit_button = st.form_submit_button("↑")

            if submit_button and user_input.strip():
                # API call
                res = requests.get(f"{API_URL}/file_bytes/{project_id}", headers=headers)
                raw_bytes = res.content
                files = {"file": (data["filename"], raw_bytes, ftype)}
                payload = {"query": user_input}
                response = requests.post(
                    f"{API_URL}/process_chat",
                    files=files,
                    data=payload,
                    headers=headers
                )
                result = response.json()

                # Store only the response
                st.session_state.current_response = result["response"]

                st.rerun()

# ---------------- PAGE ROUTING ---------------- #
if st.session_state.current_page == "main":
    show_main()
elif st.session_state.current_page == "view_uploaded":
    show_view_uploaded()
elif st.session_state.current_page == "view_project":
    show_view_project(st.session_state.selected_project_id)
