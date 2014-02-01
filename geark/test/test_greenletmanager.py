
import logging
import unittest

import gevent
from gevent.queue import Queue, Empty

from geark import greenletmanager


class GreenletManagerHappyPathTestCase(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def _release_context(self, dt=0):
        gevent.sleep(dt)

    def test_starting_greenlet(self):
        """Verify that a greenlet can be started."""
        queue = Queue()

        def loop(queue):
            queue.put("hello")

        greenletmanager.instance.start_greenlet(
            "testloop", None, False, loop, queue)
        self._release_context()

        msg = queue.get()
        self.assertEquals(msg, "hello")

    def test_stopping_greenlet(self):
        """Verify that a greenlet can be stopped."""

        ping = Queue()
        pong = Queue()

        def ping_pong(ping, pong):
            while True:
                msg = ping.get()
                pong.put(msg)

        greenletmanager.instance.start_greenlet(
            "pingpongloop", None, False, ping_pong, ping, pong)
        self._release_context()

        ping.put("hello")
        self.assertEquals("hello", pong.get())

        greenletmanager.instance.stop_greenlet("pingpongloop")

        ping.put("hello again")
        self.assertRaises(Empty, pong.get, timeout=0.01)
