from classesnfunctions import *

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
    if to_be_awaited is not None:
        await to_be_awaited


@unbreakable_async_decorator
async def gettask(conv: Conversation) -> None:
    sender = (await conv.get_chat()).id
    parr = users[id_to_ind[sender]].par
    subject = await get_subject(parr, conv)
    await show_task(parr, subject, conv, switch=True)

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

# @client.on(events.NewMessage(pattern='/tomorrow', func=is_student))
# @unbreakable_async_decorator
# async def gettomorow(event) -> None:
#     sender = (await event.get_chat()).id
#     async with client.conversation(sender, timeout=None, exclusive=not isboss(sender)) as conv:
