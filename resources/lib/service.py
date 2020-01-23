# -*- coding: utf-8 -*-

from resources.lib import kodiutils
from resources.lib import kodilogging
import subprocess
import xbmc
import xbmcaddon
import urllib2, re, os
from xml.dom import minidom
import time

ADDON = xbmcaddon.Addon()


class Monitor(xbmc.Monitor):

   def __init__(self, *args, **kwargs):
      xbmc.Monitor.__init__(self)
      self.addon = xbmcaddon.Addon()
      self.id = xbmcaddon.Addon().getAddonInfo('id')

   def onSettingsChanged(self):
       xbmc.log("settings changed")
      #subprocess.call([['systemctl',|'restart', self.id]])

def doLog(text, logLevel):
    levels = {
        "CRITICAL": xbmc.LOGFATAL,
        "ERROR": xbmc.LOGERROR,
        "WARNING": xbmc.LOGWARNING,
        "INFO": xbmc.LOGINFO,
        "DEBUG": xbmc.LOGDEBUG,
        "NOTSET": xbmc.LOGNONE,
    }
    try:
        xbmc.log("[ETVPP] "+text, levels[logLevel])
    except UnicodeEncodeError:
        xbmc.log("[ETVPP] "+text.encode(
            'utf-8', 'ignore'), levels[logLevel])


def getM3uUrlFromAddon():
    #TODO: Getting path using API
    path = os.path.join("C:\\Users\\Meskman\\AppData\\Roaming\\Kodi\\userdata\\addon_data\\pvr.iptvsimple",
                        "settings.xml")
    xmldoc = minidom.parse(path)
    itemlist = xmldoc.getElementsByTagName('setting')
    for item in itemlist:
        if item.attributes['id'].value == "m3uUrl":
            doLog("Getting M3U URL from PVR Addon: %s" %item.firstChild.data, "DEBUG")
            return item.firstChild.data


class Parser:

    def __init__(self):
        self.m3uUrl = ""

    def _getM3uUrl(self):
        if kodiutils.get_setting_as_bool("m3uUrlAddon"):
            m3uUrl = getM3uUrlFromAddon()
            if len(m3uUrl) == 0:
                doLog("m3uUrl is empty in PVR Addon", "ERROR")
                kodiutils.notification("Edem.tv parser",
                                       "Cannot get URL from PVR.SimpeIPTV. It's empty",
                                       time=5000, icon=ADDON.getAddonInfo('icon'),
                                       sound=True)
            else:
                self.m3uUrl = m3uUrl
        else:
            m3uUrl = kodiutils.get_setting("m3uUrl")
            if len(m3uUrl) == 0:
                doLog("m3uUrl is empty in settings", "ERROR")
                kodiutils.notification("Edem.tv parser",
                                       "Add  M3U URL in Settings",
                                       time=5000, icon=ADDON.getAddonInfo('icon'),
                                       sound=True)
            else:
                self.m3uUrl = m3uUrl

    def _get_m3u_playlist(self, m3uUrl):
        # Getting playlist from URL
        req = urllib2.Request(m3uUrl)
        req.add_header('User-Agent',
                       ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        data = response.read()
        return data

    def run(self):
        doLog("RUN FUNCTION START", "DEBUG")
        self._getM3uUrl()

        data = self._get_m3u_playlist(self.m3uUrl)
        #doLog("URL -, "DEBUG")


"""
def run():
    if kodiutils.get_setting_as_bool("m3uUrlAddon"):
        m3uUrl = getM3uUrlFromAddon()
    doLog("URL - %s" %m3uUrl, "DEBUG")

"""


"""
from resources.lib import kodiutils
from resources.lib import kodilogging
import logging
import time
import xbmc
import xbmcaddon
import urllib2
import re
import os
from xml.dom import minidom

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))


def loop():
    monitor = xbmc.Monitor()

    while not monitor.abortRequested():
        # Sleep/wait for abort for 10 seconds
        if kodiutils.get_setting_as_bool("debug"):
            kodiutils.notification("Edem.tv parser", "Debug :: Timer set to %d" % kodiutils.get_setting_as_int("timer"),
                                   time=5000, icon=ADDON.getAddonInfo('icon'),
                                   sound=True)
        if monitor.waitForAbort(kodiutils.get_setting_as_int("timer")):
            # Abort was requested while waiting. We should exit
            break


        logger.debug("Edem.tv.parser is launched parse function at %s" % time.time())
        parse()


def get_m3u_playlist(m3uUrl):
    # Getting playlist from URL
    req = urllib2.Request(m3uUrl)
    req.add_header('User-Agent',
                   ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    data = response.read()
    return data


def get_wishlist():
    # Getting wishlist
    path = os.path.join(kodiutils.get_setting("wlPath"), kodiutils.get_setting("wlFilename"))
    if kodiutils.get_setting("wlPath") == "":
        kodiutils.notification("Warning", "Please set a path where to store a wishlist", time=5000,
                               icon=ADDON.getAddonInfo('icon'), sound=True)
        path = os.path.join(xbmc.translatePath(ADDON.getAddonInfo('profile')), kodiutils.get_setting("wlFilename"))
    logger.debug(path)
    if os.path.exists(path):
        mode = 'r'
    else:
        mode = 'w+'
    with open(path, mode) as f:
        f_ch = f.read()
        return f_ch


def get_m3uUrl_from_addon():
    path = os.path.join("C:\\Users\\Meskman\\AppData\\Roaming\\Kodi\\userdata\\addon_data\\pvr.iptvsimple",
                        "settings.xml")
    xmldoc = minidom.parse(path)
    itemlist = xmldoc.getElementsByTagName('setting')
    for item in itemlist:
        if item.attributes['id'].value == "m3uUrl":
            return item.firstChild.data


def parse():
    logger.info("Edem.tv.parser is executed at %s" % time.time())
    # Showing debug notifications. Controlled by settings.
    if kodiutils.get_setting_as_bool("debug"):
        kodiutils.notification("Edem.tv parser", "Debug :: Check", time=5000, icon=ADDON.getAddonInfo('icon'),
                               sound=True)
    m3uUrl = kodiutils.get_setting("m3uUrl")
    """
"""
    # URL should be set in settings. Do nothing if empty and show notification
    if m3uUrl == "":
        m3uUrl = get_m3uUrl_from_addon()
        kodiutils.set_setting("m3uUrl", m3uUrl)
        if len(m3uUrl) == 0:
            kodiutils.notification("Warning", "Please set a Edem.tv M3U Play List URL", time=5000,
                               icon=ADDON.getAddonInfo('icon'), sound=True)
    else:
        """
"""    while len(m3uUrl) == 0:
        m3uUrl = get_m3uUrl_from_addon()
        if len(m3uUrl) == 0:
            kodiutils.notification("Warning", "Please set a Edem.tv M3U Play List URL", time=5000,
                                   icon=ADDON.getAddonInfo('icon'), sound=True)
        else:
            logger.debug("Setting up m3uUrl on Settings Page ")
            kodiutils.set_setting("m3uUrl", m3uUrl)
            continue
    else:
        data = get_m3u_playlist(m3uUrl)
        channels = {}
        f_ch = get_wishlist()
        # logger.debug(f_ch)
        match = re.finditer("(.*)\:(.*)", f_ch)
        for item in match:
            channels[item.group(1)] = item.group(2)
        # logger.debug(data)
        plylist_path = os.path.join(kodiutils.get_setting("m3uPath"), kodiutils.get_setting("m3uFilename"))
        if kodiutils.get_setting("m3uPath") == "":
            kodiutils.notification("Warning", "Please set a path where to store a playlist", time=5000,
                                   icon=ADDON.getAddonInfo('icon'), sound=True)
            plylist_path = os.path.join(xbmc.translatePath(ADDON.getAddonInfo('profile')),
                                        kodiutils.get_setting("m3uFilename"))
        logger.debug(plylist_path)
        if kodiutils.get_setting_as_bool("debug"):
            f_ch_list = open(os.path.join(kodiutils.get_setting("wlPath"), "channel_list.txt"), "w+")
        f = open(plylist_path, "w+")
        f.write("#EXTM3U\n")
        pattern = "(\#EXTINF\:0.*\,.*)\n(\#EXTGRP\:.*)\n(http\:\/\/.*)\n"
        match = re.finditer(pattern, data, re.M | re.I)
        for item in match:
            channel_name = item.group(1).replace("\r", "")
            channel_group = item.group(2).replace("\r", "")
            channel_link = item.group(3).replace("\r", "")
            write = True
            # print channel_name
            ch_code = channel_name.split(",")[0]
            ch_name = channel_name.split(",")[1]
            if kodiutils.get_setting_as_bool("debug"):
                logger.debug(ch_name + ":" + channel_group[8:] + '\n')
                f_ch_list.write(ch_name + ":" + channel_group[8:] + '\n')
            for key in channels:
                if ch_name == key:
                    logger.debug("%s is found" % ch_name)
                    if channel_group[8:] != channels[key]:
                        if channels[key] == "delete".lower():
                            write = False
                        logger.debug("Group is not the same for %s" % ch_name)
                        channel_group = "#EXTGRP:%s" % channels[key]
                        break
                    else:
                        logger.debug("Group is the same %s" % ch_name)
                else:
                    logger.debug("%s is NOT found" % ch_name)
            if write:
                f.write(ch_code + ' group-title="' + channel_group[
                                                     8:] + '",' + ch_name + '\n' + channel_group + "\n" + channel_link + "\n")
        f.close()
"""
