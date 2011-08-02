from collections import defaultdict
import traceback

class Hookable(object):
    def __init__(self):
        self.hooks = defaultdict(list)

    def addhook(self, name, func, *args, **kwargs):
        name = name.upper()

        if callable(func):
            self.hooks[name].append([func, args, kwargs])

    def delhook(self, name, func):
        name = name.upper()

        if func in self.hooks[name]:
            self.hooks[name].remove(func)

    def firehook(self, name, *args):
        name = name.upper()

        if name in self.hooks:
            for hookdata in self.hooks[name]:
                hook, hargs, hkwargs = hookdata
                
                try:
                    hook(*(args+hargs), **hkwargs)
                except Exception:
                    traceback.print_exc(5)

        for hookdata in self.hooks["*"]:
            hook, hargs, hkwargs = hookdata

            try:
                hook(name, *(args+hargs), **hkwargs)
            except Exception:
                traceback.print_exc(5)
