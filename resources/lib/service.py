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
       #xbmc.log("settings changed")
       doLog("Restarting Addon","INFO")
       kodiutils.notification("Edem.tv parser", "Restarting Addon",
                              time=5000, icon=ADDON.getAddonInfo('icon'),
                              sound=True)
       Parser().run()
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
        self.wishlist = self._get_wishlist()

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

    def _get_wishlist(self):
        # Getting wishlist
        path = os.path.join(kodiutils.get_setting("wlPath"), kodiutils.get_setting("wlFilename"))
        if kodiutils.get_setting("wlPath") == "":
            doLog("Please set a path where to store a wishlist", "ERROR")
            kodiutils.notification("Warning", "Please set a path where to store a wishlist", time=5000,
                                   icon=ADDON.getAddonInfo('icon'), sound=True)
            path = os.path.join(xbmc.translatePath(ADDON.getAddonInfo('profile')), kodiutils.get_setting("wlFilename"))
        if os.path.exists(path):
            mode = 'r'
        else:
            mode = 'w+'
        with open(path, mode) as f:
            f_ch = f.read()
        channels = {}
        match = re.finditer("(.*)\:(.*)", f_ch)
        for item in match:
            channels[item.group(1)] = item.group(2)
        return channels

    def _get_playlist_path(self):
        plylist_path = os.path.join(kodiutils.get_setting("m3uPath"), kodiutils.get_setting("m3uFilename"))
        if kodiutils.get_setting("m3uPath") == "":
            kodiutils.notification("Warning", "Please set a path where to store a playlist", time=5000,
                                   icon=ADDON.getAddonInfo('icon'), sound=True)
            plylist_path = os.path.join(xbmc.translatePath(ADDON.getAddonInfo('profile')),
                                        kodiutils.get_setting("m3uFilename"))
        return plylist_path


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
        if kodiutils.get_setting_as_bool("debug"):
            f_ch_list = open(os.path.join(kodiutils.get_setting("wlPath"), "channel_list.txt"), "w+")
        f = open(self._get_playlist_path(), "w+")
        f.write("#EXTM3U\n")
        pattern = "(\#EXTINF\:0.*\,.*)\n(\#EXTGRP\:.*)\n(http\:\/\/.*)\n"
        match = re.finditer(pattern, self._get_m3u_playlist(self.m3uUrl), re.M | re.I)
        for item in match:
            channel_name = item.group(1).replace("\r", "")
            channel_group = item.group(2).replace("\r", "")
            channel_link = item.group(3).replace("\r", "")
            write = True
            # print channel_name
            ch_code = channel_name.split(",")[0]
            ch_name = channel_name.split(",")[1]
            if kodiutils.get_setting_as_bool("debug"):
                doLog(ch_name + ":" + channel_group[8:] + '\n', "DEBUG")
                f_ch_list.write(ch_name + ":" + channel_group[8:] + '\n')
            for key in self.wishlist:
                if ch_name == key:
                    doLog("%s is found" % ch_name, "DEBUG")
                    if channel_group[8:] != self.wishlist[key]:
                        if self.wishlist[key] == "delete".lower():
                            write = False
                        doLog("Group is not the same for %s" % ch_name, "DEBUG")
                        channel_group = "#EXTGRP:%s" % self.wishlist[key]
                        break
                    else:
                        doLog("Group is the same %s" % ch_name, "DEBUG")
                else:
                    doLog("%s is NOT found" % ch_name, "DEBUG")
            if write:
                f.write(ch_code + ' group-title="' + channel_group[
                                                     8:] + '",' + ch_name + '\n' + channel_group + "\n" + channel_link + "\n")
        f.close()
