from pydantic import BaseModel


class WebsocketSuccessResponse(BaseModel):
    status: str = "Item marked as succcess"
    item_id: str


class WebsocketFailResponse(BaseModel):
    status: str = "Item marked as fail"
    item_id: str
