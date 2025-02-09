import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Server

logger = logging.getLogger(__name__)


class ServerService:
    """
    Service for managing servers in the database.

    Provides methods to add, retrieve, update, and delete servers.

    Attributes:
        session (AsyncSession): Database session for operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initializes the ServerService.

        Arguments:
            session (AsyncSession): The database session for interacting with the database.
        """
        self.session = session
        logger.info("ServersService initialized.")

    async def add_server(self, name: str, **kwargs) -> Server | None:
        """
        Adds a new server to the database.

        Arguments:
            name (str): The name of the server.
            kwargs (dict): Additional server attributes.

        Returns:
            Server | None: The created server if successful, None if the server already exists.
        """
        async with self.session() as session:
            if await Server.exists(session, name=name):
                logger.debug(f"Server {name} already exists. Skipping adding.")
                return None

            server = await Server.create(session, name=name, **kwargs)
            logger.info(f"Server {name} added with attributes: {kwargs}.")
            return server

    async def get_server(self, name: str) -> Server | None:
        """
        Retrieves a server by its name.

        Arguments:
            name (str): The name of the server.

        Returns:
            Server | None: The server if found, None otherwise.
        """
        async with self.session() as session:
            server = await Server.get(session, name=name)
            logger.debug(
                f"Server {name} {'retrieved' if server else 'not found'} from the database."
            )
            return server

    async def update_server(self, name: str, **kwargs) -> bool:
        """
        Updates an existing server's attributes.

        Arguments:
            name (str): The name of the server.
            kwargs (dict): New attributes for the server.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        async with self.session() as session:
            server = await Server.get(session, name=name)

            if server:
                await Server.update(session, server_id=server.id, **kwargs)
                logger.info(f"Server {name} updated with attributes: {kwargs}.")
                return True

            logger.debug(f"Server {name} not found for update.")
            return False

    async def delete_server(self, name: str) -> bool:
        """
        Deletes a server by its name.

        Arguments:
            name (str): The name of the server.

        Returns:
            bool: True if the server was deleted successfully, False otherwise.
        """
        async with self.session() as session:
            deleted = await Server.delete(session, name=name)

            if deleted:
                logger.info(f"Server {name} deleted successfully.")
                return True

            logger.debug(f"Server {name} not found for deletion.")
            return False

    async def get_all_servers(self) -> list[Server]:
        """
        Retrieves all servers from the database.

        Returns:
            list[Server]: A list of all servers.
        """
        async with self.session() as session:
            servers = await Server.get_all(session)
            logger.debug(f"Retrieved {len(servers)} servers from the database.")
            return servers
