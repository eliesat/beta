# -*- coding: utf-8 -*-
import os
from enigma import eTimer
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
from Components.config import ConfigText, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from Plugins.Extensions.ElieSatPanel.__init__ import Version

class Iptvadder(Screen, ConfigListScreen):
    skin = """
    <screen name="Iptvadder" position="0,0" size="1920,1080" backgroundColor="transparent" flags="wfNoBorder" title="Scripts">
        <ePixmap position="0,0" zPosition="-1" size="1920,1080"
            pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/background/panel_bg.jpg"/>

        <!-- 🔹 Top black bar -->
        <eLabel position="0,0" size="1920,130" zPosition="10" backgroundColor="#000000" />
        <eLabel text="● Subscription Editor"
            position="740,0" size="1400,50" zPosition="11"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <!-- 🔹 Bottom color button bars + labels -->
        <eLabel position="0,1075" size="480,5" zPosition="2" backgroundColor="red" />
        <widget name="red" position="0,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Check Path"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <eLabel position="480,1075" size="480,5" zPosition="2" backgroundColor="green" />
        <widget name="green" position="480,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Restore"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <eLabel position="960,1075" size="480,5" zPosition="2" backgroundColor="yellow" />
        <widget name="yellow" position="960,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Send Backup"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <eLabel position="1440,1075" size="480,5" zPosition="2" backgroundColor="blue" />
        <widget name="blue" position="1440,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Show Credentials"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <!-- 🔹 Left vertical black bar -->
        <eLabel position="0,130" size="80,870" zPosition="10" backgroundColor="#000000" />
        <!-- 🔹 Right vertical black bar -->
        <eLabel position="1840,130" size="80,870" zPosition="10" backgroundColor="#000000" />

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

        <!-- Config List -->
        <widget name="config" position="150,180" size="1100,700"
            font="Bold;32" itemHeight="50"
            foregroundColor="yellow"
            transparent="1" scrollbarMode="showOnDemand"
            enableWrapAround="1" valign="center"
            selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/icon/selection.png"
        />

        <!-- Playlist dirs below Password, same spacing -->
        <widget name="playlists"
            position="160,400" size="1100,200" zPosition="12"
            font="Bold;32" halign="left" valign="top"
            foregroundColor="yellow" backgroundColor="#000000" transparent="1" />

        <!-- Red button result -->
        <widget name="panel_path"
            position="150,780" size="1100,160" zPosition="12"
            font="Bold;32" halign="left" valign="top"
            foregroundColor="yellow" backgroundColor="#000000" transparent="1" />

        <!-- Left/Right bars -->
        <widget name="left_bar"
            position="20,160" size="60,760" zPosition="20"
            font="Regular;26" halign="center" valign="top"
            foregroundColor="yellow" transparent="1" noWrap="1" />
        <widget name="right_bar"
            position="1850,160" size="60,760" zPosition="20"
            font="Regular;26" halign="center" valign="top"
            foregroundColor="yellow" transparent="1" noWrap="1" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.setTitle(_("Subscription Editor"))

        # Editable fields
        self.url = ConfigText(default="http://jepro.online")
        self.port = ConfigText(default="2083")
        self.username = ConfigText(default="user")
        self.password = ConfigText(default="pass")

        clist = [
            getConfigListEntry("URL:", self.url),
            getConfigListEntry("Port:", self.port),
            getConfigListEntry("Username:", self.username),
            getConfigListEntry("Password:", self.password),
        ]
        ConfigListScreen.__init__(self, clist, session=session)
        self["config"].l.setList(clist)

        # Side bar
        self["left_bar"] = Label("\n".join(list("Version " + Version)))
        self["right_bar"] = Label("\n".join(list("By ElieSat")))

        # System info
        self["image_name"] = Label("Image: " + get_image_name())
        self["local_ip"] = Label("IP: " + get_local_ip())
        self["StorageInfo"] = Label(get_storage_info())
        self["RAMInfo"] = Label(get_ram_info())
        self["python_ver"] = Label("Python: " + get_python_version())
        self["net_status"] = Label("Net: " + check_internet())

        # Buttons
        self["red"] = Label(_("Check Path"))
        self["green"] = Label(_("Restore"))
        self["yellow"] = Label(_("Send Backup"))
        self["blue"] = Label(_("Show Credentials"))

        # Playlists and Red button label
        self["playlists"] = Label(self.get_playlists_dirs())
        self["panel_path"] = Label("")

        # Prepare panel_dir & isubscription.txt
        self.panel_dir = self.find_panel_dir()

        # Actions
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {
                "red": self.show_isubscription_path,
                "green": self.restore_reader,
                "yellow": self.send_backup,
                "blue": self.show_credentials,
                "cancel": self.close,
            },
            -1,
        )

    # -----------------------------------------------------
    # Search for panel_dir.cfg and prepare isubscription.txt
    # -----------------------------------------------------
    def find_panel_dir(self):
        search_roots = ["/media/hdd", "/media/mmc"]
        usb_dirs = [os.path.join("/media", d) for d in os.listdir("/media") if d.startswith("usb")]
        search_roots.extend(usb_dirs)

        for root in search_roots:
            path = os.path.join(root, "ElieSatPanel", "panel_dir.cfg")
            if os.path.exists(path):
                folder = os.path.dirname(path)
                subfile = os.path.join(folder, "isubscription.txt")
                if not os.path.exists(subfile):
                    open(subfile, "w").close()
                return folder
        return None

    # --- Red button ---
    def show_isubscription_path(self):
        if self.panel_dir:
            path = os.path.join(self.panel_dir, "isubscription.txt")
            self["panel_path"].setText("isubscription.txt path:\n" + path)
        else:
            self["panel_path"].setText("panel_dir.cfg not found in any folder")

        self.clear_timer = eTimer()
        self.clear_timer.timeout.get().append(self.clear_panel_path)
        self.clear_timer.start(5000, True)

    def clear_panel_path(self):
        self["panel_path"].setText("")

    # --- Green (Restore) ---
    def restore_reader(self):
        self.session.open(MessageBox, "Restore action triggered", MessageBox.TYPE_INFO, timeout=3)

    # --- Yellow (Send Backup) ---
    def send_backup(self):
        self.session.open(MessageBox, "Send Backup action triggered", MessageBox.TYPE_INFO, timeout=3)

    # --- Blue (Show Credentials) ---
    def show_credentials(self):
        self.session.open(MessageBox, f"Username: {self.username.value}\nPassword: {self.password.value}", MessageBox.TYPE_INFO, timeout=5)

    def get_playlists_dirs(self):
        dirs = []
        for root, _, files in os.walk("/etc/enigma2"):
            if "playlists.txt" in files:
                dirs.append(root)
        if not dirs:
            return "Playlists dir:\n<not found>"
        return "Playlists dirs:\n" + "\n".join(dirs[:10])

