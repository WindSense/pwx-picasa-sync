# -*- encoding: utf-8 -*-

import threading
from Queue import Queue

class ThreadPool:
    def __init__(self, worker_count, clients):
        # 记录参数
        self.worker_count = worker_count
        # 工作队列
        self.jobs = Queue()
        self.clients = {
            'POOL-%s'%i: clients[i] for i in range(0, worker_count)
        }
        # 结果存储
        self.jar = []
        self.jar_lock = threading.Lock()
        # 创建所有需要的线程
        self.workers = [
            threading.Thread(target = self._worker, name = 'POOL-%s' % i)
            for i in range(0, worker_count)
        ]
        for w in self.workers:
            w.setDaemon(True)
            w.start()
        
    def put_jar(self, obj):
        self.jar_lock.acquire_lock()
        self.jar.append(obj)
        self.jar_lock.release_lock()
        
    def _worker(self):
        while True:
            job = self.jobs.get()
            ret = job[0](self.clients[threading.current_thread().name], *job[1])
            if ret is not None:
                self.put_jar(ret)
            self.jobs.task_done()
            
    def make_job(self, proc, *args):
        self.jobs.put( (proc, args) )
        
    def wait(self):
        self.jobs.join()
            