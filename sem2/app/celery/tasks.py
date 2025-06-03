import time
from sem2.app.celery import celery_app
from sem2.app.services.binarization import decode_base64_image, encode_base64_image, binarize_image
from sem2.app.websocket.pubsub import publish_message

@celery_app.task(name="app.celery.tasks.binarize_image_task")
def binarize_image_task(task_id: str, user_id: str, image_base64: str, algorithm: str):
    publish_message(user_id, {
        "status": "STARTED",
        "task_id": task_id,
        "algorithm": algorithm
    })

    publish_message(user_id, {"status": "PROGRESS", "task_id": task_id, "progress": 10})
    time.sleep(0.5)

    image = decode_base64_image(image_base64)
    publish_message(user_id, {"status": "PROGRESS", "task_id": task_id, "progress": 30})
    time.sleep(0.5)

    bin_img = binarize_image(image, algorithm)
    publish_message(user_id, {"status": "PROGRESS", "task_id": task_id, "progress": 60})
    time.sleep(0.5)

    bin_img_base64 = encode_base64_image(bin_img)
    publish_message(user_id, {"status": "PROGRESS", "task_id": task_id, "progress": 80})
    time.sleep(0.5)

    publish_message(user_id, {
        "status": "COMPLETED",
        "task_id": task_id,
        "binarized_image": bin_img_base64
    })
