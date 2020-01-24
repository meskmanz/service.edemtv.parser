
from resources.lib import kodilogging
from resources.lib import service
from resources.lib import kodiutils
import time


if __name__ == '__main__':
    service.doLog("Starting EDEM.tv Playlist Parser Addon", "INFO")
    parser = service.Parser()
    parser.run()
    monitor = service.Monitor()
    kodiutils.notification("Edem.tv parser", "Starting Addon",
                           time=5000, icon=monitor.addon.getAddonInfo('icon'),
                           sound=True)
    while not monitor.abortRequested():
       # Sleep/wait for abort for timer seconds
       timer = kodiutils.get_setting_as_int("timer")*60
       service.doLog("Timer is set to %d" %timer, "DEBUG")
       if monitor.waitForAbort(timer):
           # Abort was requested while waiting. We should exit
           del parser
           break
       #service.xbmc.log("hello addon! %s" % time.time(), level=service.xbmc.LOGNOTICE)
       service.doLog("pareser.run loop at %s" % time.time(), "Restarting Addon")
       parser.run()




