import re
import logging
import traceback
import html
import json

import hashlib

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown
from asgiref.sync import sync_to_async

from django.conf import settings
# from django.utils.html import format_html

from openai import OpenAI
import markdown2

from hr_bot.models import EmployeeTelegram
from it.models import AccessPoint, Conversation, EmployeeComputer, Peripheral
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

def markdown_to_telegram_html(md_text: str) -> str:
    """
    Convert Markdown into Telegram-safe HTML.
    Keeps only tags that Telegram supports.
    """

    # Convert Markdown to HTML first
    html = markdown2.markdown(md_text)

    # Remove unsupported tags (like <p>, <h1>, etc.)
    html = re.sub(r'</?p>', '', html)
    html = re.sub(r'<h[1-6]>', '<b>', html)
    html = re.sub(r'</h[1-6]>', '</b>', html)
    html = re.sub(r'</?ul>', '', html)
    html = re.sub(r'<ol>', '- ', html)
    html = re.sub(r'</ol>', '', html)
    html = re.sub(r'<li>', '* ', html)
    html = re.sub(r'</li>', '', html)
    html = re.sub(r'<br\s*/?>', '\n', html)

    # Optional: collapse multiple newlines
    html = re.sub(r'\n{3,}', '\n\n', html)

    return html.strip()

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
def getUserPrompt(employee_computer):
    user_setup = f"""
        OS type: {employee_computer.computer.template.os_type} {employee_computer.computer.template.os_version}
        Installed applications: {", ".join(employee_computer.computer.template.applications.all().values_list('name',flat=True))}

        """
    for model in [Peripheral, AccessPoint]:
        qs = model.objects.filter(computer=employee_computer.computer)
        if qs.count() > 0:
            user_setup += f"""## {qs[0]._meta.verbose_name}
                {queryset_to_markdown(qs,["id","computer"])}
            """

    return f"""
            # PROMPT:
            {AI.get("prompt")}
            # CONTEXT:
            ** Network Setup: **
            {AI.get("network_setup")}
            ** User setup: **
            {user_setup}
            ** FAQ (Samples): **
            {AI.get("faq")}
        """            
            
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        employeeComputerObj = await getEmployeeComputer(update.effective_user.id)
        context.user_data.update({'employeeComputerId': employeeComputerObj.id})

        system_prompt = await getUserPrompt(employeeComputerObj)

        context.user_data.update({'user_history': [{"role": "system", "content": system_prompt}]})
        answer  = "السلام عليكم، انا مساعدك التقني. كيف يمكنني مساعدتك؟"
    except Exception as e:
        answer = f"لايمكنني الرد عليك، الرجاء الاتصال بإدارة تقنية المعلومات"

    await update.message.reply_text(answer)

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    previous_messages = context.user_data.get("user_history",[])

    if not previous_messages:
        return await start(update,context)
    
    previous_messages = [previous_messages[0] + previous_messages[-8:]] if previous_messages[0] != previous_messages[-8:][0] else previous_messages[-8:]
    for msg in previous_messages[1:]:
        msg["role"] = "assistant"   # update attribute

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
            timeout=60,
            prompt_cache_key=hashlib.md5(str(update.effective_chat.id).encode()).hexdigest(),
        )
        final_answer = markdown_to_telegram_html(response.choices[0].message.content)
        
        context.user_data.update({'user_history': previous_messages+[{"role":"assistant","content":final_answer}]})

        await update.message.reply_text(final_answer,parse_mode=ParseMode.HTML)

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
