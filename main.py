from fastapi import FastAPI

from brain.conversation_manager import (
    ConversationManager
)

app = FastAPI()

clara = ConversationManager()


@app.get("/")
def home():

    return {
        "message": "CLARA is alive"
    }


@app.get("/chat/{message}")
def chat(message: str):

    response = clara.process_message(
        message
    )

    return response