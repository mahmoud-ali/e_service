import asyncio
import re
import logging
import traceback
import html
import json

import hashlib

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown
from asgiref.sync import sync_to_async

from django.conf import settings
# from django.utils.html import format_html

from openai import OpenAI
import markdown2
import telegramify_markdown
from telegramify_markdown import customize

from hr_bot.models import EmployeeTelegram
from it.models import AccessPoint, Conversation, EmployeeComputer, Peripheral
from it.utils import AI, queryset_to_markdown

# customize.strict_markdown = True

# Set your API keys
DEVELOPER_CHAT_ID = settings.TELEGRAM_DEVELOPER_CHAT_ID

TOKEN_ID = settings.TELEGRAM_IT_TOKEN_ID

CHECK_COMPUTER, GET_COMPUTER, CHAT, COMPUTER_NOT_EXISTS = 1, 2, 3, 4

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
def getEmployeeComputerList(user_id):
    employeeTelegram = EmployeeTelegram.objects.filter(user_id=user_id).first()
    computers = list(EmployeeComputer.objects.filter(employee=employeeTelegram.employee).values_list("id","computer__code"))
    return computers

@sync_to_async
def getEmployeeComputer(user_id,index):
    # employeeTelegram = EmployeeTelegram.objects.filter(user_id=user_id).first()
    obj = EmployeeComputer.objects.get(id=index) #,employee=employeeTelegram.employee

    return obj

@sync_to_async
def getUserPrompt(employee_computer):
    apps = list(employee_computer.computer.applications.all().values_list('name',flat=True)) + list(employee_computer.computer.template.applications.all().values_list('name',flat=True))
    user_setup = f"""
        Computer name: {employee_computer.computer.code}
        OS type: {employee_computer.computer.template.os_type} {employee_computer.computer.template.os_version}
        Installed applications: {", ".join(apps)}

        """
    for model in [Peripheral, AccessPoint]:
        qs = model.objects.filter(computer=employee_computer.computer)
        if qs.count() > 0:
            user_setup += f"""## {qs[0]._meta.verbose_name}
                {queryset_to_markdown(qs,["id","computer"])}
            """

    prompt= f"""
            <PROMPT>
            {AI.get("prompt")}
            </PROMPT>
            <CONTEXT>
                <NETWORK_SETUP>
                {AI.get("network_setup")}
                </NETWORK_SETUP>
                <USER_SETUP> 
                {user_setup}
                </USER_SETUP>
            </CONTEXT>
        """            
    prompt = re.sub('__USER_ID__', str(employee_computer.uuid), prompt) 
    # print(prompt)
    return prompt

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer  = "السلام عليكم، انا مساعدك التقني."

    await update.message.reply_text(answer)

    return await check_computer(update,context)

async def check_computer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    code = update.message.text

    computers = await getEmployeeComputerList(user_id)
    computers_count = len(computers)


    if computers_count > 1:
        i=1
        choices = {}
        await update.message.reply_text("ادخل رقم الجهاز: \n")
        for (id,computer_code) in computers:
            await update.message.reply_text(f"{i}- {computer_code}\n")
            choices[i] = id
            i = i+1

        context.user_data.update({'user_computer_list': choices})

        return GET_COMPUTER
    elif computers_count == 1:
        context.user_data.update({'user_computer_list': {1:computers[0][0]}})
        return await get_computer(update,context)
    else:
        return await computer_not_exists(update,context)

async def get_computer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    computer_index = update.message.text
    
    try:
        computer_index = int(computer_index)
    except:
        computer_index = 1

    computers = context.user_data.get('user_computer_list',{})

    employeeComputerObj = await getEmployeeComputer(update.effective_user.id,computers.get(computer_index))

    if not employeeComputerObj:
        await update.message.reply_text("الرقم غير صحيح.")
        return await check_computer(update,context)
    
    context.user_data.update({'employeeComputerId': employeeComputerObj.id,'employeeComputerUUID': employeeComputerObj.uuid})

    system_prompt = await getUserPrompt(employeeComputerObj)

    context.user_data.update({'user_history': [{"role": "system", "content": system_prompt}]})

    await update.message.reply_text("كيف يمكنني المساعدة؟")

    return CHAT
async def computer_not_exists(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f'لم يتم ادخال بيانات اجهزة الكمبيوتر الخاصة بك. الرجاء مراجعة ادارة تقنية المعلومات')
        return ConversationHandler.END

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    def generate(user_id,msgs):
        def x():
            return client.chat.completions.create(
                model="deepseek/deepseek-chat-v3.1", #"openai/gpt-5-mini",  #"anthropic/claude-3.5-haiku-20241022",#"deepseek/deepseek-chat", #"openai/gpt-oss-120b", #"openai/gpt-5-mini", #"openai/o1-mini", #"openai/gpt-4.1", #"openai/gpt-5-chat",
                messages=msgs,
                stream=True,
                timeout=120,
                prompt_cache_key=hashlib.md5(str(user_id).encode()).hexdigest(),
            )
        return x

    user_message = update.message.text
    previous_messages = context.user_data.get("user_history",[])

    if not previous_messages:
        return await start(update,context)
    
    previous_messages = [previous_messages[0]] + previous_messages[-4:] if previous_messages[0] != previous_messages[-4:][0] else previous_messages[-4:]
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

        sent_message = await update.message.reply_text("🤖 ...")  # placeholder message

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        stream = await asyncio.to_thread(
            generate(
                update.effective_chat.id,
                context.user_data.get("user_history",[])
            )
        )

        final_answer = ""
        
        # Process streamed chunks
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                delta = re.sub('__USER_ID__', str(context.user_data.get("employeeComputerUUID")), delta) 
                final_answer += delta

                # Edit progressively (limit update frequency)
                if len(final_answer) % 50 == 0:  # update every ~50 chars
                    try:
                        await sent_message.edit_text(final_answer,parse_mode=None)
                        await asyncio.sleep(0.2)  # avoid hitting Telegram API too fast
                    except Exception:
                        pass  # ignore rate limit errors


        # Final update
        context.user_data.update({'user_history': context.user_data.get('user_history',[])+[{"role":"assistant","content":final_answer}]})

        final_answer = telegramify_markdown.markdownify(
            final_answer,
            max_line_length=None,  # If you want to change the max line length for links, images, set it to the desired value.
            normalize_whitespace=False
        )
        await sent_message.edit_text(final_answer,parse_mode=ParseMode.MARKDOWN_V2)

        await addConversation(context.user_data.get('employeeComputerId'),user_message,final_answer)
    except Exception as e:
        final_answer = f"لايمكنني الرد عليك، الرجاء الاتصال بإدارة تقنية المعلومات {e}"
        await update.message.reply_markdown(final_answer)

    return CHAT
  
    
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

    # app.add_handler(CommandHandler("start", start))
    # app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            # CHECK_COMPUTER:[MessageHandler(filters.TEXT, check_computer)],
            GET_COMPUTER:[MessageHandler(filters.Regex(r'\d+'), get_computer)],
            CHAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, chat)],
            # COMPUTER_NOT_EXISTS: [MessageHandler(filters.TEXT, computer_not_exists)],
        },
        fallbacks=[CommandHandler("start", start),],
    )

    app.add_handler(conv_handler)
    app.add_error_handler(error_handler) #for exceptions

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
