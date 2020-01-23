# -*- coding: utf-8 -*-
'''
from resources.lib import kodilogging
from resources.lib import service
from resources.lib import kodiutils

import logging
import xbmcaddon

# Keep this file to a minimum, as Kodi
# doesn't keep a compiled copy of this
ADDON = xbmcaddon.Addon()
kodilogging.config()
kodiutils.notification("Edem.tv parser", "Launching the app", time=5000, icon=ADDON.getAddonInfo('icon'), sound=True)
service.parse()
service.loop()
'''
from resources.lib import kodilogging
from resources.lib import service
from resources.lib import kodiutils
import time


if __name__ == '__main__':
    service.doLog("Starting EDEM.tv Playlist Parser Addon", "DEBUG")
    parser = service.Parser()
    parser.run()


    monitor = service.Monitor()
    while not monitor.abortRequested():
       # Sleep/wait for abort for timer seconds
       timer = kodiutils.get_setting_as_int("timer")*60
       service.doLog("Timer is set to %d" %timer, "DEBUG")
       if monitor.waitForAbort(timer):
           # Abort was requested while waiting. We should exit
           del parser
           break
       #service.xbmc.log("hello addon! %s" % time.time(), level=service.xbmc.LOGNOTICE)
       service.doLog("hello addon! %s" % time.time(), "DEBUG")
       parser.run()
       kodiutils.notification("Edem.tv parser",
                              "WORK",
                              time=5, icon=monitor.addon.getAddonInfo('icon'),
                              sound=True)



