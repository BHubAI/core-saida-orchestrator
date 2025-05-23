from typing import Any, List, Optional
from uuid import UUID

from models.queue import Queue
from models.queue_item import QueueItem, RPAStatus
from pydantic import BaseModel


class QueueItemCreate(BaseModel):
    payload: dict
    priority: Optional[int] = 0


class QueueItemOut(BaseModel):
    id: UUID
    payload: Any
    status: str

    class Config:
        orm_mode = True


class NoItemsAvaiable(BaseModel):
    message: str = "No items avaiable at the moment"


class AvaiableItemResponse(BaseModel):
    item: QueueItem


class AvaiableItems(BaseModel):
    items: List[QueueItem]


class QueueCreatedResponse(BaseModel):
    status: str = "Queue created"
    queue_info: Queue


class ItemAddedToQueue(BaseModel):
    status: str = "Item added successfully"
    item_status: RPAStatus = QueueItem.status
    priority: int = QueueItem.priority


class QueueStatusResponse(BaseModel):
    queue_name: str
    is_active: bool
    message: str
