# -*- coding: utf-8 -*-
from Plugins.Extensions.ElieSatPanel.menus.Helpers import (
    get_local_ip, check_internet, get_image_name,
    get_python_version, get_storage_info, get_ram_info
)
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ConfigList import ConfigListScreen
from Components.config import ConfigText, ConfigSelection, getConfigListEntry, ConfigInteger
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, fileExists
from Plugins.Extensions.ElieSatPanel.__init__ import Version
import os

class Cccamadder(Screen, ConfigListScreen):
    skin = """
    <screen name="Cccamadder" position="0,0" size="1920,1080"
        backgroundColor="transparent" flags="wfNoBorder" title="CCcam Manager">

        <!-- Background -->
        <ePixmap position="0,0" zPosition="-1" size="1920,1080"
            pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/background/panel_bg.png"/>

        <!-- Top bar -->
        <eLabel position="0,0" size="1920,130" zPosition="10" backgroundColor="#000000" />
        <eLabel text="● CCcam Subscription Editor"
            position="350,0" size="1400,50" zPosition="11"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <!-- Bottom buttons -->
        <eLabel position="0,1075" size="480,5" zPosition="2" backgroundColor="red" />
        <widget name="red" position="0,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Save" foregroundColor="yellow" backgroundColor="#000000" transparent="0" />

        <eLabel position="480,1075" size="480,5" zPosition="2" backgroundColor="green" />
        <widget name="green" position="480,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Close" foregroundColor="yellow" backgroundColor="#000000" transparent="0" />

        <eLabel position="960,1075" size="480,5" zPosition="2" backgroundColor="yellow" />
        <widget name="yellow" position="960,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Send" foregroundColor="yellow" backgroundColor="#000000" transparent="0" />

        <eLabel position="1440,1075" size="480,5" zPosition="2" backgroundColor="blue" />
        <widget name="blue" position="1440,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Report" foregroundColor="yellow" backgroundColor="#000000" transparent="0" />

        <!-- Side bars -->
        <eLabel position="0,130" size="80,870" zPosition="10" backgroundColor="#000000" />
        <eLabel position="1840,130" size="80,870" zPosition="10" backgroundColor="#000000" />

        <!-- System info -->
        <widget source="global.CurrentTime" render="Label"
            position="1350,180" size="500,35" zPosition="12"
            font="Bold;32" halign="center" valign="center"
            foregroundColor="yellow" backgroundColor="#000000" transparent="1">
            <convert type="ClockToText">Format %A %d %B</convert>
        </widget>
        <widget source="global.CurrentTime" render="Label"
            position="1350,220" size="500,35" zPosition="12"
            font="Bold;32" halign="center" valign="center"
            foregroundColor="yellow" backgroundColor="#000000" transparent="1">
            <convert type="ClockToText">Format %H:%M:%S</convert>
        </widget>

        <widget name="image_name" position="1470,420" size="450,35" zPosition="12"
            font="Bold;28" halign="left" valign="center" foregroundColor="yellow"
            backgroundColor="#000000" transparent="1" />
        <widget name="python_ver" position="1470,460" size="450,35" zPosition="12"
            font="Bold;28" halign="left" valign="center" foregroundColor="yellow"
            backgroundColor="#000000" transparent="1" />
        <widget name="local_ip" position="1470,500" size="450,35" zPosition="12"
            font="Bold;28" halign="left" valign="center" foregroundColor="yellow"
            backgroundColor="#000000" transparent="1" />
        <widget name="StorageInfo" position="1470,540" size="450,35" zPosition="12"
            font="Bold;28" halign="left" valign="center" foregroundColor="yellow"
            backgroundColor="#000000" transparent="1" />
        <widget name="RAMInfo" position="1470,580" size="450,35" zPosition="12"
            font="Bold;28" halign="left" valign="center" foregroundColor="yellow"
            backgroundColor="#000000" transparent="1" />
        <widget name="net_status" position="1470,620" size="450,35" zPosition="12"
            font="Bold;28" halign="left" valign="center" foregroundColor="yellow"
            backgroundColor="#000000" transparent="1" />

        <!-- Config list -->
        <widget name="config" position="150,300" size="1100,400"
            font="Bold;32" itemHeight="50"
            foregroundColor="yellow"
            transparent="1" scrollbarMode="showOnDemand"/>
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session

        # System info
        self["image_name"] = Label("Image: " + get_image_name())
        self["local_ip"] = Label("IP: " + get_local_ip())
        self["StorageInfo"] = Label(get_storage_info())
        self["RAMInfo"] = Label(get_ram_info())
        self["python_ver"] = Label("Python: " + get_python_version())
        self["net_status"] = Label("Net: " + check_internet())

        # Config fields
        self.protocol = ConfigSelection(choices=[("cccam", "CCcam"), ("newcamd", "NewCamd")])
        self.label = ConfigText(default="Server-Eagle")
        self.host = ConfigText(default="tv8k.cc")
        self.port = ConfigInteger(default=22222, limits=(1, 99999))
        self.user = ConfigText(default="ElieSat")
        self.passw = ConfigText(default="ServerEagle")

        cfg_list = [
            getConfigListEntry("Label:", self.label),
            getConfigListEntry("Protocol:", self.protocol),
            getConfigListEntry("Host:", self.host),
            getConfigListEntry("Port:", self.port),
            getConfigListEntry("Username:", self.user),
            getConfigListEntry("Password:", self.passw),
        ]
        ConfigListScreen.__init__(self, cfg_list, session=session)

        # Buttons
        self["red"] = Label("Save")
        self["green"] = Label("Close")
        self["yellow"] = Label("Send")
        self["blue"] = Label("Report")

        # Actions
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {
                "red": self.save_cccam,
                "green": self.close_screen,
                "yellow": self.send_cccam,
                "blue": self.report_cccam,
                "cancel": self.close_screen,
            },
            -1,
        )

    def close_screen(self):
        self.close()

    def save_cccam(self):
        line = f"{self.label.value} {self.protocol.value} {self.host.value} {self.port.value} {self.user.value} {self.passw.value}\n"
        path = "/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/sus/cccam.txt"
        with open(path, "a") as f:
            f.write(line)
        self.session.open(MessageBox, "Saved successfully!", MessageBox.TYPE_INFO, timeout=3)

    def send_cccam(self):
        os.system("/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/sus/cccam.sh &")
        self.session.open(MessageBox, "Sending CCcam config...", MessageBox.TYPE_INFO, timeout=3)

    def report_cccam(self):
        path = resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/sus/report.txt")
        if fileExists(path):
            with open(path, "r") as f:
                content = f.read()
            self.session.open(MessageBox, content, MessageBox.TYPE_INFO)
        else:
            self.session.open(MessageBox, "Report file not found!", MessageBox.TYPE_ERROR)

