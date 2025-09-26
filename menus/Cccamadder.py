# -*- coding: utf-8 -*-
import os
import re
from datetime import datetime
import gettext

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ConfigList import ConfigListScreen
from Components.config import (
    ConfigText, ConfigSelection, ConfigInteger, getConfigListEntry
)
from Components.MenuList import MenuList
from Components.Language import language

from Plugins.Extensions.ElieSatPanel.__init__ import Version
from Plugins.Extensions.ElieSatPanel.menus.Helpers import (
    get_local_ip, check_internet, get_image_name,
    get_python_version, get_storage_info, get_ram_info
)

# --- Translation setup ---
def localeInit():
    lang = language.getLanguage()
    gettext.bindtextdomain(
        "ElieSatPanel",
        "/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/locale"
    )

localeInit()
_ = gettext.gettext


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
        self["red"] = Label("Check Path")
        self["green"] = Label("Restore")
        self["yellow"] = Label("Send And Backup")
        self["blue"] = Label("Manage Readers")

        # Config fields
        self.label_choice = ConfigSelection(
            default="ServerEagle",
            choices=[("ServerEagle", "ServerEagle"),
                     ("ElieSat", "ElieSat"),
                     ("Custom", "Custom")]
        )
        self.label_custom = ConfigText(default="server_name")
        self.label_custom.useKeyboard = False

        self.status = ConfigSelection(default="enabled", choices=[("enabled","Enabled"),("disabled","Disabled")])
        self.protocol = ConfigSelection(choices=[("cccam","CCcam"),("newcamd","NewCamd"),("mgcamd","MgCamd")])
        self.host = ConfigText(default="tv8k.cc")
        self.port = ConfigInteger(default=22222, limits=(1,99999))
        self.user = ConfigText(default="User")
        self.passw = ConfigText(default="Pass")
        self.inactivitytimeout = ConfigInteger(default=30, limits=(1,99))
        self.group = ConfigInteger(default=1, limits=(0,99))
        self.disablecrccws = ConfigSelection(default="1", choices=[("0","No"),("1","Yes")])
        self.cccamversion = ConfigSelection(
    default="2.0.11",
    choices=[
        ("2.0.11", "2.0.11"),
        ("2.1.1", "2.1.1"),
        ("2.1.2", "2.1.2"),
        ("2.1.3", "2.1.3"),
        ("2.1.4", "2.1.4"),
        ("2.2.0", "2.2.0"),
        ("2.2.1", "2.2.1"),
        ("2.3.0", "2.3.0"),
        ("2.3.1", "2.3.1"),
        ("2.3.2", "2.3.2"),
    ]
)
        self.cccwantemu = ConfigSelection(default="1", choices=[("0","No"),("1","Yes")])
        self.ccckeepalive = ConfigSelection(default="1", choices=[("0","No"),("1","Yes")])
        self.audisabled = ConfigSelection(default="1", choices=[("0","No"),("1","Yes")])
        # NewCamd / MgCamd fields
        self.key = ConfigText(default="0102030405060708091011121314")
        self.disableserverfilter = ConfigSelection(default="1", choices=[("0","No"),("1","Yes")])
        self.connectoninit = ConfigSelection(default="1", choices=[("0","No"),("1","Yes")])

        for field in [self.host,self.user,self.passw,self.cccamversion,self.key]:
            field.useKeyboard = False

        ConfigListScreen.__init__(self, [], session=session)
        self.update_fields()
        self.label_choice.addNotifier(self.on_label_change, initial_call=False)
        self.protocol.addNotifier(self.on_protocol_change, initial_call=False)

        # Action map
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {
                "red": self.open_red_job,
                "green": self.open_green_job,
                "yellow": self.yellow_button,
                "blue": self.open_blue_job,
                "cancel": self.close_screen,
            }, -1
        )

    # ----------------------------
    # Config List Update
    # ----------------------------
    def update_fields(self):
        proto = self.protocol.value.lower()
        cfg_list = [
            getConfigListEntry("Label:", self.label_choice),
        ]

        # Show custom text if "Custom" selected
        if self.label_choice.value == "Custom":
            cfg_list.append(getConfigListEntry("Custom Name:", self.label_custom))

        cfg_list += [
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

    def on_label_change(self, cfg=None):
        self.update_fields()

    # ----------------------------
    # Buttons
    # ----------------------------
    def open_red_job(self):
        self.session.open(MessageBox, f"Panel folder:\n{self.panel_dir}", MessageBox.TYPE_INFO, timeout=5)

    def open_green_job(self):
        self.session.open(GreenJobScreen)

    def yellow_button(self):
        self.add_reader()

    def open_blue_job(self):
        self.session.open(BlueJobScreen)

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

        label_value = (
            self.label_custom.value if self.label_choice.value == "Custom"
            else self.label_choice.value
        )

        for r in readers:
            if r.get("device","") == f"{self.host.value},{self.port.value}" and r.get("user","") == self.user.value:
                self.session.open(MessageBox,"Reader already exists!",MessageBox.TYPE_ERROR)
                return
        if not os.path.exists(self.panel_dir):
            os.makedirs(self.panel_dir)

        # Build entry
        new_entry = f"[reader]\nlabel = {label_value}\nprotocol = {proto}\ndevice = {self.host.value},{self.port.value}\nuser = {self.user.value}\npassword = {self.passw.value}\n"
        if proto == "cccam":
            new_entry += f"inactivitytimeout = {self.inactivitytimeout.value}\ngroup = {self.group.value}\ndisablecrccws = {self.disablecrccws.value}\ncccversion = {self.cccamversion.value}\ncccwantemu = {self.cccwantemu.value}\nccckeepalive = {self.ccckeepalive.value}\naudisabled = {self.audisabled.value}\n\n"
        else:  # NewCamd / MgCamd
            new_entry += f"key = {self.key.value}\ndisableserverfilter = {self.disableserverfilter.value}\nconnectoninit = {self.connectoninit.value}\ngroup = {self.group.value}\ndisablecrccws = {self.disablecrccws.value}\n\n"

        file_path = os.path.join(self.panel_dir,"subscription.txt")
        with open(file_path,"a") as f:
            f.write(new_entry)
        self.session.open(MessageBox,f"Reader added to:\n{file_path}",MessageBox.TYPE_INFO, timeout=5)

    # ----------------------------
    # Panel folder detection
    # ----------------------------
    def detect_panel_dir(self):
        for folder in PANEL_DIRS:
            cfg_file = os.path.join(folder, "panel_dir.cfg")
            if os.path.exists(cfg_file):
                return folder
        return PANEL_DIRS[1]  # default HDD

# ----------------------------
# GreenJobScreen
# ----------------------------
class GreenJobScreen(Screen):
    skin = """
    <screen name="Blank" position="0,0" size="1920,1080" backgroundColor="transparent" flags="wfNoBorder" title="Scripts">
        <ePixmap position="0,0" zPosition="-1" size="1920,1080"
            pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/background/panel_bg.png"/>

        <!-- Top black bar -->
        <eLabel position="0,0" size="1920,130" zPosition="10" backgroundColor="#000000" />

        <!-- Title -->
        <eLabel text="● Subscription Reader Labels"
            position="350,0" size="800,50" zPosition="11"
            font="Bold;32" halign="left" valign="center" noWrap="1"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <!-- Clock -->
        <widget name="clock" position="1250,0" size="650,50" zPosition="11"
            font="Bold;32" halign="right" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <!-- Bottom color button bars -->
        <eLabel position="0,1075" size="480,5" zPosition="2" backgroundColor="red" />
        <widget name="red" position="0,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Red Button"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <eLabel position="480,1075" size="480,5" zPosition="2" backgroundColor="green" />
        <widget name="green" position="480,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Green Button"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <eLabel position="960,1075" size="480,5" zPosition="2" backgroundColor="yellow" />
        <widget name="yellow" position="960,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Yellow Button"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <eLabel position="1440,1075" size="480,5" zPosition="2" backgroundColor="blue" />
        <widget name="blue" position="1440,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Blue Button"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <!-- Left and Right black bars -->
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

        <widget name="image_name" position="1470,420" size="500,35" font="Bold;32" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <widget name="python_ver" position="1470,460" size="500,35" font="Bold;32" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <widget name="local_ip" position="1470,500" size="500,35" font="Bold;32" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <widget name="StorageInfo" position="1470,540" size="500,35" font="Bold;32" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <widget name="RAMInfo" position="1470,580" size="500,35" font="Bold;32" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <widget name="net_status" position="1470,620" size="500,35" font="Bold;32" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1" />

        <!-- Panel Version -->
        <widget name="left_bar" position="20,160" size="60,760" font="Regular;26" halign="center" valign="top" foregroundColor="yellow" transparent="1" noWrap="1" />
        <widget name="right_bar" position="1850,160" size="60,760" font="Regular;26" halign="center" valign="top" foregroundColor="yellow" transparent="1" noWrap="1" />

        <!-- Subscription Labels (scrollable list) -->
        <widget name="sub_labels" position="200,200" size="1200,700" zPosition="12"
            scrollbarMode="showOnDemand"
            font="Bold;30"
            foregroundColor="yellow"
            transparent="1"
            itemHeight="50" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.setTitle(_("Subscription Labels"))

        # Left/Right vertical bars
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

        # Clock
        now = datetime.now().strftime("%Y-%m-%d  %H:%M")
        self["clock"] = Label(now)

        # Subscription labels list
        self.sub_labels_list = MenuList([], enableWrapAround=True)
        self["sub_labels"] = self.sub_labels_list
        self.update_subscription_list()

        # Buttons
        self["red"] = Label(_("Remove Reader"))
        self["green"] = Label(_("Test reader"))
        self["yellow"] = Label(_("Show reader"))
        self["blue"] = Label(_("Show Reader path"))

        # Actions
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {
                "red": self.dummy,
                "green": self.dummy,
                "yellow": self.dummy,
                "blue": self.dummy,
                "ok": self.print_selected_label,
                "cancel": self.close,
            },
            -1,
        )

    def dummy(self):
        self.session.open(MessageBox, _("This button is not linked yet."), MessageBox.TYPE_INFO, timeout=3)

    def update_subscription_list(self):
        labels = self.get_subscription_labels()
        items = []
        if labels == "No subscription files found.":
            items.append(("No subscription files found.", ""))
        else:
            for line in labels.split("\n\n"):
                parts = line.split("--->")
                if len(parts) == 2:
                    items.append((parts[1].strip(), parts[1].strip()))
        self.sub_labels_list.setList(items)

    def print_selected_label(self):
        selected = self.sub_labels_list.getCurrent()
        if selected:
            label_name = selected[1]
            print("Selected label:", label_name)
            self.session.open(MessageBox, _("Selected: %s" % label_name), MessageBox.TYPE_INFO, 3)

    def read_labels_from_file(self, path):
        found = []
        try:
            with open(path, "r") as f:
                content = f.read()
            # Split content into [reader] blocks
            reader_blocks = re.findall(r"\[reader\](.*?)(?=\n\[|$)", content, re.DOTALL | re.IGNORECASE)
            for block in reader_blocks:
                label_match = re.search(r"label\s*=\s*(.+)", block, re.IGNORECASE)
                user_match = re.search(r"user\s*=\s*(.+)", block, re.IGNORECASE)
                password_match = re.search(r"password\s*=\s*(.+)", block, re.IGNORECASE)
                
                # Only show if user or password is present
                if label_match and (user_match or password_match):
                    label_text = label_match.group(1).strip()
                    found.append(f"{path} ---> {label_text}\n")
        except Exception as e:
            found.append(f"{path} ERROR: {str(e)}\n")
        return found

    def get_subscription_labels(self):
        # Directories and files
        dirs = ["/media/hdd/ElieSatPanel", "/media/usb/ElieSatPanel", "/media/mmc/ElieSatPanel"]
        files = ["subscription.txt"]
        # Full file paths
        single_files = ["/etc/tuxbox/config/oscam.server", "/etc/tuxbox/config/ncam.server"]

        labels_found = []

        # Read from directories
        for d in dirs:
            for fname in files:
                path = os.path.join(d, fname)
                if os.path.exists(path):
                    labels_found.extend(self.read_labels_from_file(path))

        # Read from single file paths
        for path in single_files:
            if os.path.exists(path):
                labels_found.extend(self.read_labels_from_file(path))

        if not labels_found:
            return "No subscription files found."
        return "\n\n".join(labels_found)

# -*- coding: utf-8 -*-
import os
import re
import socket
from datetime import datetime
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Plugins.Extensions.ElieSatPanel.__init__ import Version
from Plugins.Extensions.ElieSatPanel.menus.Helpers import (
    get_local_ip, check_internet, get_image_name,
    get_python_version, get_storage_info, get_ram_info
)

class BlueJobScreen(Screen):
    skin = """
    <screen name="BlueJobScreen" position="0,0" size="1920,1080" backgroundColor="transparent" flags="wfNoBorder" title="Scripts">
        <ePixmap position="0,0" zPosition="-1" size="1920,1080"
            pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/background/panel_bg.png"/>
        <eLabel position="0,0" size="1920,130" zPosition="10" backgroundColor="#000000" />
        <eLabel text="● Subscription Reader Labels"
            position="350,0" size="800,50" zPosition="11"
            font="Bold;32" halign="left" valign="center" noWrap="1"
            foregroundColor="yellow" backgroundColor="#000000" transparent="0" />
        <widget name="clock" position="1250,0" size="650,50" zPosition="11"
            font="Bold;32" halign="right" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />
        <eLabel position="0,1075" size="480,5" zPosition="2" backgroundColor="red" />
        <widget name="red" position="0,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Red Button"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />
        <eLabel position="480,1075" size="480,5" zPosition="2" backgroundColor="green" />
        <widget name="green" position="480,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Green Button"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />
        <eLabel position="960,1075" size="480,5" zPosition="2" backgroundColor="yellow" />
        <widget name="yellow" position="960,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Yellow Button"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />
        <eLabel position="1440,1075" size="480,5" zPosition="2" backgroundColor="blue" />
        <widget name="blue" position="1440,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Blue Button"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />
        <eLabel position="0,130" size="80,870" zPosition="10" backgroundColor="#000000" />
        <eLabel position="1840,130" size="80,870" zPosition="10" backgroundColor="#000000" />
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
        <widget name="image_name" position="1470,420" size="500,35" font="Bold;32" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <widget name="python_ver" position="1470,460" size="500,35" font="Bold;32" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <widget name="local_ip" position="1470,500" size="500,35" font="Bold;32" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <widget name="StorageInfo" position="1470,540" size="500,35" font="Bold;32" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <widget name="RAMInfo" position="1470,580" size="500,35" font="Bold;32" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <widget name="net_status" position="1470,620" size="500,35" font="Bold;32" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <widget name="left_bar" position="20,160" size="60,760" font="Regular;26" halign="center" valign="top" foregroundColor="yellow" transparent="1" noWrap="1" />
        <widget name="right_bar" position="1850,160" size="60,760" font="Regular;26" halign="center" valign="top" foregroundColor="yellow" transparent="1" noWrap="1" />
        <widget name="sub_labels" position="200,200" size="1200,700" zPosition="12"
            scrollbarMode="showOnDemand"
            font="Bold;30"
            foregroundColor="yellow"
            transparent="1"
            itemHeight="50" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.setTitle(_("Subscription Labels"))

        # Left/Right vertical bars
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

        # Clock
        now = datetime.now().strftime("%Y-%m-%d  %H:%M")
        self["clock"] = Label(now)

        # Subscription labels list
        self.sub_labels_list = MenuList([], enableWrapAround=True)
        self["sub_labels"] = self.sub_labels_list
        self.update_subscription_list()

        # Buttons
        self["red"] = Label(_("Remove Reader"))
        self["green"] = Label(_("Show Reader"))
        self["yellow"] = Label(_("Test Connection"))
        self["blue"] = Label(_("Show Reader Details"))

        # Actions
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {
                "red": self.remove_selected_reader,
                "green": self.show_selected_reader,
                "yellow": self.test_selected_connection,
                "blue": self.show_reader_details,
                "ok": self.print_selected_label,
                "cancel": self.close,
            },
            -1,
        )

    # ---------------- Subscription List ----------------

    def update_subscription_list(self):
        labels = self.get_subscription_labels()
        items = []
        if labels == "No subscription files found.":
            items.append(("No subscription files found.", ""))
        else:
            for line in labels.split("\n\n"):
                items.append((line.strip(), line.strip()))
        self.sub_labels_list.setList(items)

    def print_selected_label(self):
        selected = self.sub_labels_list.getCurrent()
        if selected:
            label_name = selected[1]
            self.session.open(MessageBox, _("Selected: %s" % label_name), MessageBox.TYPE_INFO, 3)

    # ---------------- File Reading ----------------

    def read_labels_from_file(self, path):
        found = []
        try:
            with open(path, "r") as f:
                content = f.read()
            reader_blocks = re.findall(r"\[reader\](.*?)(?=\n\[|$)", content, re.DOTALL | re.IGNORECASE)
            for block in reader_blocks:
                label_match = re.search(r"label\s*=\s*(.+)", block, re.IGNORECASE)
                user_match = re.search(r"user\s*=\s*(.+)", block, re.IGNORECASE)
                password_match = re.search(r"password\s*=\s*(.+)", block, re.IGNORECASE)
                if label_match and (user_match or password_match):
                    label_text = label_match.group(1).strip()
                    directory = os.path.dirname(path)
                    found.append(f"{label_text} ---> {directory}")
        except Exception as e:
            found.append(f"{path} ERROR: {str(e)}")
        return found

    def get_subscription_labels(self):
        dirs = ["/media/hdd/ElieSatPanel", "/media/usb/ElieSatPanel", "/media/mmc/ElieSatPanel"]
        files = ["subscription.txt"]
        single_files = ["/etc/tuxbox/config/oscam.server", "/etc/tuxbox/config/ncam.server"]

        labels_found = []

        for d in dirs:
            for fname in files:
                path = os.path.join(d, fname)
                if os.path.exists(path):
                    labels_found.extend(self.read_labels_from_file(path))

        for path in single_files:
            if os.path.exists(path):
                labels_found.extend(self.read_labels_from_file(path))

        if not labels_found:
            return "No subscription files found."
        return "\n\n".join(labels_found)

    # ---------------- Button Actions ----------------

    def remove_selected_reader(self):
        selected = self.sub_labels_list.getCurrent()
        if not selected or "--->" not in selected[1]:
            return

        label_line = selected[1]
        label_name = label_line.split("--->")[0].strip()
        path = label_line.split("--->")[1].strip()
        file_path = os.path.join(path, "subscription.txt")

        if not os.path.exists(file_path):
            self.session.open(MessageBox, _("File not found."), MessageBox.TYPE_ERROR, 3)
            return

        try:
            with open(file_path, "r") as f:
                content = f.read()

            reader_blocks = re.findall(r"(\[reader\].*?)(?=\n\[|$)", content, re.DOTALL | re.IGNORECASE)
            new_blocks = []
            removed = False
            for block in reader_blocks:
                match = re.search(r"label\s*=\s*(.+)", block, re.IGNORECASE)
                if match and match.group(1).strip() == label_name:
                    removed = True
                else:
                    new_blocks.append(block.strip())

            if not removed:
                self.session.open(MessageBox, _("Selected reader not found in file."), MessageBox.TYPE_ERROR, 3)
                return

            with open(file_path, "w") as f:
                f.write("\n\n".join(new_blocks))

            self.update_subscription_list()
            self.session.open(MessageBox, _("Reader removed successfully."), MessageBox.TYPE_INFO, 3)

        except Exception as e:
            self.session.open(MessageBox, _("Error removing reader: %s" % str(e)), MessageBox.TYPE_ERROR, 5)

    def show_selected_reader(self):
        selected = self.sub_labels_list.getCurrent()
        if not selected or "--->" not in selected[1]:
            return

        label_line = selected[1]
        label_name = label_line.split("--->")[0].strip()
        path = label_line.split("--->")[1].strip()
        file_path = os.path.join(path, "subscription.txt")

        if not os.path.exists(file_path):
            self.session.open(MessageBox, _("File not found."), MessageBox.TYPE_ERROR, 3)
            return

        try:
            with open(file_path, "r") as f:
                content = f.read()

            reader_blocks = re.findall(r"(\[reader\].*?)(?=\n\[|$)", content, re.DOTALL | re.IGNORECASE)
            for block in reader_blocks:
                match = re.search(r"label\s*=\s*(.+)", block, re.IGNORECASE)
                if match and match.group(1).strip() == label_name:
                    self.session.open(MessageBox, _(block.strip()), MessageBox.TYPE_INFO, 10)
                    return

            self.session.open(MessageBox, _("Reader not found."), MessageBox.TYPE_ERROR, 3)

        except Exception as e:
            self.session.open(MessageBox, _("Error showing reader: %s" % str(e)), MessageBox.TYPE_ERROR, 5)

    def test_selected_connection(self):
        selected = self.sub_labels_list.getCurrent()
        if not selected or "--->" not in selected[1]:
            return

        label_line = selected[1]
        label_name = label_line.split("--->")[0].strip()
        path = label_line.split("--->")[1].strip()
        file_path = os.path.join(path, "subscription.txt")

        if not os.path.exists(file_path):
            self.session.open(MessageBox, _("File not found."), MessageBox.TYPE_ERROR, 3)
            return

        try:
            with open(file_path, "r") as f:
                content = f.read()

            reader_blocks = re.findall(r"(\[reader\].*?)(?=\n\[|$)", content, re.DOTALL | re.IGNORECASE)
            for block in reader_blocks:
                match = re.search(r"label\s*=\s*(.+)", block, re.IGNORECASE)
                if match and match.group(1).strip() == label_name:
                    device_match = re.search(r"device\s*=\s*([\w\.-]+),(\d+)", block, re.IGNORECASE)
                    if device_match:
                        host, port = device_match.group(1).strip(), int(device_match.group(2).strip())
                        try:
                            sock = socket.create_connection((host, port), timeout=3)
                            sock.close()
                            self.session.open(MessageBox, _("Connection OK: %s:%d" % (host, port)), MessageBox.TYPE_INFO, 3)
                        except Exception as e:
                            self.session.open(MessageBox, _("Connection failed: %s" % str(e)), MessageBox.TYPE_ERROR, 5)
                    else:
                        self.session.open(MessageBox, _("No device info found."), MessageBox.TYPE_ERROR, 3)
                    return

            self.session.open(MessageBox, _("Reader not found."), MessageBox.TYPE_ERROR, 3)

        except Exception as e:
            self.session.open(MessageBox, _("Error testing connection: %s" % str(e)), MessageBox.TYPE_ERROR, 5)

    def show_reader_details(self):
        selected = self.sub_labels_list.getCurrent()
        if not selected or "--->" not in selected[1]:
            return

        label_line = selected[1]
        label_name = label_line.split("--->")[0].strip()
        path = label_line.split("--->")[1].strip()
        file_path = os.path.join(path, "subscription.txt")

        if not os.path.exists(file_path):
            self.session.open(MessageBox, _("File not found."), MessageBox.TYPE_ERROR, 3)
            return

        try:
            with open(file_path, "r") as f:
                content = f.read()

            reader_blocks = re.findall(r"(\[reader\].*?)(?=\n\[|$)", content, re.DOTALL | re.IGNORECASE)
            for block in reader_blocks:
                match = re.search(r"label\s*=\s*(.+)", block, re.IGNORECASE)
                if match and match.group(1).strip() == label_name:
                    details = []
                    for key in ["label", "status", "protocol", "device", "user", "password"]:
                        m = re.search(r"%s\s*=\s*(.+)" % key, block, re.IGNORECASE)
                        if m:
                            details.append("%s: %s" % (key.capitalize(), m.group(1).strip()))
                    if details:
                        self.session.open(MessageBox, _("\n".join(details)), MessageBox.TYPE_INFO, 10)
                    else:
                        self.session.open(MessageBox, _("No details found."), MessageBox.TYPE_ERROR, 3)
                    return

            self.session.open(MessageBox, _("Reader not found."), MessageBox.TYPE_ERROR, 3)

        except Exception as e:
            self.session.open(MessageBox, _("Error showing details: %s" % str(e)), MessageBox.TYPE_ERROR, 5)

