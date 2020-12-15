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
to_pi = ['pscp.exe -P 22 -r -pw secretpw1 C:\\Users\\Simon\\python\\tg\\HTbot\\* root@192.168.1.107:/home/pi/telegram/HTbot']
to_us_tasks = ['pscp.exe -P 22 -pw secretpw1 root@192.168.1.107:/home/pi/telegram/HTbot/bot.session C:\\Users\\Simon\\python\\tg\\HTbot',
               'pscp.exe -P 22 -pw secretpw1 root@192.168.1.107:/home/pi/telegram/HTbot/databases/* C:\\Users\\Simon\\python\\tg\\HTbot\\databases']

hotfix = to_us_tasks + to_pi
for el in hotfix:
    subprocess.call(el)
