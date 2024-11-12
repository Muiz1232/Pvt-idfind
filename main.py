from fastapi import FastAPI, HTTPException, Query
from pyrogram import Client
from pyrogram.errors import UsernameNotOccupied, PeerIdInvalid, FloodWait, RPCError
from pydantic import BaseModel
import os

# FastAPI app instance
app = FastAPI()

# Fetch environment variables for Telegram API credentials
api_id = os.getenv('API_ID')  # Your Telegram API ID
api_hash = os.getenv('API_HASH')  # Your Telegram API Hash
bot_token = os.getenv('BOT_TOKEN')  # Your Bot Token

# This is a global client instance that we will reinitialize on each request
client = None

class UsernameResponse(BaseModel):
    username: str
    chat_id: int

def create_client():
    """Helper function to create a new Pyrogram client with an in-memory database."""
    return Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token, session_name=":memory:")

@app.on_event("startup")
async def startup():
    """Initialize the client at the start of the application."""
    global client
    client = create_client()
    try:
        await client.start()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting Pyrogram client: {str(e)}")

@app.on_event("shutdown")
async def shutdown():
    """Clean up the Pyrogram client when the app shuts down."""
    global client
    if client:
        await client.stop()

@app.get("/get_chat_id", response_model=UsernameResponse)
async def get_chat_id(username: str = Query(..., min_length=5, max_length=32)):
    """
    Get the chat ID for the provided username.
    Handles errors like username not found, invalid format, etc.
    """
    global client
    if not client:
        client = create_client()
        await client.start()  # Ensure client is started before use

    try:
        # Fetch the chat information using Pyrogram
        chat = await client.get_chat(username)
        return {"username": username, "chat_id": chat.id}

    except UsernameNotOccupied:
        raise HTTPException(status_code=404, detail=f"Username '{username}' does not exist or is invalid.")
    except PeerIdInvalid:
        raise HTTPException(status_code=403, detail=f"Username '{username}' is private or the bot cannot access it.")
    except FloodWait as e:
        raise HTTPException(status_code=429, detail=f"Flood wait. Please try again in {e.x} seconds.")
    except RPCError as e:
        raise HTTPException(status_code=500, detail=f"Telegram API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# To allow Vercel to run the app, we need to define the entry point.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
