from fastapi import FastAPI, HTTPException
from pyrogram import Client
from pydantic import BaseModel
import os

app = FastAPI()

# Replace with your actual API ID, API hash, and Bot Token (if you're using a bot).
api_id = os.getenv('API_ID')  # or hardcode the value
api_hash = os.getenv('API_HASH')  # or hardcode the value
bot_token = os.getenv('BOT_TOKEN')  # or hardcode the value

# Initialize the Pyrogram client
client = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

class UsernameResponse(BaseModel):
    username: str
    chat_id: int

@app.get("/get_chat_id", response_model=UsernameResponse)
async def get_chat_id(username: str):
    """Get the chat ID for the provided username."""
    try:
        # Fetch chat information using Pyrogram
        chat = await client.get_chat(username)
        return {"username": username, "chat_id": chat.id}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error fetching chat: {str(e)}")

# Run the FastAPI app using uvicorn when deployed in Vercel
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
