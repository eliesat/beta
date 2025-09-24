# -*- coding: utf-8 -*-
from Plugins.Extensions.ElieSatPanel.__init__ import Version
from Plugins.Extensions.ElieSatPanel.menus.Helpers import (
    get_local_ip, check_internet, get_image_name,
    get_python_version, get_storage_info, get_ram_info
)
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ConfigList import ConfigListScreen
from Components.config import ConfigText, ConfigSelection, ConfigInteger, getConfigListEntry
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, fileExists
import os

class Cccamadder(Screen, ConfigListScreen):
    skin = """
    <screen name="Cccamadder" position="0,0" size="1920,1080" backgroundColor="transparent" flags="wfNoBorder" title="CCcam Manager">
        <!-- Background -->
        <ePixmap position="0,0" zPosition="-1" size="1920,1080"
            pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/background/panel_bg.png"/>
        <!-- Top bar -->
        <eLabel position="0,0" size="1920,130" zPosition="10" backgroundColor="#000000" />
        <eLabel text="● CCcam Subscription Editor" position="350,0" size="1400,50" zPosition="11"
            font="Bold;32" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="0" />
        <!-- Bottom buttons -->
        <widget name="red" position="0,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center" text="Save" foregroundColor="yellow" backgroundColor="#000000" transparent="0" />
        <widget name="green" position="480,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center" text="Close" foregroundColor="yellow" backgroundColor="#000000" transparent="0" />
        <widget name="yellow" position="960,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center" text="Print" foregroundColor="yellow" backgroundColor="#000000" transparent="0" />
        <widget name="blue" position="1440,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center" text="Report" foregroundColor="yellow" backgroundColor="#000000" transparent="0" />
        <!-- Side bars -->
        <eLabel position="0,130" size="80,870" zPosition="10" backgroundColor="#000000" />
        <eLabel position="1840,130" size="80,870" zPosition="10" backgroundColor="#000000" />
        <!-- System info -->
        <widget source="global.CurrentTime" render="Label" position="1350,180" size="500,35" zPosition="12"
            font="Bold;32" halign="center" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1">
            <convert type="ClockToText">Format %A %d %B</convert>
        </widget>
        <widget source="global.CurrentTime" render="Label" position="1350,220" size="500,35" zPosition="12"
            font="Bold;32" halign="center" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1">
            <convert type="ClockToText">Format %H:%M:%S</convert>
        </widget>
        <widget name="image_name" position="1470,420" size="450,35" zPosition="12"
            font="Bold;28" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <widget name="python_ver" position="1470,460" size="450,35" zPosition="12"
            font="Bold;28" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <widget name="local_ip" position="1470,500" size="450,35" zPosition="12"
            font="Bold;28" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <widget name="StorageInfo" position="1470,540" size="450,35" zPosition="12"
            font="Bold;28" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <widget name="RAMInfo" position="1470,580" size="450,35" zPosition="12"
            font="Bold;28" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <widget name="net_status" position="1470,620" size="450,35" zPosition="12"
            font="Bold;28" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <!-- Config list -->
        <widget name="config" position="150,180" size="1100,900"
            font="Bold;32" itemHeight="50" foregroundColor="yellow" transparent="1"
            scrollbarMode="showOnDemand" enableWrapAround="1" valign="center"
            selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/icon/selection.png"/>
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
        self["left_bar"] = Label("\n".join(list("Version " + Version)))
        self["right_bar"] = Label("\n".join(list("By ElieSat")))

        # Config fields
        self.label = ConfigText(default="Server-Eagle")
        self.status = ConfigSelection(default="enabled", choices=[("enabled", "Enabled"), ("disabled", "Disabled")])
        self.protocol = ConfigSelection(choices=[("cccam", "CCcam"), ("newcamd", "NewCamd")])
        self.host = ConfigText(default="tv8k.cc")
        self.port = ConfigInteger(default=22222, limits=(1, 99999))
        self.user = ConfigText(default="ElieSat")
        self.passw = ConfigText(default="ServerEagle")
        self.inactivitytimeout = ConfigInteger(default=30, limits=(1, 99))
        self.group = ConfigInteger(default=1, limits=(0, 99))
        self.disablecrccws = ConfigSelection(default="1", choices=[("0", "No"), ("1", "Yes")])
        self.cccamversion = ConfigText(default="2.0.11")
        self.cccwantemu = ConfigSelection(default="1", choices=[("0", "No"), ("1", "Yes")])
        self.ccckeepalive = ConfigSelection(default="1", choices=[("0", "No"), ("1", "Yes")])
        self.audisabled = ConfigSelection(default="1", choices=[("0", "No"), ("1", "Yes")])

        # Disable virtual keyboard completely
        for field in [self.label, self.host, self.user, self.passw, self.cccamversion]:
            field.useKeyboard = False

        # Config list
        cfg_list = [
            getConfigListEntry("Label:", self.label),
            getConfigListEntry("Status:", self.status),
            getConfigListEntry("Protocol:", self.protocol),
            getConfigListEntry("Host:", self.host),
            getConfigListEntry("Port:", self.port),
            getConfigListEntry("Username:", self.user),
            getConfigListEntry("Password:", self.passw),
            getConfigListEntry("Inactivity Timeout:", self.inactivitytimeout),
            getConfigListEntry("Group:", self.group),
            getConfigListEntry("Disable CRC/CWS:", self.disablecrccws),
            getConfigListEntry("CCcam Version:", self.cccamversion),
            getConfigListEntry("Want Emu:", self.cccwantemu),
            getConfigListEntry("Keep Alive:", self.ccckeepalive),
            getConfigListEntry("Audio Disabled:", self.audisabled),
        ]
        ConfigListScreen.__init__(self, cfg_list, session=session)

        # Buttons
        self["red"] = Label("Save")
        self["green"] = Label("Close")
        self["yellow"] = Label("Print")
        self["blue"] = Label("Report")

        # Actions
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {
                "red": self.show_default_path,  # Red button now shows default path
                "green": self.close_screen,
                "yellow": self.print_fields,    # Yellow prints subscription
                "blue": self.report_cccam,
                "cancel": self.close_screen,
            },
            -1,
        )

    def close_screen(self):
        self.close()

    # ======================
    # Red button: show default path
    # ======================
    def show_default_path(self):
        # Default path for ElieSatPanel
        path = "/media/hdd/ElieSatPanel"
        self.session.open(MessageBox, f"Default path folder:\n{path}", MessageBox.TYPE_INFO, timeout=5)

    # ======================
    # Yellow button: print subscription
    # ======================
    def print_fields(self):
        # Build entry text
        new_entry = (
            "[reader]\n"
            f"label                         = {self.label.value}\n"
            f"status                        = {self.status.value}\n"
            f"protocol                      = {self.protocol.value}\n"
            f"device                        = {self.host.value},{self.port.value}\n"
            f"user                          = {self.user.value}\n"
            f"password                      = {self.passw.value}\n"
            f"inactivitytimeout             = {self.inactivitytimeout.value}\n"
            f"group                         = {self.group.value}\n"
            f"disablecrccws                 = {self.disablecrccws.value}\n"
            f"cccversion                    = {self.cccamversion.value}\n"
            f"cccwantemu                    = {self.cccwantemu.value}\n"
            f"ccckeepalive                  = {self.ccckeepalive.value}\n"
            f"audisabled                    = {self.audisabled.value}\n"
        )
        # Save in default path
        folder = "/media/hdd/ElieSatPanel"
        file_path = os.path.join(folder, "subscription.txt")
        with open(file_path, "w") as f:
            f.write(new_entry)
        self.session.open(MessageBox, f"Subscription saved to:\n{file_path}", MessageBox.TYPE_INFO, timeout=5)

    # ======================
    # Report (blue button)
    # ======================
    def report_cccam(self):
        path = resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/sus/report.txt")
        if fileExists(path):
            with open(path, "r") as f:
                content = f.read()
            self.session.open(MessageBox, content, MessageBox.TYPE_INFO)
        else:
            self.session.open(MessageBox, "Report file not found!", MessageBox.TYPE_ERROR)

