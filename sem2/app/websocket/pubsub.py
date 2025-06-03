import json
import threading
import asyncio
from redislite import Redis
from sem2.app.websocket.connection_manager import manager

redis_path = "/tmp/redislite.db"
redis = Redis(redis_path)

EVENT_LOOP = None

def publish_message(user_id: str, message: dict):
    print(f"[PUB] → user:{user_id}: {message}")
    redis.publish(f"user:{user_id}", json.dumps(message))


def subscribe_to_user_channel(user_id: str):
    def listen():
        pubsub = redis.pubsub()
        pubsub.subscribe(f"user:{user_id}")

        for msg in pubsub.listen():
            if msg['type'] == 'message':
                try:
                    data = json.loads(msg['data'])
                    if EVENT_LOOP:
                        asyncio.run_coroutine_threadsafe(
                            manager.send_json(user_id, data),
                            EVENT_LOOP
                        )
                except Exception as e:
                    print(f"[WebSocket ERROR] {e}")

    thread = threading.Thread(target=listen, daemon=True)
    thread.start()
