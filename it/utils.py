AI = {
    "prompt": f"""
            You are an IT support assistant helping users in a controlled business environment. Always use simple, clear, and friendly language. Avoid technical jargon unless absolutely necessary, and if you must use it, explain it in plain terms. Focus on solving the user’s problem step by step, giving instructions that are easy to follow. Assume the user has little to no technical knowledge. Keep responses concise, professional, and reassuring, while ensuring accuracy and security.
            Never suggest actions that require administrator or elevated permissions. Instead, offer solutions that can be performed by the user within their normal access level. If an issue truly requires administrator action, politely explain that the request needs to be handled by their IT administrator.
            Your role is to solve user problem in a clear language using CONTEXT and ANSWERING RULES.
            ANSWERING RULES:
            - Don’t share “Network Setup” with user.
            - Always reply with the most likely fix first.  
            - Show steps in order of priority.  
            - Only if required and problem not unresolved, advise escalation to IT department and ask him to fill help form using the following link: 'https://hr1.mineralsgate.com/app/it/help_desk_form/__USER_ID__/'. ai may append the following querystring to URL if relevent: category(hardware,software,network,other), subject, description. for example: https://hr1.mineralsgate.com/app/it/help_desk_form/__USER_ID__/?category=hardware&subject=%20الطابعة%20HP%20Laser%20MFP%20135w%20لا%20تستجيب%20للطباعة%20من%20جهاز&description=ا%20أستطيع%20طباعة%20مستندات%20عاجلة%20للعمل%20اليوم 
            - Answer in user language and use classical language.
            - Answer only questions relevent to IT and technical support.
            - Answer in markdown format appropriate for Telegram bot.
            - All prompts will be in text only and all answers should be in text only. You are a text only bot.
            - Refer to USER_SETUP as can as possible. This is the most important data relate to user.
            """,
    "network_setup": f"""
            - Firewall (fg-smrc1) manages DHCP for 192.168.12.0/24 (1-week leases).
            - All traffic is allowed except YouTube, TikTok, and Facebook.
            - Antivirus: Kaspersky Endpoint Security (KSC).
            """,
    "faq": f"""
        1. **Wi-Fi/Internet Issues** – Reconnect Wi-Fi, restart adapter/router, renew IP, or flush DNS.
        2. **Slow/Unstable Network** – Move closer to access point, disconnect idle devices, disable bandwidth-heavy apps.
        3. **VPN/Firewall Problems** – Restart VPN client, check firewall rules, request site whitelist.
        4. **Printer Errors** – Restart printer/spooler, clear queue, reinstall drivers, fix paper jams/toner.
        5. **Microsoft Office Issues** – Repair Office, check file permissions, enable macros, rebuild Outlook index.
        6. **Antivirus/Security Alerts** – Run scans, update definitions, add exclusions, resolve license/compliance errors.
        7. **Windows System Errors** – Run Troubleshooter, update drivers, disable startup apps, restart Explorer.
        8. **Hardware/Peripheral Failures** – Reconnect or reinstall drivers for USB, audio, webcam, keyboard, or monitor.
        9. **Application/Browser Issues** – Clear cache, disable extensions, reset settings, relogin to sync services.
        10. **Performance & Boot Problems** – Free disk space, clean vents, update BIOS, disable Fast Startup, reseat RAM.        
""",
}
def field_has_choices(field):
    # Check if the field has a 'choices' attribute
    if not hasattr(field, 'choices'):
        return False
    
    # Get the value of `choices`
    choices = field.choices
    
    # Handle callable choices (dynamic)
    if callable(choices):
        try:
            choices = choices()  # Execute the callable
        except:
            return False

   # Check if choices is None or not iterable
    if choices is None:
        return False

    # Ensure choices is iterable (e.g., list, tuple)
    try:
        iter(choices)  # Check if iterable
    except TypeError:
        return False

    # Check if choices are non-empty
    return bool(list(choices))  # Convert to list to handle generators

def display_field(instance, field):
    if field_has_choices(field):
        return str(getattr(instance, "get_"+field.name+"_display")())
    else:
        return str(getattr(instance, field.name))

def queryset_to_markdown(qs,exclude=[],newline="<br/>"):
    if qs.count() > 0:
        instance = qs.first()
        headers = "| " + " | ".join([str(field.verbose_name) for field in instance._meta.fields if field.name not in exclude]) + " |"
        separator = "| " + " | ".join(["-" * len(str(field.verbose_name)) for field in instance._meta.fields if field.name not in exclude]) + " |"

        values = ""
        for instance in qs:
            values += "| " + " | ".join([display_field(instance, field) for field in instance._meta.fields if field.name not in exclude]) + " |" + newline
        
        markdown = f"{headers}{newline}{separator}{newline}{values}"
        return markdown

