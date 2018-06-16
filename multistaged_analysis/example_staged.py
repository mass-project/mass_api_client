import asyncio
from random import randint
from time import gmtime, strftime

from multistaged_analysis.staged_analysis import AnalysisFrame


async def func0(sockets):
    await asyncio.sleep(1)
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())


async def func1(sockets):
    temp = await sockets.receive()
    return temp + ' greetings from 1'


async def func2(sockets):
    temp = await sockets.receive()
    return temp + ' greetings from 2'


async def func3(sockets):
    temp = await sockets.receive()
    if randint(0, 1) == 0:
        await sockets.send(temp, 2)
    else:
        print('func3: ', temp)


if __name__ == '__main__':
    frame = AnalysisFrame(
        ["tcp://127.0.0.1:5559", "tcp://127.0.0.1:5560", "tcp://127.0.0.1:5561", "tcp://127.0.0.1:5562",
         "tcp://127.0.0.1:5563", "tcp://127.0.0.1:5564", "tcp://127.0.0.1:5565", "tcp://127.0.0.1:5566"])
    frame.add_stage(func0, 0, 1)
    frame.add_stage(func1, 1, 1)
    frame.add_stage(func2, 2, 2)
    frame.add_stage(func3, 3, 2)
    frame.start_all_stages()
