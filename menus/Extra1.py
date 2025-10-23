# -*- coding: utf-8 -*-
from __future__ import absolute_import
from Plugins.Extensions.ElieSatPanel.menus.Helpers import (
    get_local_ip,
    check_internet,
    get_image_name,
    get_python_version,
    get_storage_info,
    get_ram_info,
)
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ProgressBar import ProgressBar
from Components.ChoiceList import ChoiceEntryComponent, ChoiceList
from enigma import eTimer
import requests
import os
from Plugins.Extensions.ElieSatPanel.__init__ import Version

USER_AGENT = {'User-agent': 'Enigma2-FlashOnline-Style/1.0'}

FEEDS = {
    "OpenHDF": "https://flash.hdfreaks.cc/openhdf/json/{box}",
    "OpenATV": "https://images.mynonpublic.com/openatv/json/{box}",
    "OpenViX": "https://www.openvix.co.uk/json/{box}",
    "OpenPLI": "https://downloads.openpli.org/json/{box}",
    "OpenblackHole": "https://images.openbh.net/json/{box}"
}

GROUPS = [
    ["zgemmah7", "h7", "zgh7"],
    ["maram9", "maram9s"],
    ["classm", "starsatlx", "genius"],
]

BOX_FALLBACKS = {}
for group in GROUPS:
    for hostname in group:
        BOX_FALLBACKS[hostname] = group

class Extra1(Screen):
    skin = """<screen name="Imagesdownload" position="0,0" size="1920,1080" backgroundColor="transparent" flags="wfNoBorder">
<ePixmap position="0,0" zPosition="-1" size="1920,1080" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/background/panel_bg.jpg"/>
<eLabel position="0,0" size="1920,130" zPosition="10" backgroundColor="#000000"/>
<eLabel text="● Images Downloader – Feeds: OpenATV, OpenHDF, OpenViX, OpenPLI, OpenblackHole" position="350,0" size="1400,50" zPosition="11" font="Bold;32" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="0"/>
<widget name="image_name" position="48,840" size="1240,60" zPosition="12" font="Bold;36" halign="center" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1"/>
<widget name="download_info" position="48,910" size="1240,50" zPosition="12" font="Bold;32" halign="center" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1"/>
<widget name="progress" position="48,970" size="1240,60" zPosition="12" foregroundColor="yellow" backgroundColor="#000000"/>
<widget name="python_ver" position="1470,420" size="500,35" zPosition="12" font="Bold;32" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1"/>
<widget name="local_ip" position="1470,460" size="500,35" zPosition="12" font="Bold;32" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1"/>
<widget name="StorageInfo" position="1470,500" size="500,35" zPosition="12" font="Bold;32" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1"/>
<widget name="RAMInfo" position="1470,540" size="500,35" zPosition="12" font="Bold;32" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1"/>
<widget name="net_status" position="1470,580" size="500,35" zPosition="12" font="Bold;32" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1"/>
<widget name="device_name" position="1470,620" size="500,35" zPosition="12" font="Bold;32" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1"/>
<widget name="list" position="48,200" size="1240,620" scrollbarMode="showOnDemand" font="Bold;36" render="Listbox" itemHeight="66" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/icon/selection.png" foregroundColor="yellow" transparent="1"/>
<widget source="global.CurrentTime" render="Label" position="1350,180" size="500,35" zPosition="12" font="Bold;32" halign="center" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1"><convert type="ClockToText">Format %A %d %B</convert></widget>
<widget source="global.CurrentTime" render="Label" position="1350,220" size="500,35" zPosition="12" font="Bold;32" halign="center" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1"><convert type="ClockToText">Format %H:%M:%S</convert></widget>
<eLabel position="0,1075" size="480,5" zPosition="2" backgroundColor="red"/><widget name="red" position="0,1000" size="480,75" zPosition="2" font="Bold;32" halign="center" valign="center" text="Cancel Download" foregroundColor="yellow" backgroundColor="#000000" transparent="0"/>
<eLabel position="480,1075" size="480,5" zPosition="2" backgroundColor="green"/><widget name="green" position="480,1000" size="480,75" zPosition="2" font="Bold;32" halign="center" valign="center" text="" foregroundColor="yellow" backgroundColor="#000000" transparent="0"/>
<eLabel position="960,1075" size="480,5" zPosition="2" backgroundColor="yellow"/><widget name="yellow" position="960,1000" size="480,75" zPosition="2" font="Bold;32" halign="center" valign="center" text="" foregroundColor="yellow" backgroundColor="#000000" transparent="0"/>
<eLabel position="1440,1075" size="480,5" zPosition="2" backgroundColor="blue"/><widget name="blue" position="1440,1000" size="480,75" zPosition="2" font="Bold;32" halign="center" valign="center" text="" foregroundColor="yellow" backgroundColor="#000000" transparent="0"/>
<eLabel position="0,130" size="80,870" zPosition="10" backgroundColor="#000000"/><eLabel position="1840,130" size="80,870" zPosition="10" backgroundColor="#000000"/>
<widget name="left_bar" position="20,160" size="60,760" zPosition="20" font="Regular;26" halign="center" valign="top" foregroundColor="yellow" transparent="1" noWrap="1"/>
<widget name="right_bar" position="1850,160" size="60,760" zPosition="20" font="Regular;26" halign="center" valign="top" foregroundColor="yellow" transparent="1" noWrap="1"/>
</screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.setTitle("Images Downloader")
        self.hostname = self.getHostname()
        self["image_name"] = Label("Image: " + get_image_name())
        self["local_ip"] = Label("IP: " + get_local_ip())
        self["StorageInfo"] = Label(get_storage_info())
        self["RAMInfo"] = Label(get_ram_info())
        self["python_ver"] = Label("Python: " + get_python_version())
        self["net_status"] = Label("Net: " + check_internet())
        self["device_name"] = Label("Device: " + self.hostname)
        self["download_info"] = Label("")
        self["left_bar"] = Label("\n".join(list("Version " + Version)))
        self["right_bar"] = Label("\n".join(list("By ElieSat")))
        self["red"] = Label(_("Red"))
        self["green"] = Label(_("Green"))
        self["yellow"] = Label(_("Yellow"))
        self["blue"] = Label(_("Blue"))
        self["list"] = ChoiceList([])
        self.feedData = {}
        self.expanded = []
        self["progress"] = ProgressBar()
        self.progress_timer = eTimer()
        self.progress_timer.callback.append(self._updateDownload)
        self.download_resp = None
        self.download_file = None
        self.download_target = None
        self.download_total = 0
        self.download_current = 0
        self.chunk_iter = None
        self.download_in_progress = False
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {"ok": self.keyOk, "cancel": self.keyCancel, "back": self.keyCancel, "red": self.cancelDownload},
            -1,
        )
        self.onLayoutFinish.append(self.loadAllFeeds)

    # ---------------- Helpers ----------------
    def getHostname(self):
        try:
            with open("/etc/hostname", "r") as f:
                return f.readline().strip()
        except Exception:
            return os.uname().nodename.strip()

    def getBoxList(self, feed_name):
        return BOX_FALLBACKS.get(self.hostname, [self.hostname, "h7"])

    def fetchFeed(self, feed_name):
        for box in self.getBoxList(feed_name):
            url = FEEDS[feed_name].format(box=box)
            try:
                r = requests.get(url, headers=USER_AGENT, timeout=15)
                r.raise_for_status()
                data = r.json()
                if not isinstance(data, dict):
                    continue
                for cat in data:
                    cat_data = data[cat]
                    if isinstance(cat_data, list):  # OpenHDF style
                        new_cat_data = {}
                        for idx, link in enumerate(cat_data):
                            if not isinstance(link, str):
                                continue
                            name = os.path.basename(link)
                            new_cat_data[f"{cat}_{idx}"] = {"link": link, "name": name}
                        data[cat] = new_cat_data
                    else:  # other feeds
                        for k in cat_data:
                            item = cat_data[k]
                            if isinstance(item, dict):
                                link = item.get("link") or item.get("url") or k
                            else:
                                link = item
                                cat_data[k] = {"link": link}
                            cat_data[k]["link"] = link
                            cat_data[k]["name"] = os.path.basename(link)
                return data
            except Exception:
                continue
        return {"Error": {"Device unsupported": ""}}

    def loadAllFeeds(self):
        for f in FEEDS.keys():
            if f not in self.feedData:
                self.feedData[f] = self.fetchFeed(f)
        self.updateFeeds()

    def updateFeeds(self):
        items = []
        for f in sorted(FEEDS.keys()):
            feed = self.feedData.get(f, {})
            if not isinstance(feed, dict):
                continue
            expanded = f in self.expanded
            items.append(ChoiceEntryComponent("feed", (f"● {f}", "Expanded" if expanded else "Collapsed")))
            if expanded:
                for cat in sorted(feed.keys(), reverse=True):
                    key = f"{f}|{cat}"
                    cat_exp = key in self.expanded
                    items.append(ChoiceEntryComponent("category", (f"    ● {cat}", "Expanded" if cat_exp else "Collapsed")))
                    if cat_exp:
                        for img in sorted(feed[cat].keys(), reverse=True):
                            info = feed[cat][img]
                            name = info.get("name", img)
                            items.append(ChoiceEntryComponent("image", (f"        - {name}", info)))
        self["list"].setList(items)

    # ---------------- Actions ----------------
    def keyCancel(self):
        if self.download_in_progress:
            self.cancelDownload()
            self.session.open(MessageBox, "Download canceled", MessageBox.TYPE_INFO)
        elif self.expanded:
            self.expanded = []
            self.updateFeeds()
        else:
            self.close()

    def keyOk(self):
        if self.download_in_progress:
            return
        cur = self["list"].getCurrent()
        if not cur:
            return
        text, status = cur[0][0], cur[0][1]
        name = text.strip().lstrip("●-").strip()
        if name in FEEDS:
            self._toggleExpand(name)
        elif status in ["Collapsed", "Expanded"]:
            for f in FEEDS:
                if name in self.feedData.get(f, {}):
                    self._toggleExpand(f"{f}|{name}")
                    break
        elif isinstance(status, dict) and "link" in status:
            self._startDownload(status["link"])
        self.updateFeeds()

    def _toggleExpand(self, key):
        if key in self.expanded:
            self.expanded.remove(key)
        else:
            self.expanded.append(key)

    # ---------------- Download ----------------
    def getDownloadPath(self):
        if os.path.exists("/media/hdd/images"):
            return "/media/hdd/images"
        elif os.path.exists("/media/usb/images"):
            return "/media/usb/images"
        return "/tmp"

    def _startDownload(self, url):
        try:
            self.download_in_progress = True
            filename = os.path.basename(url)
            if not os.path.splitext(filename)[1]:
                filename += ".zip"
            path = self.getDownloadPath()
            os.makedirs(path, exist_ok=True)
            self.download_target = os.path.join(path, filename)
            self.download_resp = requests.get(url, headers=USER_AGENT, stream=True, timeout=30)
            self.download_resp.raise_for_status()
            self.download_total = int(self.download_resp.headers.get("Content-Length", 0))
            self.download_current = 0
            self.download_file = open(self.download_target, "wb")
            self.chunk_iter = self.download_resp.iter_content(1024 * 64)
            self["progress"].setValue(0)
            self["image_name"].setText(os.path.basename(self.download_target))
            self["download_info"].setText("0% (0 KB)")
            self.progress_timer.start(100, True)
        except Exception as e:
            self.download_in_progress = False
            self.session.open(MessageBox, f"Download failed:\n{e}", MessageBox.TYPE_ERROR)

    def _updateDownload(self):
        if not self.download_in_progress:
            return
        try:
            chunk = next(self.chunk_iter, None)
            if chunk:
                self.download_file.write(chunk)
                self.download_current += len(chunk)
                percent = int(self.download_current * 100 / self.download_total) if self.download_total else 0
                size_info = f"{self.download_current // 1024}/{self.download_total // 1024} KB"
                self["progress"].setValue(percent)
                self["download_info"].setText(f"{percent}% ({size_info})")
                self.progress_timer.start(100, True)
            else:
                self._finishDownload()
        except StopIteration:
            self._finishDownload()
        except Exception as e:
            self.download_in_progress = False
            try: self.download_file.close()
            except: pass
            try: self.download_resp.close()
            except: pass
            self.session.open(MessageBox, f"Download error:\n{e}", MessageBox.TYPE_ERROR)

    def _finishDownload(self):
        if self.download_file:
            self.download_file.close()
        if self.download_resp:
            self.download_resp.close()
        self.download_in_progress = False
        self["progress"].setValue(100)
        self["image_name"].setText(f"Downloaded: {os.path.basename(self.download_target)}")
        self["download_info"].setText("100%")
        self.session.open(MessageBox, f"Download complete:\n{self.download_target}", MessageBox.TYPE_INFO)

    def cancelDownload(self):
        if not self.download_in_progress:
            return
        self.download_in_progress = False
        try:
            if self.download_file:
                self.download_file.close()
            if self.download_resp:
                self.download_resp.close()
        except: pass
        if self.download_target and os.path.exists(self.download_target):
            try: os.remove(self.download_target)
            except: pass
        self["progress"].setValue(0)
        self["download_info"].setText("Canceled")
        self["image_name"].setText("Download canceled")

