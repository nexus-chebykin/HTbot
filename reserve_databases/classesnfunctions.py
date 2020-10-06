from pickle import load, dump
import datetime
from telethon import Button
class Student():
    tg_id = 0
    par = '11В'
    name = ''
    name_by = ''

    def __init__(self, tg_id, name, name_by, par='11В'):
        self.tg_id = tg_id
        self.name = name
        self.name_by = name_by
        self.par = par

    def __str__(self):
        return "Student(tg_id = {}, name = {}, name_by = {}, par = {})".format(self.tg_id, self.name, self.name_by, self.par)


class MsgGroup():
    messages = []

    def __init__(self, msg=[], student=0, timestamp=datetime.datetime.now()):
        self.messages = msg[:]
        self.student = student
        self.timestamp = timestamp

class Teacher():
    tg_id = 0
    par = []
    name = ''
    name_by = ''
    subjects = []

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

def readfile(file, single):
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


def writefile(file, *data):
    '''Сначала файл, потом [данные]'''
    print(data)
    f = open(file, 'bw')
    for el in data:
        dump(el, f)
    f.close()
