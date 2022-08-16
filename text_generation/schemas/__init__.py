from pydantic import BaseModel

from enums import DeviceTypeEnum


class ServerStatus(BaseModel):
    device_type: DeviceTypeEnum
