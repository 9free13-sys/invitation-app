@echo off
cd /d C:\Users\Admin\Desktop\convite_app

echo ============================== > reminder_log.txt
echo INICIO: %date% %time% >> reminder_log.txt
echo PASTA ATUAL: %cd% >> reminder_log.txt

C:\Users\Admin\AppData\Local\Programs\Python\Python313\python.exe manage.py send_event_reminders >> reminder_log.txt 2>&1

echo FIM: %date% %time% >> reminder_log.txt
echo ============================== >> reminder_log.txt