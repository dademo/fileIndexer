import queue

_queue = None

def getAppInputQueue(maxsize: int = 10) -> queue.Queue:

    global _queue

    if _queue == None:
        _queue = queue.Queue(maxsize=maxsize)

    return queue
