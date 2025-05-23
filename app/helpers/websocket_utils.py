from abc import ABC, abstractmethod
from typing import Dict
from uuid import UUID

from fastapi import WebSocket
from schemas.queues import AvaiableItemResponse, NoItemsAvaiable
from schemas.websocket import WebsocketFailResponse, WebsocketSuccessResponse
from service.rpa.queue_services import QueueService


class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, worker_id: str, websocket: WebSocket):
        self.active_connections[worker_id] = websocket

    async def disconnect(self, worker_id: str):
        websocket = self.active_connections.pop(worker_id, None)
        if websocket and websocket.client_state.value != 3:  # 3 = CLOSED
            await websocket.close()

    def get_next_item(self, queue_name: str, worker_id: str, db):
        item = QueueService.get_next_item(queue_name, worker_id, db)

        if item is None:
            return NoItemsAvaiable()

        return AvaiableItemResponse(item=item)

    def mark_success(self, item_id: UUID, db):
        try:
            QueueService.mark_success(item_id, db)
        except Exception as e:
            raise e
        response = WebsocketSuccessResponse(item_id=str(item_id))
        return response.model_dump(mode="json")

    def mark_fail(self, item_id: UUID, error: str, db):
        try:
            QueueService.mark_fail(item_id, error, db)
        except Exception as e:
            raise e
        response = WebsocketFailResponse(item_id=str(item_id))
        return response.model_dump(mode="json")


class WebSocketContext:
    def __init__(self, websocket: WebSocket, data: dict, db, manager):
        self.websocket = websocket
        self.data = data
        self.db = db
        self.manager = manager

    @property
    def worker_id(self) -> str:
        return self.data.get("worker_id")

    @property
    def queue_name(self) -> str:
        return self.data.get("queue_name")

    @property
    def item_id(self) -> UUID:
        return UUID(self.data.get("item", {}).get("id"))

    @property
    def error_msg(self) -> str:
        return self.data.get("item", {}).get("error_msg", "Unknown error")


class WebSocketAction(ABC):
    @abstractmethod
    async def execute(self, websocket: WebSocket, data: dict, db, manager):
        pass


class GetNextItemAction(WebSocketAction):
    async def execute(self, context: WebSocketContext):
        item = context.manager.get_next_item(context.queue_name, context.worker_id, context.db)
        await context.websocket.send_json(item.model_dump(mode="json"))


class MarkSuccessAction(WebSocketAction):
    async def execute(self, context: WebSocketContext):
        item_id = context.item_id
        result = context.manager.mark_success(item_id, context.db)
        await context.websocket.send_json(result)


class MarkFailAction(WebSocketAction):
    async def execute(self, context: WebSocketContext):
        item_id = context.item_id
        error_msg = context.error_msg
        result = context.manager.mark_fail(item_id, error_msg, context.db)
        await context.websocket.send_json(result)


ACTION_REGISTRY: Dict[str, WebSocketAction] = {
    "get_next": GetNextItemAction(),
    "mark_success": MarkSuccessAction(),
    "mark_fail": MarkFailAction(),
}
