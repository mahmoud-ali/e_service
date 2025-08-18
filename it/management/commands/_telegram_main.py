import logging
import traceback
import html
import json

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown
from asgiref.sync import sync_to_async

from django.conf import settings
# from django.utils.html import format_html

from openai import OpenAI

from hr_bot.models import EmployeeTelegram
from it.models import AccessPoint, Conversation, EmployeeComputer, NetworkAdapter, Peripheral
from it.utils import AI, queryset_to_markdown
# Set your API keys
DEVELOPER_CHAT_ID = settings.TELEGRAM_DEVELOPER_CHAT_ID

TOKEN_ID = settings.TELEGRAM_IT_TOKEN_ID

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

@sync_to_async
def addConversation(employee_computer_id,question,answer):
    Conversation.objects.create(
        master=EmployeeComputer.objects.get(id=employee_computer_id),
        question=question,
        answer=answer,
    )

@sync_to_async
def getEmployeeComputer(user_id):
    employeeTelegram = EmployeeTelegram.objects.filter(user_id=user_id).first()
    return EmployeeComputer.objects.filter(employee=employeeTelegram.employee).first()

@sync_to_async
def getUserSetup(employee_computer):
    user_setup = f"""
        OS type: {employee_computer.computer.template.os_type} {employee_computer.computer.template.os_version}
        Installed applications: {", ".join(employee_computer.computer.template.applications.all().values_list('name',flat=True))}

        """
    for model in [NetworkAdapter, Peripheral, AccessPoint]:
        qs = model.objects.filter(computer=employee_computer.computer)
        if qs.count() > 0:
            user_setup += f"""## {qs[0]._meta.verbose_name}
                {queryset_to_markdown(qs,["id","computer"])}
            """
    return user_setup
            
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    employeeComputerObj = await getEmployeeComputer(update.effective_user.id)
    context.user_data.update({'employeeComputerId': employeeComputerObj.id})
    try:
        system_prompt = f"""
            # PROMPT:
            {AI.get("prompt")}
            # CONTEXT:
            ** Network Setup: **
            {AI.get("network_setup")}
            ** User setup: **
            {await getUserSetup(employeeComputerObj)}
            ** FAQ (Samples): **
            {AI.get("faq")}
        """

        context.user_data.update({'user_history': [{"role": "system", "content": system_prompt}]})
        answer  = "السلام عليكم، انا مساعدك التقني. كيف يمكنني مساعدتك؟"
    except Exception as e:
        answer = f"لايمكنني الرد عليك، الرجاء الاتصال بإدارة تقنية المعلومات"

    await update.message.reply_text(answer)

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    previous_messages = context.user_data.get("user_history",[])
    context.user_data.update({'user_history': previous_messages+[{"role":"user","content":user_message}]})
    
    try:
        client = OpenAI(
            base_url=settings.OPENAI_BASE_URL,
            api_key=settings.OPENAI_API_KEY,
        )

        # print("request---------------------------------------------------------------------------------------",context.user_data.get("user_history"))
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        response = client.chat.completions.create(
            model="openai/gpt-5-mini", #"openai/o1-mini", #"openai/gpt-4.1", #"openai/gpt-5-chat",
            messages=context.user_data.get("user_history"),
        )
        final_answer = response.choices[0].message.content

        await update.message.reply_text(escape_markdown(final_answer, version=2),parse_mode=ParseMode.MARKDOWN_V2)

        await addConversation(context.user_data.get('employeeComputerId'),user_message,final_answer)
    except Exception as e:
        final_answer = f"لايمكنني الرد عليك، الرجاء الاتصال بإدارة تقنية المعلومات {e}"
        await update.message.reply_markdown(final_answer)
  
    
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
    app = Application.builder().token(TOKEN_ID).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.add_error_handler(error_handler) #for exceptions

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
