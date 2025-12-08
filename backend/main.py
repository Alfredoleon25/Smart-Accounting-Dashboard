from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
from PIL import Image
import io
from database import engine
from models import Base
from sqlalchemy.orm import Session
from database import SessionLocal
from models import UploadedFile
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from collections import Counter
import base64
from auth import router as auth_router
from starlette.middleware.sessions import SessionMiddleware
from fastapi import Header
import os
from jose import jwt
from AI import router as ai_router 
from fastapi.responses import Response

JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "supersecretkey"))
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)
app.include_router(auth_router)
app.include_router(ai_router)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def clean_df_for_json(df: pd.DataFrame) -> pd.DataFrame:
    """Replace NaN and Inf with None for JSON serialization."""
    df = df.replace([np.inf, -np.inf], np.nan)
    return df.where(pd.notnull(df), None)

def safe_describe(df: pd.DataFrame) -> dict:
    """Create JSON-safe description of a DataFrame."""
    desc = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            desc[col] = df[col].describe().to_dict()
        else:
            counts = df[col].value_counts(dropna=True).to_dict()
            desc[col] = {
                "unique": df[col].nunique(),
                "top": df[col].mode().iloc[0] if not df[col].mode().empty else None,
                "freq": counts.get(df[col].mode().iloc[0], 0) if not df[col].mode().empty else 0
            }
    return desc
# def get_current_user(authorization: str = Header(None)):
#     if not authorization:
#         raise HTTPException(status_code=401, detail="Missing authorization header")
#     token = authorization.replace("Bearer ", "")
#     print(token)
#     # Check token against sessions
#     for email, t in user_sessions.items():
#         print(email)
#         if t == token:
#             return email
#     raise HTTPException(status_code=401, detail="Invalid token")
def get_current_user(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload["sub"]
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    filename = file.filename.lower()
    content = await file.read()   # always read file fully once
    buffer = io.BytesIO(content)  # reusable stream

    # ----------------------- CSV -----------------------
    if filename.endswith(".csv"):
        try:
            df = pd.read_csv(buffer)
            return {
                "type": "csv",
                "columns": df.columns.tolist(),
                "rows": len(df)
            }
        except Exception as e:
            return {"error": f"CSV parsing failed: {e}"}

    # ----------------------- Excel -----------------------
    elif filename.endswith(".xlsx"):
        try:
            df = pd.read_excel(buffer)
            return {
                "type": "excel",
                "columns": df.columns.tolist(),
                "rows": len(df)
            }
        except Exception as e:
            return {"error": f"Excel parsing failed: {e}"}

    # ----------------------- JSON -----------------------
    elif filename.endswith(".json"):
        try:
            data = json.loads(content.decode())
            if isinstance(data, dict):
                return {"type": "json_object", "keys": list(data.keys())}
            else:
                return {"type": "json_array", "length": len(data)}
        except Exception as e:
            return {"error": f"JSON parsing failed: {e}"}

    # ----------------------- Text -----------------------
    elif filename.endswith(".txt"):
        text = content.decode("utf-8", errors="ignore")
        return {
            "type": "text",
            "preview": text[:200],
            "length": len(text)
        }

    # ----------------------- Parquet -----------------------
    elif filename.endswith(".parquet"):
        try:
            df = pd.read_parquet(buffer)
            return {
                "type": "parquet",
                "columns": df.columns.tolist(),
                "rows": len(df)
            }
        except Exception as e:
            return {"error": f"Parquet parsing failed: {e}"}

    # ----------------------- Images -----------------------
    elif filename.endswith((".png", ".jpg", ".jpeg")):
        try:
            img = Image.open(buffer)
            return {
                "type": "image",
                "format": img.format,
                "size": img.size,
                "mode": img.mode
            }
        except Exception as e:
            return {"error": f"Image processing failed: {e}"}

    # ----------------------- Unsupported -----------------------
    return {"error": "Unsupported file type"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...),
                      db: Session = Depends(get_db),
                      current_user: str =Depends(get_current_user)):
    content = await file.read()

    db_file = UploadedFile(
        filename=file.filename,
        content_type=file.content_type,
        data=content,
        user_email =current_user

    )

    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return {"id": db_file.id, "status": "File saved successfully!"}

@app.get("/files")
def list_files(current_user: str = Depends(get_current_user), 
               db: Session = Depends(get_db)
               ):
    files = db.query(UploadedFile).filter(UploadedFile.user_email==current_user).all()
    return [{"id": f.id, "filename": f.filename, "content_type": f.content_type} for f in files]


@app.get("/file/{file_id}")
def get_file_dashboard(file_id: int, 
                       db: Session = Depends(get_db),
                       current_user: str = Depends(get_current_user)):
    file = db.query(UploadedFile).filter(UploadedFile.id == file_id,UploadedFile.user_email 
                                         ==current_user).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    filename = file.filename.lower()
    content = file.data

    try:
        # # --- Excel ---
        if filename.endswith(".xlsx"):
            file_bytes = io.BytesIO(content)
            file_bytes.seek(0)

            xls = pd.ExcelFile(file_bytes)
            sheets = xls.sheet_names
            first_sheet = sheets[0]

            file_bytes.seek(0)
            df = pd.read_excel(file_bytes, sheet_name=first_sheet)

            # Clean DataFrame
            df = df.replace([np.inf, -np.inf], None)
            df = df.where(pd.notnull(df), None)

            # --- Preview ---
            preview = df.head(10).to_dict(orient="records")

            # --- SAFE DESCRIPTION (never breaks) ---
            try:
                desc = df.describe(include="all")
                desc = desc.replace([np.inf, -np.inf], None)
                desc = desc.where(pd.notnull(desc), None)
                description = desc.to_dict()
            except Exception:
                # Fallback summary
                description = {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": df.columns.tolist(),
                    "non_null_count": df.notnull().sum().to_dict(),
                    "types": df.dtypes.astype(str).to_dict()
                }

            # --- Clean JSON double-pass ---
            def clean_json(obj):
                if isinstance(obj, dict):
                    return {k: clean_json(v) for k, v in obj.items()}
                if isinstance(obj, list):
                    return [clean_json(v) for v in obj]
                if isinstance(obj, float):
                    if obj is None:
                        return None
                    if pd.isna(obj) or obj in [float("inf"), float("-inf")]:
                        return None
                return obj

            return {
                "filename": filename,
                "type": "tabular",
                "columns": df.columns.tolist(),
                "preview": clean_json(preview),
                "description": clean_json(description),
                "sheets": sheets,
                "sheet_used": first_sheet
            }

        # --- CSV ---
        elif filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
            df_clean = clean_df_for_json(df)
            preview = df_clean.head(10).to_dict(orient="records")
            description = safe_describe(df_clean)
            return {
                "filename": file.filename,
                "type": "tabular",
                "columns": df_clean.columns.tolist(),
                "preview": preview,
                "description": description
            }

        # --- Parquet ---
        elif filename.endswith(".parquet"):
            df = pd.read_parquet(io.BytesIO(content))
            df_clean = clean_df_for_json(df)
            preview = df_clean.head(10).to_dict(orient="records")
            description = safe_describe(df_clean)
            return {
                "filename": file.filename,
                "type": "tabular",
                "columns": df_clean.columns.tolist(),
                "preview": preview,
                "description": description
            }

        # --- JSON ---
        elif filename.endswith(".json"):
            data = json.load(io.BytesIO(content))
            if isinstance(data, list) and all(isinstance(i, dict) for i in data):
                df = pd.DataFrame(data)
                df_clean = clean_df_for_json(df)
                preview = df_clean.head(10).to_dict(orient="records")
                description = safe_describe(df_clean)
                return {
                    "filename": file.filename,
                    "type": "tabular_json",
                    "columns": df_clean.columns.tolist(),
                    "preview": preview,
                    "description": description
                }
            else:
                keys = list(data.keys()) if isinstance(data, dict) else None
                return {
                    "filename": file.filename,
                    "type": "json",
                    "keys": keys,
                    "preview": data if isinstance(data, dict) else data[:10]
                }

        # --- Text ---
        elif filename.endswith(".txt"):
            text = content.decode("utf-8", errors="ignore")
            words = text.split()
            preview = text[:500]
            return {
                "filename": file.filename,
                "type": "text",
                "preview": preview,
                "char_count": len(text),
                "word_count": len(words),
                "line_count": len(text.splitlines()),
                "top_words": Counter(words).most_common(10)
            }

        # --- Images ---
        elif filename.endswith((".png", ".jpg", ".jpeg")):
            img = Image.open(io.BytesIO(content))
            encoded_img = base64.b64encode(content).decode("utf-8")
            return {
                "filename": file.filename,
                "type": "image",
                "image_size": img.size,
                "color_mode": img.mode,
                "image_base64": encoded_img
            }

        # --- Unknown ---
        else:
            return {
                "filename": file.filename,
                "type": "unknown",
                "size_bytes": len(content),
                "message": "No dashboard available. Metadata shown."
            }

    except Exception as e:
        return {"error": f"Failed to process file: {str(e)}"}
    
# ---------------- UPDATE ----------------
@app.put("/file/{file_id}")
async def update_file(file_id: int, 
                      new_file: UploadFile = File(...), 
                      db: Session = Depends(get_db),
                      current_user: str = Depends(get_current_user)):
    db_file = db.query(UploadedFile).filter(UploadedFile.id == file_id, 
                                            UploadedFile.user_email == current_user).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    content = await new_file.read()
    db_file.filename = new_file.filename
    db_file.content_type = new_file.content_type
    db_file.data = content
    # db_file.user_email = current_user
    db.commit()
    db.refresh(db_file)
    return {"status": "File updated successfully!", "id": db_file.id}

@app.delete("/file/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db),current_user:str = Depends(get_current_user)):
    db_file = db.query(UploadedFile).filter(UploadedFile.id == file_id,UploadedFile.user_email == current_user).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    db.delete(db_file)
    db.commit()
    return {"status": "File deleted successfully!"}
@app.get("/file_bytes/{file_id}")
def get_raw_file_bytes(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    file = db.query(UploadedFile).filter(
        UploadedFile.id == file_id,
        UploadedFile.user_email == current_user
    ).first()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    return Response(
        content=file.data,
        media_type=file.content_type
    )

