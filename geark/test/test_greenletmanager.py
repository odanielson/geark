
import logging
import unittest

import gevent
from gevent.queue import Queue

from geark import greenletmanager

class GreenletManagerHappyPathTestCase(unittest.TestCase):

    def _release_context(self, dt=0):
        gevent.sleep(dt)

    def test_starting_greenlets(self):
        logging.basicConfig(level=logging.DEBUG)

        queue = Queue()
        def loop(queue):
            queue.put("hello")


        greenletmanager.instance.start_greenlet(
            "testloop", None, False, loop, queue)
        self._release_context()

        msg = queue.get()
        self.assertEquals(msg, "hello")
