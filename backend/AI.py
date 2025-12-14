from fastapi import Form, APIRouter, UploadFile,File
from openai import OpenAI 
import os  # if using OpenAI API
import io
import pandas as pd
from dotenv import load_dotenv
from typing import Optional
from PIL import Image
import pytesseract

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
router = APIRouter()

@router.post("/process_chat")
async def process_chat(
    query: str = Form(...),
    # file: UploadFile = File(...)
    file: Optional[UploadFile] = File(None),
    metadata: Optional[str] = Form(None)
):
    # print("it this working ")
    # print("QUERY RECEIVED:", query)
    # print("FILE RECEIVED:", file.filename)

    """
    Chat endpoint: user asks a question about the uploaded file.
    AI analyzes content + user question and returns instructions/answers.
    """

    # filename = file.filename.lower()
    # content = await file.read()
    # buffer = io.BytesIO(content)

    # ---- Detect file type (reuse your "/process" logic) ----
    df = None
    text_content = None
    # -------- If file was uploaded (tabular/text) --------
    if file:
        filename = file.filename.lower()
        content = await file.read()
        buffer = io.BytesIO(content)

        if filename.endswith(".csv"):
            df = pd.read_csv(buffer)

        elif filename.endswith(".xlsx"):
            df = pd.read_excel(buffer)

        elif filename.endswith(".json"):
            try:
                df = pd.read_json(buffer)
            except:
                text_content = content.decode()

        elif filename.endswith(".txt"):
            text_content = content.decode()

        elif filename.endswith((".png", ".jpg", ".jpeg")):
            # Actual image bytes can’t be processed by GPT
            # text_content = "Image file provided"
            img = Image.open(buffer)
            # text_content = f"this is an image file{img}"
            try:
                text_from_image = pytesseract.image_to_string(img)
                if text_from_image.strip():
                    text_content = f"Extracted text from image:\n{text_from_image}"
                else:
                    text_content = "Image contains no readable text. Metadata only."
            except Exception as e:
                text_content = f"Could not extract text: {e}"

    # -------- If metadata was sent (image case) --------
    if metadata:
        text_content += metadata 

    # -------- Build the AI input --------
    if df is not None:
        file_info = f"""
        Columns: {df.columns.tolist()}
        First rows: {df.head().to_dict(orient='records')}
        Description: {df.describe(include='all').to_dict()}
        """
    else:
        print("is this working too")
        file_info = text_content if text_content else "No readable data available."

    prompt = f"""
    The user uploaded a file.

    File information:
    {file_info}

    User question:
    "{query}"

    Respond clearly and helpfully.
    """

    ai_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = ai_response.choices[0].message.content
    return {"response": answer}
