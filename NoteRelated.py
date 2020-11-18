from classesnfunctions import *

@unbreakable_async_decorator
async def viewnote(conv: Conversation):
    ind = id_to_ind[await get_id(conv)]
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
            if isinstance(us, Student) and us.par == users[ind].par and us.tg_id != await get_id(conv):
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

async def mynotes(conv: Conversation):
    ind = id_to_ind[await get_id(conv)]
    user = users[ind]
    res = 'Твои записки:\n'
    pos = []
    cnt = 1
    for i in range(len(notes[user.par])):
        if notes[user.par][i].student == ind:
            res += '{}. {}\n'.format(cnt, notes[user.par][i].header)
            pos.append(i)
            cnt += 1
    if pos:
        await conv.send_message(res)
        await conv.send_message("Какую хочешь поменять? (Номер, я же их не просто так нумеровал 😡😡😡😡😡)")
        resp = (await conv.get_response()).message
        try:
            pos = pos[int(resp) - 1]
        except:
            await conv.send_message('Что-то пошло не так.')
        await conv.send_message('Вот она:')
        await notes[user.par][pos].show(conv)
        res = await send_inline_message(conv, "Что хочешь с ней сделать?", ["Изменить", "Переоповестить", "Ничего"])
        if res is not None and res == 0:
            tmp = await get_msg_group(conv, 'Скидывай ее новый вид. В конце, как всегда, /end')
            notes[users[ind].par][pos] = Note(notes[users[ind].par][pos].header, tmp, ind)
            writefile(notes_storage, notes)
            await conv.send_message('OK')
        elif res == 1:
            await conv.send_message("Допустим... За злоупотребление и бан можно получить")
            cant = []
            for us in users:
                if isinstance(us, Student) and us.par == users[ind].par and us.tg_id != await get_id(conv):
                    try:
                        await client.send_message(us.tg_id, 'Просят посмотреть старую записку от {}'.format(users[ind].name))
                    except:
                        cant.append(us.name)
            if cant:
                message = 'Не смог отправить:\n'
                for el in cant:
                    message += el + '\n'
                await conv.send_message(message)
            else:
                await conv.send_message('Успешно отправлено всем')
        else:
            await conv.send_message('OK')
    else:
        await conv.send_message("Ты еще не создавал ни одной!")

@unbreakable_async_decorator
async def addnote_teacher(conv: Conversation):
    ind = id_to_ind[await get_id(conv)]
    teacher: Teacher = users[ind]
    # teacher = Teacher(boss, 'Сеня', 'Сеней', ['11Б', "11В"], ['phy', 'ast'])
    if len(teacher.classes) > 1:
        par = teacher.classes[await send_inline_message(conv, 'Для какого она класса?', teacher.classes)]
    else:
        par = teacher.classes[0]
    await conv.send_message('Озаглавьте ее')
    header = await conv.get_response()
    header = header.message
    note = await get_msg_group(conv, 'Ок, а теперь скидывайте саму записку. В конце, как всегда, /end')
    notes[par].append(Note(header, note, ind))
    writefile(notes_storage, notes)
    res = await send_inline_message(conv,
                              "Готово. Хотите отправить уведомление о ней всем в этом классе?",
                              ['Да', "Нет"],
                              30,
                              )
    if res is not None and res == 0:
        cant = []
        for us in users:
            if isinstance(us, Student) and us.par == par:
                try:
                    await client.send_message(us.tg_id, 'Появилась новая записка от {}'.format(teacher.name))
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
async def mynotes_teacher(conv: Conversation):
    ind = id_to_ind[await get_id(conv)]
    teacher = users[ind]
    # teacher = Teacher(boss, 'Сеня', 'Сеней', ['11Б', "11В"], ['phy', 'ast'])
    if len(teacher.classes) > 1:
        par = teacher.classes[await send_inline_message(conv, 'Для какого она предназначалась класса?', teacher.classes)]
    else:
        par = teacher.classes[0]
    res = 'Ваши записки:\n'
    pos = []
    cnt = 1
    for i in range(len(notes[par])):
        if notes[par][i].student == ind:
            res += '{}. {}\n'.format(cnt, notes[par][i].header)
            pos.append(i)
            cnt += 1
    if pos:
        await conv.send_message(res)
        await conv.send_message("Какую хотите поменять? (Номер)")
        resp = (await conv.get_response()).message
        try:
            pos = pos[int(resp) - 1]
        except:
            await conv.send_message('Что-то пошло не так.')
        await conv.send_message('Вот она:')
        await notes[par][pos].show(conv)
        res = await send_inline_message(conv, "Что хотите с ней сделать?", ["Изменить", "Переоповестить", "Ничего"])
        if res is not None and res == 0:
            tmp = await get_msg_group(conv, 'Скидывай ее новый вид. В конце, как всегда, /end')
            notes[par][pos] = Note(notes[par][pos].header, tmp, ind)
            writefile(notes_storage, notes)
            await conv.send_message('OK')
        elif res == 1:
            await conv.send_message('OK')
            cant = []
            for us in users:
                if isinstance(us, Student) and us.par == par:
                    try:
                        await client.send_message(us.tg_id, 'Просят посмотреть старую записку от {}'.format(users[ind].name))
                    except:
                        cant.append(us.name)
            if cant:
                message = 'Не смог отправить:\n'
                for el in cant:
                    message += el + '\n'
                await conv.send_message(message)
            else:
                await conv.send_message('Успешно отправлено всем')
        else:
            await conv.send_message('OK')
    else:
        await conv.send_message("Вы еще не создавали ни одной!")