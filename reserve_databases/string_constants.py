# coding=UTF-8
from telethon import TelegramClient
from classesnfunctions import *
from passwords import *


home_task_storage = 'databases/ht.bn'
solution_storage = 'databases/sol.bn'
id_to_ind_storage = 'databases/us.bn'
students_storage = 'databases/usnm.bn'
teachers_storage = 'databases/tch.bn'
something_wrong = 'Что-то пошло не так, попробуй всё снова'
user_already_signed_in = 'Ты уже зарегистрирован'
student_sign_in_guide = 'Привет, видимо, ты хочешь зарегистрироваться. Представься на первой строке в именительном, а на второй в творительном падеже, на третьей - свой класс. Вот так:\nСеня Чебыкин\nСеней Чебыкиным\n11В\n'
teacher_sign_in_guide = 'Здравствуйте, видимо, вы хотите зарегистрироваться. Представтесь на первой строке в именительном, а на второй в творительном падеже.\n'
success_sign_in = "Отлично, спасибо большое!"
which_subject = 'Для какого предмета? (аббревиатуры в /abbvhelp)'
wrong_subject = 'Нет такого предмета'
help_str = 'Ты можешь загрузить (/addtask) в меня дз и выгрузить (/gettask). А еще было бы неплохо иногда загружать решения (/addsol))'
abbvhelp = 'Информатика - inf, Геометрия - geo... (для умственно отсталых - первые 3 буквы в нглийском названии предмета) Английский у Сметаны Барбарисовны - eng1, у *коронавирусной* - eng2'
sure_to_change = 'Точно хочешь его изменить? (/replace, или /append, или /exit для выхода без изменений)'

normal = '0123456789абвгдеёжзийклмнопрстуфхцчшщъыьэюя '
boss = 242023883

# client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
client = TelegramClient('test_bot', api_id, api_hash).start(bot_token=test_bot_token)
print('ok')
home_tasks = readfile(home_task_storage, True) # Словарь: Параллель -> Словарь: предмет (str) -> задание (MsgGroup)
solutions = readfile(solution_storage, True) # Словарь: Параллель -> Словарь: предмет (str) -> решение (MsgGroup)
id_to_ind, max_ind_students, max_ind_teachers = readfile(id_to_ind_storage, False) # Словарь: tg_id -> индекс в массиве студентов; Количество пользователей
students = readfile(students_storage, True) # Массив пользователей (Students)
teachers = readfile(teachers_storage, True)
pending_review = set()
accepted = set()
pending_review_teachers = set()
accepted_teachers = set()
current_review = 1
