from classesnfunctions import *



@unbreakable_async_decorator
async def show_task(parr: str, subject: str, conv: Conversation, switch: bool = False, shift = 0) -> None:
    '''
    Показывает задание на урок строго больше текущего
    '''
    # if shift == 0:
    ind_to_be_showed = -1
    cur_date = datetime.date.today()
    for ind in range(len(home_tasks[parr][subject].history)):
        if home_tasks[parr][subject].history[ind].deadline > cur_date:
            ind_to_be_showed = ind
            break
    else:
        await conv.send_message('*Пусто*')
    if ind_to_be_showed != -1:
        current_pos = ind_to_be_showed + shift
        to_be_awaited = await home_tasks[parr][subject].history[current_pos].show(conv)
    else:
        to_be_awaited = None
        current_pos = len(home_tasks[parr][subject].history) - shift
        for el in home_tasks[parr][subject].history:
            print(el.deadline, el.messages)
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
            if to_be_awaited is not None:
                await to_be_awaited
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
    possible_days = rasp[parr].find_next(subject[:3], 4) # ОСТОРОЖНО
    cur_day = datetime.date.today()
    possible_days = [cur_day + datetime.timedelta(days=el) for el in possible_days]
    ui = [str(el)[5:] for el in possible_days]
    day = await send_inline_message(conv, 'На какой день?', ui, max_per_row=4)
    pointer = 0
    if (not home_tasks[parr][subject].history) or (home_tasks[parr][subject].history[-1].deadline < possible_days[day]):
        if not home_tasks[parr][subject].history:
            pos = 0
        else:
            try:
                pos = possible_days.index(home_tasks[parr][subject].history[-1].deadline)
            except:
                pos = -1
            pos += 1
        for i in range(pos, day + 1):
            home_tasks[parr][subject].history.append(Task(possible_days[i]))
        pointer = -1
    else:
        for i in range(len(home_tasks[parr][subject].history)):
            if home_tasks[parr][subject].history[i].deadline == possible_days[day]:
                pointer = i
                break
    writefile(home_task_storage, home_tasks)
    to_be_awaited = await home_tasks[parr][subject].history[pointer].show(conv)
    result = await send_inline_message(conv, 'Выбери функцию', ['Заменить', 'Добавить', 'Ничего'])
    if result == 0:
        if isinstance(users[home_tasks[parr][subject].history[pointer].student], Teacher):
            await conv.send_message("Нельзя, его добавил учитель, можно только добавить.")
            return
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
    if to_be_awaited is not None:
        await to_be_awaited

@unbreakable_async_decorator
async def addtask_teacher(conv: Conversation) -> None:
    sender = await get_id(conv)
    teacher = users[id_to_ind[sender]]
    # teacher = Teacher(boss, 'Сеня', 'Сеней', ['11Б', "11В"], ['phy', 'ast'])
    async with client.conversation(sender, timeout=None, exclusive=not isboss(sender)) as conv:
        parr = 0 if len(teacher.classes) == 1 else (await send_inline_message(conv, 'Какому классу?', buttons=teacher.classes))
        if len(teacher.subjects) > 1:
            subject = teacher.subjects[await send_inline_message(conv, 'А по какому предмету?', teacher.subjects)]
        else:
            subject = teacher.subjects[0]
        parr = teacher.classes[parr]
        possible_days = rasp[parr].find_next(subject[:3], 4)  # ОСТОРОЖНО
        cur_day = datetime.date.today()
        possible_days = [cur_day + datetime.timedelta(days=el) for el in possible_days]
        ui = [str(el)[5:] for el in possible_days]
        day = await send_inline_message(conv, 'На какой день?', ui, max_per_row=4)
        pointer = 0
        if (not home_tasks[parr][subject].history) or (
                home_tasks[parr][subject].history[-1].deadline < possible_days[day]):
            if not home_tasks[parr][subject].history:
                pos = 0
            else:
                pos = possible_days.index(home_tasks[parr][subject].history[-1].deadline)
                pos += 1
            for i in range(pos, day + 1):
                home_tasks[parr][subject].history.append(Task(possible_days[i]))
            pointer = -1
        else:
            for i in range(len(home_tasks[parr][subject].history)):
                if home_tasks[parr][subject].history[i].deadline == possible_days[day]:
                    pointer = i
                    break
        writefile(home_task_storage, home_tasks)
        await conv.send_message(('Вы собираетесь добавить {} дз по {} на {}').format(parr, subject, ui[day]))
        messages = await get_msg_group(conv,
                                       "Скидывайте мне сообщения. После последнего напишите /end.")
        if messages:
                home_tasks[parr][subject].history[pointer] = Task(possible_days[day], messages, id_to_ind[sender])
        writefile(home_task_storage, home_tasks)
        await conv.send_message('Готово!')

@unbreakable_async_decorator
async def tomorrow(conv: Conversation) -> None:
    sender = await get_id(conv)
    ind = id_to_ind[sender]
    par = users[ind].par
    to_be_awaited = []
    today = datetime.date.today()
    for subj in set(rasp[par].timetable[today.weekday() + 1 if today.weekday() < 5 else 0].subjects):
        await conv.send_message("По {}".format(subj))
        if subj != 'eng':
            for el in home_tasks[par][subj].history:
                if el.deadline == today + datetime.timedelta(days=1):
                    to_be_awaited.append(await el.show(conv))
                    break
            else:
                await conv.send_message('*Пусто*')
        else:
            await conv.send_message("Первая группа")
            for el in home_tasks[par]['eng1'].history:
                if el.deadline == today + datetime.timedelta(days=1):
                    to_be_awaited.append(await el.show(conv))
                    break
            else:
                await conv.send_message('*Пусто*')
            await conv.send_message("Вторая группа")
            for el in home_tasks[par]['eng2'].history:
                if el.deadline == today + datetime.timedelta(days=1):
                    to_be_awaited.append(await el.show(conv))
                    break
            else:
                await conv.send_message('*Пусто*')
    for el in to_be_awaited:
        if el is not None:
            await el
