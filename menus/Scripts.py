# -*- coding: utf-8 -*-
import os
from os import chmod
from os.path import exists, join
from random import choice
from requests import get, exceptions

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.ScrollLabel import ScrollLabel
from enigma import eConsoleAppContainer, getDesktop
from Plugins.Extensions.ElieSatPanel.menus.Helpers import (
    get_local_ip,
    check_internet,
    get_image_name,
    get_python_version,
    get_storage_info,
    get_ram_info,
)
from Plugins.Extensions.ElieSatPanel.__init__ import Version
from Plugins.Extensions.ElieSatPanel.menus.Console import Console
scriptpath = "/usr/script/"
if not os.path.exists(scriptpath):
    os.makedirs(scriptpath, exist_ok=True)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/93.0.4577.82 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0"
]

class Scripts(Screen):
    def __init__(self, session):
        # Load correct skin
        width, height = getDesktop(0).size().width(), getDesktop(0).size().height()
        skin_file = "/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/skin/scripts_fhd.xml" \
            if width >= 1920 else "/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/skin/scripts_hd.xml"
        with open(skin_file, "r") as f:
            self.skin = f.read()

        Screen.__init__(self, session)
        self.session = session
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

        # Console output area
        self["console"] = ScrollLabel("")
        self.container = None

        # Actions
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {
                "ok": self.run,        # run with console
                "green": self.update,  # green keeps original function
                "yellow": self.bgrun,  # run in background
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

    # -------------------------
    # Scripts list
    # -------------------------
    def loadScripts(self):
        self.scripts = []
        if os.path.exists(scriptpath):
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
        idx = min(len(self.scripts) - 1, self["list"].getCurrentIndex() + self.items_per_page)
        self["list"].setIndex(idx)
        self.updateSelection()

    # -------------------------
    # Script execution with embedded console (OK button)
    # -------------------------
    def run(self):
        script = self["list"].getCurrent()
        if not script:
            self.session.open(MessageBox, _("No script selected!"), MessageBox.TYPE_INFO)
            return

        full_path = os.path.join(scriptpath, script)
        if not os.path.exists(full_path):
            self.session.open(MessageBox, _("Script not found!"), MessageBox.TYPE_ERROR)
            return

        if full_path.endswith(".sh"):
            chmod(full_path, 0o755)
            cmd = full_path
        else:
            cmd = "python " + full_path

        # Clear console
        self["console"].setText("")
        self.container = eConsoleAppContainer()
        try:
            self.container.dataAvail.append(self.logData)
        except:
            self.container.dataAvail_conn = self.container.dataAvail.connect(self.logData)
        try:
            self.container.appClosed.append(self.finishExecution)
        except:
            self.container.appClosed_conn = self.container.appClosed.connect(self.finishExecution)

        self.container.execute(cmd)

    def logData(self, data):
        text = data.decode()
        old = self["console"].getText()
        new_text = old + text
        self["console"].setText(new_text)

    def finishExecution(self, retval):
        if retval == 0:
            self.session.open(MessageBox, _("Execution completed!"), MessageBox.TYPE_INFO)
        else:
            self.session.open(MessageBox, _("Error while running (Code: %d)") % retval, MessageBox.TYPE_ERROR)

    # -------------------------
    # Yellow button: run in background silently
    # -------------------------
    def bgrun(self):
        script = self["list"].getCurrent()
        if not script:
            self.session.open(MessageBox, _("No script selected!"), MessageBox.TYPE_INFO)
            return

        full_path = os.path.join(scriptpath, script)
        if not exists(full_path):
            self.session.open(MessageBox, _("Script not found!"), MessageBox.TYPE_ERROR)
            return

        if full_path.endswith(".sh"):
            chmod(full_path, 0o755)
            cmd = "{} &".format(full_path)
        else:
            cmd = "python {} &".format(full_path)

        os.system(cmd)
        self.session.open(MessageBox, _("Script is running in background!"), MessageBox.TYPE_INFO, timeout=3)

    # -------------------------
    # Other actions
    # -------------------------
    def restart(self):
        self.session.open(Console, _("Restarting Enigma2..."), ["killall -9 enigma2"])

    def remove(self):
        self.session.openWithCallback(self.xremove, MessageBox, _('Remove all scripts?'), MessageBox.TYPE_YESNO)

    def xremove(self, answer=False):
      os.system('rm -rf /usr/script/*')
      self.session.open(MessageBox,(_("Remove of scripts lists is done , press the green button to reinstall")), MessageBox.TYPE_INFO, timeout = 4 )

    def update(self):
      self.session.open(Console, _("Installing scripts please wait..."), [
            "wget --no-check-certificate https://raw.githubusercontent.com/eliesat/scripts/main/installer.sh -qO - | /bin/sh"
        ])
