from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection
import matplotlib
from matplotlib import pyplot
from time import sleep
from enum import Enum
import marshal
import types
import time

class Action(Enum):
    CREATE = 0
    CALL_METHOD_ASSIGN = 1
    CALL_METHOD_NOASSIGN = 2
    CALL_METHOD_DROPASSIGN = 3
    DELETE = 4
    STOP = 5
    FUNCTION = 6

class ProxyId:

    def __init__(self, _id):
        self._id = _id

class ProxyObject:

    def __init__(self, conn: Connection, _id):
        self.conn: Connection = conn
        self._id = _id

    @staticmethod
    def create(conn: Connection, obj):
        conn.send((Action.CREATE, obj))
        return ProxyObject(conn, conn.recv())

    def callmethod_assign(self, name: str, *args, **kwargs):
        args = [ProxyId(a._id) if isinstance(a, ProxyObject) else a for a in args]
        kwargs = {key: ProxyId(a._id) if isinstance(a, ProxyObject) else a for key, a in kwargs.items()}
        self.conn.send((Action.CALL_METHOD_ASSIGN, self._id, name, args, kwargs))
        obj = self.conn.recv()
        if isinstance(obj, Exception):
            raise obj
        else:
            return ProxyObject(self.conn, obj)

    def callmethod_noassign(self, name: str, *args, **kwargs):
        args = [ProxyId(a._id) if isinstance(a, ProxyObject) else a for a in args]
        kwargs = {key: ProxyId(a._id) if isinstance(a, ProxyObject) else a for key, a in kwargs.items()}
        self.conn.send((Action.CALL_METHOD_NOASSIGN, self._id, name, args, kwargs))
        obj = self.conn.recv()
        if isinstance(obj, Exception):
            raise obj
        else:
            return obj

    def callmethod_dropassign(self, name: str, *args, **kwargs):
        args = [ProxyId(a._id) if isinstance(a, ProxyObject) else a for a in args]
        kwargs = {key: ProxyId(a._id) if isinstance(a, ProxyObject) else a for key, a in kwargs.items()}
        self.conn.send((Action.CALL_METHOD_NOASSIGN, self._id, name, args, kwargs))

    def __del__(self):
        if not self.conn.closed:
            self.conn.send((Action.DELETE, self._id))

    def __repr__(self):
        return f'ProxyObject({self.callmethod_noassign("__repr__")})'

    def __next__(self):
        return self.callmethod_assign('__next__')

    def __iter__(self):
        return self.callmethod_assign('__iter__')

    def __getattribute__(self, name):
        if name in ['conn', '_id'] or name in ProxyObject.__dict__:
            return object.__getattribute__(self, name)

        def method(*args, **kwargs):
            return self.callmethod_assign(name, *args, **kwargs)

        return method


class MplProc:

    def __init__(self):
        parent_conn, child_conn = Pipe()
        self.conn = parent_conn
        self.proxy_fig = ProxyObject(self.conn, 'fig')
        self.proxy_ax = ProxyObject(self.conn, 'ax')
        self.proc = Process(target=self.foo, args=(child_conn,))

    def __del__(self):
        self.stop()

    def start(self):
        self.proc.start()

    def stop(self):
        self.conn.send((Action.STOP,))
        self.conn.close()
        self.proc.join()

    def new_proxy(self, ini):
        return ProxyObject.create(self.conn, ini)

    def call_function(self, func, *args, **kwargs):
        self.conn.send((Action.FUNCTION, marshal.dumps(func.__code__), args, kwargs))

    def foo(self, conn: Connection):
        fig: matplotlib.figure.Figure
        ax: matplotlib.axes.Axes
        fig, ax = pyplot.subplots()
        pyplot.show(block=False)
        objs = {'fig': fig, 'ax': ax}
        running = True
        while running:
            drawn = False
            while conn.poll():
                drawn = True
                action, *rest = conn.recv()
                if action == Action.STOP:
                    running = False
                    break
                elif action == Action.FUNCTION:
                    code, args, kwargs = rest
                    func = types.FunctionType(marshal.loads(code), globals(), 'func')
                    func(objs, *args, **kwargs)
                elif action == Action.CREATE:
                    newobj, = rest
                    objs[id(newobj)] = newobj
                    conn.send(id(newobj))
                elif action == Action.DELETE:
                    _id, = rest
                    del objs[_id]
                elif action == Action.CALL_METHOD_ASSIGN:
                    _id, method, args, kwargs = rest
                    args = (objs[a._id] if isinstance(a, ProxyId) else a for a in args)
                    kwargs = {key: objs[a._id] if isinstance(a, ProxyId) else a for key, a in kwargs.items()}
                    try:
                        newobj = getattr(objs[_id], method)(*args, **kwargs)
                    except Exception as ex:
                        conn.send(ex)
                    else:
                        objs[id(newobj)] = newobj
                        conn.send(id(newobj))
                elif action == Action.CALL_METHOD_NOASSIGN:
                    _id, method, args, kwargs = rest
                    args = (objs[a._id] if isinstance(a, ProxyId) else a for a in args)
                    kwargs = {key: objs[a._id] if isinstance(a, ProxyId) else a for key, a in kwargs.items()}
                    try:
                        newobj = getattr(objs[_id], method)(*args, **kwargs)
                    except Exception as ex:
                        conn.send(ex)
                    else:
                        conn.send(newobj)
                elif action == Action.CALL_METHOD_DROPASSIGN:
                    _id, method, args, kwargs = rest
                    args = (objs[a._id] if isinstance(a, ProxyId) else a for a in args)
                    kwargs = {key: objs[a._id] if isinstance(a, ProxyId) else a for key, a in kwargs.items()}
                    getattr(objs[_id], method)(*args, **kwargs)
            if not running:
                break

            if drawn:
                fig.canvas.draw()
                fig.canvas.flush_events()
            while not conn.poll():
                fig.canvas.flush_events()
                sleep(0.01)
