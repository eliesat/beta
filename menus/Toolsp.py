# -*- coding: utf-8 -*-
import os
from Screens.Screen import Screen
from Components.Label import Label
from Components.ActionMap import NumberActionMap
from Components.MenuList import MenuList
from Tools.LoadPixmap import LoadPixmap
from Screens.Console import Console
from Plugins.Extensions.ElieSatPanel.__init__ import Version
from Plugins.Extensions.ElieSatPanel.menus.Helpers import (
    get_local_ip,
    check_internet,
    get_image_name,
    get_python_version,
    get_storage_info,
    get_ram_info,
)


class Toolsp(Screen):
    skin = """<screen name="Addons" position="0,0" size="1920,1080"
    backgroundColor="transparent" flags="wfNoBorder" title="ElieSatPanel">
    
    <!-- Background -->
    <ePixmap position="0,0" size="1920,1080" zPosition="1"
        pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/background/panel_bg.png"
        transparent="0" alphatest="blend" />

    <!-- Top black bar -->
    <eLabel position="0,0" size="1920,130" zPosition="10" backgroundColor="#000000" />

    <!-- Title -->
    <eLabel text="● Welcome to ElieSatPanel – Enjoy the best plugins, addons and tools for your E2 box."
        position="350,0" size="1400,50" zPosition="11"
        font="Bold;32" halign="left" valign="center" noWrap="1"
        foregroundColor="yellow" backgroundColor="#000000" transparent="0" />

    <!-- Top info bar -->
    <eLabel position="160,60" size="1690,70" zPosition="11" backgroundColor="#000000" transparent="0" />

    <!-- Info labels -->
    <widget name="image_name" position="180,60" size="350,35" zPosition="12"
        font="Regular;24" halign="left" valign="center"
        foregroundColor="yellow" backgroundColor="#000000" transparent="1" />

    <widget name="local_ip" position="550,60" size="350,35" zPosition="12"
        font="Regular;24" halign="left" valign="center"
        foregroundColor="yellow" backgroundColor="#000000" transparent="1" />

    <widget name="StorageInfo" position="950,60" size="350,35" zPosition="12"
        font="Regular;24" halign="left" valign="center"
        foregroundColor="yellow" backgroundColor="#000000" transparent="1" />

    <widget name="RAMInfo" position="950,95" size="350,35" zPosition="12"
        font="Regular;24" halign="left" valign="center"
        foregroundColor="yellow" backgroundColor="#000000" transparent="1" />

    <widget name="python_ver" position="180,95" size="350,35" zPosition="12"
        font="Regular;24" halign="left" valign="center"
        foregroundColor="yellow" backgroundColor="#000000" transparent="1" />

    <widget name="net_status" position="550,95" size="350,35" zPosition="12"
        font="Regular;24" halign="left" valign="center"
        foregroundColor="yellow" backgroundColor="#000000" transparent="1" />

    <!-- Package description -->
    <widget name="top_description"
        position="350,180" size="1200,35" zPosition="11"
        font="Bold;28" halign="center" valign="center"
        foregroundColor="orange" backgroundColor="#000000"
        transparent="0"
        options="movetype=running,wrap=0" />

    <!-- Date -->
    <widget source="global.CurrentTime" render="Label"
        position="1350,60" size="500,35" zPosition="12"
        font="Regular;24" halign="center" valign="center"
        foregroundColor="yellow" backgroundColor="#000000" transparent="1">
        <convert type="ClockToText">Format %A %d %B</convert>
    </widget>

    <!-- Clock -->
    <widget source="global.CurrentTime" render="Label"
        position="1350,95" size="500,35" zPosition="12"
        font="Regular;24" halign="center" valign="center"
        foregroundColor="yellow" backgroundColor="#000000" transparent="1">
        <convert type="ClockToText">Format %H:%M:%S</convert>
    </widget>

    <!-- Main menu -->
    <widget name="menu"
        position="center,center" size="1660,585" zPosition="5"
        boxSize="240" activeSize="285" panelheight="570"
        itemPerPage="12" margin="30"
        itemPixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/icon/Box_off.png"
        selPixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/icon/Box_on.png"
        foregroundColor="yellow"
        transparent="1" />

    <!-- Bottom buttons -->
    <eLabel position="0,1075" size="480,5" zPosition="2" backgroundColor="red" />
    <widget name="red" position="0,1000" size="480,75" zPosition="2"
        font="Bold;32" halign="center" valign="center"
        text="IPTV Adder" foregroundColor="yellow" backgroundColor="#000000" transparent="0" />

    <eLabel position="480,1075" size="480,5" zPosition="2" backgroundColor="green" />
    <widget name="green" position="480,1000" size="480,75" zPosition="2"
        font="Bold;32" halign="center" valign="center"
        text="Cccam Adder" foregroundColor="yellow" backgroundColor="#000000" transparent="0" />

    <eLabel position="960,1075" size="480,5" zPosition="2" backgroundColor="yellow" />
    <widget name="yellow" position="960,1000" size="480,75" zPosition="2"
        font="Bold;32" halign="center" valign="center"
        text="News" foregroundColor="yellow" backgroundColor="#000000" transparent="0" />

    <eLabel position="1440,1075" size="480,5" zPosition="2" backgroundColor="blue" />
    <widget name="blue" position="1440,1000" size="480,75" zPosition="2"
        font="Bold;32" halign="center" valign="center"
        text="Scripts" foregroundColor="yellow" backgroundColor="#000000" transparent="0" />

    <!-- Side bars -->
    <eLabel position="0,130" size="80,870" zPosition="2" backgroundColor="#000000" transparent="0" />
    <eLabel position="1840,130" size="80,870" zPosition="2" backgroundColor="#000000" transparent="0" />

    <!-- Left / Right bars -->
    <widget name="left_bar" position="20,160" size="60,760" zPosition="20"
        font="Regular;26" halign="center" valign="top"
        backgroundColor="#000000" foregroundColor="yellow" transparent="1" noWrap="1" />
    <widget name="right_bar" position="1850,160" size="60,760" zPosition="20"
        font="Regular;26" halign="center" valign="top"
        backgroundColor="#000000" foregroundColor="yellow" transparent="1" noWrap="1" />

    <!-- Pager dots -->
    <widget name="pagelabel" position="center,800" size="400,30" zPosition="5"
        font="Regular;26" halign="center" valign="center"
        foregroundColor="orange" backgroundColor="#000000" transparent="1" />

    <!-- Page counter -->
    <widget name="pageinfo" position="1600,940" size="340,50"
        font="Bold;32" halign="center" valign="center"
        foregroundColor="yellow" shadowColor="black" shadowOffset="1,1"
        transparent="1" zPosition="5" />

</screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.list = []
        self.status_filter = "Pan"

        # Vertical labels
        self["left_bar"] = Label("\n".join(list("Version " + Version)))
        self["right_bar"] = Label("\n".join(list("By ElieSat")))

        # Info labels
        self["image_name"] = Label(get_image_name())
        self["local_ip"] = Label(get_local_ip())
        self["StorageInfo"] = Label(get_storage_info())
        self["RAMInfo"] = Label(get_ram_info())
        self["python_ver"] = Label(f"Python {get_python_version()}")
        self["net_status"] = Label("Online" if check_internet() else "Offline")

        # Top description
        self["top_description"] = Label("")

        # Menu
        self["menu"] = MenuList([])
        self["pagelabel"] = Label("●")
        self["pageinfo"] = Label("Page 1/1")

        # Colored buttons
        self["red"] = Label("IPTV Adder")
        self["green"] = Label("Cccam Adder")
        self["yellow"] = Label("News")
        self["blue"] = Label("Scripts")

        self["version"] = Label(f"ElieSatPanel {Version}")

        # Actions
        self["setupActions"] = NumberActionMap(
            ["OkCancelActions", "ColorActions", "ShortcutActions"],
            {
                "cancel": self.close,
                "red": lambda: None,
                "green": lambda: None,
                "yellow": lambda: None,
                "blue": lambda: None,
                "ok": self.run_selected,
            },
            -1
        )

        # Load menu
        self.load_list()

    def load_list(self):
        self.list = []
        icon_path = "/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/compet/icons/toolsp.png"
        icon_pixmap = LoadPixmap(icon_path) if os.path.exists(icon_path) else None

        try:
            with open(self.status_path()) as f:
                lines = [line.strip() for line in f if line.strip()]

            pkg_name = pkg_ver = pkg_desc = pkg_url = ""
            for idx, line in enumerate(lines):
                if line.startswith("Package:"):
                    pkg_name = line.split(":", 1)[1].strip()
                    pkg_ver = pkg_desc = pkg_url = ""
                elif line.startswith("Version:"):
                    parts = line.split(None, 2)
                    if len(parts) >= 2:
                        pkg_ver = parts[1].strip()
                    if len(parts) == 3:
                        pkg_desc = parts[2].strip()
                elif line.startswith("Status:") and self.status_filter in line:
                    # Search for URL in following lines
                    for next_line in lines[idx+1:]:
                        if next_line.startswith(pkg_name + "="):
                            pkg_url = next_line.split("=", 1)[1].strip().strip("'").strip('"')
                            break
                    display_name = f"{pkg_name} {pkg_ver}"
                    self.list.append((display_name, icon_pixmap, pkg_url, pkg_desc))

        except Exception as e:
            print("Error loading panel data:", e)

        self.list.sort(key=lambda x: x[0].lower())
        self["menu"].setList(self.list)
        self.update_description()
        self["menu"].onSelectionChanged.append(self.update_description)

    def update_description(self):
        cur = self["menu"].getCurrent()
        if cur:
            _, _, _, pkg_desc = cur
            self["top_description"].setText(pkg_desc)
        else:
            self["top_description"].setText("")

    def run_selected(self):
        cur = self["menu"].getCurrent()
        if not cur:
            return
        display_name, icon, url, _ = cur
        if not url:
            self.session.open(Console, f"No URL found for {display_name}", ["echo 'No URL assigned'"])
            return
        cmd = f"wget --no-check-certificate -O - {url} | /bin/sh"
        self.session.open(Console, f"Running {display_name}", [cmd])

    def status_path(self):
        return "/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/data/panels"

