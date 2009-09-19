#!/usr/bin/env python
import logging
import logging.handlers

def setup_log(logfile):
    if len(logging.getLogger('').handlers) == 0:
        handler = logging.handlers.RotatingFileHandler(
            logfile, maxBytes=500000, backupCount=2)
        handler.setLevel(logging.DEBUG)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(asctime)s %(name)-20s: %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)

        # add the handler to the root logger
        logging.getLogger('').addHandler(handler)
        logging.getLogger('MARKDOWN').setLevel(logging.INFO)
        #logging.getLogger('eveapi').setLevel(logging.INFO)
        logging.set_up_done=True
        logging.debug("Logging started.")
