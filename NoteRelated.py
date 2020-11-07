from classesnfunctions import *

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
