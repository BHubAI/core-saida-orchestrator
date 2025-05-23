import json

from api.base.endpoints import BaseEndpoint
from api.deps import get_session
from fastapi import WebSocket, WebSocketDisconnect
from helpers.websocket_utils import (
    ACTION_REGISTRY,
    WebSocketConnectionManager,
    WebSocketContext,
)


ROUTE_PREFIX = "/api/ws"


class BHubWebSocket(BaseEndpoint):
    def __init__(self):
        super().__init__(tags=["BHub", "WebSocket"], prefix=ROUTE_PREFIX)
        self.manager = WebSocketConnectionManager()

        @self.router.websocket("/worker/{queue_name}")
        async def worker_ws(websocket: WebSocket, queue_name: str):
            await websocket.accept()
            session_gen = get_session()
            db = next(session_gen)

            try:
                while True:
                    message = await websocket.receive_text()
                    data = json.loads(message)
                    action_name = data.get("action")
                    data["queue_name"] = queue_name

                    action = ACTION_REGISTRY.get(action_name)
                    if not action:
                        await websocket.send_json({"error": f"Ação '{action_name}' inválida."})
                        continue

                    try:
                        context = WebSocketContext(websocket, data, db, self.manager)
                        await action.execute(context)
                    except Exception as e:
                        await websocket.send_json({"error": str(e)})

            except WebSocketDisconnect:
                worker_id = data.get("worker_id", "unknown")
                await self.manager.disconnect(worker_id)
            finally:
                try:
                    next(session_gen)
                except StopIteration:
                    pass
