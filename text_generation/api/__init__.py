import torch
from fastapi import APIRouter, Request
from schemas import ServerStatus

from api import prediction
from enums import DeviceTypeEnum


router = APIRouter()
router.include_router(prediction.router, prefix="/prediction")


@router.get("/", response_model=ServerStatus)
async def get_server_status(request: Request) -> ServerStatus:
    device: torch.device = request.app.state.device
    return ServerStatus(device_type=DeviceTypeEnum.GPU if device.type == "cuda" else DeviceTypeEnum.CPU)
