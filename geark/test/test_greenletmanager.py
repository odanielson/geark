
#import logging
#logging.basicConfig(level=logging.DEBUG)
import unittest

import gevent
from gevent.queue import Queue, Empty

from geark import greenletmanager


class GreenletManagerHappyPathTestCase(unittest.TestCase):

    def setUp(self):
        self.ping = Queue()
        self.pong = Queue()

    def _release_context(self, dt=0):
        gevent.sleep(dt)

    def test_starting_greenlet(self):
        """Verify that a greenlet can be started."""

        def loop(queue):
            queue.put("hello")

        greenletmanager.instance.start_greenlet(
            "testloop", None, False, loop, self.ping)
        self._release_context()

        msg = self.ping.get()
        self.assertEquals(msg, "hello")

    def test_stopping_greenlet(self):
        """Verify that a greenlet can be stopped."""

        def ping_pong(ping, pong):
            while True:
                msg = ping.get()
                pong.put(msg)

        greenletmanager.instance.start_greenlet(
            "pingpongloop", None, False, ping_pong, self.ping, self.pong)
        self._release_context()

        self.ping.put("hello")
        self.assertEquals("hello", self.pong.get())

        greenletmanager.instance.stop_greenlet("pingpongloop")

        self.ping.put("hello again")
        self.assertRaises(Empty, self.pong.get, timeout=0.01)

    def test_graceful_stopping_greenlet_restarts(self):
        """Verify that a greenlet that stops gracefully is restarted."""

        def stopping_ping_pong(ping, pong):
            msg = ping.get()
            pong.put(msg)

        greenletmanager.instance.start_greenlet(
            "stoppingpingpongloop", None, True, stopping_ping_pong, self.ping,
            self.pong)
        self._release_context()

        self.ping.put("hello")
        self.assertEquals("hello", self.pong.get())

        # The first ping-pong stopped the greenlet,
        # so let's make sure it's up again!

        self.ping.put("hello")
        self.assertEquals("hello", self.pong.get())

    def test_crashing_greenlet_restarts(self):
        """Verify that a greenlet that crashes is restarted."""

        def crashing_ping_pong(ping, pong):
            msg = ping.get()
            pong.put(msg)
            raise Exception("Crash bing bong!")

        greenletmanager.instance.start_greenlet(
            "crashingpingpongloop", None, True, crashing_ping_pong, self.ping,
            self.pong)
        self._release_context()

        self.ping.put("hello")
        self.assertEquals("hello", self.pong.get())

        # The first ping-pong stopped the greenlet,
        # so let's make sure it's up again!

        self.ping.put("hello")
        self.assertEquals("hello", self.pong.get())

        greenletmanager.instance.stop_greenlet("crashingpingpongloop")

    def test_list_greenlets(self):
        """Verify that list_greenlets returns the of running greenlets."""
        def stopping_loop():
            pass

        def running_loop():
            while True:
                gevent.sleep(0.1)

        greenletmanager.instance.start_greenlet(
            "stoppingloop", None, False, stopping_loop)

        greenletmanager.instance.start_greenlet(
            "runningloop1", None, False, running_loop)

        greenletmanager.instance.start_greenlet(
            "runningloop2", None, False, running_loop)

        self._release_context()
        greenlets = greenletmanager.instance.list_greenlets()
        self.assertTrue("runningloop1" in greenlets)
        self.assertTrue("runningloop2" in greenlets)
        self.assertFalse("stoppingloop" in greenlets)
