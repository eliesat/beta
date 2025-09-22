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
from Tools.LoadPixmap import LoadPixmap
from enigma import eSize, getDesktop

scriptpath = "/usr/script/"
if not os.path.exists(scriptpath):
    os.makedirs(scriptpath, exist_ok=True)

class Scripts(Screen):
    def __init__(self, session):
        # Detect resolution and load appropriate skin
        width, height = getDesktop(0).size().width(), getDesktop(0).size().height()
        if width >= 1920:
            skin_file = "/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/skin/scripts_fhd.xml"
        else:
            skin_file = "/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/skin/scripts_hd.xml"

        # Load skin from XML
        with open(skin_file, "r") as f:
            self.skin = f.read()

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

