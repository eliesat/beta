# -*- coding: utf-8 -*-
from Plugins.Extensions.ElieSatPanel.menus.Helpers import (
    get_local_ip,
    check_internet,
    get_image_name,
    get_python_version,
    get_storage_info,
    get_ram_info,
)
import os
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Tools.Directories import pathExists
from Plugins.Extensions.ElieSatPanel.__init__ import Version

scriptpath = "/usr/script/"
if not os.path.exists(scriptpath):
    os.makedirs(scriptpath, exist_ok=True)

class Scripts(Screen):
    skin = """
    <screen name="Scripts" position="0,0" size="1920,1080" backgroundColor="transparent" flags="wfNoBorder" title="Scripts">
        <ePixmap position="0,0" zPosition="-1" size="1920,1080"
            pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/background/panel_bg.png"/>

        <!-- 🔹 Script list -->
        <widget name="list" position="48,200" size="1240,680"
            font="Bold;32"
            halign="center" valign="center"
            render="Listbox" itemHeight="66"
            foregroundColor="yellow"
            foregroundColorSelected="orange"
            selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/icon/selection.png"
            transparent="1" scrollbarMode="showOnDemand" />

        <!-- 🔹 Selected script bar at top -->
        <widget name="script_name"
            position="48,880" size="1240,50" zPosition="12"
            font="Bold;36" halign="center" valign="center"
            foregroundColor="orange" backgroundColor="#000000"
            transparent="1" />

        <!-- 🔹 Page indicator -->
        <widget name="page_info" position="1650,940" size="200,60" zPosition="12"
            font="Bold;32" halign="center" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="1" />

        <!-- 🔹 Info text -->
        <eLabel text="Select and press OK to execute"
            position="320,125" size="700,50" zPosition="1"
            font="Bold;36" halign="center"
            backgroundColor="#000000" foregroundColor="orange"
            transparent="0" />

        <!-- 🔹 Top black bar -->
        <eLabel position="0,0" size="1920,130" zPosition="10"
            backgroundColor="#000000" />

        <!-- 🔹 Title -->
        <eLabel text="● Scripts Manager – Run, manage and control your scripts"
            position="350,0" size="1400,50" zPosition="11"
            font="Bold;32" halign="left" valign="center" noWrap="1"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <!-- 🔹 Bottom color button bars + labels -->
        <eLabel position="0,1075" size="480,5" zPosition="2" backgroundColor="red" />
        <widget name="red" position="0,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Remove List"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <eLabel position="480,1075" size="480,5" zPosition="2" backgroundColor="green" />
        <widget name="green" position="480,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Update List"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <eLabel position="960,1075" size="480,5" zPosition="2" backgroundColor="yellow" />
        <widget name="yellow" position="960,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Background run"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <eLabel position="1440,1075" size="480,5" zPosition="2" backgroundColor="blue" />
        <widget name="blue" position="1440,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Restart Enigma2"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <!-- 🔹 Left vertical black bar -->
        <eLabel position="0,130" size="80,870" zPosition="10"
            backgroundColor="#000000" />
        <!-- 🔹 Right vertical black bar -->
        <eLabel position="1840,130" size="80,870" zPosition="10"
            backgroundColor="#000000" />

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

        <!-- 🔹 System info -->
        <widget name="image_name" position="1470,420" size="500,35" zPosition="12"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <widget name="python_ver" position="1470,460" size="500,35" zPosition="12"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <widget name="local_ip" position="1470,500" size="500,35" zPosition="12"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <widget name="StorageInfo" position="1470,540" size="500,35" zPosition="12"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <widget name="RAMInfo" position="1470,580" size="500,35" zPosition="12"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000" transparent="1" />
        <widget name="net_status" position="1470,620" size="500,35" zPosition="12"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000" transparent="1" />

        <!-- 🔹 Panel Version LEFT / RIGHT -->
        <widget name="left_bar" position="20,160" size="60,760" zPosition="20"
            font="Regular;26" halign="center" valign="top"
            foregroundColor="yellow" transparent="1" noWrap="1" />
        <widget name="right_bar" position="1850,160" size="60,760" zPosition="20"
            font="Regular;26" halign="center" valign="top"
            foregroundColor="yellow" transparent="1" noWrap="1" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.script = ""
        self.items_per_page = 10
        self.current_page = 1
        self.total_pages = 1
        self.setTitle(_("Scripts Manager"))

        # Vertical bars
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
        self["red"] = Label(_("Remove List"))
        self["green"] = Label(_("Update List"))
        self["yellow"] = Label(_("Background run"))
        self["blue"] = Label(_("Restart Enigma2"))
        self["script_name"] = Label("")
        self["page_info"] = Label("Page 1/1")

        # Actions
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {
                "ok": self.run,
                "green": self.update,
                "yellow": self.bgrun,
                "red": self.remove,
                "blue": self.restart,
                "up": self.moveUp,
                "down": self.moveDown,
                "left": self.pageLeft,
                "right": self.pageRight,
                "cancel": self.close,
            },
            -1,
        )

        # Load scripts
        self.loadScripts()

    def loadScripts(self):
        self.scripts = []
        if pathExists(scriptpath):
            self.scripts = [x for x in os.listdir(scriptpath) if x.endswith(".sh") or x.endswith(".py")]
        self.scripts.sort()
        self["list"] = MenuList(self.scripts)
        self["list"].onSelectionChanged.append(self.updateSelection)
        self.updateSelection()

    def updateSelection(self):
        idx = self["list"].getCurrentIndex()
        total = len(self.scripts)
        self["script_name"].setText(self.scripts[idx] if self.scripts else _("No scripts found"))
        self.total_pages = max(1, (total + self.items_per_page - 1) // self.items_per_page)
        self.current_page = (idx // self.items_per_page) + 1
        self["page_info"].setText("Page %d/%d" % (self.current_page, self.total_pages))

    def moveUp(self):
        self["list"].moveUp()
        self.updateSelection()

    def moveDown(self):
        self["list"].moveDown()
        self.updateSelection()

    def pageLeft(self):
        idx = max(0, self["list"].getCurrentIndex() - self.items_per_page)
        self["list"].setIndex(idx)
        self.updateSelection()

    def pageRight(self):
        idx = min(len(self.scripts)-1, self["list"].getCurrentIndex() + self.items_per_page)
        self["list"].setIndex(idx)
        self.updateSelection()

    def run(self):
        script = self["list"].getCurrent()
        if script:
            full_path = os.path.join(scriptpath, script)
            if full_path.endswith(".sh"):
                os.chmod(full_path, 0o755)
                cmd = full_path
            else:
                cmd = "python " + full_path
            self.session.open(Console, script, cmdlist=[cmd])
            self.loadScripts()

    def restart(self):
        self.session.open(Console, _("Restarting Enigma2..."), ["killall -9 enigma2"])

    def bgrun(self):
        self.session.open(MessageBox, _("Background run executed"), MessageBox.TYPE_INFO, timeout=4)

    def remove(self):
        os.system("rm -rf " + scriptpath + "*")
        self.loadScripts()
        self.session.open(MessageBox, _("All scripts removed. Press Green to reinstall."), MessageBox.TYPE_INFO, timeout=4)

    def update(self):
        self.session.open(Console, _("Installing scripts..."), ["wget --no-check-certificate https://raw.githubusercontent.com/eliesat/scripts/main/installer.sh -qO - | /bin/sh"])
        self.loadScripts()

