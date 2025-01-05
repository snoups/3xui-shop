import logging

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsDev, IsPrivate
from app.bot.keyboards.admin_tools import (
    confirm_add_server_keyboard,
    server_keyboard,
    servers_keyboard,
)
from app.bot.keyboards.back import back_keyboard
from app.bot.navigation import NavAdminTools
from app.bot.services import NotificationService, ServerService

logger = logging.getLogger(__name__)
router = Router(name=__name__)


class AddServerStates(StatesGroup):
    """
    States for adding a server.
    """

    name_input = State()
    host_input = State()
    subscription_url_input = State()
    max_clients_input = State()
    confirmation = State()


@router.callback_query(F.data == NavAdminTools.SERVER_MANAGEMENT, IsPrivate(), IsDev())
async def callback_server_management(
    callback: CallbackQuery,
    state: FSMContext,
    server_service: ServerService,
) -> None:
    """
    Handler for opening the servers menu.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
        state (FSMContext): The state context for managing conversation state.
        server_service (ServerService): Service for handling server-related operations.
    """
    logger.info(f"Dev {callback.from_user.id} opened servers.")
    await state.set_state(None)

    text = _("🌐 *Server management:*\n") + "\n"
    servers = await server_service.get_all_servers()

    if servers:
        for server in servers:
            text += _("- {name} ({status})\n").format(name=server.name, status="server.status")
    else:
        text += _("_The list of servers is empty._")
    # TODO: PING SERVERS
    await callback.message.edit_text(text=text, reply_markup=servers_keyboard(servers))


# region Add Server
@router.callback_query(
    StateFilter("*"), F.data == NavAdminTools.ADD_SERVER_BACK, IsPrivate(), IsDev()
)
async def process_back_command(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handles the 'back' command to move to the previous step.

    Arguments:
        message (Message): The message containing the 'back' command.
        state (FSMContext): The state context for managing steps.
    """
    current_state = await state.get_state()
    data = await state.get_data()
    message: Message = data.get("message")
    server_name = data.get("server_name")
    server_host = data.get("server_host")
    server_subscription = data.get("server_subscription")

    if current_state == AddServerStates.host_input:

        await state.set_state(AddServerStates.name_input)
        await message.edit_text(
            text=_("🌐 *Server management:*\n" "\n" "_Please provide the server name_"),
            reply_markup=back_keyboard(NavAdminTools.SERVER_MANAGEMENT),
        )
    elif current_state == AddServerStates.subscription_url_input:
        await state.set_state(AddServerStates.host_input)
        await message.edit_text(
            text=_("🌐 *Server management:*\n")
            + "\n"
            + _("- name: {server_name}\n".format(server_name=server_name))
            + _("_Please provide the server host_"),
            reply_markup=back_keyboard(NavAdminTools.ADD_SERVER_BACK),
        )
    elif current_state == AddServerStates.max_clients_input:
        await state.set_state(AddServerStates.subscription_url_input)
        await message.edit_text(
            text=_("🌐 *Server management:*\n")
            + "\n"
            + _("- name: {server_name}\n".format(server_name=server_name))
            + _("- host: {server_host}\n".format(server_host=server_host))
            + _("_Please provide the server subscription_"),
            reply_markup=back_keyboard(NavAdminTools.ADD_SERVER_BACK),
        )
    elif current_state == AddServerStates.confirmation:
        await state.set_state(AddServerStates.max_clients_input)
        await message.edit_text(
            text=_("🌐 *Server management:*\n")
            + "\n"
            + _("- name: {server_name}\n".format(server_name=server_name))
            + _("- host: {server_host}\n".format(server_host=server_host))
            + _(
                "- subscription: {server_subscription}\n".format(
                    server_subscription=server_subscription
                )
            )
            + _("_Please provide the maximum number of clients_"),
            reply_markup=back_keyboard(NavAdminTools.ADD_SERVER_BACK),
        )


@router.callback_query(F.data == NavAdminTools.ADD_SERVER, IsPrivate(), IsDev())
async def callback_add_server(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handler for starting the server addition process.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
        state (FSMContext): The state context for managing conversation state.
    """
    logger.info(f"Dev {callback.from_user.id} started adding server.")
    await state.set_state(AddServerStates.name_input)
    await state.update_data(message=callback.message)
    await callback.message.edit_text(
        text=_("🌐 *Server management:*\n" "\n" "_Please provide the server name_"),
        reply_markup=back_keyboard(NavAdminTools.SERVER_MANAGEMENT),
    )


@router.message(AddServerStates.name_input, IsPrivate(), IsDev())
async def handle_name_input(
    message: Message,
    state: FSMContext,
    server_service: ServerService,
) -> None:
    """
    Handler for processing the input of the server name.

    Arguments:
        message (Message): The incoming message containing the server name.
        state (FSMContext): The state context for managing conversation state.
        server_service (ServerService): Service for handling server-related operations.
    """
    server_name = message.text.strip()
    logger.info(f"Dev {message.from_user.id} entered server name: {server_name}")
    existing_server = await server_service.get_server(server_name)

    if existing_server:
        await NotificationService.notify_by_message(
            message=message,
            text=_("❌ A server with this name already exists. Please provide a different name."),
            duration=5,
        )
    else:
        await state.set_state(AddServerStates.host_input)
        await state.update_data(server_name=server_name)
        message = await state.get_value("message")
        await message.edit_text(
            text=_("🌐 *Server management:*\n")
            + "\n"
            + _("- name: {server_name}\n".format(server_name=server_name))
            + _("_Please provide the server host_"),
            reply_markup=back_keyboard(NavAdminTools.ADD_SERVER_BACK),
        )


@router.message(AddServerStates.host_input, IsPrivate(), IsDev())
async def handle_host_input(message: Message, state: FSMContext) -> None:
    """
    Handler for processing the input of the server host.

    Arguments:
        message (Message): The incoming message containing the server host.
        state (FSMContext): The state context for managing conversation state.
    """
    server_host = message.text.strip()
    logger.info(f"Dev {message.from_user.id} entered server host: {server_host}")
    await state.set_state(AddServerStates.subscription_url_input)
    await state.update_data(server_host=server_host)
    data = await state.get_data()
    server_name = data.get("server_name")
    message = data.get("message")
    await message.edit_text(
        text=_("🌐 *Server management:*\n")
        + "\n"
        + _("- name: {server_name}\n".format(server_name=server_name))
        + _("- host: {server_host}\n".format(server_host=server_host))
        + _("_Please provide the server subscription_"),
        reply_markup=back_keyboard(NavAdminTools.ADD_SERVER_BACK),
    )


@router.message(AddServerStates.subscription_url_input, IsPrivate(), IsDev())
async def handle_subscription_url_input(message: Message, state: FSMContext) -> None:
    """
    Handler for processing the input of the server subscription.

    Arguments:
        message (Message): The incoming message containing the server subscription URL.
        state (FSMContext): The state context for managing conversation state.
    """
    server_subscription = message.text.strip()
    logger.info(f"Dev {message.from_user.id} entered server subscription: {server_subscription}")
    await state.update_data(server_subscription=server_subscription)
    await state.set_state(AddServerStates.max_clients_input)
    data = await state.get_data()
    server_name = data.get("server_name")
    server_host = data.get("server_host")
    message = data.get("message")
    await message.edit_text(
        text=_("🌐 *Server management:*\n")
        + "\n"
        + _("- name: {server_name}\n".format(server_name=server_name))
        + _("- host: {server_host}\n".format(server_host=server_host))
        + _(
            "- subscription: {server_subscription}\n".format(
                server_subscription=server_subscription
            )
        )
        + _("_Please provide the maximum number of clients_"),
        reply_markup=back_keyboard(NavAdminTools.ADD_SERVER_BACK),
    )


@router.message(AddServerStates.max_clients_input, IsPrivate(), IsDev())
async def handle_max_clients_input(message: Message, state: FSMContext) -> None:
    """
    Handler for processing the input of the maximum number of clients.

    Arguments:
        message (Message): The incoming message containing the maximum number of clients.
        state (FSMContext): The state context for managing conversation state.
    """
    server_max_clients = message.text.strip()
    if server_max_clients.isdigit() and int(server_max_clients) > 0:
        server_max_clients = int(server_max_clients)
    else:
        await NotificationService.notify_by_message(
            message=message,
            text=_("❌ Please enter a valid number."),
            duration=5,
        )
        return

    logger.info(f"Dev {message.from_user.id} entered server max clients: {server_max_clients}")
    await state.update_data(server_max_clients=server_max_clients)
    data = await state.get_data()
    server_name = data.get("server_name")
    server_host = data.get("server_host")
    server_subscription = data.get("server_subscription")
    message: Message = data.get("message")
    await state.set_state(AddServerStates.confirmation)
    await message.edit_text(
        text=_("🌐 *Server management:*\n")
        + "\n"
        + _("- name: {server_name}\n".format(server_name=server_name))
        + _("- host: {server_host}\n".format(server_host=server_host))
        + _(
            "- subscription: {server_subscription}\n".format(
                server_subscription=server_subscription
            )
        )
        + _("- max clients: {server_max_clients}\n".format(server_max_clients=server_max_clients))
        + "\n"
        + _("_Press confirm to add the server._"),
        reply_markup=confirm_add_server_keyboard(),
    )


@router.callback_query(AddServerStates.confirmation, IsPrivate(), IsDev())
async def handle_max_clients_input(
    callback: CallbackQuery,
    state: FSMContext,
    server_service: ServerService,
) -> None:
    logger.info(f"Dev {callback.from_user.id} confirmed adding server.")
    data = await state.get_data()
    server_name = data.get("server_name")
    server_host = data.get("server_host")
    server_subscription = data.get("server_subscription")
    server_max_clients = data.get("server_max_clients")

    server = await server_service.add_server(
        name=server_name,
        host=server_host,
        subscription=server_subscription,
        max_clients=server_max_clients,
    )

    if server:
        await state.set_state(None)
        text = _("🌐 *Server management:*\n") + "\n"
        servers = await server_service.get_all_servers()

        if servers:
            for server in servers:
                text += _("- {name} ({status})\n").format(name=server.name, status="server.status")
        else:
            text += _("_The list of servers is empty._")

        await callback.message.edit_text(text=text, reply_markup=servers_keyboard())
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
@router.callback_query(F.data.startswith(NavAdminTools.SHOW_SERVER), IsPrivate(), IsDev())
def callback_server(
    callback: CallbackQuery,
    state: FSMContext,
    server_service: ServerService,
) -> None:
    """
    Handler for starting the server deletion process.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
        state (FSMContext): The state context for managing conversation state.
    """
    server_name = callback.data.split("_")[2]
    logger.info(f"Dev {callback.from_user.id} open server {server_name}.")
    server_service.get_server(server_name)
    callback.message.answer(text="Server", reply_markup=server_keyboard(server_name))
