import logging
import traceback
import html
import json

from telegram import KeyboardButton, MenuButton, MenuButtonCommands, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, filters
from telegram.constants import ParseMode

from uuid import uuid4

import re
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

from hr.models import EmployeeBasic, EmployeeFamily, EmployeeTelegram, EmployeeTelegramRegistration

GET_NAME, GET_CODE, GET_CONTACT, CHOOSING, ADD_CHILD, GET_CHILDREN = range(6)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


# This can be your own ID, or one for a developer group/channel.

# You can use the /start command of this bot to see your chat id.

DEVELOPER_CHAT_ID = 5624823325

TOKEN_ID = "7654221372:AAFpmuPgA0F9pN35QHMeedz3wPVXTVkoa7k"

def compare_phone(phone1,phone2):
    return (re.sub(r'\D', '', phone1) == re.sub(r'\D', '', phone2))

@sync_to_async
def register(code,user_id,phone,name):
    admin_user = get_user_model().objects.get(id=1)

    emp = EmployeeBasic.objects.get(code=code)
    return EmployeeTelegramRegistration.objects.create(
        employee=emp,
        user_id=user_id,
        phone=phone,
        name=name,
        created_by=admin_user,
        updated_by=admin_user,
    )

@sync_to_async
def get_employee(user_id):
    return EmployeeTelegram.objects.filter(user_id=user_id).first()

@sync_to_async
def get_employee_info(user_id):
    emp = EmployeeTelegram.objects.filter(user_id=user_id).first()
    if emp:
        return emp.employee
    
    return None

@sync_to_async
def get_employee_children(user_id):
    emp = EmployeeTelegram.objects.filter(user_id=user_id).first()
    
    if emp:
        ch =  list(emp.employee.employeefamily_set.filter(relation=EmployeeFamily.FAMILY_RELATION_CHILD).values_list('name',flat=True))
        return ch
    
    return None

@sync_to_async
def get_employee_by_code(code):
    emp = EmployeeBasic.objects.filter(code=code).first()
    if emp:
        return emp
    
    return None

@sync_to_async
def register_employee(code,user_id,phone):
    admin_user = get_user_model().objects.get(id=1)
    emp = EmployeeBasic.objects.get(code=code)
    print('Emp',emp)
    obj, _ = EmployeeTelegram.objects.get_or_create(
        employee=emp,
        user_id=user_id,
        phone=phone,
        created_by=admin_user,
        updated_by=admin_user,
    )

    return obj

#register_employee
@sync_to_async
def get_employees_count():
    return EmployeeBasic.objects.all().count()

async def check_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    is_registered = await get_employee(user_id)
    
    return True if is_registered else False

def menu():
    keyboard = [
                [
                    'Get children data',
                    'Add a child',
                ],
            ]
    return ReplyKeyboardMarkup(keyboard,one_time_keyboard=True,resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    if await check_registration(update,context):
        emp = await get_employee_info(user_id)
        
        await update.message.reply_text(f'Hello {emp.name}, You can explore your can do the following:', reply_markup=menu())
        return CHOOSING
    else:
        await update.message.reply_text(f'You are not registered, please enter your name:') #, reply_markup=reply_markup

    return GET_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    name = update.message.text

    context.user_data = {
        'name': name,
        'code': None,
        'phone': None,
    }
    await update.message.reply_text(f'ok, now enter your code:')
    return GET_CODE

async def get_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    code = update.message.text

    if await get_employee_by_code(code):
        context.user_data.update({'code': code})

        keyboard = [
            [
                KeyboardButton("Share your contact", request_contact=True)
            ]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard,one_time_keyboard=True,resize_keyboard=True)

        await update.message.reply_text(f'Now share your contact', reply_markup=reply_markup)
        return GET_CONTACT
    else:
        await update.message.reply_text(f'Invalid code!', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    contact = update.effective_message.contact
    if contact and contact.phone_number:
        context.user_data.update({'phone': contact.phone_number})

        await register(
            context.user_data['code'],
            user_id,
            context.user_data['phone'],
            context.user_data['name'],
        )

        context.user_data.clear()

        await update.message.reply_text(f'Thank you. HR staf will contact with you to confirm your data.', reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END
    else:
        keyboard = [
            [
                KeyboardButton("Share your contact", request_contact=True)
            ]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard,one_time_keyboard=True,resize_keyboard=True)

        await update.message.reply_text(f'Please share your contact', reply_markup=reply_markup)
        return GET_CONTACT

async def get_children(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    children = await get_employee_children(user_id)
    await update.message.reply_html("<b>You have: </b> \n - {0}".format('\n - '.join(children)))

    await update.message.reply_html("Do you want to make a new choise or /cancel?",reply_markup=menu())
    return CHOOSING

async def add_child(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    await update.message.reply_text(f'add a child',reply_markup=ReplyKeyboardRemove())
    return CHOOSING

async def get_choise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message.text
    if message == 'Get children data':
        return await get_children(update,context)
    elif message == 'Add a child':
        return await add_child(update,context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Ok you can try later.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

async def my_contact_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_message.from_user.id
    contact = update.effective_message.contact

    if contact:
        phone = contact.phone_number
        if(contact.user_id and user_id == contact.user_id):
            tel_obj = await get_employee(user_id)
            if tel_obj and compare_phone(tel_obj.phone, phone):
                await update.message.reply_text(f'You already registerd')
            else:
                code = 420
                tel_obj = await register_employee(code,user_id,phone)
                await update.message.reply_text(f'Registration successfull', reply_markup=ReplyKeyboardRemove())

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Log the error and send a telegram message to notify the developer."""

    # Log the error before we do anything else, so we can see it even if something breaks.

    logger.error("Exception while handling an update:", exc_info=context.error)


    # traceback.format_exception returns the usual python message about an exception, but as a

    # list of strings rather than a single string, so we have to join them together.

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)

    tb_string = "".join(tb_list)


    # Build the message with some markup and additional information about what happened.

    # You might need to add some logic to deal with messages longer than the 4096 character limit.

    update_str = update.to_dict() if isinstance(update, Update) else str(update)

    message = (

        "An exception was raised while handling an update\n"

        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"

        "</pre>\n\n"

        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"

        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"

        f"<pre>{html.escape(tb_string)}</pre>"

    )


    # Finally, send the message

    await context.bot.send_message(
        chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
    )

def main():
    app = ApplicationBuilder().token(TOKEN_ID).build()

    # app.add_handler(CommandHandler("start", start))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GET_NAME:[MessageHandler(filters.TEXT, get_name)],
            GET_CODE: [MessageHandler(filters.Regex("\d+"), get_code)],
            GET_CONTACT: [MessageHandler(filters.CONTACT, get_contact)],
            CHOOSING: [MessageHandler(filters.Regex("^(Get children data|Add a child)$"), get_choise)],
            GET_CHILDREN:[MessageHandler(filters.TEXT, get_children)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    #app.bot.set_chat_menu_button
    app.add_handler(MessageHandler(filters.COMMAND, unknown)) #for unknown commands

    app.add_error_handler(error_handler) #for exceptions

    # app.add_handler(MessageHandler(filters.CONTACT, my_contact_callback))

    app.run_polling()