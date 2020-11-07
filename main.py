# coding=UTF-8
from string_constants import *

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


@client.on(events.NewMessage(pattern='/start'))
@unbreakable_async_decorator
async def new_user(event: NewMessage.Event) -> None:
    sender = (await event.get_chat()).id
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


async def is_student(event):
    return (await event.get_chat()).id in id_to_ind and isinstance(users[id_to_ind[(await event.get_chat()).id]], Student)


async def is_teacher(event):
    return ((await event.get_chat()).id in id_to_ind and isinstance(users[id_to_ind[(await event.get_chat()).id]],
                                                              Teacher)) or (await event.get_chat()).id == boss

@client.on(events.NewMessage(pattern='/abbvhelp', func=is_student))
@unbreakable_async_decorator
async def help_abbv(event):
    await client.send_message((await event.get_chat()).id, abbvhelp)


@client.on(events.NewMessage(pattern='/help', func=is_student))
@unbreakable_async_decorator
async def helper_student(event):
    await client.send_message((await event.get_chat()).id, help_str)


@client.on(events.NewMessage(pattern='/help', func=is_teacher))
@unbreakable_async_decorator
async def helper_teacher(event):
    await client.send_message((await event.get_chat()).id, help_str_teacher)


@unbreakable_async_decorator
async def show_task(parr: str, subject: str, conv: Conversation, switch: bool = False, shift = 0) -> None:
    '''
    Показывает задание на урок строго больше текущего
    '''
    cur_date = datetime.date.today()
    for ind in range(len(home_tasks[parr][subject].history)):
        if home_tasks[parr][subject].history[ind].deadline > cur_date:
            ind_to_be_showed = ind
            break
    else:
        await conv.send_message('*Пусто*')
        return
    current_pos = ind_to_be_showed + shift
    to_be_awaited = await home_tasks[parr][subject].history[current_pos].show(conv)
    if switch:
        # Поиск предыдущего задания
        buttons = []
        for ind in range(current_pos - 1, -1, -1):
            if (home_tasks[parr][subject].history[ind].messages):
                buttons.append((ind, home_tasks[parr][subject].history[ind].deadline))
                break
        for ind in range(current_pos + 1, len(home_tasks[parr][subject].history)):
            if (home_tasks[parr][subject].history[ind].messages):
                buttons.append((ind, home_tasks[parr][subject].history[ind].deadline))
                break
        if len(buttons) == 0:
            return
        result = await send_inline_message(conv,
                                  'Хочешь посмотреть другое задание?',
                                  [str(option[1]) for option in buttons] + ['Нет'],
                                  timeout=180)
        if result is not None and result != len(buttons):
            await show_task(parr, subject, conv, True, buttons[result][0] - ind_to_be_showed)
    await to_be_awaited

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

@unbreakable_async_decorator
async def get_subject(parr, conv) -> str:
    tmp = list(home_tasks[parr].keys())
    res = await send_inline_message(conv, which_subject, tmp)
    return tmp[res]

@unbreakable_async_decorator
async def gettask(conv: Conversation) -> None:
    sender = (await conv.get_chat()).id
    parr = users[id_to_ind[sender]].par
    subject = await get_subject(parr, conv)
    await show_task(parr, subject, conv, switch=True)

# @client.on(events.NewMessage(pattern='/tomorrow', func=is_student))
# @unbreakable_async_decorator
# async def gettomorow(event) -> None:
#     sender = (await event.get_chat()).id
#     async with client.conversation(sender, timeout=None, exclusive=not isboss(sender)) as conv:

@unbreakable_async_decorator
async def viewnote(conv: Conversation):
    ind = id_to_ind[get_id(conv)]
    msg = "Какую записку хотел бы посмотреть?\n"
    i = -1
    buttons = []
    prev_message = None
    while -i <= len(notes[users[ind].par]):
        parse = users[notes[users[ind].par][i].student].name
        parse = parse.split()
        if len(parse) == 2:
            parse = parse[0] + ' ' + parse[1][0] + '.'
        else:
            parse = ' '.join(parse)
        msg += '{}. {} от {}\n'.format(-i, notes[users[ind].par][i].header, parse)
        buttons.append(-i)
        if len(buttons) == 10 or -i == len(notes[users[ind].par]):
            buttons.append('Назад')
            buttons.append("Вперед")
            bts = [Button.text(str(el), single_use=True) for el in buttons]
            bts = [bts[i : i + 4] for i in range(0, len(bts), 4)]
            if prev_message is None:
                prev_message = await conv.send_message(msg, buttons = bts)
            else:
                await prev_message.delete(revoke=True)
                prev_message = await conv.send_message(msg, buttons = bts)
            res = (await conv.get_response()).message
            if res.isnumeric():
                res = int(res)
                if res not in buttons:
                    await conv.send_message('Ban')
                    return
                await notes[users[ind].par][-res].show(conv)
                return
            elif res[0] == 'Н':
                i = min(i + 19, -1)
            else:
                i -= 1
            buttons = []
            msg = ''
        else:
            i -= 1
    await conv.send_message('Записки кончились')

@unbreakable_async_decorator
async def addnote(conv: Conversation):
    ind = id_to_ind[await get_id(conv)]
    await conv.send_message('Для начала озаглавь ее')
    header = await conv.get_response()
    header = header.message
    note = await get_msg_group(conv, 'Хрш, а теперь скидывай саму записку. В конце, как всегда, /end')
    notes[users[ind].par].append(Note(header, note, ind))
    writefile(notes_storage, notes)
    res = await send_inline_message(conv,
                              "Готово. Хочешь отправить уведомление о ней всем одноклассникам?",
                              ['Да', "Нет"],
                              30,
                              edited_message=["Ща сделаем", 'Оки'])
    if res is not None and res == 0:
        cant = []
        for us in users:
            if isinstance(us, Student) and us.par == users[ind].par:
                try:
                    await client.send_message(us.tg_id, 'Появилась новая записка от {}'.format(users[ind].name))
                except:
                    cant.append(us.name)
        if cant:
            message = 'Не смог отправить:\n'
            for el in cant:
                message += el + '\n'
            await conv.send_message(message)
        else:
            await conv.send_message('Успешно отправлено всем')


@unbreakable_async_decorator
async def get_msg_group(conv: Conversation, msg: MessageLike) -> Union[List[Tuple[Any, Any]], int]:
    await conv.send_message(msg)
    task_part = await conv.get_response()
    messages = []
    while task_part.message != '/end':
        messages.append((task_part.message, task_part.media))
        print(task_part.media)
        task_part = await conv.get_response()
    return messages


@unbreakable_async_decorator
async def addtask_student(conv: Conversation) -> None:
    sender = (await conv.get_chat()).id
    parr = users[id_to_ind[sender]].par
    subject = await get_subject(parr, conv)
    possible_days = rasp[parr].find_next(subject, 4)
    cur_day = datetime.date.today()
    possible_days = [cur_day + datetime.timedelta(days=el) for el in possible_days]
    ui = [str(el)[5:] for el in possible_days]
    day = await send_inline_message(conv, 'На какой день?', ui, max_per_row=4)
    pointer = 0
    if (not home_tasks[parr][subject].history) or (home_tasks[parr][subject].history[-1].deadline < possible_days[day]):
        if not home_tasks[parr][subject].history:
            pos = 0
        else:
            pos = possible_days.index(home_tasks[parr][subject].history[-1].deadline)
            pos += 1
        for i in range(pos, day + 1):
            print(i)
            home_tasks[parr][subject].history.append(Task(possible_days[i]))
        pointer = -1
    else:
        for i in range(len(home_tasks[parr][subject].history)):
            if home_tasks[parr][subject].history[i].deadline == possible_days[day]:
                pointer = i
                break
    await home_tasks[parr][subject].history[pointer].show(conv)
    result = await send_inline_message(conv, 'Выбери функцию', ['Заменить', 'Добавить', 'Ничего'])
    if result == 0:
        messages = await get_msg_group(conv, 'Скидывай сообщения. Как только закончишь - напиши /end')
        home_tasks[parr][subject].history[pointer] = Task(possible_days[day], messages, id_to_ind[sender])
        writefile(home_task_storage, home_tasks)
        await conv.send_message('Спасибо, сохранил!')
    elif result == 1:
        messages = await get_msg_group(conv, 'Скидывай сообщения. Как только закончишь - напиши /end')
        home_tasks[parr][subject].history[pointer] = Task(possible_days[day],
                                                          home_tasks[parr][subject].history[pointer].messages + messages,
                                                          id_to_ind[sender])
        writefile(home_task_storage, home_tasks)
        await conv.send_message('Спасибо, сохранил!')
    else:
        await conv.send_message("OK")

async def addtask_teacher(conv: Conversation) -> None:
    teacher = users[id_to_ind[sender]]
    # teacher = User.Teacher(boss, 'Сеня', 'Сеней', ['11Б', "11В"], ['phy', 'ast'])
    async with client.conversation(sender, timeout=None, exclusive=not isboss(sender)) as conv:
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
                home_tasks[parr][subj].history.append(
                    MsgGroup(
                        messages, id_to_ind[sender], datetime.datetime.now()
                    )
                )
                if len(home_tasks[parr][subj].history) > 4:
                    home_tasks[parr][subj].history.pop(0)
        writefile(home_task_storage, home_tasks)
        await conv.send_message('Готово!')


@client.on(events.NewMessage(pattern='/getsol', func=is_student))
@unbreakable_async_decorator
async def getsol(event) -> None:
    sender = (await event.get_chat()).id
    async with client.conversation(sender, timeout=None, exclusive=not isboss(sender)) as conv:
        parr = users[id_to_ind[sender]].par
        subject = await get_subject(parr, conv)
        if not subject:
            return
        await show_sol(parr, subject, conv)





@client.on(events.NewMessage(pattern='/menu', func=is_student))
@unbreakable_async_decorator
async def menu(event) -> None:
    sender = (await event.get_chat()).id
    async with client.conversation(sender, timeout=None, exclusive=not isboss(sender)) as conv:
        if False and await is_teacher(event):
            result = await send_inline_message(conv, 'Choose your Destiny', buttons=teacher_functions, max_per_row=1)
        else:
            result = await send_inline_message(conv, 'Choose your Destiny', buttons=student_functions, max_per_row=1)
            if result == 0:
                # await tomorrow(conv)
                pass
            elif result == 1:
                await gettask(conv)
            elif result == 2:
                await addtask_student(conv)
            elif result == 6:
                await addnote(conv)
            elif result == 7:
                await viewnote(conv)

@unbreakable_async_decorator
async def addsol(event) -> None:
    sender = (await event.get_chat()).id
    if is_student(event):
        parr = users[id_to_ind[sender]].par
        async with client.conversation(sender, timeout=None, exclusive=not isboss(sender)) as conv:
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
