from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List
import base64
from io import BytesIO
from datetime import date
import psycopg2
import face_recognition
import numpy as np
from PIL import Image
from .database import conn

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Connect to the database
# conn = psycopg2.connect(database="fakecoder_postgres", user="fakecoder", password="FakeCoder01", host="localhost", port="5432")

# Endpoint to add new user
@app.post("/users")
async def add_user(name: str, email : str, image: UploadFile = File(...)):
    # Read image file and convert to numpy array
    img_data = await image.read()
    nparr = np.frombuffer(img_data, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Encode image as base64 string
    img_str = base64.b64encode(img_data).decode("utf-8")

    # Store user information in database
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, email, image) VALUES (%s, %s, %s)", (name, email, img_data))
    conn.commit()

    return {"message": "User added successfully"}

# Endpoint to get user information
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    cur = conn.cursor()
    cur.execute("SELECT name, email, image FROM users WHERE id = %s", (user_id,))
    row = cur.fetchone()

    if row is None:
        return {"error": "User not found"}

    name, email, img_data = row
    img_str = base64.b64encode(img_data).decode("utf-8")

    return {"name": name, "email" : email, "image": img_str}

# Endpoint to mark attendance
@app.post("/attendance")
async def mark_attendance(user_id: int):
    # Capture image from camera
    # Implement

    # Load user images from database
    cur = conn.cursor()
    cur.execute("SELECT image FROM users WHERE id = %s", (user_id,))
    rows = cur.fetchall()
    known_face_encodings = [np.frombuffer(row[0], np.uint8) for row in rows]

    # Convert captured image to numpy array
    img_np = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)

    # Find faces in the captured image
    face_locations = face_recognition.face_locations(img_np)
    face_encodings = face_recognition.face_encodings(img_np, face_locations)

    # Check if any of the detected faces match the user's face
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

        if any(matches):
            # Mark attendance in the database
            cur.execute("INSERT INTO attendance (user_id, date, status) VALUES (%s, %s, %s)", (user_id, date.today(), "present"))
            conn.commit()

            return {"message": "Attendance marked successfully"}

    return {"error": "Face not recognized"}


# Endpoint to get attendance records for a user
@app.get("/attendance/{user_id}")
async def get_attendance(user_id: int):
    cur = conn.cursor()
    cur.execute("SELECT date, status FROM attendance WHERE user_id = %s", (user_id,))
    rows = cur.fetchall()

    attendance_records = [{"date": row[0], "status": row[1]} for row in rows]

    return {"attendance": attendance_records}


# Render Add User
@app.get('/add-user')
def add_user_form():
    return templates.TemplateResponse('add-user.html')

# Render Add User
@app.get('/verify')
def verify_user():
    return templates.TemplateResponse('main.html')

# See User Attendance
@app.get('/dash')
def add_user_form():
    return templates.TemplateResponse('attendance.html')

# All user list page
@app.get('/')
def add_user_form():
    return templates.TemplateResponse('index.html')
