import logging

from py3xui import AsyncApi
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.bot.models import Connection
from app.config import Config
from app.db.models import Server, User

logger = logging.getLogger(__name__)


class ServerPoolService:
    def __init__(self, config: Config, session: async_sessionmaker) -> None:
        self.config = config
        self.session = session
        self.__servers: dict[int, Connection] = {}
        logger.info("Server Pool Service initialized.")

    async def __add_server(self, server: Server) -> None:
        if server.id not in self.__servers:
            api = AsyncApi(
                host=server.host,
                username=self.config.xui.USERNAME,
                password=self.config.xui.PASSWORD,
                token=self.config.xui.TOKEN,
                use_tls_verify=False,
                logger=logging.getLogger(f"xui_{server.name}"),
            )
            try:
                await api.login()
                server_conn = Connection(server=server, api=api)
                self.__servers[server.id] = server_conn
                logger.info(f"Server {server.name} ({server.host}) added successfully.")
            except Exception as exception:
                logger.error(
                    f"Failed to initialize server {server.name} ({server.host}): {exception}"
                )

    def __remove_server(self, server: Server) -> None:
        if server.id in self.__servers:
            try:
                del self.__servers[server.id]
                logger.info(f"Server {server.name} removed successfully.")
            except Exception as exception:
                logger.error(f"Failed to remove server {server.name}: {exception}")

    async def get_connection(self, user: User) -> Connection | None:
        if not user.server_id:
            logger.debug(f"User {user.tg_id} not assigned to any server.")
            return None

        connection = self.__servers.get(user.server_id)

        if not connection:
            available_servers = list(self.__servers.keys())
            logger.critical(
                f"Server {user.server_id} not found in pool. "
                f"User assigned server: {user.server_id}, "
                f"Available servers in pool: {available_servers}"
            )

            async with self.session() as session:
                server = await Server.get_by_id(session, user.server_id)

            if server:
                logger.debug(f"Server {server.name} ({server.host}) found in database.")
                # TODO: Try to add server to pool
            else:
                logger.error(f"Server {user.server_id} not found in database.")

            return None

        async with self.session() as session:
            server = await Server.get_by_id(session, user.server_id)

        connection.server = server
        return connection

    async def sync_servers(self) -> None:
        async with self.session() as session:
            db_servers = await Server.get_all(session)

        if not db_servers and not self.__servers:
            logger.warning("No servers found in the database.")
            return

        db_server_map = {server.id: server for server in db_servers}

        for server_id in list(self.__servers.keys()):
            if server_id not in db_server_map:
                self.__remove_server(self.__servers[server_id].server)

        for server in db_servers:
            if server.id not in self.__servers:
                await self.__add_server(server)

        logger.info(f"Sync complete. Currently active servers: {len(self.__servers)}")

    async def assign_server_to_user(self, user: User) -> None:
        async with self.session() as session:
            server = await Server.get_available(session)
            await User.update(session, user.tg_id, server_id=server.id)
            # await session.refresh(user, ["server"])
