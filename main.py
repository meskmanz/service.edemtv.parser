# -*- coding: utf-8 -*-

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


