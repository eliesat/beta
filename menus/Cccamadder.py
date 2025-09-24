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
# Unified Protocol Editor
# ----------------------------
class Cccamadder(Screen, ConfigListScreen):
    skin = """
    <screen name="ProtocolEditorScreen" position="0,0" size="1920,1080" backgroundColor="transparent">
        <!-- Background -->
        <ePixmap position="0,0" zPosition="-1" size="1920,1080"
            pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/background/panel_bg.png"/>
        <!-- Top bar -->
        <eLabel position="0,0" size="1920,130" zPosition="10" backgroundColor="#000000" />
        <eLabel text="● Subscription Editor"
            position="740,0" size="1400,50" zPosition="11"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <!-- Bottom buttons -->
        <eLabel position="0,1075" size="480,5" zPosition="2" backgroundColor="red" />
        <widget name="red" position="0,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            foregroundColor="yellow" backgroundColor="#000000" transparent="0" />
        <eLabel position="480,1075" size="480,5" zPosition="2" backgroundColor="green" />
        <widget name="green" position="480,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            foregroundColor="yellow" backgroundColor="#000000" transparent="0" />
        <eLabel position="960,1075" size="480,5" zPosition="2" backgroundColor="yellow" />
        <widget name="yellow" position="960,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            foregroundColor="yellow" backgroundColor="#000000" transparent="0" />
        <eLabel position="1440,1075" size="480,5" zPosition="2" backgroundColor="blue" />
        <widget name="blue" position="1440,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            foregroundColor="yellow" backgroundColor="#000000" transparent="0" />

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
        <widget name="config" position="150,180" size="1100,900"
            font="Bold;32" itemHeight="50"
            foregroundColor="yellow"
            transparent="1" scrollbarMode="showOnDemand"
            enableWrapAround="1"
            valign="center"
            selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/icon/selection.png"
        />

        <!-- Vertical texts -->
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

        # System info
        self["image_name"] = Label("Image: " + get_image_name())
        self["local_ip"] = Label("IP: " + get_local_ip())
        self["StorageInfo"] = Label(get_storage_info())
        self["RAMInfo"] = Label(get_ram_info())
        self["python_ver"] = Label("Python: " + get_python_version())
        self["net_status"] = Label("Net: " + check_internet())
        self["left_bar"] = Label("\n".join(list("Version " + Version)))
        self["right_bar"] = Label("\n".join(list("By ElieSat")))

        # Colored buttons
        self["red"] = Label("Red")
        self["green"] = Label("Green")
        self["yellow"] = Label("Yellow")
        self["blue"] = Label("Blue")

        # Config fields
        self.label = ConfigText(default="Server")
        self.status = ConfigSelection(default="enabled", choices=[("enabled","Enabled"),("disabled","Disabled")])
        self.protocol = ConfigSelection(choices=[("cccam","CCcam"),("newcamd","NewCamd"),("mgcamd","MgCamd")])
        self.host = ConfigText(default="127.0.0.1")
        self.port = ConfigInteger(default=22222, limits=(1,99999))
        self.user = ConfigText(default="User")
        self.passw = ConfigText(default="Pass")
        self.inactivitytimeout = ConfigInteger(default=30, limits=(1,99))
        self.group = ConfigInteger(default=1, limits=(0,99))
        self.disablecrccws = ConfigSelection(default="1", choices=[("0","No"),("1","Yes")])
        self.cccamversion = ConfigText(default="2.0.11")
        self.cccwantemu = ConfigSelection(default="1", choices=[("0","No"),("1","Yes")])
        self.ccckeepalive = ConfigSelection(default="1", choices=[("0","No"),("1","Yes")])
        self.audisabled = ConfigSelection(default="1", choices=[("0","No"),("1","Yes")])
        # NewCamd / MgCamd fields
        self.key = ConfigText(default="0102030405060708091011121314")
        self.disableserverfilter = ConfigSelection(default="1", choices=[("0","No"),("1","Yes")])
        self.connectoninit = ConfigSelection(default="1", choices=[("0","No"),("1","Yes")])

        for field in [self.label,self.host,self.user,self.passw,self.cccamversion,self.key]:
            field.useKeyboard = False

        ConfigListScreen.__init__(self, [], session=session)
        self.update_fields()
        self.protocol.addNotifier(self.on_protocol_change, initial_call=False)

        # Action map
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {
                "red": self.red_button,
                "green": self.green_button,
                "yellow": self.yellow_button,
                "blue": self.blue_button,
                "cancel": self.close_screen,
            }, -1
        )

    # ----------------------------
    # Config List Update
    # ----------------------------
    def update_fields(self):
        proto = self.protocol.value.lower()
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
        ]
        if proto == "cccam":
            cfg_list += [
                getConfigListEntry("Disable CRC/CWS:", self.disablecrccws),
                getConfigListEntry("CCcam Version:", self.cccamversion),
                getConfigListEntry("Want Emu:", self.cccwantemu),
                getConfigListEntry("Keep Alive:", self.ccckeepalive),
                getConfigListEntry("Audio Disabled:", self.audisabled),
            ]
        elif proto in ["newcamd","mgcamd"]:
            cfg_list += [
                getConfigListEntry("Key:", self.key),
                getConfigListEntry("Disable Server Filter:", self.disableserverfilter),
                getConfigListEntry("Connect on Init:", self.connectoninit),
            ]
        self["config"].l.setList(cfg_list)

    def on_protocol_change(self, cfg=None):
        self.update_fields()

    # ----------------------------
    # Buttons
    # ----------------------------
    def red_button(self):
        self.session.open(MessageBox, f"Panel folder:\n{self.panel_dir}", MessageBox.TYPE_INFO, timeout=5)

    def green_button(self):
        self.manage_readers()

    def yellow_button(self):
        self.add_reader()

    def blue_button(self):
        self.report_readers()

    def close_screen(self):
        self.close()

    # ----------------------------
    # Reader Management
    # ----------------------------
    def load_readers(self):
        file_path = os.path.join(self.panel_dir,"subscription.txt")
        readers = []
        if os.path.exists(file_path):
            with open(file_path,"r") as f:
                content = f.read()
            blocks = content.split("[reader]")
            for block in blocks:
                if not block.strip():
                    continue
                reader_info = {}
                for line in block.splitlines():
                    if "=" in line:
                        key,val = line.split("=",1)
                        reader_info[key.strip()] = val.strip()
                readers.append(reader_info)
        return readers

    def add_reader(self):
        readers = self.load_readers()
        proto = self.protocol.value.lower()
        for r in readers:
            if r.get("device","") == f"{self.host.value},{self.port.value}" and r.get("user","") == self.user.value:
                self.session.open(MessageBox,"Reader already exists!",MessageBox.TYPE_ERROR)
                return
        if not os.path.exists(self.panel_dir):
            os.makedirs(self.panel_dir)

        # Build entry
        new_entry = f"[reader]\nlabel = {self.label.value}\nprotocol = {proto}\ndevice = {self.host.value},{self.port.value}\nuser = {self.user.value}\npassword = {self.passw.value}\n"
        if proto == "cccam":
            new_entry += f"inactivitytimeout = {self.inactivitytimeout.value}\ngroup = {self.group.value}\ndisablecrccws = {self.disablecrccws.value}\ncccversion = {self.cccamversion.value}\ncccwantemu = {self.cccwantemu.value}\nccckeepalive = {self.ccckeepalive.value}\naudisabled = {self.audisabled.value}\n\n"
        else:  # NewCamd / MgCamd
            new_entry += f"key = {self.key.value}\ndisableserverfilter = {self.disableserverfilter.value}\nconnectoninit = {self.connectoninit.value}\ngroup = {self.group.value}\ndisablecrccws = {self.disablecrccws.value}\n\n"

        file_path = os.path.join(self.panel_dir,"subscription.txt")
        with open(file_path,"a") as f:
            f.write(new_entry)
        self.session.open(MessageBox,f"Reader added to:\n{file_path}",MessageBox.TYPE_INFO, timeout=5)

    def manage_readers(self):
        path = os.path.join(self.panel_dir,"sus","report.txt")
        if os.path.exists(path):
            with open(path,"r") as f:
                content = f.read()
            self.session.open(MessageBox,content,MessageBox.TYPE_INFO)
        else:
            self.session.open(MessageBox,"Report file not found!",MessageBox.TYPE_ERROR)

    def report_readers(self):
        self.manage_readers()

    # ----------------------------
    # Panel folder detection
    # ----------------------------
    def detect_panel_dir(self):
        for folder in PANEL_DIRS:
            cfg_file = os.path.join(folder, "panel_dir.cfg")
            if os.path.exists(cfg_file):
                return folder
        return PANEL_DIRS[1]  # default HDD

