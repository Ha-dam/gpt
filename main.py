# pip install -q openai
# pip install --upgrade openai
# pip install fastapi uvicorn
# pip install python-dotenv
# pip install SQLAlchemy

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, DiaryEntry, create_diary_entry
from dotenv import load_dotenv
import openai 
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

#CORS 설정 (안드로이드 애플리케이션과의 HTTP 통신을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
model = "gpt-3.5-turbo"

messages = [{"role": "system", "content": "You are a program that receives keywords related to time, location, people, and experience to generate diaries. "
                       + "The main information provided will include emotional state scores (comfortable, happy, angry, sad), date, location, and people as basic information, "
                       + "and the user will input text about their experiences that day.\n\nBased on the information provided, please write a diary. "
                       + "The diary will be written in Korean."
                       + "make the content longer and more natural"
                       + "Don't talk about emotion's score"}]

class Item(BaseModel):
    date: str
    location: float
    people: str
    happy: int
    comfortable: int
    sad: int
    angry: int
    experience: str

@app.get("/")
def home():
    return {"message": "Hello, World!"}

@app.route('/mypage')
def mypage():
    return 'This is My Page!'

@app.post("/items/")
async def create_item(item: Item):
    return item
@app.route('/chat')
def chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post('/chat_response')
async def chat_response(
        request: Request,
        date: str = Form(...),
        location: str = Form(...),
        people: str = Form(...),
        happy: int = Form(0),
        comfortable: int = Form(0),
        sad: int = Form(0),
        angry: int = Form(0),
        experience: str = Form(...)
):
    category = categorize_response(date, location, people, experience)    

    messages = [
        {
            "role": "system",
            "content": "You are a program that receives keywords related to time, location, people, and experience to generate diaries. "
            + "The main information provided will include emotional state scores (comfortable, happy, angry, sad), date, location, and people as basic information, "
            + "and the user will input text about their experiences that day.\n\nBased on the information provided, please write a diary. "
            + "The diary will be written in Korean."
            + "make the content longer and more natural"
            + "Don't talk about emotion's score"
        },
        {
            "role": "user",
            "content": f"Date: {date}, Location: {location}, People: {people}, Happy: {happy}, Comfortable: {comfortable}, Sad: {sad}, Angry: {angry}, Experience: {experience}, Category: {category}"
        }
    ]

    response = openai.ChatCompletion.create(
        model="ft:gpt-3.5-turbo-1106:personal::8RgY8JYa",
        messages=messages,
        temperature=1,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0.7,
        presence_penalty=0
    )
    reply = response.choices[0].message.content
    
    #SQL 데이터베이스로 데이터 전송 (필요 없으면 생략하기)
    db = SessionLocal()
    create_diary_entry(db, reply=reply, category=category)
    db.close()

    return templates.TemplateResponse("chat.html", {"request": request, "date": date, "location": location, "people": people,
                                                    "happy": happy, "comfortable": comfortable, "sad": sad,
                                                    "angry": angry, "experience": experience,
                                                    "model_response": reply, "category": category})

# 제목 생성
def categorize_response(date, location, people, experience):
    summary_instruct = [
        {
            "role": "system",
            "content": "Please generate a sentence using the given parameters that can be used as a title for a diary entry."
            +"in 15 letters or less than 15 letters"
            +f" Date:  {date}, Location: {location}, People: {people}, Experience: {experience}"
        }
    ]

    summary = openai.ChatCompletion.create(
        model="ft:gpt-3.5-turbo-1106:personal::8RpLwK9R",
        messages=summary_instruct,
        max_tokens=100,
        temperature=0.5,
        top_p=1
    ).choices[0].message.content
    return summary


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

#uvicorn main:app --reload