import datetime
from telethon import Button
import asyncio
import datetime
from telethon import TelegramClient
from passwords import *
from telethon import TelegramClient, events, tl, Button
from telethon.tl.types import InputMediaPoll, Poll, PollAnswer
from telethon.tl.custom.conversation import Conversation
from telethon.errors.common import AlreadyInConversationError
from telethon.tl.custom.message import Message
from telethon.hints import MessageLike
from telethon.events.newmessage import NewMessage
from random import shuffle
import logging
from boot import *
from pickle import load, dump
from typing import *

def readfile(file: str, single: bool) -> Union[Any, List[Any]]:
    f = open(file, 'br')
    if single:
        t = load(f)
        f.close()
        return t
    t = []
    while True:
        try:
            t.append(load(f))
        except EOFError:
            return t


def writefile(file: str, *data: Any) -> None:
    '''Сначала файл, потом [данные]'''
    print(data)
    f = open(file, 'bw')
    for el in data:
        dump(el, f)
    f.close()


class User():
    tg_id: int
    name: str
    name_by: str

    def __init__(self, tg_id, name, name_by):
        self.tg_id = tg_id
        self.name = name
        self.name_by = name_by


class Student(User):
    parr: str
    money: int

    def __init__(self, tg_id, name, name_by, par='11В'):
        super().__init__(tg_id, name, name_by)
        self.par = par
        self.money = 30


class Teacher(User):
    classes: List[str]
    subjects: List[str]

    def __init__(self, tg_id, name, name_by, classes=(), subjects=()):
        super().__init__(tg_id, name, name_by)
        self.classes = list(classes[:])
        self.subjects = list(subjects[:])

class MsgGroup():
    messages: List[Tuple[Any, Any]]
    student: int
    timestamp: datetime.datetime

    def __init__(self, msg=(), student=0, timestamp=datetime.datetime.now()):
        self.messages = list(msg[:])
        self.student = student
        self.timestamp = timestamp


class Note(MsgGroup):
    header: str

    def __init__(self, header='', msg=(), student=0, timestamp=datetime.datetime.now()):
        super().__init__(msg, student, timestamp)
        self.header = header


class Task(MsgGroup):
    deadline: datetime.date

    async def show(self, conv: Conversation, ask_for_money: bool = True) -> Optional[Tuple[int, int]]:
        '''
        Возвращает (student_from, student_to), если кинули монетку
        '''

        if self.messages:
            await conv.send_message('Дз к {}:'.format(self.deadline))
            for el in self.messages:
                await conv.send_message(message=el[0], file=el[1])
            if ask_for_money:
                res = await send_inline_message(conv,
                                                "Последний раз оно было изменено {} {}".format(
                                                    users[self.student].name_by,
                                                    str(self.timestamp)[:-10]),
                                                ['Кинуть ему монетку!', 'Я жмот'],
                                                timeout=10,
                                                edited_message=['{} очень рад(а)'.format(
                                                    users[self.student].name),
                                                    'Чел...']
                                                )
                return (res and res[0] == 'К')
            else:
                await conv.send_message("Последний раз оно было изменено {} {}".format(
                                                    users[self.student].name_by,
                                                    str(self.timestamp)[:-10]))
        else:
            await conv.send_message('*Пусто*')

class HomeTask():
    history: List[Task]

    def __init__(self):
        self.history = []

class RaspDay():
    subjects: List[str]

    def __init__(self, data: List[str]):
        self.subjects = data

class Rasp():
    timetable: List[RaspDay] = []

    def __init__(self, rasp: List[RaspDay]):
        self.timetable = rasp[:]

    def find_next(self, subject, amount = 1, today = False):
        '''Возвращает первые amount сдвигов до дней,
        в которые будет предмет subject, включая текущий, если today'''
        cur_week_day = datetime.date.today()
        cur_week_day = cur_week_day.weekday()
        ans = []
        for i in range(int(today), 1000):
            if subject in self.timetable[(cur_week_day + i) % 7].subjects:
                ans.append(i)
                if len(ans) == amount:
                    return ans

def unbreakable_async_decorator(func):
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as s:
            await client.send_message(boss, str(s) + ' ' + func.__name__)
            if isinstance(s, AlreadyInConversationError):
                if isinstance(args[0], NewMessage.Event):
                    await client.send_message(args[0].message.from_id, "Дурачок, ты уже заходил в какую-то функцию и не вышел!\n😡😡😡😡😡")
    return wrapper

def button_event(user, msg) -> events.CallbackQuery:
    return events.CallbackQuery(func=lambda e: e.sender_id == user and e.query.msg_id == msg)

@unbreakable_async_decorator
async def send_inline_message(conv: Conversation, message: MessageLike, buttons: Sequence[str], timeout: Optional[float] = None, edited_message: Optional[List[str]] = None) -> Optional[int]:
    '''
    Отправляет сообщение с кнопками в чат и ждет ответа на него

    Аргументы
        conv:
            Сonversation, куда будет  отправлено сообщение

        message:
            Сообщение, которое будет отправлено помимо кнопок

        buttons:
            Тексты на кнопках

        timeout (optional):
            Если пользователь не отвечает в течение timeout секунд,
            сообщение удаляется, а функция ничего не возвращает

        edited_message (optional):
            После ответа пользователя i-ым вариантом
            сообщение заменяется на edited_message[i]

    Возвращает
        Индекс ответа пользователя в buttons, или ничего
    '''

    buttons = [Button.inline(el) for el in buttons]
    if len(buttons) > 3:
        le = len(buttons) // 3 + (len(buttons) % 3 != 0)
        real_buttons = [buttons[i * le: (i + 1) * le] for i in range(3)]
    else:
        real_buttons = buttons
    markup = client.build_reply_markup(real_buttons)
    # await conv.send_message(message, buttons=markup)
    sent_message = await conv.send_message(message, buttons=markup)
    try:
        clicked_button = await conv.wait_event(button_event(conv.chat_id, sent_message.id), timeout=timeout)
        print(sent_message)
        print(clicked_button)
    except asyncio.exceptions.TimeoutError:
        for i in range(3, 0, -1):
            await sent_message.edit('Самоуничтожение через {}...'.format(i))
            await asyncio.sleep(1)
        await sent_message.edit('Аллах Акбар')
        await sent_message.delete(revoke=True)
        return
    subject = clicked_button.query.data.decode('UTF-8')
    pos = -1
    for i in range(len(buttons)):
        if buttons[i].text == subject:
            pos = i
            break
    if edited_message:
        await clicked_button.edit(edited_message[pos])
    else:
        await clicked_button.edit('Ты выбрал {}'.format(subject))
    return pos

home_task_storage = 'databases/ht.bn'
solution_storage = 'databases/sol.bn'
id_to_ind_storage = 'databases/us.bn'
users_storage = 'databases/users.bn'
notes_storage = 'databases/notes.bn'
rasp_storage = 'databases/rasp.bn'
home_tasks = readfile(home_task_storage, True)  # Словарь: Параллель -> Словарь: предмет -> задание
solutions = readfile(solution_storage, True)  # Словарь: Параллель -> Словарь: предмет -> решение
notes = readfile(notes_storage, True)
rasp = readfile(rasp_storage, True)  # Словарь: Параллель -> расписание
id_to_ind, max_ind = readfile(id_to_ind_storage,
                              False)  # Словарь: tg_id -> индекс в массиве студентов; Количество пользователей
users = readfile(users_storage, True)  # Массив пользователей
pending_review = set()
accepted = set()
current_review = 1


async def main():
    async with client.conversation(boss, timeout=None) as conv:
        await asyncio.gather(send_inline_message(conv, 'asd', ['a', 'b'], 10), send_inline_message(conv, 'asd', ['a', 'b'], 10))


if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
        client.run_until_disconnected()
