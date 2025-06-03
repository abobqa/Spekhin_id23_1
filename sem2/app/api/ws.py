from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sem2.app.websocket.connection_manager import manager
from sem2.app.websocket.pubsub import subscribe_to_user_channel
from jose import JWTError, jwt
from sem2.app.core.config import settings

router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: str = Query(...)
):

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        token_user_email: str = payload.get("sub")
        if token_user_email is None:
            await websocket.close(code=1008)
            return
    except JWTError:
        await websocket.close(code=1008)
        return

    await manager.connect(user_id, websocket)
    subscribe_to_user_channel(user_id)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)
