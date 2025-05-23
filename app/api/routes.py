from api.audit.rpa_audit import RPAAuditoriaEndpoint
from api.base.endpoints import BaseEndpoint
from api.camunda.process_starter import ProcessMessageEndpoint
from api.camunda.side_effect import SideEffectEndpoint
from api.deps import DDLogger
from api.rpa.bhub import BHubLogsEndpoint, BHubQueuesEndpoint
from api.rpa.bhub_websocket import BHubWebSocket
from api.rpa.melius import MeliusEndpoint
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse, PlainTextResponse


class Routers:
    def __init__(self):
        self.endpoints: list[BaseEndpoint] = [
            SideEffectEndpoint(),
            ProcessMessageEndpoint(),
            MeliusEndpoint(),
            BHubQueuesEndpoint(),
            BHubLogsEndpoint(),
            BHubWebSocket(),
            RPAAuditoriaEndpoint(),
        ]

    def get_routers(self):
        for endpoint in self.endpoints:
            yield endpoint.get_router()


def register_routes(app: FastAPI):
    api_routers = Routers()

    @app.get("/robots.txt")
    def robots():
        return PlainTextResponse("User-agent: *\nDisallow: /")

    @app.get("/health")
    def health_check(logger: DDLogger) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok"})

    for router in api_routers.get_routers():
        app.include_router(router)
