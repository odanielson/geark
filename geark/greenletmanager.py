
import logging

import gevent

log = logging.getLogger("GreenletManager")


class GreenletAlreadyExistsError(Exception):
    pass


class GreenletNotFoundError(Exception):
    pass


class GreenletManager(object):

    def __init__(self):
        self.greenlet_map = {}

    def _run_greenlet(self, key, auto_restart, function, *args, **kwargs):

        while True:
            try:
                function(*args, **kwargs)
                log.warning("greenlet \"%s\" stopped gracefully." % key)
            except Exception as e:
                log.warning("greenlet \"%s\" crashed: %s" % (key, e))
                # TODO: dump a stacktrace here

            if not auto_restart:
                break

            log.info("restarting greenlet \"%s\"" % key)
        del self.greenlet_map[key]

    def start_greenlet(self, key, parent, auto_restart, function,
                       *args, **kwargs):

        if key in self.greenlet_map:
            raise GreenletAlreadyExistsError(
                "Greenlet \"%s\" already exists." % (key))

        self.greenlet_map[key] = {
            "greenlet": gevent.spawn(self._run_greenlet, key, auto_restart,
                                     function, *args, **kwargs),
            "children": [],
            "auto_restart": auto_restart,
            "restart_count": 0}
        log.info("Started greenlet \"%s\"" % key)

    def list_greenlets(self):
        """Returns a list with greenlet keys."""
        return self.greenlet_map.keys()

    def status(self, key):
        """Return a status dict for greenlet give by key.

        return: dict with status for greenlet
        raise: GreenletNotFoundError if greenlet for key does not exist."""
        greenlet = self.greenlet_map.get(key)
        if greenlet:
            return {"key": key,
                    "auto_restart": greenlet["auto_restart"],
                    "restart_count": greenlet["restart_count"]}
        else:
            raise GreenletNotFoundError("Greenlet \"%s\" not found." % key)

    def stop_greenlet(self, key):
        """Stop greenlet given by key

        raise: GreenletNotFoundError if greenlet does not exist.
        """
        greenlet = self.greenlet_map.get(key)
        if greenlet:
            gevent.kill(greenlet["greenlet"])
            del self.greenlet_map[key]
            log.info("Stopped greenlet \"%s\"" % key)
        else:
            raise GreenletNotFoundError("Greenlet \"%s\" not found." % key)

instance = GreenletManager()
