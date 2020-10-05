# coding=UTF-8
import subprocess
to_us = ['pscp.exe -pw 123456 semen@192.168.1.110:/home/semen/Desktop/tg/HTbot/databases/* C:\\Users\\Сеня\\Desktop\\python\\tg\\HTbot\\databases',
                        \
               'pscp.exe -pw 123456 semen@192.168.1.110:/home/semen/Desktop/tg/HTbot/*.py C:\\Users\\Сеня\\Desktop\\python\\tg\\HTbot',
            \
               'pscp.exe -pw 123456 semen@192.168.1.110:/home/semen/Desktop/tg/HTbot/bot.session C:\\Users\\Сеня\\Desktop\\python\\tg\\HTbot']
to_averatec = ['pscp.exe -pw 123456 C:\\Users\\Сеня\\Desktop\\python\\tg\\HTbot\\databases\\* semen@192.168.1.110:/home/semen/Desktop/tg/HTbot/databases',
            \
         'pscp.exe -pw 123456 C:\\Users\\Сеня\\Desktop\\python\\tg\\HTbot\\*.py semen@192.168.1.110:/home/semen/Desktop/tg/HTbot',
            \
         'pscp.exe -pw 123456 C:\\Users\\Сеня\\Desktop\\python\\tg\\HTbot\\bot.session semen@192.168.1.110:/home/semen/Desktop/tg/HTbot']
for el in to_averatec:
    subprocess.call(el)
