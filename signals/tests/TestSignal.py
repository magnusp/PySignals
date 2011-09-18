from signals import Signal
from signals.tests import *
import unittest

class SignalTest(unittest.TestCase):
    def setUp(self):
        self.signal = Signal()

    def test_basic_construction_works(self):
        assert self.signal.add_once(simple_listener_returning_true) is None
        assert self.signal.num_listeners is 1

    def test_add_once_then_add_raises(self):
        self.signal = Signal()

        self.signal.add_once(simple_listener_returning_true)
        self.assertRaises(RuntimeError, self.signal.add, simple_listener_returning_true)

    def test_dispatch_no_listeners(self):
        self.signal.dispatch()

    def test_no_param_dispatch(self):
        self.signal.add(simple_listener_returning_true)
        self.signal.dispatch()

        self.assertRaises(TypeError, self.signal.dispatch, 1)
        self.assertRaises(TypeError, self.signal.dispatch, {'someKeyWord': 1})

    def test_no_param_dispatch_multiple_times(self):
        self.signal.add(simple_listener_returning_true)

        self.signal.dispatch()
        self.signal.dispatch()
        self.signal.dispatch()

    def test_add_once_only_fires_once(self):
        def mylistener(f):
            f.callcount = f.callcount + 1

        mylistener.callcount = 0
        self.signal.add_once(mylistener)
        self.signal.dispatch(mylistener)
        self.signal.dispatch(mylistener)

        self.assertEqual(mylistener.callcount, 1)

    def test_removed_listener_doesnt_fire(self):
        def mylistener(f):
            f.callcount = f.callcount + 1

        mylistener.callcount = 0
        self.signal.add(mylistener)
        self.signal.remove(mylistener)
        self.signal.dispatch(mylistener)

        self.assertEqual(mylistener.callcount, 0)

    def test_listener_added_twice_doesnt_duplicate(self):
        self.signal.add(simple_listener_returning_false)
        self.signal.add(simple_listener_returning_false)
        self.assertEqual(self.signal.num_listeners, 1)
        self.signal.dispatch()

    def test_adding_null_doesnt_add_listener(self):
        self.assertRaises(ValueError, self.signal.add, None)