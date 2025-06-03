import requests
import websockets
import asyncio
import base64
import json
from getpass import getpass

API_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"

def login():
    email = input("Email: ")
    password = getpass("Password: ")

    response = requests.post(f"{API_URL}/login/", json={"email": email, "password": password})
    response.raise_for_status()
    data = response.json()
    return data["id"], data["token"]

def send_image(task_token: str, image_path: str, algorithm: str):
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    img_b64 = base64.b64encode(img_bytes).decode()

    headers = {"Authorization": f"Bearer {task_token}"}
    resp = requests.post(f"{API_URL}/binary_image", json={
        "image": img_b64,
        "algorithm": algorithm
    }, headers=headers)
    resp.raise_for_status()
    return resp.json()["task_id"]

async def websocket_listener(user_id, token, queue):
    uri = f"{WS_URL}/{user_id}?token={token}"
    async with websockets.connect(uri) as websocket:
        print("[WebSocket] Подключено. Ожидание статусов...")
        while True:
            msg = await websocket.recv()
            await queue.put(msg)

async def listen_ws_and_process(queue, task_id):
    while True:
        msg = await queue.get()
        data = json.loads(msg)

        if data["task_id"] != task_id:
            continue

        if data["status"] == "STARTED":
            print(f"[STARTED] Алгоритм: {data['algorithm']}")
        elif data["status"] == "PROGRESS":
            print(f"[PROGRESS] {data['progress']}%")
        elif data["status"] == "COMPLETED":
            print("[COMPLETED] Сохраняем изображение...")
            image_bytes = base64.b64decode(data["binarized_image"])
            with open("result.png", "wb") as f:
                f.write(image_bytes)
            print("Готово: result.png")
            break

async def main():
    user_id, token = login()
    img_path = input("Путь к изображению: ")
    algorithm = input("Алгоритм (otsu/niblack/sauvola): ")

    queue = asyncio.Queue()
    listener_task = asyncio.create_task(websocket_listener(user_id, token, queue))
    await asyncio.sleep(0.5)
    task_id = send_image(token, img_path, algorithm)
    print(f"[REST] Задача отправлена. task_id = {task_id}")

    await listen_ws_and_process(queue, task_id)

if __name__ == "__main__":
    asyncio.run(main())
