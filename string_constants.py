# coding=UTF-8
from telethon import TelegramClient
from classesnfunctions import *
from passwords import *


home_task_storage = 'databases/ht.bn'
solution_storage = 'databases/sol.bn'
id_to_ind_storage = 'databases/us.bn'
students_storage = 'databases/usnm.bn'
something_wrong = 'Что-то пошло не так, попробуй всё снова'
user_already_signed_in = 'Ты уже зарегистрирован'
user_sign_in_guide = 'Привет, видимо, ты хочешь зарегистрироваться. Представься на первой строке в именительном, а на второй в творительном падеже, на третьей - свой класс. Вот так:\nСеня Чебыкин\nСеней Чебыкиным\n11В\n'
success_sign_in = "Отлично, спасибо большое!"
which_subject = 'Для какого предмета? (аббревиатуры в /abbvhelp)'
wrong_subject = 'Нет такого предмета'
help_str = 'Ты можешь загрузить (/addtask) в меня дз и выгрузить (/gettask). А еще было бы неплохо иногда загружать решения (/addsol))'
abbvhelp = 'Информатика - inf, Геометрия - geo... (для умственно отсталых - первые 3 буквы в нглийском названии предмета) Английский у Сметаны Барбарисовны - eng1, у *коронавирусной* - eng2'
sure_to_change = 'Точно хочешь его изменить? (/replace, или /append, или /exit для выхода без изменений)'

normal = '0123456789абвгдеёжзийклмнопрстуфхцчшщъыьэюя '
download_types = ['Аудио', 'Видео']
want_download = ["Скачать!", "Забей"]
boss = 242023883

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
home_tasks = readfile(home_task_storage, True) # Словарь: Параллель -> Словарь: предмет (str) -> задание (MsgGroup)
solutions = readfile(solution_storage, True) # Словарь: Параллель -> Словарь: предмет (str) -> решение (MsgGroup)
id_to_ind, max_ind = readfile(id_to_ind_storage, False) # Словарь: tg_id -> индекс в массиве студентов; Количество пользователей
students = readfile(students_storage, True) # Массив пользователей (Students)
pending_review = set()
accepted = set()
current_review = 1
