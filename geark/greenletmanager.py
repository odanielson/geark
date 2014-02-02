"""greenletmanager is part of the geark library and is responsible for
managing greenlets.

https://github.com/odanielson/geark
Copyright 2014, odanielson@github.com
MIT-license
"""

import logging
import traceback

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
        """Runs a greenlet and takes care of autorestart."""
        while True:
            try:
                function(*args, **kwargs)
                log.warning("greenlet \"%s\" stopped gracefully." % key)
            except Exception as e:
                log.warning("greenlet \"%s\" crashed: %s\n"
                            "---- stacktrace ----\n%s\n"
                            "---- end of stacktrace ----" %
                            (key, e, traceback.format_exc()))

            if not auto_restart:
                break

            log.info("restarting greenlet \"%s\"" % key)
        del self.greenlet_map[key]

    def _add_to_parent(self, key):
        """Add key as child for the current running greenlet if it is known
        to the greenletmanager.
        """
        parent = gevent.getcurrent()
        for parent_key in (key for key, item in
                           self.greenlet_map.iteritems() if (
                item.get("greenlet") == parent)):
            self.greenlet_map[parent_key]["children"].append(key)

    def _remove_from_parent(self, key):
        """Remove key from parents where it exist."""
        for children in (item["children"] for item in
                         self.greenlet_map.values() if (
                key in item.get("children"))):
            children.remove(key)

    def start_greenlet(self, key, auto_restart, function, *args, **kwargs):
        """Start function with *args and **kwargs as an greenlet.
        The greenlet is registered in the greenletmanager with identifier key.

        auto_restart specifies whether the function should be recalled
        whenever is stop or crashes.

        raise: GreenletAlreadyExistsError if the key already exists
        """
        if key in self.greenlet_map:
            raise GreenletAlreadyExistsError(
                "Greenlet \"%s\" already exists." % (key))

        self._add_to_parent(key)
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
                    "restart_count": greenlet["restart_count"],
                    "children": greenlet["children"]}
        else:
            raise GreenletNotFoundError("Greenlet \"%s\" not found." % key)

    def stop_greenlet(self, key):
        """Stop greenlet given by key

        raise: GreenletNotFoundError if greenlet does not exist.
        """
        greenlet = self.greenlet_map.get(key)
        if greenlet:
            self._remove_from_parent(key)
            for child in greenlet["children"]:
                self.stop_greenlet(child)
            gevent.kill(greenlet["greenlet"])
            del self.greenlet_map[key]
            log.info("Stopped greenlet \"%s\"" % key)
        else:
            raise GreenletNotFoundError("Greenlet \"%s\" not found." % key)

instance = GreenletManager()
