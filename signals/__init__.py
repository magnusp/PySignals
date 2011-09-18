import heapq

class Slot(object):
    def __init__(self, listener, signal, once=False, priority=0):
        super(Slot, self).__init__()
        self.signal = signal
        self.listener = listener
        self.once = once
        self.priority = priority

        self.enabled = True
        self.params = []

    def __cmp__(self, other):
        if self.priority < other.priority: return -1
        if self.priority == other.priority: return 0
        return 1

    def execute0(self):
        if not self.enabled: return
        if self.once: self.remove()
        if self.params and len(self.params):
            self.listener(*self.params)
            return
        self.listener()

    def execute1(self, value):
        if not self.enabled: return
        if self.once: self.remove()
        if self.params and len(self.params):
            params = [value] + self.params
            self.listener(*params)
            return
        self.listener(value)

    def execute(self, *args, **kwargs):
        if not self.enabled: return
        if self.once: self.remove()
        if self.params and len(self.params):
            valueObjects = valueObjects + self.params

        self.listener(*args, **kwargs)

    @property
    def listener(self):
        return self._listener

    @listener.setter
    def listener(self, listener):
        if listener is None: raise ValueError('Given listener is null. Did you want to set enabled to false instead?')
        self.verify_listener(listener)
        self._listener = listener

    def __str__(self):
        return "[Slot listener: %s, once: %s, priority %i, enabled: %s" % (
        self.listener, self.once, self.priority, self.enabled)

    def remove(self):
        self.signal.remove(self._listener)

    def verify_listener(self, listener):
        if listener is None: raise ValueError('Given listener is None')
        if self.signal is None: raise ValueError('Internal signal reference has not been set yet.')


class SlotList(set):
    def __init__(self, *args, **kwargs):
        super(SlotList, self).__init__(*args, **kwargs)

    def append(self, slot):
        return SlotList(list(self) + [slot])

    def prepend(self, slot):
        l = list(self)
        l = [slot] + l
        l = SlotList(l)
        return l

    def filter_not(self, listener):
        if not len(self) or listener is None: return self
        return SlotList([slot for slot in list(self) if slot.listener is not listener])

    def contains_listener(self, item):
        for i in list(self):
            if item is i.listener: return True
        return False

    def find(self, listener):
        for slot in list(self):
            if slot.listener is listener: return slot
        return None


class OnceSignal(object):
    value_classes = None
    slots = SlotList([])

    num_listeners = property(lambda self: len(self.slots))

    def __init__(self, *args, **kwargs):
        self.value_classes = args

    def add_once(self, listener):
        self.register_listener(listener, True)

    def remove(self, listener):
        slot = self.slots.find(listener)
        if not slot: return None

        self.slots = self.slots.filter_not(listener)
        return slot

    def remove_all(self):
        self.slots = SlotList()

    def dispatch(self, *args, **kwargs):
        l = list(self.slots)
        heapq.heapify(l)

        while len(l):
            heapq.heappop(l).execute(*args, **kwargs)

    def register_listener(self, listener, once=False):
        if self.registration_possible(listener, once):
            slot = Slot(listener, self, once)
            self.slots = self.slots.prepend(slot)

    def registration_possible(self, listener, once):
        if not len(self.slots): return True
        existing_slot = self.slots.find(listener)
        if existing_slot is None: return True

        if existing_slot.once is not once: raise RuntimeError(
            'You cannot addOnce() then add() the same listener without removing the relationship first.')
        return False


class Signal(OnceSignal):
    def add(self, listener):
        return self.register_listener(listener)