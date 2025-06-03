import uuid
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.image import BinaryImageRequest
from app.celery.tasks import binarize_image_task
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/binary_image", tags=["Бинаризация"])
def binary_image(request: BinaryImageRequest, current_user: User = Depends(get_current_user)):
    if request.algorithm not in ["otsu", "niblack", "sauvola"]:
        raise HTTPException(status_code=400, detail="Unsupported algorithm")

    task_id = str(uuid.uuid4())

    binarize_image_task.delay(
        task_id=task_id,
        user_id=str(current_user.id),
        image_base64=request.image,
        algorithm=request.algorithm
    )

    return {"task_id": task_id}
