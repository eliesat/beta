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
import os


# ----------------------------
# Panel directories
# ----------------------------
PANEL_DIRS = [
    "/media/usb/ElieSatPanel",
    "/media/hdd/ElieSatPanel",
    "/media/mmc/ElieSatPanel"
]


# ----------------------------
# Class for NewCamd / MgCamd readers
# ----------------------------
class OtherProtocolAdder(Screen, ConfigListScreen):
    skin = """
    <screen name="OtherProtocolAdder" position="0,0" size="1920,1080" backgroundColor="transparent" title="Other Protocol Manager">
        <widget name="config" position="150,180" size="1100,900"
            font="Bold;32" itemHeight="50"
            foregroundColor="yellow"
            transparent="1"
            scrollbarMode="showOnDemand"
            enableWrapAround="1" />

        <!-- Background -->
        <ePixmap position="0,0" zPosition="-1" size="1920,1080"
            pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/background/panel_bg.png"/>

        <!-- Top bar -->
        <eLabel position="0,0" size="1920,130" zPosition="10" backgroundColor="#000000" />
        <eLabel text="● CCcam Subscription Editor"
            position="740,0" size="1400,50" zPosition="11"
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

    def __init__(self, session, panel_dir):
        Screen.__init__(self, session)
        self.session = session
        self.panel_dir = panel_dir

        vertical_left = "\n".join(list("Version " + Version))
        vertical_right = "\n".join(list("By ElieSat"))
        self["left_bar"] = Label(vertical_left)
        self["right_bar"] = Label(vertical_right)

        # System info labels
        self["image_name"] = Label("Image: " + get_image_name())
        self["local_ip"] = Label("IP: " + get_local_ip())
        self["StorageInfo"] = Label(get_storage_info())
        self["RAMInfo"] = Label(get_ram_info())
        self["python_ver"] = Label("Python: " + get_python_version())
        self["net_status"] = Label("Net: " + check_internet())

        # Config fields for NewCamd / MgCamd
        self.label = ConfigText(default="Server-Eagle")
        self.protocol = ConfigSelection(choices=[("newcamd", "NewCamd"), ("mgcamd", "MgCamd")])
        self.host = ConfigText(default="tv8k.cc")
        self.port = ConfigInteger(default=22222, limits=(1, 99999))
        self.user = ConfigText(default="server-eagle")
        self.passw = ConfigText(default="eagle")
        self.key = ConfigText(default="0102030405060708091011121314")
        self.disableserverfilter = ConfigSelection(default="1", choices=[("0","No"),("1","Yes")])
        self.connectoninit = ConfigSelection(default="1", choices=[("0","No"),("1","Yes")])
        self.group = ConfigInteger(default=1, limits=(0,99))
        self.disablecrccws = ConfigSelection(default="1", choices=[("0","No"),("1","Yes")])

        for field in [self.label, self.host, self.user, self.passw, self.key]:
            field.useKeyboard = False

        ConfigListScreen.__init__(self, [], session=session)
        self.update_fields()
        # Buttons
        self["red"] = Label("Show Path")
        self["green"] = Label("Close")
        self["yellow"] = Label("Print")
        self["blue"] = Label("Report")


        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {
                "red": self.close,
                "green": self.add_reader,
                "cancel": self.close
            }, -1
        )

    def update_fields(self):
        cfg_list = [
            getConfigListEntry("Label:", self.label),
            getConfigListEntry("Protocol:", self.protocol),
            getConfigListEntry("Host:", self.host),
            getConfigListEntry("Port:", self.port),
            getConfigListEntry("Username:", self.user),
            getConfigListEntry("Password:", self.passw),
            getConfigListEntry("Key:", self.key),
            getConfigListEntry("Disable Server Filter:", self.disableserverfilter),
            getConfigListEntry("Connect on Init:", self.connectoninit),
            getConfigListEntry("Group:", self.group),
            getConfigListEntry("Disable CRC/CWS:", self.disablecrccws),
        ]
        self["config"].l.setList(cfg_list)

    def add_reader(self):
        if not os.path.exists(self.panel_dir):
            os.makedirs(self.panel_dir)

        file_path = os.path.join(self.panel_dir, "subscription.txt")
        new_entry = f"""[reader]
label                         = {self.label.value}
protocol                      = {self.protocol.value}
device                        = {self.host.value},{self.port.value}
key                           = {self.key.value}
user                          = {self.user.value}
password                      = {self.passw.value}
disableserverfilter           = {self.disableserverfilter.value}
connectoninit                 = {self.connectoninit.value}
group                         = {self.group.value}
disablecrccws                 = {self.disablecrccws.value}

"""
        with open(file_path, "a") as f:
            f.write(new_entry)

        self.session.open(MessageBox, f"Reader added to:\n{file_path}", MessageBox.TYPE_INFO, timeout=5)


# ----------------------------
# Main CCcam Adder class
# ----------------------------
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
            position="740,0" size="1400,50" zPosition="11"
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
        self.panel_dir = self.detect_panel_dir()
        if not os.path.exists(self.panel_dir):
            os.makedirs(self.panel_dir)

        vertical_left = "\n".join(list("Version " + Version))
        vertical_right = "\n".join(list("By ElieSat"))
        self["left_bar"] = Label(vertical_left)
        self["right_bar"] = Label(vertical_right)

        # System info labels
        self["image_name"] = Label("Image: " + get_image_name())
        self["local_ip"] = Label("IP: " + get_local_ip())
        self["StorageInfo"] = Label(get_storage_info())
        self["RAMInfo"] = Label(get_ram_info())
        self["python_ver"] = Label("Python: " + get_python_version())
        self["net_status"] = Label("Net: " + check_internet())

        # Config fields
        self.label = ConfigText(default="Server-Eagle")
        self.status = ConfigSelection(default="enabled", choices=[("enabled", "Enabled"), ("disabled", "Disabled")])
        self.protocol = ConfigSelection(choices=[("cccam", "CCcam"), ("newcamd", "NewCamd"), ("mgcamd", "MgCamd")])
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

        for field in [self.label, self.host, self.user, self.passw, self.cccamversion]:
            field.useKeyboard = False

        ConfigListScreen.__init__(self, [], session=session)
        self.update_fields_by_protocol()

        # ✅ Fixed: notifier passes cfg argument
        self.protocol.addNotifier(self.on_protocol_change, initial_call=False)

        # Buttons
        self["red"] = Label("Show Path")
        self["green"] = Label("Close")
        self["yellow"] = Label("Print")
        self["blue"] = Label("Report")

        # Buttons
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {
                "red": self.show_default_path,
                "green": self.manage_readers,
                "yellow": self.add_reader,
                "blue": self.report_cccam,
                "cancel": self.close_screen,
            }, -1
        )

    # Detect panel folder
    def detect_panel_dir(self):
        for folder in PANEL_DIRS:
            cfg_file = os.path.join(folder, "panel_dir.cfg")
            if os.path.exists(cfg_file):
                return folder
        return PANEL_DIRS[1]  # default HDD

    def close_screen(self):
        self.close()

    def show_default_path(self):
        self.session.open(MessageBox, f"Default panel folder:\n{self.panel_dir}", MessageBox.TYPE_INFO, timeout=5)

    # Load readers
    def load_readers(self):
        file_path = os.path.join(self.panel_dir, "subscription.txt")
        readers = []
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                content = f.read()
            blocks = content.split("[reader]")
            for block in blocks:
                if not block.strip():
                    continue
                reader_info = {}
                for line in block.splitlines():
                    if "=" in line:
                        key, val = line.split("=", 1)
                        reader_info[key.strip()] = val.strip()
                readers.append(reader_info)
        return readers

    # Update fields dynamically
    def update_fields_by_protocol(self):
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
        ]

        proto = self.protocol.value.lower()
        if proto == "cccam":
            cfg_list += [
                getConfigListEntry("CCcam Version:", self.cccamversion),
                getConfigListEntry("Want Emu:", self.cccwantemu),
                getConfigListEntry("Keep Alive:", self.ccckeepalive),
                getConfigListEntry("Audio Disabled:", self.audisabled),
            ]

        self["config"].l.setList(cfg_list)

    # Protocol change handler
    def on_protocol_change(self, cfg=None):
        proto = self.protocol.value.lower()
        if proto in ["newcamd", "mgcamd"]:
            self.session.open(OtherProtocolAdder, self.panel_dir)
        else:
            self.update_fields_by_protocol()

    # Add reader
    def add_reader(self):
        if self.protocol.value.lower() != "cccam":
            self.on_protocol_change()
            return

        readers = self.load_readers()
        for r in readers:
            if r.get("device", "") == f"{self.host.value},{self.port.value}" and r.get("user", "") == self.user.value:
                self.session.open(MessageBox, "Reader already exists!", MessageBox.TYPE_ERROR)
                return

        if not os.path.exists(self.panel_dir):
            os.makedirs(self.panel_dir)

        new_entry = f"""[reader]
label = {self.label.value}
protocol = cccam
device = {self.host.value},{self.port.value}
user = {self.user.value}
password = {self.passw.value}
inactivitytimeout = {self.inactivitytimeout.value}
group = {self.group.value}
disablecrccws = {self.disablecrccws.value}
cccversion = {self.cccamversion.value}
cccwantemu = {self.cccwantemu.value}
ccckeepalive = {self.ccckeepalive.value}
audisabled = {self.audisabled.value}

"""

        file_path = os.path.join(self.panel_dir, "subscription.txt")
        with open(file_path, "a") as f:
            f.write(new_entry)

        self.session.open(MessageBox, f"Reader added to:\n{file_path}", MessageBox.TYPE_INFO, timeout=5)

    # Manage readers / Report
    def manage_readers(self):
        path = os.path.join(self.panel_dir, "sus", "report.txt")
        if os.path.exists(path):
            with open(path, "r") as f:
                content = f.read()
            self.session.open(MessageBox, content, MessageBox.TYPE_INFO)
        else:
            self.session.open(MessageBox, "Report file not found!", MessageBox.TYPE_ERROR)

    def report_cccam(self):
        self.manage_readers()

    # Yellow button: save subscription
    def print_fields(self):
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
        if not os.path.exists(self.panel_dir):
            os.makedirs(self.panel_dir)

        file_path = os.path.join(self.panel_dir, "subscription.txt")
        with open(file_path, "w") as f:
            f.write(new_entry)
        self.session.open(MessageBox, f"Subscription saved to:\n{file_path}", MessageBox.TYPE_INFO, timeout=5)

    # Blue button: report
    def report_cccam(self):
        path = os.path.join(self.panel_dir, "sus/report.txt")
        if os.path.exists(path):
            with open(path, "r") as f:
                content = f.read()
            self.session.open(MessageBox, content, MessageBox.TYPE_INFO)
        else:
            self.session.open(MessageBox, "Report file not found!", MessageBox.TYPE_ERROR)
