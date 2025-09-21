# -*- coding: utf-8 -*-
import os
import urllib
try:
    import urllib.request as urllib2  # Python3
except:
    import urllib2  # Python2

from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from Components.Label import Label
from Plugins.Extensions.ElieSatPanel.menus.Helpers import (
    get_local_ip,
    check_internet,
    get_image_name,
    get_python_version,
    get_storage_info,
    get_ram_info,
)
from Plugins.Extensions.ElieSatPanel.__init__ import Version


class News(Screen):
    skin = """
    <screen name="News" position="0,0" size="1920,1080" backgroundColor="transparent" flags="wfNoBorder" title="Info">
        <ePixmap position="0,0" zPosition="-1" size="1920,1080"
            pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/background/panel_bg.png"/>

        <!-- 🔹 Top black bar -->
        <eLabel position="0,0" size="1920,130" zPosition="10" backgroundColor="#000000" />

        <!-- 🔹 Title -->
        <eLabel text="● Addons update news."
            position="350,0" size="1400,50" zPosition="11"
            font="Bold;32" halign="left" valign="center" noWrap="1"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <!-- 🔹 Bottom RED bar -->
        <eLabel position="0,1075" size="480,5" zPosition="2" backgroundColor="red" />
        <widget name="red" position="0,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Close"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />
        <eLabel position="480,1075" size="480,5" zPosition="2" backgroundColor="green" />
        <widget name="green" position="480,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text=""
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <eLabel position="960,1075" size="480,5" zPosition="2" backgroundColor="yellow" />
        <widget name="yellow" position="960,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text=""
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <eLabel position="1440,1075" size="480,5" zPosition="2" backgroundColor="blue" />
        <widget name="blue" position="1440,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text=""
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <!-- 🔹 Left vertical black bar -->
        <eLabel position="0,130" size="80,870" zPosition="10" backgroundColor="#000000" />
        <!-- 🔹 Right vertical black bar -->
        <eLabel position="1840,130" size="80,870" zPosition="10" backgroundColor="#000000" />

        <!-- 🔹 Scrollable GitHub Text -->
        <widget name="github_text"
            position="200,180" size="1200,800" zPosition="12"
            font="Bold;32" halign="left" valign="top"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="1" />

        <!-- 🔹 Page indicator -->
        <widget name="page_info"
            position="1650,940" size="600,60" zPosition="12"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="1" />

        <!-- 🔹 Date -->
        <widget source="global.CurrentTime" render="Label"
            position="1350,180" size="500,35" zPosition="12"
            font="Bold;32" halign="center" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="1">
            <convert type="ClockToText">Format %A %d %B</convert>
        </widget>

        <!-- 🔹 Clock -->
        <widget source="global.CurrentTime" render="Label"
            position="1350,220" size="500,35" zPosition="12"
            font="Bold;32" halign="center" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="1">
            <convert type="ClockToText">Format %H:%M:%S</convert>
        </widget>

        <!-- 🔹 Image name -->
        <widget name="image_name"
            position="1470,420" size="500,35" zPosition="12"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="1" />

        <!-- 🔹 Python version -->
        <widget name="python_ver"
            position="1470,460" size="500,35" zPosition="12"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="1" />

        <!-- 🔹 Local IP -->
        <widget name="local_ip"
            position="1470,500" size="500,35" zPosition="12"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="1" />

        <!-- 🔹 Storage Info -->
        <widget name="StorageInfo"
            position="1470,540" size="500,35" zPosition="12"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="1" />

        <!-- 🔹 Ram Info -->
        <widget name="RAMInfo"
            position="1470,580" size="500,35" zPosition="12"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="1" />

        <!-- 🔹 Net Status -->
        <widget name="net_status"
            position="1470,620" size="500,35" zPosition="12"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="1" />

        <!-- 🔹 Panel Version on LEFT bar -->
        <widget name="left_bar"
            position="20,160" size="60,760" zPosition="20"
            font="Regular;26" halign="center" valign="top"
            foregroundColor="yellow" transparent="1" noWrap="1" />

        <!-- 🔹 Custom text on RIGHT bar -->
        <widget name="right_bar"
            position="1850,160" size="60,760" zPosition="20"
            font="Regular;26" halign="center" valign="top"
            foregroundColor="yellow" transparent="1" noWrap="1" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.setTitle(_("Info"))

        # Vertical bars text
        vertical_left = "\n".join(list("Version " + Version))
        vertical_right = "\n".join(list("By ElieSat"))
        self["left_bar"] = Label(vertical_left)
        self["right_bar"] = Label(vertical_right)

        # System info
        self["image_name"] = Label("Image: " + get_image_name())
        self["local_ip"] = Label("IP: " + get_local_ip())
        self["StorageInfo"] = Label(get_storage_info())
        self["RAMInfo"] = Label(get_ram_info())
        self["python_ver"] = Label("Python: " + get_python_version())
        self["net_status"] = Label("Net: " + check_internet())

        # Scrollable GitHub text
        self["github_text"] = ScrollLabel("Loading...")
        self["page_info"] = Label("Page 1/1")

        # Button labels
        self["red"] = Label(_("Close"))
        self["green"] = Label(_(""))
        self["yellow"] = Label(_(""))
        self["blue"] = Label(_(""))

        # Actions
        self["actions"] = ActionMap(
            ["OkCancelActions", "DirectionActions", "ColorActions"],
            {
                "cancel": self.close,
                "red": self.close,
                "up": self.pageUp,
                "down": self.pageDown,
                "left": self.pageUp,
                "right": self.pageDown,
            },
            -1,
        )

        self.total_pages = 1
        self.current_page = 1

        # Load info.txt from GitHub
        self.loadGithubText()

    def updatePageInfo(self):
        self["page_info"].setText("Page %d/%d" % (self.current_page, self.total_pages))

    def pageUp(self):
        self["github_text"].pageUp()
        if self.current_page > 1:
            self.current_page -= 1
        self.updatePageInfo()

    def pageDown(self):
        self["github_text"].pageDown()
        if self.current_page < self.total_pages:
            self.current_page += 1
        self.updatePageInfo()

    def loadGithubText(self):
        try:
            url = "https://raw.githubusercontent.com/eliesat/eliesatpanel/main/info.txt"
            try:
                response = urllib2.urlopen(url)
            except:
                response = urllib.urlopen(url)
            data = response.read()
            try:
                data = data.decode("utf-8")
            except:
                pass

            self["github_text"].setText(data)

            # 🔹 Calculate approximate pages
            lines = data.splitlines()
            lines_per_page = 20
            self.total_pages = max(1, (len(lines) + lines_per_page - 1) // lines_per_page)
            self.current_page = 1
            self.updatePageInfo()

        except Exception as e:
            print("Error loading info.txt:", e)
            self["github_text"].setText("Server down or unreachable.")
            self.total_pages = 1
            self.current_page = 1
            self.updatePageInfo()

