from classesnfunctions import *

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
async def getsol(conv) -> None:
    sender = (await conv.get_chat()).id
    parr = users[id_to_ind[sender]].par
    subject = await get_subject(parr, conv)
    await show_sol(parr, subject, conv)

@unbreakable_async_decorator
async def add_sol(event) -> None:
    sender = (await event.get_chat()).id
    if is_student(event):
        parr = users[id_to_ind[sender]].par
        async with client.conversation(sender, timeout=None, exclusive=not isboss(sender)) as conv:
            subject = await get_subject(parr, conv)
            if not subject:
                return
            await show_sol(parr, subject, conv)
            result = await send_inline_message(conv, 'Выбери функцию', ['Заменить', 'Добавить', 'Ничего'])
            if result == 0:
                messages = await get_msg_group(conv, 'Скидывай сообщения. Как только закончишь - напиши /end')
                home_tasks[parr][subject].history[pointer] = Task(possible_days[day], messages, id_to_ind[sender])
                writefile(home_task_storage, home_tasks)
                await conv.send_message('Спасибо, сохранил!')
            elif result == 1:
                messages = await get_msg_group(conv, 'Скидывай сообщения. Как только закончишь - напиши /end')
                home_tasks[parr][subject].history[pointer] = Task(possible_days[day],
                                                                  home_tasks[parr][subject].history[
                                                                      pointer].messages + messages,
                                                                  id_to_ind[sender])
                writefile(home_task_storage, home_tasks)
                await conv.send_message('Спасибо, сохранил!')
            else:
                await conv.send_message("OK")
