# coding=UTF-8
from classesnfunctions import *

home_task_storage = 'databases/ht.bn'
solution_storage = 'databases/sol.bn'
id_to_ind_storage = 'databases/us.bn'
users_storage = 'databases/users.bn'
notes_storage = 'databases/notes.bn'
rasp_storage = 'databases/rasp.bn'
something_wrong = 'Что-то пошло не так, попробуй всё снова'
user_already_signed_in = 'Ты уже зарегистрирован'
student_sign_in_guide = 'Привет, видимо, ты хочешь зарегистрироваться. Представься на первой строке в именительном, а на второй в творительном падеже, на третьей - свой класс, на четвертой - город и школу (Если ты не из ФМЛ №31). Вот так:\nСеня Чебыкин\nСеней Чебыкиным\n11В\nЧелябинск, ФМЛ №31'
teacher_sign_in_guide = 'Здравствуйте, видимо, вы хотите зарегистрироваться. Представтесь на первой строке в именительном, а на второй в творительном падеже.\n'
success_sign_in = "Отлично, спасибо большое!"
which_subject = 'Для какого предмета? (аббревиатуры в /abbvhelp)'
wrong_subject = 'Нет такого предмета'
help_str = 'Ты можешь загрузить (/addtask) в меня дз и выгрузить (/gettask). А еще было бы неплохо иногда загружать решения (/addsol))'
help_str_teacher = 'Вы можете загрузить домашнее задание (/addtask), или добавить заметку (/addnote).'
abbvhelp = 'Информатика - inf, Геометрия - geo... (для умственно отсталых - первые 3 буквы в нглийском названии предмета) Английский у Сметаны Барбарисовны - eng1, у *коронавирусной* - eng2'
sure_to_change = 'Точно хочешь его изменить?'
normal = '0123456789абвгдеёжзийклмнопрстуфхцчшщъыьэюя '


home_tasks: Dict[str, Dict[str, HomeTask]] = readfile(home_task_storage,
                                                      True)  # Словарь: Параллель -> Словарь: предмет -> задание
solutions: Dict[str, Dict[str, MsgGroup]] = readfile(solution_storage,
                                                     True)  # Словарь: Параллель -> Словарь: предмет -> решение
notes: Dict[str, Note] = readfile(notes_storage, True)
rasp: Dict[str, Rasp] = readfile(rasp_storage, True)  # Словарь: Параллель -> расписание
id_to_ind: Dict[int, int]
max_ind: int
id_to_ind, max_ind = readfile(id_to_ind_storage,
                              False)  # Словарь: tg_id -> индекс в массиве студентов; Количество пользователей
users: List[Union[Student, Teacher]] = readfile(users_storage, True)  # Массив пользователей
pending_review = set()
accepted = set()
current_review = 1