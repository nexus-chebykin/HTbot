# coding=UTF-8
import asyncio
import datetime
from classesnfunctions import *
from string_constants import *
from telethon import TelegramClient, events, tl, Button
from telethon.tl.types import InputMediaPoll, Poll, PollAnswer

from random import shuffle
import logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

def unbreakable_async_decorator(func):
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as s:
            await client.send_message(boss, str(s))
    return wrapper

@client.on(events.NewMessage(pattern='/start'))
@unbreakable_async_decorator
async def new_user(event):
    global current_review, max_ind
    sender = event.message.from_id
    s = await client.get_entity(sender)
    print(s)
    if sender in id_to_ind:
        await client.send_message(sender, user_already_signed_in)
    else:
        async with client.conversation(sender, timeout=None, exclusive=not (sender == boss)) as conv:
            await conv.send_message(user_sign_in_guide)
            try:
                t = await conv.get_response()
                msg = t.message
                msg = msg.split('\n')
                if len(msg) != 3:
                    assert False
                assert(all(el in normal for el in msg[0].lower()))
                assert(all(el in normal for el in msg[1].lower()))
                assert(all(el in normal for el in msg[2].lower()))
                form = str(current_review) + '\n' + '\n'.join(msg) + '\n' + \
                    s.first_name
                await client.send_message(boss, form)
                await conv.send_message('Твоя анкета принята на обработку. Жди.')
                pending_review.add(current_review)
                cur = current_review
                current_review += 1
                while cur in pending_review:
                    await asyncio.sleep(15)
                if cur in accepted:
                    accepted.discard(cur)
                    await conv.send_message('Принято')
                else:
                    await conv.send_message('Отклонено, попробуй снова')
                    return 0
                id_to_ind[sender] = max_ind
                max_ind += 1
                students.append(Student(sender, msg[0], msg[1], msg[2].upper()))
                print(*students)
                writefile(id_to_ind_storage, id_to_ind, max_ind)
                writefile(students_storage, students)
                await conv.send_message(success_sign_in)
            except Exception as s:
                print(s)
                await conv.send_message(something_wrong)
                return 0


@client.on(events.NewMessage(pattern='/accept', chats=boss))
@unbreakable_async_decorator
async def ac(event):
    async with client.conversation(boss, timeout=None, exclusive=False) as conv:
        await conv.send_message('Какую заявку?')
        resp = await conv.get_response()
        # print(int(resp.text))
        accepted.add(int(resp.text))
        pending_review.discard(int(resp.text))
        await conv.send_message('OK')


@client.on(events.NewMessage(pattern='/decline', chats=boss))
@unbreakable_async_decorator
async def dec(event):
    async with client.conversation(boss, timeout=None, exclusive=False) as conv:
        await conv.send_message('Какую заявку?')
        resp = await conv.get_response()
        # print(int(resp.text))
        pending_review.discard(int(resp.text))
        await conv.send_message('OK')

def is_student(event):
    return event.message.from_id in id_to_ind and students[id_to_ind[event.message.from_id]].par != 'УЧИТЕЛЬ'

def is_teacher(event):
    return (event.message.from_id in id_to_ind and students[id_to_ind[event.message.from_id]].par == 'УЧИТЕЛЬ') or event.message.from_id == boss

@client.on(events.NewMessage(pattern='/abbvhelp', func=is_student))
@unbreakable_async_decorator
async def help_abbv(event):
    await client.send_message(event.message.from_id, abbvhelp)


@client.on(events.NewMessage(pattern='/help', func=is_student))
@unbreakable_async_decorator
async def helper(event):
    await client.send_message(event.message.from_id, help_str)

@unbreakable_async_decorator
async def show_task(parr, subject, conv):
    await conv.send_message('На данный момент дз выглядит так:')
    if isinstance(home_tasks[parr][subject], MsgGroup) and home_tasks[parr][subject].messages:
        for el in home_tasks[parr][subject].messages:
            await conv.send_message(message=el[0], file=el[1])
        await conv.send_message("Последний раз оно было изменено " +
                                students[home_tasks[parr][subject].student].name_by + ' ' + str(home_tasks[parr][subject].timestamp)[:-10])
    else:
        await conv.send_message('*Пусто*')

@unbreakable_async_decorator
async def show_sol(parr, subject, conv):
    await conv.send_message('На данный момент решение выглядит так:')
    if isinstance(solutions[parr][subject], MsgGroup) and solutions[parr][subject].messages:
        for el in solutions[parr][subject].messages:
            await conv.send_message(message=el[0], file=el[1])
        await conv.send_message("Последний раз оно было изменено " +
                                students[solutions[parr][subject].student].name_by + ' ' + str(solutions[parr][subject].timestamp)[:-10])
    else:
        await conv.send_message('*Пусто*')

def subject_button_event(user):
    return events.CallbackQuery(func=lambda e: e.sender_id == user)

@unbreakable_async_decorator
async def get_subject(parr, conv):
    buttons = [Button.inline(el) for el in home_tasks[parr]]
    le = len(home_tasks[parr]) // 3 + (len(home_tasks[parr]) % 3 != 0)
    real_buttons = [buttons[i * le : (i + 1) * le] for i in range(3)]
    markup = client.build_reply_markup(real_buttons)
    await conv.send_message(which_subject, buttons=markup)
    clicked_button = await conv.wait_event(subject_button_event(conv.chat_id))
    subject = clicked_button.query.data.decode('UTF-8').lower()
    await clicked_button.edit('Ты выбрал {}'.format(subject))
    return subject


@client.on(events.NewMessage(pattern='/gettask', func=is_student))
@unbreakable_async_decorator
async def gettask(event):
    sender = event.message.from_id
    async with client.conversation(sender, timeout=None, exclusive=not (boss == sender)) as conv:
        parr = students[id_to_ind[sender]].par
        subject = await get_subject(parr, conv)
        if not subject:
            return 0
        await show_task(parr, subject, conv)

@unbreakable_async_decorator
async def get_msg_group(conv):
    await conv.send_message("Ладно. Скидывай мне сообщения. После последнего напиши /end")
    task_part = await conv.get_response()
    messages = []
    while task_part.message != '/end':
        if task_part.message == '/exit':
            await conv.send_message("Ок :)")
            return -1
        messages.append((task_part.message, task_part.media))
        task_part = await conv.get_response()
    return messages


@client.on(events.NewMessage(pattern='/addtask', func=is_student))
@unbreakable_async_decorator
async def addtask(event):
    sender = event.message.from_id
    parr = students[id_to_ind[sender]].par
    async with client.conversation(sender, timeout=None, exclusive=not (boss == sender)) as conv:
        subject = await get_subject(parr, conv)
        if not subject:
            return 0
        await show_task(parr, subject, conv)
        await conv.send_message(sure_to_change)
        ans = await conv.get_response()
        if ans.message == '/replace' or ans.message == '/append':
            messages = await get_msg_group(conv)
            if messages == -1:
                return 0
            await conv.send_message("Понимаю. Сохранил. Спасибо папаша.")
            if ans.message == '/replace':
                home_tasks[parr][subject] = MsgGroup(
                    messages, id_to_ind[sender], datetime.datetime.now())
            else:
                if isinstance(home_tasks[parr][subject], MsgGroup):
                    home_tasks[parr][subject].messages.extend(messages)
                    home_tasks[parr][subject].student = id_to_ind[sender]
                    home_tasks[parr][subject].timestamp = datetime.datetime.now()
                else:
                    home_tasks[parr][subject] = MsgGroup(
                        messages, id_to_ind[sender], datetime.datetime.now())
            writefile(home_task_storage, home_tasks)
        else:
            await conv.send_message("Ок :)")


@client.on(events.NewMessage(pattern='/getsol', func=is_student))
@unbreakable_async_decorator
async def getsol(event):
    sender = event.message.from_id
    async with client.conversation(sender, timeout=None, exclusive=not (boss == sender)) as conv:
        parr = students[id_to_ind[sender]].par
        subject = await get_subject(parr, conv)
        if not subject:
            return 0
        await show_sol(parr, subject, conv)


@client.on(events.NewMessage(pattern='/addsol', func=is_student))
@unbreakable_async_decorator
async def addsol(event):
    sender = event.message.from_id
    parr = students[id_to_ind[sender]].par
    async with client.conversation(sender, timeout=None, exclusive=not (boss == sender)) as conv:
        subject = await get_subject(parr, conv)
        if not subject:
            return 0
        await show_sol(parr, subject, conv)
        await conv.send_message(sure_to_change)
        ans = await conv.get_response()
        if ans.message == '/replace' or ans.message == '/append':
            messages = await get_msg_group(conv)
            if not messages:
                return 0
            await conv.send_message("Понимаю. Сохранил. Тебя обязательно отблагодарят (но это не точно)")
            if ans.message == '/replace':
                solutions[parr][subject] = MsgGroup(
                    messages, id_to_ind[sender], datetime.datetime.now())
                print('here')
            else:
                if isinstance(solutions[parr][subject], MsgGroup):
                    solutions[parr][subject].messages.extend(messages)
                    solutions[parr][subject].student = id_to_ind[sender]
                    solutions[parr][subject].timestamp = datetime.datetime.now()
                else:
                    solutions[parr][subject] = MsgGroup(
                        messages, id_to_ind[sender], datetime.datetime.now())
            writefile(solution_storage, solutions)
        else:
            await conv.send_message("Ок :)")

# @client.on(events.NewMessage(pattern=='/addtest'))
# @unbreakable_async_decorator
# async def addtest(event):
#     sender = event.message.from_id
#     async with client.conversation(sender, timeout=None, exclusive=not (sender == boss)) as conv:
#         conv.send_message()


async def main():
    print("done")


with client:
    client.loop.run_until_complete(main())
    client.loop.run_forever()
