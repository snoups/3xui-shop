import logging
import uuid

from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.services.vpn import VPNService
from app.db.models.promocode import Promocode

logger = logging.getLogger(__name__)


class PromocodeService:
    def __init__(self, session: AsyncSession, vpn: VPNService) -> None:
        self.session = session
        self.vpn = vpn

    def _generate_code(self) -> str:
        return str(uuid.uuid4()).replace("-", "").upper()[:8]

    async def create_promocode(self, traffic: int, duration: int) -> Promocode:
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
        async with self.session() as session:
            promocode = await Promocode.get(session, code=code)
            if promocode:
                logger.info(f"Promocode {code} retrieved from the database.")
            else:
                logger.warning(f"Promocode {code} not found.")
            return promocode

    async def delete_promocode(self, code: str) -> bool:
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
