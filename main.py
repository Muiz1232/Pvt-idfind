from fastapi import FastAPI, HTTPException, Query
from pyrogram import Client
from pyrogram.errors import UsernameNotOccupied, PeerIdInvalid, FloodWait, RPCError
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

@app.on_event("startup")
async def startup():
    """Start the Pyrogram client when the FastAPI app starts."""
    try:
        await client.start()  # Start the client asynchronously
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting Pyrogram client: {str(e)}")

@app.on_event("shutdown")
async def shutdown():
    """Stop the Pyrogram client when the FastAPI app shuts down."""
    await client.stop()

@app.get("/get_chat_id", response_model=UsernameResponse)
async def get_chat_id(username: str = Query(..., min_length=5, max_length=32)):
    """
    Get the chat ID for the provided username.
    Includes error handling for username not found, invalid format, and other exceptions.
    """
    try:
        # Fetch chat information using Pyrogram
        chat = await client.get_chat(username)
        return {"username": username, "chat_id": chat.id}

    except UsernameNotOccupied:
        raise HTTPException(status_code=404, detail=f"Username '{username}' does not exist or is not valid.")
    except PeerIdInvalid:
        raise HTTPException(status_code=403, detail=f"Username '{username}' is private or the bot cannot access it.")
    except FloodWait as e:
        raise HTTPException(status_code=429, detail=f"Flood wait. Please try again in {e.x} seconds.")
    except RPCError as e:
        raise HTTPException(status_code=500, detail=f"Telegram API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Run the FastAPI app using uvicorn when deployed in Vercel
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
