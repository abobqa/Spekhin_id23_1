from celery import Celery
from redislite import Redis

redis_path = '/tmp/redislite.db'
redis_connection = Redis(redis_path)

celery_app = Celery(
    "binarization_tasks",
    broker=f'redis+socket://{redis_connection.socket_file}',
    backend=f'redis+socket://{redis_connection.socket_file}'
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
)
