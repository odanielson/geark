
import logging

import gevent

log = logging.getLogger("GreenletManager")

class GreenletAlreadyExistsError(Exception):
    pass

class GreenletManager(object):

    def __init__(self):
        self.greenlets = {}

    def start_greenlet(self, key, parent, auto_restart, function,
                       *args, **kwargs):

        if key in self.greenlets:
            raise GrennletAlreadyExistsError(
                "Greenlet with key %s already exists." % (key))

        self.greenlets[key] = {
            "greenlet": gevent.spawn(function, *args, **kwargs),
            "children": [],
            "auto_restart": auto_restart,
            "restart_count": 0
            }
        log.info("Started greenlet %s" % key)

    def list_greenlets(self):
        """Returns a list with greenlet keys."""
        return self.greenlets.keys()

    def stop_greenlet(self, key):

        greenlet = self.greenlets.get(key)
        if greenlet:
            gevent.kill(greenlet["greenlet"])
            del self.greenlets[key]
            log.info("Stopped greenlet %s" % key)


instance = GreenletManager()
