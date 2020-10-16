# coding=UTF-8
import asyncio
import datetime
from string_constants import *
from telethon import TelegramClient, events, tl, Button
from telethon.tl.types import InputMediaPoll, Poll, PollAnswer
from telethon.tl.custom.conversation import Conversation
from telethon.errors.common import AlreadyInConversationError
from telethon.tl.custom.message import Message
from telethon.hints import MessageLike
from telethon.events.newmessage import NewMessage

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
            await client.send_message(boss, str(s) + ' ' + func.__name__)
            if isinstance(s, AlreadyInConversationError):
                if isinstance(args[0], NewMessage.Event):
                    await client.send_message(args[0].message.from_id, "Дурачок, ты уже заходил в какую-то функцию и не вышел!\n😡😡😡😡😡")
    return wrapper


@unbreakable_async_decorator
async def register_student(conv: Conversation, sender: int) -> None:
    global current_review, max_ind
    s = await client.get_entity(sender)
    print(s)
    await conv.send_message(student_sign_in_guide)
    try:
        t = await conv.get_response()
        msg = t.message
        msg = msg.split('\n')
        if len(msg) != 3:
            assert False
        assert (all(el in normal for el in msg[0].lower()))
        assert (all(el in normal for el in msg[1].lower()))
        assert (all(el in normal for el in msg[2].lower()))
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
            return
        id_to_ind[sender] = max_ind
        max_ind += 1
        users.append(Student(sender, msg[0], msg[1], msg[2].upper()))
        print(*users)
        writefile(id_to_ind_storage, id_to_ind, max_ind)
        writefile(users_storage, users)
        await conv.send_message(success_sign_in)
    except Exception as s:
        print(s)
        await conv.send_message(something_wrong)


@unbreakable_async_decorator
async def register_teacher(conv: Conversation, sender: int) -> None:
    global max_ind, current_review
    s = await client.get_entity(sender)
    print(s)
    await conv.send_message(teacher_sign_in_guide)
    try:
        t = await conv.get_response()
        msg = t.message
        msg = msg.split('\n')
        if len(msg) != 2:
            assert False
        assert (all(el in normal for el in msg[0].lower()))
        assert (all(el in normal for el in msg[1].lower()))
        await conv.send_message(
            'Над какими классами властвуете? (В одном сообщении через пробел / на новой строке классы, например "11А 11Б")')
        classes = (await conv.get_response()).message.split()
        subjects = []
        await conv.send_message(
            'А какие предметы ведете? (Если больше 1, то напишите /another после очередного выбора, иначе /end)')
        while True:
            t = await send_inline_message(conv, 'Какие?', list(home_tasks[classes[0]].keys()))
            subjects.append(t.strip())
            p = await conv.get_response()
            if p.message == '/end':
                break
        form = str(current_review) + '\n' + '\n'.join(msg) + '\n' + \
               s.first_name + '\n' + '\n'.join(subjects) + '\n' + '\n'.join(classes)
        await client.send_message(boss, form)
        await conv.send_message('Ваша анкета принята на обработку. Ждите.')
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
            return
        id_to_ind[sender] = max_ind
        max_ind += 1
        users.append(Teacher(sender, msg[0], msg[1], classes, subjects))
        print(*users)
        writefile(id_to_ind_storage, id_to_ind, max_ind)
        writefile(users_storage, users)
        await conv.send_message(success_sign_in)
    except Exception as s:
        print(s)
        await conv.send_message(something_wrong)
        return


@unbreakable_async_decorator
async def send_inline_message(conv: Conversation, message: MessageLike, buttons: Sequence[str]) -> str:
    buttons = [Button.inline(el) for el in buttons]
    if len(buttons) > 3:
        le = len(buttons) // 3 + (len(buttons) % 3 != 0)
        real_buttons = [buttons[i * le: (i + 1) * le] for i in range(3)]
    else:
        real_buttons = buttons
    markup = client.build_reply_markup(real_buttons)
    await conv.send_message(message, buttons=markup)
    clicked_button = await conv.wait_event(button_event(conv.chat_id))
    subject = clicked_button.query.data.decode('UTF-8')
    await clicked_button.edit('Ты выбрал {}'.format(subject))
    return subject


@client.on(events.NewMessage(pattern='/start'))
@unbreakable_async_decorator
async def new_user(event: NewMessage.Event) -> None:
    sender = event.message.from_id
    if sender in id_to_ind:
        await client.send_message(sender, user_already_signed_in)
    else:
        async with client.conversation(sender, timeout=None, exclusive=not (sender == boss)) as conv:
            ans = await send_inline_message(conv, 'Ты ученик или учитель?', ['Ученик', 'Учитель'])
            if ans == 'Ученик':
                await register_student(conv, sender)
            else:
                await register_teacher(conv, sender)


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
    return event.message.from_id in id_to_ind and isinstance(users[id_to_ind[event.message.from_id]], Student)


def is_teacher(event):
    return (event.message.from_id in id_to_ind and isinstance(users[id_to_ind[event.message.from_id]],
                                                              Teacher)) or event.message.from_id == boss


@client.on(events.NewMessage(pattern='/abbvhelp', func=is_student))
@unbreakable_async_decorator
async def help_abbv(event):
    await client.send_message(event.message.from_id, abbvhelp)


@client.on(events.NewMessage(pattern='/help', func=is_student))
@unbreakable_async_decorator
async def helper(event):
    await client.send_message(event.message.from_id, help_str)


@client.on(events.NewMessage(pattern='/help', func=is_teacher))
@unbreakable_async_decorator
async def helper_teacher(event):
    await client.send_message(event.message.from_id, help_str_teacher)


@unbreakable_async_decorator
async def show_task(parr: str, subject: str, conv: Conversation) -> None:
    await conv.send_message('На данный момент дз выглядит так:')
    if isinstance(home_tasks[parr][subject], MsgGroup) and home_tasks[parr][subject].messages:
        for el in home_tasks[parr][subject].messages:
            await conv.send_message(message=el[0], file=el[1])
        await conv.send_message("Последний раз оно было изменено " +
                                users[home_tasks[parr][subject].student].name_by + ' ' + str(
            home_tasks[parr][subject].timestamp)[:-10])
    else:
        await conv.send_message('*Пусто*')


@unbreakable_async_decorator
async def show_sol(parr: str, subject: str, conv: Conversation) -> None:
    await conv.send_message('На данный момент решение выглядит так:')
    if isinstance(solutions[parr][subject], MsgGroup) and solutions[parr][subject].messages:
        for el in solutions[parr][subject].messages:
            await conv.send_message(message=el[0], file=el[1])
        print(solutions[parr][subject].student)
        await conv.send_message("Последний раз оно было изменено " +
                                users[solutions[parr][subject].student].name_by + ' ' + str(
            solutions[parr][subject].timestamp)[:-10])
    else:
        await conv.send_message('*Пусто*')


def button_event(user) -> events.CallbackQuery:
    return events.CallbackQuery(func=lambda e: e.sender_id == user)


@unbreakable_async_decorator
async def get_subject(parr, conv) -> str:
    return await send_inline_message(conv, which_subject, home_tasks[parr])


@client.on(events.NewMessage(pattern='/gettask', func=is_student))
@unbreakable_async_decorator
async def gettask(event) -> None:
    sender = event.message.from_id
    async with client.conversation(sender, timeout=None, exclusive=not (boss == sender)) as conv:
        parr = users[id_to_ind[sender]].par
        subject = await get_subject(parr, conv)
        if not subject:
            return
        await show_task(parr, subject, conv)


@unbreakable_async_decorator
async def get_msg_group(conv: Conversation, msg: MessageLike) -> Union[List[Tuple[Any, Any]], int]:
    await conv.send_message(msg)
    task_part = await conv.get_response()
    messages = []
    while task_part.message != '/end':
        if task_part.message == '/exit':
            await conv.send_message("Ок :)")
            return -1
        messages.append((task_part.message, task_part.media))
        task_part = await conv.get_response()
    return messages


@client.on(events.NewMessage(pattern='/addtask'))
@unbreakable_async_decorator
async def addtask(event) -> None:
    sender = event.message.from_id
    if is_student(event):
        async with client.conversation(sender, timeout=None, exclusive=not (boss == sender)) as conv:
            parr = users[id_to_ind[sender]].par
            subject = await get_subject(parr, conv)
            if not subject:
                return
            await show_task(parr, subject, conv)
            await conv.send_message(sure_to_change)
            ans = await conv.get_response()
            if ans.message == '/replace' or ans.message == '/append':
                messages = await get_msg_group(conv, "Ладно. Скидывай мне сообщения. После последнего напиши /end")
                if messages == -1:
                    return
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
    elif is_teacher(event):
        teacher = users[id_to_ind[sender]]
        # teacher = User.Teacher(boss, 'Сеня', 'Сеней', ['11Б', "11В"], ['phy', 'ast'])
        async with client.conversation(sender, timeout=None, exclusive=not (boss == sender)) as conv:
            await conv.send_message('Каким классам хотите добавить домашнее задание?')
            classes = []
            while True:
                classes.append(await send_inline_message(conv, 'Классы', teacher.classes))
                if len(classes) < len(teacher.classes):
                    ans = await send_inline_message(conv, 'Может, еще 1?', ['Да', 'Нет'])
                    if len(ans) == 3:
                        break
                else:
                    break
            if len(teacher.subjects) > 1:
                subj = await send_inline_message(conv, 'А по какому предмету?', teacher.subjects)
            else:
                subj = teacher.subjects[0]
            t = '{}, ' * (len(classes) - 1)
            await conv.send_message(('Вы собираетесь добавить ' + t + '{} дз по {}').format(*classes, subj))
            messages = await get_msg_group(conv,
                                           "Скидывайте мне сообщения. После последнего напишите /end. Чтобы прервать без сохранения - /exit")
            if messages != -1:
                for parr in classes:
                    home_tasks[parr][subj] = MsgGroup(
                        messages, id_to_ind[sender], datetime.datetime.now()
                    )
            writefile(home_task_storage, home_tasks)
            await conv.send_message('Готово!')


@client.on(events.NewMessage(pattern='/getsol', func=is_student))
@unbreakable_async_decorator
async def getsol(event) -> None:
    sender = event.message.from_id
    async with client.conversation(sender, timeout=None, exclusive=not (boss == sender)) as conv:
        parr = users[id_to_ind[sender]].par
        subject = await get_subject(parr, conv)
        if not subject:
            return
        await show_sol(parr, subject, conv)


# @client.on(events.NewMessage(pattern='/addnote'))
# @unbreakable_async_decorator
# async def addnote(event) -> None:
#     sender = event.message.from_id
#     async with client.conversation(sender, timeout=None, exclusive=not (boss == sender)) as conv:
#         await conv.send_message('Как она будет называться?')
#         name = await conv.get_response()
#         body = await get_msg_group(conv, 'Скидывайте мне сообщения. После последнего напишите /end. Чтобы прервать без сохранения - /exit')
#         if body != -1:
#             s


@client.on(events.NewMessage(pattern='/addsol'))
@unbreakable_async_decorator
async def addsol(event) -> None:
    sender = event.message.from_id
    if is_student(event):
        parr = users[id_to_ind[sender]].par
        async with client.conversation(sender, timeout=None, exclusive=not (boss == sender)) as conv:
            subject = await get_subject(parr, conv)
            if not subject:
                return
            await show_sol(parr, subject, conv)
            await conv.send_message(sure_to_change)
            ans = await conv.get_response()
            if ans.message == '/replace' or ans.message == '/append':
                messages = await get_msg_group(conv, "Ладно. Скидывай мне сообщения. После последнего напиши /end")
                if not messages:
                    return
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
    print('done')
    current_time = datetime.datetime.now()
    if current_time.hour >= 7:
        try:
            new_time = current_time.replace(day=current_time.day + 1)
        except:
            new_time = current_time.replace(month=current_time.month + 1, day=1)
        new_time = new_time.replace(hour=7, minute=0, second=0)
        print(new_time)
        delta = new_time - current_time
        await asyncio.sleep(delta.total_seconds())
    else:
        new_time = current_time.replace(hour=7, minute=0, second=0)
        print(new_time)
        delta = new_time - current_time
        await asyncio.sleep(delta.total_seconds())
    while True:
        await client.send_message(boss, 'Я жив!')
        await asyncio.sleep(60 * 60 * 24)


with client:
    client.loop.run_until_complete(main())
