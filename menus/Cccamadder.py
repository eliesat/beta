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
            text="Print" foregroundColor="yellow" backgroundColor="#000000" transparent="0" />

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

            <!-- Config list with selection highlight -->
    <widget name="config" position="150,180" size="1100,900"
        font="Bold;32" itemHeight="50"
        foregroundColor="yellow"
        transparent="1" scrollbarMode="showOnDemand"
        enableWrapAround="1"
        valign="center"
        selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/icon/selection.png"
        />

    <!-- 🔹 Vertical texts -->
    <widget name="left_bar"
        position="20,160" size="60,760" zPosition="20"
        font="Regular;26" halign="center" valign="top"
        noWrap="1" foregroundColor="yellow" backgroundColor="#000000"
        transparent="0" />
    <widget name="right_bar"
        position="1850,160" size="60,760" zPosition="20"
        font="Regular;26" halign="center" valign="top"
        noWrap="1" foregroundColor="yellow" backgroundColor="#000000"
        transparent="0" />

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
        vertical_left = "\n".join(list("Version " + Version))
        vertical_right = "\n".join(list("By ElieSat"))
        self["left_bar"] = Label(vertical_left)
        self["right_bar"] = Label(vertical_right)


        # Config fields
        self.label = ConfigText(default="Server-Eagle")
        self.status = ConfigSelection(default="enabled", choices=[("enabled", "Enabled"), ("disabled", "Disabled")])
        self.protocol = ConfigSelection(choices=[("cccam", "CCcam"), ("newcamd", "NewCamd")])
        self.host = ConfigText(default="tv8k.cc")
        self.port = ConfigInteger(default=22222, limits=(1, 99999))
        self.user = ConfigText(default="ElieSat")
        self.passw = ConfigText(default="ServerEagle")

        # Additional CCcam parameters
        self.inactivitytimeout = ConfigInteger(default=30, limits=(1, 99))
        self.group = ConfigInteger(default=1, limits=(0, 99))
        self.disablecrccws = ConfigSelection(default="1", choices=[("0", "No"), ("1", "Yes")])
        self.cccamversion = ConfigText(default="2.0.11")
        self.cccwantemu = ConfigSelection(default="1", choices=[("0", "No"), ("1", "Yes")])
        self.ccckeepalive = ConfigSelection(default="1", choices=[("0", "No"), ("1", "Yes")])
        self.audisabled = ConfigSelection(default="1", choices=[("0", "No"), ("1", "Yes")])

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

        # Remove virtual keyboard for text fields
        for field in [self.label, self.host, self.user, self.passw, self.cccamversion]:
            field.useKeyboard = False

        # Buttons
        self["red"] = Label("Save")
        self["green"] = Label("Close")
        self["yellow"] = Label("Print")
        self["blue"] = Label("Report")

        # Actions
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {
                "red": self.save_cccam,
                "green": self.close_screen,
                "yellow": self.print_fields_to_tmp,  # smart print with duplicate check
                "blue": self.report_cccam,
                "cancel": self.close_screen,
            },
            -1,
        )

    def close_screen(self):
        self.close()

    def save_cccam(self):
        line = (
            f"{self.label.value} {self.status.value} {self.protocol.value} {self.host.value} {self.port.value} {self.user.value} {self.passw.value} "
            f"inactivitytimeout={self.inactivitytimeout.value} group={self.group.value} disablecrccws={self.disablecrccws.value} "
            f"cccamversion={self.cccamversion.value} cccwantemu={self.cccwantemu.value} ccckeepalive={self.ccckeepalive.value} audisabled={self.audisabled.value}\n"
        )
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

    def print_fields_to_tmp(self):
        tmp_path = "/tmp/tmpfile"
        new_device = f"{self.host.value},{self.port.value}"
        new_user = self.user.value
        new_pass = self.passw.value

        # Build new reader entry
        new_entry = (
            "[reader]\n"
            f"label                         = {self.label.value}\n"
            f"status                        = {self.status.value}\n"
            f"protocol                      = {self.protocol.value}\n"
            f"device                        = {new_device}\n"
            f"user                          = {new_user}\n"
            f"password                      = {new_pass}\n"
            f"inactivitytimeout             = {self.inactivitytimeout.value}\n"
            f"group                         = {self.group.value}\n"
            f"disablecrccws                 = {self.disablecrccws.value}\n"
            f"cccversion                    = {self.cccamversion.value}\n"
            f"cccwantemu                    = {self.cccwantemu.value}\n"
            f"ccckeepalive                  = {self.ccckeepalive.value}\n"
            f"audisabled                    = {self.audisabled.value}\n"
        )

        # Check if the server already exists (host, port, user, password)
        exists = False
        if os.path.exists(tmp_path):
            with open(tmp_path, "r") as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if line.startswith("device") and line.strip().endswith(new_device):
                        # Check the next two lines for matching user and password
                        if i + 1 < len(lines) and i + 2 < len(lines):
                            user_line = lines[i + 1].strip()
                            pass_line = lines[i + 2].strip()
                            if user_line == f"user                          = {new_user}" and pass_line == f"password                      = {new_pass}":
                                exists = True
                                break

        if exists:
            self.session.open(MessageBox, "Server already exists!", MessageBox.TYPE_INFO, timeout=3)
        else:
            # Append new entry while keeping existing ones
            with open(tmp_path, "a") as f:
                if os.path.getsize(tmp_path) > 0:
                    f.write("\n")  # blank line between entries
                f.write(new_entry)
            self.session.open(MessageBox, "New server added to /tmp/tmpfile", MessageBox.TYPE_INFO, timeout=3)

