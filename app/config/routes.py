from fastapi import APIRouter,WebSocket, WebSocketDisconnect ,Request ,HTTPException
from app.logging_config import logger
from app.services.sesame_voice_model.voicechat import handle_voice_ws
from app.services.sesame_voice_model.csm_voice_trainer import train_csm
from app.services.vv.vv import VIV ,VVSupabase
from fastapi.responses import FileResponse
from starlette.responses import PlainTextResponse  
from pydantic import BaseModel

router = APIRouter()

@router.get("/voice-chat")
async def voice_chat():
    return FileResponse("app/static/voice_chat.html")

@router.post("/voice-train")
async def voice_train():
    train_csm()
    return PlainTextResponse("CSM training started and completed successfully.")

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        await handle_voice_ws(websocket)
    except WebSocketDisconnect:
        print("Client disconnected")


class BotRequest(BaseModel):
    user_id: str
    message: str

@router.post("/bot")
async def bot(request: BotRequest):
    vv_chat = VIV(user_id=request.user_id)
    vv_chat._upload_message(message=request.message, sender="user")
    return vv_chat.bot_reply(request.message)

@router.post("/load_chat")
async def load_chat(request: Request):
    data = await request.json()
    user_id = data.get('user_id')
    vv_supabase = VVSupabase(user_id=user_id)
    user_chat = vv_supabase.check_for_chat_in_supabase()
    vv_chat = VIV(user_id=user_id)
    if not user_chat:
        return vv_chat.initialise_new_chat()
    else:
        return vv_chat.bot_reply(greet_user=True)