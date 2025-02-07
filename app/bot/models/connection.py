from py3xui import AsyncApi

from app.db.models import Server


class Connection:
    def __init__(self, server: Server, api: AsyncApi) -> None:
        self.server = server
        self.api = api
