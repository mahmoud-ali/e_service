AI = {
    "prompt": f"""
            You are an IT support assistant helping users in a controlled business environment. Always use simple, clear, and friendly language. Avoid technical jargon unless absolutely necessary, and if you must use it, explain it in plain terms. Focus on solving the user’s problem step by step, giving instructions that are easy to follow. Assume the user has little to no technical knowledge. Keep responses concise, professional, and reassuring, while ensuring accuracy and security.
            Never suggest actions that require administrator or elevated permissions. Instead, offer solutions that can be performed by the user within their normal access level. If an issue truly requires administrator action, politely explain that the request needs to be handled by their IT administrator.
            Your role is to solve user problem in a clear language using CONTEXT and ANSWERING RULES.
            ANSWERING RULES:
            - Don’t share “Network Setup” with user.
            - Always reply with the most likely fix first.  
            - Show steps in order of priority.  
            - If unresolved, advise escalation to IT department.
            - Answer in user language.
            - Answer only questions relevent to IT and technical support.
            - Answer in markdown format appropriate for Telegram bot.
            """,
    "network_setup": f"""
            - Firewall (fg-smrc1) manages DHCP for 192.168.12.0/24 (1-week leases).
            - All traffic is allowed except YouTube, TikTok, and Facebook.
            - Antivirus: Kaspersky Endpoint Security (KSC).
            """,
    "faq": f"""
            ## 🔹 Network & Connectivity (1–20)
            1. **Problem:** Can’t connect to Wi-Fi  
            **Solution:** Enable Wi-Fi adapter → Reconnect to access points → Restart router  
            2. **Problem:** Internet disconnects frequently  
            **Solution:** Move closer to AP → Update adapter driver → Reboot PC  
            3. **Problem:** Slow internet speed  
            **Solution:** Disconnect idle devices → Pause background updates → Restart firewall  
            4. **Problem:** No IP assigned  
            **Solution:** Run `ipconfig /renew` → Restart adapter → Check firewall DHCP  
            5. **Problem:** Can’t access YouTube/TikTok/Facebook  
            **Solution:** Blocked by firewall policy, access restricted  
            6. **Problem:** “Limited Connectivity”  
            **Solution:** Forget/reconnect Wi-Fi → Restart DHCP Client service  
            7. **Problem:** Connected to wrong Wi-Fi  
            **Solution:** Forget wrong SSID → Connect only to access points  
            8. **Problem:** VPN won’t connect  
            **Solution:** Ensure internet → Disable antivirus conflicts → Restart VPN client  
            9. **Problem:** DNS issues  
            **Solution:** Flush DNS (`ipconfig /flushdns`) → Change DNS to 8.8.8.8  
            10. **Problem:** Can’t access intranet resources  
                **Solution:** Ensure connected to corporate Wi-Fi → Check firewall routing  
            11. **Problem:** Wi-Fi password forgotten  
                **Solution:** Request IT for credentials  
            12. **Problem:** Dropping from Wi-Fi after sleep  
                **Solution:** Disable power saving on Wi-Fi adapter  
            13. **Problem:** Duplicate IP conflict  
                **Solution:** Renew DHCP lease → Restart system  
            14. **Problem:** Wi-Fi keeps asking for password  
                **Solution:** Forget and reconnect network  
            15. **Problem:** Can’t access file share  
                **Solution:** Verify network discovery enabled  
            16. **Problem:** High ping/latency  
                **Solution:** Disconnect bandwidth-heavy apps  
            17. **Problem:** Network adapter missing  
                **Solution:** Reinstall TP-Link T3U driver  
            18. **Problem:** Firewall blocks safe site  
                **Solution:** Request whitelist from IT  
            19. **Problem:** Wi-Fi authentication error  
                **Solution:** Re-enter password correctly  
            20. **Problem:** Public hotspot auto-connects  
                **Solution:** Disable auto-connect to unsafe networks  
            ---
            ## 🔹 Printing Issues (21–35)
            21. Printer not detected → Connect to printer Wi-Fi → Reinstall driver  
            22. Print job stuck → Restart Print Spooler → Clear queue  
            23. Prints blank pages → Check toner → Clean printer  
            24. Can’t print color → Change settings → Replace cartridge  
            25. Wrong printer selected → Set HP 4103 as default  
            26. Printer Wi-Fi not showing → Restart printer Wi-Fi  
            27. Paper jam → Remove paper manually → Restart printer  
            28. Printer offline → Reconnect to Wi-Fi → Restart  
            29. Slow printing → Reduce quality → Update driver  
            30. Can’t print PDF → Update Acrobat → Reinstall driver  
            31. Faded prints → Replace toner  
            32. Double-sided not working → Enable duplex in settings  
            33. Printer shows “Low Memory” → Cancel large jobs → Print smaller batches  
            34. Printer won’t power on → Check power cable  
            35. Printer error codes → Refer to printer manual  
            ---
            ## 🔹 Microsoft Office (36–50)
            36. Word crashes → Repair Office → Update  
            37. Excel formulas broken → Check format → Retype formula  
            38. Outlook won’t send → Verify SMTP settings  
            39. Chrome won’t open → Clear cache → Reinstall  
            40. WinRAR extraction fails → Update WinRAR → Check archive  
            41. Excel file locked → Close elsewhere → Save copy  
            42. Office activation failed → Verify license  
            43. Excel macros disabled → Enable in Trust Center  
            44. Word won’t save → Save with new name/location  
            45. PowerPoint crashes → Disable add-ins → Repair Office  
            46. Outlook slow search → Rebuild index  
            47. Access file corrupted → Use Compact & Repair tool  
            48. Excel printing misaligned → Adjust print area  
            49. Word document not opening → Open in safe mode  
            50. Office updates failing → Run Update Troubleshooter  
            ---
            ## 🔹 Antivirus & Security (51–65)
            51. Kaspersky won’t update → Check internet → Restart service  
            52. Virus detected → Quarantine/delete → Full scan  
            53. Safe app blocked → Add to exclusions → Report IT  
            54. Kaspersky missing from tray → Restart service  
            55. Certificate error → Update system time  
            56. Compliance error in KSC → Ensure agent installed  
            57. Antivirus slows PC → Schedule scans off-hours  
            58. USB blocked → Enable in Kaspersky policy (admin)  
            59. Can’t uninstall → Requires admin rights  
            60. Antivirus blocks downloads → Adjust web protection  
            61. License expired → Renew or contact IT  
            62. Scheduled scan missed → Ensure device was online  
            63. Full scan too slow → Run quick scan instead  
            64. Kaspersky conflicts with Windows Defender → Disable Defender  
            65. Can’t disable protection → Policy locked by IT  
            ---
            ## 🔹 Windows 11 System (66–85)
            66. Windows Update failing → Run Troubleshooter  
            67. Blue screen error → Note code → Update drivers  
            68. Slow startup → Disable startup apps  
            69. Taskbar unresponsive → Restart Explorer  
            70. Bluetooth not working → Reinstall driver  
            71. Wrong system clock → Sync with NTP  
            72. No audio → Select correct playback device  
            73. External monitor not detected → Win+P → Update drivers  
            74. USB not recognized → Update USB controller  
            75. Windows Defender alert → Ignore (Kaspersky active)  
            76. App won’t install → Run as admin  
            77. File Explorer freezing → Clear Quick Access cache  
            78. Keyboard not working → Reconnect → Reinstall driver  
            79. Mouse lagging → Change USB port  
            80. Laptop overheating → Clean vents → Update BIOS  
            81. Low disk space → Run Disk Cleanup  
            82. Cortana won’t launch → Enable in Settings  
            83. Wi-Fi toggle missing → Reinstall adapter driver  
            84. PC won’t shut down → Disable Fast Startup  
            85. Windows activation error → Connect to internet → Retry  
            ---
            ## 🔹 User Applications & Browsing (86–95)
            86. Chrome sync not working → Sign in again  
            87. Downloads blocked in Chrome → Check browser settings  
            88. Chrome extensions crashing → Disable conflicting add-ons  
            89. Google Docs offline → Enable offline mode in Drive  
            90. Chrome homepage changed → Reset browser  
            91. MS Teams won’t start → Clear Teams cache  
            92. OneDrive not syncing → Restart OneDrive client  
            93. Edge opens automatically → Disable from startup apps  
            94. Default apps reset → Set defaults manually  
            95. Browser history missing → Check sync settings  
            ---
            ## 🔹 Hardware & Peripherals (96–100)
            96. External HDD not detected → Change USB port → Update drivers  
            97. Webcam not working → Enable in Privacy settings  
            98. Headphones not detected → Set as default playback device  
            99. Keyboard shortcuts not working → Disable Sticky Keys  
            100. PC won’t boot → Check power → Reseat RAM → Contact IT  
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

