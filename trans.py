# coding=UTF-8
import subprocess
def form(from_us):
    if from_us:
        ans = 'pscp.exe -P 22 -r -pw 123456 C:\\Users\\Simon\\python\\tg\\HTbot\\ semen@192.168.1.110:/home/semen/Desktop/tg/HTbot/'
    else:
        ans = 'pscp.exe -P 22 -pw 123456 semen@192.168.1.110:/home/semen/Desktop/tg/HTbot/ C:\\Users\\Simon\\python\\tg\\HTbot'
to_us = ['pscp.exe -pw 123456 semen@192.168.1.110:/home/semen/Desktop/tg/HTbot/databases/* C:\\Users\\Сеня\\Desktop\\python\\tg\\HT =bot\\databases',
                        \
               'pscp.exe -pw 123456 semen@192.168.1.110:/home/semen/Desktop/tg/HTbot/*.py C:\\Users\\Сеня\\Desktop\\python\\tg\\HTbot',
            \
               'pscp.exe -pw 123456 semen@192.168.1.110:/home/semen/Desktop/tg/HTbot/bot.session C:\\Users\\Сеня\\Desktop\\python\\tg\\HTbot']
to_averatec = ['pscp.exe -P 22 -r -pw 123456 C:\\Users\\Simon\\python\\tg\\HTbot\\* semen@192.168.1.110:/home/semen/Desktop/tg/HTbot']
to_us_tasks = ['pscp.exe -P 22 -pw 123456 semen@192.168.1.110:/home/semen/Desktop/tg/HTbot/bot.session C:\\Users\\Simon\\python\\tg\\HTbot',
               'pscp.exe -P 22 -pw 123456 semen@192.168.1.110:/home/semen/Desktop/tg/HTbot/databases/* C:\\Users\\Simon\\python\\tg\\HTbot\\databases']
ans = ['pscp.exe -P 22 -pw 123456 semen@192.168.1.110:/home/semen/Desktop/tg/bot/bot_.py C:\\Users\\Simon\\python\\tg\\']

hotfix = to_us_tasks + to_averatec
for el in hotfix:
    subprocess.call(el)
