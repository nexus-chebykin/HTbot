from classesnfunctions import *

@unbreakable_async_decorator
async def show_sol(parr: str, subject: str, conv: Conversation) -> None:
    await conv.send_message('На данный момент решение выглядит так:')
    if isinstance(solutions[parr][subject], MsgGroup) and solutions[parr][subject].messages:
        for el in solutions[parr][subject].messages:
            await conv.send_message(message=el[0], file=el[1])
        await transuction(conv,
                    id_to_ind[await get_id(conv)],
                    solutions[parr][subject].student,
                    "Последний раз оно было изменено {} {}".format(
                        users[solutions[parr][subject].student].name_by,
                        str(solutions[parr][subject].timestamp)[:-10]),
                    )
    else:
        await conv.send_message('*Пусто*')

@unbreakable_async_decorator
async def getsol(conv) -> None:
    sender = await get_id(conv)
    parr = users[id_to_ind[sender]].par
    subject = await get_subject(parr, conv)
    await show_sol(parr, subject, conv)

@unbreakable_async_decorator
async def add_sol(conv) -> None:
    sender = await get_id(conv)
    parr = users[id_to_ind[sender]].par
    subject = await get_subject(parr, conv)
    await show_sol(parr, subject, conv)
    result = await send_inline_message(conv, 'Выбери функцию', ['Заменить', 'Добавить', 'Ничего'])
    if result == 0:
        messages = await get_msg_group(conv, 'Скидывай сообщения. Как только закончишь - напиши /end')
        solutions[parr][subject] = MsgGroup(messages, id_to_ind[sender])
        writefile(solution_storage, solutions)
        await conv.send_message('Спасибо, сохранил!')
    elif result == 1:
        messages = await get_msg_group(conv, 'Скидывай сообщения. Как только закончишь - напиши /end')
        solutions[parr][subject] = MsgGroup(solutions[parr][subject].messages + messages,
                                                          id_to_ind[sender])
        writefile(solution_storage, solutions)
        await conv.send_message('Спасибо, сохранил!')
    else:
        await conv.send_message("OK")
