from pickle import load, dump
import datetime
from telethon import Button
from typing import *


class MsgGroup():
    messages: Union[Tuple, List[Tuple[Any, Any]]]
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

    def __init__(self, tg_id, name, name_by, par='11В'):
        super().__init__(tg_id, name, name_by)
        self.par = par


class Teacher(User):
    classes: List[str]
    subjects: List[str]

    def __init__(self, tg_id, name, name_by, classes=(), subjects=()):
        super().__init__(tg_id, name, name_by)
        self.classes = list(classes[:])
        self.subjects = list(subjects[:])

class Test():
    quests = []

    def __init__(self, qsts=[], name='', timestamp=datetime.datetime.now()):
        self.quests = qsts
        self.name = name
        self.timestamp = timestamp

class Quest():
    buttons = []
    correct_ans = 0
    questions = []

    def __init__(self, opts, corr):
        self.questions = opts[:]
        self.buttons = [Button.text(str(i)) for i in range(len(opts))]
        self.correct_ans = corr

    async def get_ans(self, conv):
        await conv.send_message('В каком из слов неправильно поставлено ударение:\n' + '\n'.join(self.questions))
        ans = conv.get_response()
        if ans != self.correct_ans:
            return 0
        return 1

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
