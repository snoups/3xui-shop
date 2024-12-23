import logging
import uuid

from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.services.vpn import VPNService
from app.db.models.promocode import Promocode

logger = logging.getLogger(__name__)


class PromocodeService:
    """
    Service for managing promocodes, including creation, retrieval, deletion, and activation.

    This service provides methods for handling promocodes, such as generating new promocodes,
    retrieving them by code, deleting, and activating them.

    Attributes:
        session (AsyncSession): The session used for interacting with the database.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the PromocodeService instance.

        Arguments:
            session (AsyncSession): The database session for performing operations.
        """
        self.session = session
        logger.info("PromocodeService initialized.")

    def _generate_code(self) -> str:
        """
        Generate a unique 8-character promocode.

        Returns:
            str: The generated promocode, consisting of uppercase alphanumeric characters.
        """
        code = str(uuid.uuid4()).replace("-", "").upper()[:8]
        logger.debug(f"Generated promocode: {code}")
        return code

    async def create_promocode(self, traffic: int, duration: int) -> Promocode:
        """
        Create a new promocode with specified traffic and duration.

        Arguments:
            traffic (int): The amount of traffic in GB for the promocode.
            duration (int): The duration in days for the promocode.

        Returns:
            Promocode: The created Promocode instance.
        """
        async with self.session() as session:
            code = self._generate_code()

            existing_promocode = await Promocode.exists(session, code=code)
            if existing_promocode:
                logger.warning(f"Promocode {code} already exists. Retrying code generation.")
                code = self._generate_code()

            promocode = await Promocode.create(
                session,
                code=code,
                traffic=traffic,
                duration=duration,
            )
            logger.info(
                f"Promocode {code} created with {traffic} GB traffic and {duration} days duration."
            )
            return promocode

    async def get_promocode(self, code: str) -> Promocode | None:
        """
        Retrieve a promocode by its code.

        Arguments:
            code (str): The promocode to retrieve.

        Returns:
            Promocode | None: The retrieved Promocode if found, otherwise None.
        """
        async with self.session() as session:
            promocode = await Promocode.get(session, code=code)
            if promocode:
                logger.info(f"Promocode {code} retrieved from the database.")
            else:
                logger.warning(f"Promocode {code} not found.")
            return promocode

    async def delete_promocode(self, code: str) -> bool:
        """
        Delete a promocode by its code.

        Arguments:
            code (str): The promocode to delete.

        Returns:
            bool: True if the promocode was deleted successfully, False otherwise.
        """
        session: AsyncSession
        async with self.session() as session:
            promocode = await Promocode.get(session, code=code)
            if promocode:
                await session.delete(promocode)
                await session.commit()
                logger.info(f"Promocode {code} deleted successfully.")
                return True
            else:
                logger.error(f"Promocode {code} not found for deletion.")
                return False

    async def activate_promocode(self, code: str, user_id: int) -> bool:
        """
        Activate a promocode for a specific user.

        Arguments:
            code (str): The promocode to activate.
            user_id (int): The user ID who is activating the promocode.

        Returns:
            bool: True if the promocode was successfully activated, False otherwise.
        """
        session: AsyncSession
        async with self.session() as session:
            promocode: Promocode = await Promocode.get(session, code=code)

            if promocode:
                if promocode.is_activated:
                    logger.warning(f"Promocode {code} is already activated.")
                    return False

                promocode.is_activated = True
                promocode.activated_by = user_id
                await session.commit()
                logger.info(f"Promocode {code} activated by user {user_id}.")
                return True
            else:
                logger.error(f"Promocode {code} not found for activation.")
                return False
