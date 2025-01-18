import logging

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsDev
from app.bot.navigation import NavAdminTools
from app.bot.routes.utils.keyboard import back_keyboard
from app.bot.services import NotificationService, ServerService
from app.utils import is_valid_client_count, is_valid_host, ping_url

from .keyboard import confirm_add_server_keyboard, server_keyboard, servers_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


class AddServerStates(StatesGroup):
    name = State()
    host = State()
    subscription = State()
    max_clients = State()
    confirmation = State()


@router.callback_query(F.data == NavAdminTools.SERVER_MANAGEMENT, IsDev())
async def callback_server_management(
    callback: CallbackQuery,
    state: FSMContext,
    server_service: ServerService,
) -> None:
    logger.info(f"Dev {callback.from_user.id} opened servers.")
    await state.set_state(None)
    text = _("🌐 *Server management:*\n")
    servers = await server_service.get_all_servers()
    for server in servers:
        ping = await ping_url(server.host)
        online = True if ping else False
        if online != server.online:
            await server_service.update_server(server.name, online=online)

    if not servers:
        text += "\n" + _("_The list of servers is empty._")

    await callback.message.edit_text(text=text, reply_markup=servers_keyboard(servers))


# region Add Server
async def show_add_server(state: FSMContext) -> None:
    current_state = await state.get_state()
    data = await state.get_data()
    message: Message = data.get("message")

    server_name = data.get("server_name")
    server_host = data.get("server_host")
    server_subscription = data.get("server_subscription")
    server_max_clients = data.get("server_max_clients")

    text = _("🌐 *Server management:*\n") + "\n"
    name = _("- name: {server_name}\n".format(server_name=server_name))
    host = _("- host: {server_host}\n".format(server_host=server_host))
    subscription = _(
        "- subscription: {server_subscription}\n".format(server_subscription=server_subscription)
    )
    max_clients = _(
        "- max clients: {server_max_clients}\n".format(server_max_clients=server_max_clients)
    )
    reply_markup = back_keyboard(NavAdminTools.ADD_SERVER_BACK)

    match current_state:
        case AddServerStates.name:
            text += _(" _Enter the server name_")
            reply_markup = back_keyboard(NavAdminTools.SERVER_MANAGEMENT)
        case AddServerStates.host:
            text += name + "\n"
            text += _(" _Enter the server host_")
        case AddServerStates.subscription:
            text += name + host + "\n"
            text += _(" _Enter the subscription host_")
        case AddServerStates.max_clients:
            text += name + host + subscription + "\n"
            text += _(" _Enter the maximum number of clients_")
        case AddServerStates.confirmation:
            text += name + host + subscription + max_clients + "\n"
            text += _("_Press confirm to add the server_")
            reply_markup = confirm_add_server_keyboard()

    await message.edit_text(
        text=text,
        reply_markup=reply_markup,
    )


@router.callback_query(StateFilter("*"), F.data == NavAdminTools.ADD_SERVER_BACK, IsDev())
async def callback_add_server_back(callback: CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()

    match current_state:
        case AddServerStates.host:
            await state.set_state(AddServerStates.name)
        case AddServerStates.subscription:
            await state.set_state(AddServerStates.host)
        case AddServerStates.max_clients:
            await state.set_state(AddServerStates.subscription)
        case AddServerStates.confirmation:
            await state.set_state(AddServerStates.max_clients)

    await show_add_server(state)


@router.callback_query(F.data == NavAdminTools.ADD_SERVER, IsDev())
async def callback_add_server(callback: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"Dev {callback.from_user.id} started adding server.")
    await state.set_state(AddServerStates.name)
    await state.update_data(message=callback.message)
    await show_add_server(state)


@router.message(AddServerStates.name, IsDev())
async def message_name(
    message: Message,
    state: FSMContext,
    server_service: ServerService,
) -> None:
    server_name = message.text.strip()
    logger.info(f"Dev {message.from_user.id} entered server name: {server_name}")
    existing_server = await server_service.get_server(server_name)

    if not existing_server:
        await state.set_state(AddServerStates.host)
        await state.update_data(server_name=server_name)
        await show_add_server(state)
    else:
        await NotificationService.notify_by_message(
            message=message,
            text=_("❌ A server with that name already exists. Enter a different name."),
            duration=5,
        )


@router.message(AddServerStates.host, IsDev())
async def message_host(message: Message, state: FSMContext) -> None:
    server_host = message.text.strip()
    logger.info(f"Dev {message.from_user.id} entered server host: {server_host}")

    if is_valid_host(server_host):
        await state.set_state(AddServerStates.subscription)
        await state.update_data(server_host=server_host)
        await show_add_server(state)
    else:
        await NotificationService.notify_by_message(
            message=message,
            text=_("❌ Enter a valid URL or IP address."),
            duration=5,
        )


@router.message(AddServerStates.subscription, IsDev())
async def message_subscription(message: Message, state: FSMContext) -> None:
    server_subscription = message.text.strip()
    logger.info(f"Dev {message.from_user.id} entered server subscription: {server_subscription}")

    if is_valid_host(server_subscription):
        await state.set_state(AddServerStates.max_clients)
        await state.update_data(server_subscription=server_subscription)
        await show_add_server(state)
    else:
        await NotificationService.notify_by_message(
            message=message,
            text=_("❌ Enter a valid URL or IP address."),
            duration=5,
        )


@router.message(AddServerStates.max_clients, IsDev())
async def message_max_clients(message: Message, state: FSMContext) -> None:
    server_max_clients = message.text.strip()
    logger.info(f"Dev {message.from_user.id} entered server max clients: {server_max_clients}")

    if is_valid_client_count(server_max_clients):
        await state.set_state(AddServerStates.confirmation)
        await state.update_data(server_max_clients=server_max_clients)
        await show_add_server(state)
    else:
        await NotificationService.notify_by_message(
            message=message,
            text=_("❌ Enter a valid number."),
            duration=5,
        )


@router.callback_query(AddServerStates.confirmation, IsDev())
async def callback_confirmation(
    callback: CallbackQuery,
    state: FSMContext,
    server_service: ServerService,
) -> None:
    logger.info(f"Dev {callback.from_user.id} confirmed adding server.")
    data = await state.get_data()

    server = await server_service.add_server(
        name=data.get("server_name"),
        host=data.get("server_host"),
        subscription=data.get("server_subscription"),
        max_clients=data.get("server_max_clients"),
    )

    if server:
        await state.set_state(None)
        await callback_server_management(callback, state, server_service)
        await NotificationService.notify_by_message(
            message=callback.message,
            text=_("✅ _Server added successfully._"),
            duration=5,
        )

    else:
        await NotificationService.notify_by_message(
            message=callback.message,
            text=_("❌ _Failed to add the server._"),
            duration=5,
        )


# endregion


# region Server
@router.callback_query(F.data.startswith(NavAdminTools.SHOW_SERVER), IsDev())
async def callback_show_server(callback: CallbackQuery, server_service: ServerService) -> None:
    server_name = callback.data.split("_")[2]
    logger.info(f"Dev {callback.from_user.id} open server {server_name}.")
    server = await server_service.get_server(server_name)
    status = "🟢" if server.online else "🔴"
    text = _(
        "️️️️🌐 *Server {server_name}:*\n"
        "\n"
        "*Host:* {host}\n"
        "*Status:* {status}\n"
        "*Clients:* {clients}/{max_clients}\n"
    ).format(
        server_name=server.name,
        host=server.host,
        status=status,
        clients=server.current_clients,
        max_clients=server.max_clients,
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=server_keyboard(server_name),
    )


@router.callback_query(F.data.startswith(NavAdminTools.PING_SERVER), IsDev())
async def callback_ping_server(callback: CallbackQuery, server_service: ServerService) -> None:
    server_name = callback.data.split("_")[2]
    logger.info(f"Dev {callback.from_user.id} pinging server {server_name}.")
    server = await server_service.get_server(server_name)
    ping = await ping_url(server.host)
    online = True if ping else False
    if online != server.online:
        await server_service.update_server(server.name, online=online)
    if ping:
        await NotificationService.notify_by_message(
            message=callback.message,
            text=_("🟢 _Ping: {ping} ms._").format(server_name=server_name, ping=ping),
            duration=5,
        )
    else:
        await NotificationService.notify_by_message(
            message=callback.message,
            text=_("❌ _Failed to ping server {server_name}._").format(server_name=server_name),
            duration=5,
        )


@router.callback_query(F.data.startswith(NavAdminTools.DELETE_SERVER), IsDev())
async def callback_delete_server(
    callback: CallbackQuery,
    state: FSMContext,
    server_service: ServerService,
) -> None:
    server_name = callback.data.split("_")[2]
    logger.info(f"Dev {callback.from_user.id} open server {server_name}.")
    deleted = await server_service.delete_server(server_name)
    await callback_server_management(callback, state, server_service)

    if deleted:
        await NotificationService.notify_by_message(
            message=callback.message,
            text=_("✅ _Server deleted successfully._"),
            duration=5,
        )
    else:
        await NotificationService.notify_by_message(
            message=callback.message,
            text=_("❌ _Failed to delete the server._"),
            duration=5,
        )


# endregion
