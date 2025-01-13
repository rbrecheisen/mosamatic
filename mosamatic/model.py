import time

from multiprocessing import Process, Queue


class AppModel:
    def __init__(self, root):
        self.root = root
        
    def run_task(self, callback):
        queue = Queue()
        process = Process(target=task_func, args=(queue,))
        process.start()

        def poll_queue():
            try:
                while not queue.empty():
                    progress = queue.get_nowait()
                    callback(progress)
                if process.is_alive() or not queue.empty():
                    self.root.after(100, poll_queue)
            except Exception as e:
                print("Error:", e)

        poll_queue()


def task_func(queue):
    for i in range(1, 6):
        time.sleep(1)
        queue.put(i * 20)
