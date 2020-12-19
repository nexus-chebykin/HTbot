# coding=UTF-8

import datetime
import asyncio
import datetime

import traceback
from string_constants import *
from telethon import TelegramClient
from telethon import TelegramClient, events, tl, Button
from telethon.tl.types import InputMediaPoll, Poll, PollAnswer
from telethon.tl.custom.conversation import Conversation
from telethon.errors.common import AlreadyInConversationError
from telethon.tl.custom.message import Message
from telethon.tl.types import MessageMediaWebPage
from telethon.hints import MessageLike
from telethon.events.newmessage import NewMessage
from random import shuffle
import logging
from boot import *
from pickle import load, dump
from typing import *
import time


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

async def my_log(*data: Any,) -> None:
    if not Test:
        await client.send_message('https://t.me/joinchat/Dmz9yxzt7_5BzdSj5q8-cg', '\n'.join(list(map(str, data))))


async def is_student(event):
    return (await event.get_chat()).id in id_to_ind and isinstance(users[id_to_ind[(await event.get_chat()).id]],
                                                                   Student)


async def is_teacher(event):
    tmp = (await event.get_chat()).id
    return tmp in id_to_ind and (isinstance(users[id_to_ind[tmp]], Teacher)) or isboss(tmp)


async def get_id(event_or_conv) -> int:
    return (await event_or_conv.get_chat()).id


class User():
    tg_id: int
    name: str
    name_by: str

    def __init__(self, tg_id, name, name_by):
        self.tg_id = tg_id
        self.name = name
        self.name_by = name_by

    def __str__(self):
        return '''{}(
        id in tg: {}
        name: {}
        name_by: {}
        )'''.format(self.__class__.__name__, self.tg_id, self.name, self.name_by)


class Student(User):
    par: str
    money: int

    def __init__(self, tg_id, name, name_by, par='11В'):
        super().__init__(tg_id, name, name_by)
        self.par = par
        self.money = 31

    def __str__(self):
        return super().__str__()[:-1] + '''parralel: {}
        money: {})'''.format(self.par, self.money)


class Teacher(User):
    classes: List[str]
    subjects: List[str]

    def __init__(self, tg_id, name, name_by, classes=(), subjects=()):
        super().__init__(tg_id, name, name_by)
        self.classes = list(classes[:])
        self.subjects = list(subjects[:])

    def __str__(self):
        classes = ' '.join(self.classes)
        subjects = ' '.join(self.subjects)
        return super().__str__()[:-1] + '''classes: {}
        subjects: {})'''.format(classes, subjects)


class MsgGroup():
    messages: List[Tuple[Any, Any]]
    student: int
    timestamp: datetime.datetime

    def __init__(self, msg=(), student=0, timestamp=datetime.datetime.now()):
        self.messages = list(msg[:])
        self.student = student
        self.timestamp = timestamp


def unbreakable_async_decorator(func):
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result
        except BaseException as s:
            await client.send_message(boss, str(s) + ' ' + func.__name__)
            try:
                await client.send_message(boss, users[id_to_ind[await(get_id(args[0]))]].name)
            except:
                pass
            if isinstance(s, AlreadyInConversationError):
                await client.send_message(await get_id(args[0]),
                                          "Дурачок, ты уже заходил в какую-то функцию и не вышел!\n😡😡😡😡😡")

    return wrapper
    # return func


class Note(MsgGroup):
    header: str

    def __init__(self, header='', msg=(), student=0, timestamp=datetime.datetime.now()):
        super().__init__(msg, student, timestamp)
        self.header = header

    @unbreakable_async_decorator
    async def show(self, conv: Conversation):
        for el in self.messages:
            await conv.send_message(el[0], file=el[1])


class Task(MsgGroup):
    deadline: datetime.date

    def __init__(self, deadline: datetime.date, msg=(), student=0, timestamp=datetime.date.today()):
        super().__init__(msg, student, timestamp)
        self.deadline = deadline

    @unbreakable_async_decorator
    async def show(self, conv: Conversation, ask_for_money: bool = True):
        if self.messages:
            await conv.send_message('Дз к {}:'.format(self.deadline))
            for el in self.messages:
                await conv.send_message(message=el[0], file=el[1])
            if ask_for_money:
                return client.loop.create_task(transuction(conv,
                                                           id_to_ind[(await conv.get_chat()).id],
                                                           self.student,
                                                           "Последний раз оно было изменено {} {}".format(
                                                               users[self.student].name_by,
                                                               str(self.timestamp)[:-10]),
                                                           )
                                               )
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

    def fill_until_day(self, day_until: datetime.date, subject: str, parr: str):
        if not self.history:
            self.history = [Task(datetime.date.today() + datetime.timedelta(days=rasp[parr].find_next(subject)[0]))]
        cur_week_day = self.history[-1].deadline
        cur_week_day = cur_week_day.weekday()
        amount = day_until - self.history[-1].deadline
        pos = len(self.history) - 1
        for i in range(1, amount.days + 1):
            if ((cur_week_day + i) % 7) != 6 and subject in rasp[parr].timetable[(cur_week_day + i) % 7].subjects:
                self.history.append(Task(self.history[pos].deadline + datetime.timedelta(days=i)))
        writefile(home_task_storage, home_tasks)

class RaspDay():
    subjects: List[str]

    def __init__(self, data: List[str]):
        self.subjects = data[:]


class Rasp():
    timetable: List[RaspDay] = []

    def __init__(self, rasp: List[RaspDay]):
        self.timetable = rasp[:]

    def find_next(self, subject, amount=1, today=False):
        '''Возвращает первые amount сдвигов до дней,
        в которые будет предмет subject, включая текущий, если today'''
        cur_week_day = datetime.date.today()
        cur_week_day = cur_week_day.weekday()
        ans = []
        for i in range(1 - int(today), 1000):
            if ((cur_week_day + i) % 7) != 6 and subject in self.timetable[(cur_week_day + i) % 7].subjects:
                ans.append(i)
                if len(ans) == amount:
                    return ans


def button_event(user, msg) -> events.CallbackQuery:
    return events.CallbackQuery(func=lambda e: e.sender_id == user and e.query.msg_id == msg)


def isboss(tg_id):
    return tg_id == boss #or tg_id == timur


async def is_boss(event):
    return isboss(await get_id(event))


@unbreakable_async_decorator
async def transuction(conv, fro, to, msg):
    res = await send_inline_message(conv, msg, ['Кинуть ему монетку!', 'Я жмот'],
                                    timeout=30,
                                    edited_message=['{} очень рад(а)'.format(
                                        users[to].name),
                                        'Чел...'])
    if res == 0:
        if users[fro].money == 0:
            await conv.send_message("Ты на мели")
        else:
            users[fro].money -= 1
            users[to].money += 1


@unbreakable_async_decorator
async def send_inline_message(conv: Conversation, message: MessageLike, buttons: Sequence[str],
                              timeout: Optional[float] = None, edited_message: Optional[List[str]] = None,
                              max_per_row: Optional[int] = 3) -> Optional[int]:
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
    buttons = [Button.inline(el, bytes([i])) for i, el in enumerate(buttons, 1)]
    real_buttons = [buttons[i:i + max_per_row] for i in range(0, len(buttons), max_per_row)]
    markup = client.build_reply_markup(real_buttons)
    sent_message = await conv.send_message(message, buttons=markup)
    try:
        clicked_button = await conv.wait_event(button_event(conv.chat_id, sent_message.id), timeout=timeout)
    except asyncio.TimeoutError:
        for i in range(3, 0, -1):
            await sent_message.edit('Самоуничтожение через {}...'.format(i), buttons=None)
            await asyncio.sleep(1)
        await sent_message.edit('Аллах Акбар')
        await sent_message.delete(revoke=True)
        return
    pos = int.from_bytes(clicked_button.query.data, 'big') - 1
    if edited_message:
        await sent_message.edit(edited_message[pos], buttons=None)
    else:
        await sent_message.edit('Ты выбрал {}'.format(buttons[pos].text), buttons=None)
    return pos


@unbreakable_async_decorator
async def get_subject(parr, conv) -> str:
    tmp = list(home_tasks[parr].keys())
    res = await send_inline_message(conv, which_subject, tmp)
    return tmp[res]


@unbreakable_async_decorator
async def get_msg_group(conv: Conversation, msg: MessageLike) -> Union[List[Tuple[Any, Any]], int]:
    await conv.send_message(msg)
    task_part = await conv.get_response()
    messages = []
    while task_part.message != '/end':
        messages.append((task_part.message, task_part.media if not isinstance(task_part.media, MessageMediaWebPage) else None))
        task_part = await conv.get_response()
    return messages



home_tasks: Dict[str, Dict[str, HomeTask]] = readfile(home_task_storage, True)
'''Словарь: Параллель -> Словарь: предмет -> задание'''
solutions: Dict[str, Dict[str, MsgGroup]] = readfile(solution_storage, True)
# for el in solutions:
#     for subj in solutions[el]:
#         solutions[el][subj] = None
# writefile(solution_storage, solutions)
'''Словарь: Параллель -> Словарь: предмет -> решение'''
notes: Dict[str, List[Note]] = readfile(notes_storage, True)
rasp: Dict[str, Rasp] = readfile(rasp_storage, True)
'''Словарь: Параллель -> расписание'''
tmp = readfile(id_to_ind_storage, False)
id_to_ind: Dict[int, int] = tmp[0]
'''Словарь: tg_id -> индекс в массиве студентов'''
max_ind: int = tmp[1]
'''Количество пользователей'''
users: List[Union[Student, Teacher]] = readfile(users_storage, True)
'''Массив пользователей'''
stickers: Dict[str, Any] = readfile(stickers_storage, True)
'''Словарь: название -> стикер'''
pending_review = set()
accepted = set()
# for el in notes:
#     notes[el].clear()
# writefile(notes_storage, notes)
# for par in home_tasks:
#     for subj in home_tasks[par]:
#         home_tasks[par][subj].history.clear()
# writefile(home_task_storage, home_tasks)

current_review = 1

if __name__ == '__main__':
    # async def main():
    #     async with client.conversation(timur, timeout=None) as conv:
    #         await send_inline_message(conv, 'asd', ['a', 'b'], 10)

    with client:
        client.run_until_disconnected()
