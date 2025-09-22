# -*- coding: utf-8 -*-
import os
from os import chmod
from os.path import exists, join
from random import choice
from requests import get, exceptions

from Screens.Screen import Screen
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from enigma import getDesktop
from Plugins.Extensions.ElieSatPanel.menus.Helpers import (
    get_local_ip,
    check_internet,
    get_image_name,
    get_python_version,
    get_storage_info,
    get_ram_info,
)
from Plugins.Extensions.ElieSatPanel.__init__ import Version

scriptpath = "/usr/script/"
if not os.path.exists(scriptpath):
    os.makedirs(scriptpath, exist_ok=True)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/93.0.4577.82 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0"
]

SCRIPT_TARBALL_URL = "https://raw.githubusercontent.com/eliesat/scripts/main/installer.tar"


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
    # Script execution via Console
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

        # Open Console screen
        self.session.open(Console, _("Executing: {}").format(script), cmdlist=[cmd])

    # -------------------------
    # Other actions
    # -------------------------
    def restart(self):
        self.session.open(Console, _("Restarting Enigma2..."), ["killall -9 enigma2"])

    def bgrun(self):
        # Run in background with Console screen
        script = self["list"].getCurrent()
        if not script:
            self.session.open(MessageBox, _("No script selected!"), MessageBox.TYPE_INFO)
            return

        full_path = os.path.join(scriptpath, script)
        if full_path.endswith(".sh"):
            chmod(full_path, 0o755)
            cmd = full_path
        else:
            cmd = "python " + full_path

        self.session.open(Console, _("Background Script: {}").format(script), cmdlist=[cmd])

    def remove(self):
        self.session.openWithCallback(self.xremove, MessageBox, _('Remove all scripts?'), MessageBox.TYPE_YESNO)

    def xremove(self, answer=False):
        if answer:
            for f in os.listdir(scriptpath):
                os.remove(os.path.join(scriptpath, f))
            self.loadScripts()
            self.session.open(MessageBox, _('Scripts removed!'), MessageBox.TYPE_INFO)

    def update(self):
        dest = '/tmp/scripts.tar'
        try:
            headers = {"User-Agent": choice(USER_AGENTS)}
            response = get(SCRIPT_TARBALL_URL, headers=headers, timeout=10)
            response.raise_for_status()
            with open(dest, 'wb') as f:
                f.write(response.content)
            os.system("tar -xf {} -C '{}'".format(dest, scriptpath))
            os.remove(dest)
            for script in os.listdir(scriptpath):
                if script.endswith(".sh"):
                    os.chmod(os.path.join(scriptpath, script), 0o755)
            self.loadScripts()
            self.session.open(MessageBox, _("Scripts updated successfully!"), MessageBox.TYPE_INFO)
        except exceptions.RequestException as e:
            self.session.open(MessageBox, _("Network error: %s") % str(e), MessageBox.TYPE_ERROR)
        except Exception as e:
            self.session.open(MessageBox, str(e), MessageBox.TYPE_ERROR)

