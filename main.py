# coding=UTF-8
from SolRelated import *
from NoteRelated import *
from TaskRelated import *

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.INFO)


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
        assert (all(el in normal for el in msg[4].lower()))
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
    except BaseException as s:
        print(s)
        await conv.send_message(something_wrong)


# @unbreakable_async_decorator
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
        pt = list(home_tasks[classes[0]].keys())
        while True:
            t = await send_inline_message(conv, 'Какие?', pt)
            subjects.append(pt[t])
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


@client.on(events.NewMessage(pattern='/start'))
@unbreakable_async_decorator
async def new_user(event: NewMessage.Event) -> None:
    sender = await get_id(event)
    if sender in id_to_ind:
        await client.send_message(sender, user_already_signed_in)
    else:
        async with client.conversation(sender, timeout=None, exclusive=not isboss(sender)) as conv:
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


@unbreakable_async_decorator
async def help_abbv(conv):
    await conv.send_message(abbvhelp_student)


@unbreakable_async_decorator
async def helper_student(conv: Conversation):
    await conv.send_message(file=stickers['student_in_help'])


@client.on(events.NewMessage(pattern='/add', func=is_boss))
async def stick(event):
    try:
        async with client.conversation(await get_id(event), timeout=None, exclusive=False) as conv:
            await conv.send_message('Название:')
            name = (await conv.get_response()).message
            await conv.send_message('Стикер:')
            res = (await conv.get_response()).media
            await conv.send_message(file=res)
            if name in stickers:
                await conv.send_message('such name already exists')
                return
            stickers[name] = res
            writefile(stickers_storage, stickers)
    except BaseException as s:
        print(s)


@client.on(events.NewMessage(pattern='/menu', func=is_student))
@unbreakable_async_decorator
async def menu(event) -> None:
    sender = await get_id(event)
    async with client.conversation(sender, timeout=None, exclusive=not isboss(sender)) as conv:
        if await is_teacher(event) and not isboss(sender):
            result = await send_inline_message(conv, 'Choose your Destiny', buttons=teacher_functions, max_per_row=1)
            if result == 0:
                await addnote_teacher(conv)
            elif result == 1:
                await mynotes_teacher(conv)
            elif result == 2:
                await addtask_teacher(conv)
            elif result == 3:
                await conv.send_message(help_str_teacher)
        else:
            result = await send_inline_message(conv, 'Choose your Destiny', buttons=student_functions, max_per_row=1)
            await my_log(student_functions[result] + ' ' + users[id_to_ind[sender]].name)
            if result == 0:
                await tomorrow(conv)
            elif result == 1:
                await gettask(conv)
            elif result == 2:
                await addtask_student(conv)
            elif result == 3:
                await getsol(conv)
            elif result == 4:
                await add_sol(conv)
            elif result == 5:
                await conv.send_message(abbvhelp_student)
            elif result == 6:
                await addnote(conv)
            elif result == 7:
                await viewnote(conv)
            else:
                result = await send_inline_message(conv, 'Что на этот раз?', buttons=addition, max_per_row=1)
                if result == 1:
                    await helper_student(conv)
                elif result == 0:
                    await mynotes(conv)
                elif result == 2:
                    await conv.send_message("У тебя {} ♂cum♂coin".format(users[id_to_ind[sender]].money))
        await conv.send_message('/menu')

async def main():
    print('done')
    current_time = datetime.datetime.now()
    if current_time.hour >= 7:
        new_time = current_time + datetime.timedelta(days=1)
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
