from typing import Literal

from pydantic import BaseModel

class BinaryImageRequest(BaseModel):
    image: str
    algorithm: Literal["otsu", "niblack", "sauvola"]

class BinaryImageResponse(BaseModel):
    binarized_image: str
