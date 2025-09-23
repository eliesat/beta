# -*- coding: utf-8 -*-
from Plugins.Extensions.ElieSatPanel.__init__ import Version
from Plugins.Extensions.ElieSatPanel.menus.Console import Console
from Plugins.Extensions.ElieSatPanel.menus.Iptvadder import Iptvadder
from Plugins.Extensions.ElieSatPanel.menus.Cccamadder import Cccamadder
from Plugins.Extensions.ElieSatPanel.menus.News import News
from Plugins.Extensions.ElieSatPanel.menus.Scripts import Scripts
from Plugins.Extensions.ElieSatPanel.menus.Addons import Addons
from Plugins.Extensions.ElieSatPanel.menus.Display import Display
from Plugins.Extensions.ElieSatPanel.menus.Feeds import Feeds
from Plugins.Extensions.ElieSatPanel.menus.Imagesdownload import Imagesdownload
from Plugins.Extensions.ElieSatPanel.menus.Imagesbackup import Imagesbackup
from Plugins.Extensions.ElieSatPanel.menus.Picons import Picons
from Plugins.Extensions.ElieSatPanel.menus.Settings import Settings
from Plugins.Extensions.ElieSatPanel.menus.Skins import Skins
from Plugins.Extensions.ElieSatPanel.menus.Softcams import Softcams
from Plugins.Extensions.ElieSatPanel.menus.Tools import Tools
from Plugins.Extensions.ElieSatPanel.menus.Toolsp import Toolsp
from Plugins.Extensions.ElieSatPanel.menus.About import Abt
from Plugins.Extensions.ElieSatPanel.menus.Helpers import (
    get_local_ip,
    check_internet,
    get_image_name,
    get_python_version,
    get_storage_info,
    get_ram_info,
)

import os
import socket
import sys
import math
import subprocess
from Plugins.Plugin import PluginDescriptor
from skin import parseColor
from Screens.InputBox import InputBox
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from sys import version_info
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, fileExists
from threading import Timer
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.GUIComponent import GUIComponent
from Components.MultiContent import (
    MultiContentEntryText,
    MultiContentEntryPixmap,
    MultiContentEntryPixmapAlphaTest,
)
from Components.ConfigList import ConfigListScreen
from Components.config import ConfigText, getConfigListEntry
from enigma import (
    eListboxPythonMultiContent,
    eListbox,
    ePixmap,
    eLabel,
    eSize,
    ePoint,
    gFont,
    getDesktop,
    BT_SCALE,
    BT_KEEP_ASPECT_RATIO,
    BT_ALIGN_CENTER,
    RT_HALIGN_CENTER,
    RT_VALIGN_CENTER,
)

PY3 = version_info[0] == 3
try:
    # Python 3
    from urllib.request import Request as compat_Request, urlopen as compat_urlopen
except ImportError:
    # Python 2
    from urllib2 import Request as compat_Request, urlopen as compat_urlopen

installer = 'https://raw.githubusercontent.com/eliesat/beta/main/installer1.sh'

# ---------------- PANEL DIRECTORIES ----------------
PANEL_DIRS = [
    "/media/hdd/ElieSatPanel",   # default
    "/media/usb/ElieSatPanel",
    "/media/mmc/ElieSatPanel"
]
CONFIG_FILE = "/media/hdd/ElieSatPanel/panel_dir.cfg"

def save_last_dir(directory):
    try:
        folder = os.path.dirname(CONFIG_FILE)
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(CONFIG_FILE, "w") as f:
            f.write(directory)
    except Exception as e:
        print("[ElieSatPanel] save_last_dir error:", e)

def load_last_dir():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                dir = f.read().strip()
                if dir in PANEL_DIRS:
                    return dir
    except:
        pass
    return PANEL_DIRS[0]  # default HDD

# Ensure ElieSatPanel folder exists on startup #change here
for folder in PANEL_DIRS:
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
            print(f"[ElieSatPanel] Created folder: {folder}")
        except Exception as e:
            print(f"[ElieSatPanel] Failed to create folder {folder}: {e}")


# ---------------- FLEXIBLE MENU ----------------
class FlexibleMenu(GUIComponent):
    def __init__(self, list_):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.list = list_ or []
        self.entries = dict()
        self.onSelectionChanged = []
        self.current = 0
        self.total_pages = 1

        # Defaults
        self.itemPerPage = 18
        self.columns = 6
        self.margin = 10
        self.boxwidth = 200
        self.boxheight = 220
        self.activeboxwidth = 220
        self.activeboxheight = 240
        self.panelheight = 700

        # pager icons (optional)
        self.ptr_pagerleft = None
        self.ptr_pagerright = None
        try:
            self.ptr_pagerleft = LoadPixmap(
                resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/assets/icon/pager_left.png")
            )
        except Exception:
            self.ptr_pagerleft = None
        try:
            self.ptr_pagerright = LoadPixmap(
                resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/assets/icon/pager_right.png")
            )
        except Exception:
            self.ptr_pagerright = None

        self.itemPixmap = None
        self.selPixmap = None
        self.listWidth = 0
        self.listHeight = 0

        if PY3:
            import html

            self.selectedicon = str(html.unescape("&#xe837;"))
            self.unselectedicon = str(html.unescape("&#xe836;"))
        else:
            try:
                import HTMLParser

                h = HTMLParser.HTMLParser()
                self.selectedicon = str(h.unescape("&#xe837;"))
                self.unselectedicon = str(h.unescape("&#xe836;"))
            except Exception:
                self.selectedicon = "*"
                self.unselectedicon = "."

    def applySkin(self, desktop, parent):
        attribs = []
        for (attrib, value) in getattr(self, "skinAttributes", []):
            if attrib == "itemPerPage":
                try:
                    self.itemPerPage = int(value)
                    if self.itemPerPage % 3 == 0:
                        self.columns = 6 if self.itemPerPage >= 18 else max(1, self.itemPerPage // 2)
                    else:
                        self.columns = max(1, int(self.itemPerPage // 2))
                except Exception:
                    pass
            elif attrib == "panelheight":
                try:
                    self.panelheight = int(value)
                except Exception:
                    pass
            elif attrib == "margin":
                try:
                    self.margin = int(value)
                except Exception:
                    pass
            elif attrib == "boxSize":
                if "," in value:
                    try:
                        self.boxwidth, self.boxheight = [int(v) for v in value.split(",")]
                    except Exception:
                        pass
                else:
                    try:
                        self.boxwidth = self.boxheight = int(value)
                    except Exception:
                        pass
            elif attrib == "activeSize":
                if "," in value:
                    try:
                        self.activeboxwidth, self.activeboxheight = [int(v) for v in value.split(",")]
                    except Exception:
                        pass
                else:
                    try:
                        self.activeboxwidth = self.activeboxheight = int(value)
                    except Exception:
                        pass
            elif attrib == "size":
                try:
                    self.listWidth, self.listHeight = [int(v) for v in value.split(",")]
                    if self.instance:
                        self.instance.resize(eSize(self.listWidth, self.listHeight))
                except Exception:
                    pass
            elif attrib == "itemPixmap":
                try:
                    self.itemPixmap = LoadPixmap(value)
                except Exception:
                    self.itemPixmap = None
            elif attrib == "selPixmap":
                try:
                    self.selPixmap = LoadPixmap(value)
                except Exception:
                    self.selPixmap = None
            else:
                attribs.append((attrib, value))

        self.l.setFont(0, gFont("Bold", 32))
        self.l.setItemHeight(self.panelheight)

        self.skinAttributes = attribs
        self.buildEntry()
        return GUIComponent.applySkin(self, desktop, parent)

    GUI_WIDGET = eListbox

    def postWidgetCreate(self, instance):
        self.instance = instance
        instance.setContent(self.l)
        instance.setSelectionEnable(0)
        instance.setScrollbarMode(eListbox.showNever)

        # Pager controls
        self.pager_left = ePixmap(self.instance)
        self.pager_center = eLabel(self.instance)
        self.pager_right = ePixmap(self.instance)
        self.pagelabel = eLabel(self.instance)

        self.pagelabel.setFont(gFont("Icons", 18))
        self.pagelabel.setVAlign(eLabel.alignCenter)
        self.pagelabel.setHAlign(eLabel.alignCenter)
        self.pagelabel.setBackgroundColor(parseColor("#FF272727"))
        self.pagelabel.setTransparent(1)
        self.pagelabel.setZPosition(100)
        self.pagelabel.move(ePoint(0, self.panelheight - 10))
        self.pagelabel.resize(eSize(1660, 20))

        self.pager_center.setBackgroundColor(parseColor("#00272727"))
        self.pager_left.resize(eSize(20, 20))
        self.pager_right.resize(eSize(20, 20))
        try:
            if self.ptr_pagerleft:
                self.pager_left.setPixmap(self.ptr_pagerleft)
            if self.ptr_pagerright:
                self.pager_right.setPixmap(self.ptr_pagerright)
        except Exception:
            pass
        try:
            self.pager_left.setScale(2)
            self.pager_right.setScale(2)
            self.pager_left.setAlphatest(2)
            self.pager_right.setAlphatest(2)
        except Exception:
            pass
        self.pager_left.hide()
        self.pager_right.hide()
        self.pager_center.hide()
        self.pagelabel.hide()

    def preWidgetRemove(self, instance):
        instance.setContent(None)
        self.instance = None

    def selectionChanged(self):
        for f in self.onSelectionChanged:
            try:
                f()
            except Exception:
                pass

    def setList(self, list_):
        self.list = list_
        if self.instance:
            self.setL(True)

    def buildEntry(self):
        # clear previous entries
        self.entries.clear()
        if len(self.list) > 0:
            width = self.boxwidth + self.margin
            height = self.boxheight + self.margin
            xoffset = (self.activeboxwidth - self.boxwidth) // 2 if self.activeboxwidth > self.boxwidth else 0
            yoffset = (self.activeboxheight - self.boxheight) // 2 if self.activeboxheight > self.boxheight else 0
            x = 0
            y = 0
            count = 0
            page = 1
            list_dummy = []
            self.total_pages = int(math.ceil(float(len(self.list)) / self.itemPerPage)) if self.itemPerPage > 0 else 1

            for elem in self.list:
                # ensure tuple/list with a name at [0]
                try:
                    name = elem[0]
                except Exception:
                    continue

                if count >= self.itemPerPage:
                    count = 0
                    page += 1
                    y = 0

                logo = None
                try:
                    icon_name = name.lower().replace(" ", "_") + ".png"
                    logoPath = resolveFilename(
                        SCOPE_PLUGINS,
                        "Extensions/ElieSatPanel/assets/compet/icons/{}".format(icon_name),
                    )
                    if not fileExists(logoPath):
                        logoPath = resolveFilename(
                            SCOPE_PLUGINS,
                            "Extensions/ElieSatPanel/assets/compet/icons/default.png",
                        )
                    if fileExists(logoPath):
                        logo = LoadPixmap(logoPath)
                except Exception:
                    logo = None

                self.entries.update({
                    name: {
                        "active": (
                            MultiContentEntryPixmap(
                                pos=(x, y),
                                size=(self.activeboxwidth, self.activeboxheight),
                                png=self.selPixmap,
                                flags=BT_SCALE,
                            ),
                            MultiContentEntryPixmapAlphaTest(
                                pos=(x, y),
                                size=(self.activeboxwidth, self.activeboxheight - 40),
                                png=logo,
                                flags=BT_SCALE | BT_ALIGN_CENTER | BT_KEEP_ASPECT_RATIO,
                            ),
                            MultiContentEntryText(
                                pos=(x, y + self.activeboxheight - 35),
                                size=(self.activeboxwidth, 30),
                                font=0,
                                text=name,
                                flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                               color=0x00FF8C00
                            ),
                        ),
                        "u_active": (
                            MultiContentEntryPixmap(
                                pos=(x + xoffset, y + yoffset),
                                size=(self.boxwidth, self.boxheight),
                                png=self.itemPixmap,
                                flags=BT_SCALE,
                            ),
                            MultiContentEntryPixmapAlphaTest(
                                pos=(x + xoffset, y + yoffset),
                                size=(self.boxwidth, self.boxheight - 40),
                                png=logo,
                                flags=BT_SCALE | BT_ALIGN_CENTER | BT_KEEP_ASPECT_RATIO,
                            ),
                            MultiContentEntryText(
                                pos=(x + xoffset, y + yoffset + self.boxheight - 45),
                                size=(self.boxwidth, 30),
                                font=0,
                                text=name,
                                flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                            ),
                        ),
                        "page": page,
                    }
                })

                x += width
                list_dummy.append(name)
                if len(list_dummy) == self.columns:
                    list_dummy[:] = []
                    x = 0
                    y += height
                count += 1

        # update visual list
        self.setL()

    def setL(self, refresh=False):
        if refresh:
            self.entries.clear()
            self.setpage()
            self.buildEntry()
            return
        if len(self.entries) > 0 and len(self.list) > 0:
            res = [None]
            if self.current > (len(self.list) - 1):
                self.current = (len(self.list) - 1)
            try:
                current = self.entries[self.list[self.current][0]]
            except Exception:
                # fallback to first entry
                first_key = next(iter(self.entries))
                current = self.entries[first_key]
                self.current = 0
            current_page = current["page"]
            for _, value in self.entries.items():
                if current_page == value["page"] and value != current:
                    res.extend(value["u_active"])
            res.extend(current["active"])
            self.l.setList([res])
            self.setpage()
        else:
            # no items: clear list
            self.l.setList([])

    def setpage(self):
        if self.total_pages > 1:
            self.pagetext = ""
            if len(self.list) > 0:
                for i in range(1, self.total_pages + 1):
                    if self.getCurrentPage() > 0 and i == self.getCurrentPage():
                        self.pagetext += " " + self.selectedicon
                    else:
                        self.pagetext += " " + self.unselectedicon
                self.pagetext += " "
            self.pagelabel.setText(self.pagetext)
            try:
                w = int(self.pagelabel.calculateSize().width() / 2)
            except Exception:
                w = 100
            if self.total_pages > 1:
                y = self.panelheight - 10
                try:
                    self.pager_center.resize(eSize((w * 2), 20))
                    self.pager_center.move(ePoint((self.listWidth // 2) - w + 20, y))
                    self.pager_left.move(ePoint((self.listWidth // 2) - w, y))
                    self.pager_right.move(ePoint((self.listWidth // 2) + (w - 16), y))
                except Exception:
                    pass
                self.pager_left.show()
                self.pager_right.show()
                self.pager_center.show()
                self.pagelabel.show()
        else:
            try:
                self.pager_left.hide()
                self.pager_right.hide()
                self.pager_center.hide()
                self.pagelabel.hide()
            except Exception:
                pass

    def getCurrentPage(self):
        if len(self.entries) > 0 and len(self.list) > 0:
            if self.current > (len(self.list) - 1):
                self.current = (len(self.list) - 1)
            current = self.entries.get(self.list[self.current][0], None)
            if current:
                return current["page"]
        return 0

    def left(self):
        self.move(1, "backwards")

    def right(self):
        self.move(1, "forward")

    def up(self):
        self.move(self.columns, "backwards")

    def down(self):
        if len(self.list) > 0:
            if self.current + self.columns > (len(self.list) - 1) and self.current != (len(self.list) - 1):
                self.current = len(self.list) - 1
                self.setL()
                self.selectionChanged()
            else:
                self.move(self.columns, "forward")

    def move(self, step, direction):
        if len(self.list) > 0:
            if direction == "backwards":
                self.current -= step
            else:
                self.current += step
            if self.current > (len(self.list) - 1):
                self.current = 0
            if self.current < 0:
                self.current = len(self.list) - 1
            self.setL()
            self.selectionChanged()

    def getCurrent(self):
        if len(self.list) > 0:
            return self.list[self.current]

    def getSelectedIndex(self):
        return self.current

    def setIndex(self, index):
        self.current = index
        if self.instance:
            self.setL()

# ---------------- PANEL MANAGER SCREEN ----------------

class PanelManager(Screen):
    skin = """
    <screen name="PanelManager" position="center,center" size="1280,720" title="">
        <!-- Background -->
        <ePixmap position="0,0" zPosition="-1" size="1280,720"
            pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/background/panel_bg.png"/>

        <!-- Custom Title -->
        <widget name="title_custom" position="40,20" size="1200,50" font="Bold;34"
            foregroundColor="yellow" backgroundColor="#000000" transparent="0" />

        <!-- Label for Default Folder -->
        <widget name="dir_label" position="40,100" size="400,50" font="Bold;34"
            foregroundColor="white" backgroundColor="#000000" transparent="0" />

        <!-- Current Directory (aligned right) -->
        <widget name="dir" position="460,100" size="780,50" font="Bold;34"
            foregroundColor="yellow" backgroundColor="#000000" transparent="0" />

        <!-- Colored Buttons at the bottom -->
        <ePixmap pixmap="skin_default/buttons/red.png" position="100,650" size="140,40" alphatest="on"/>
        <ePixmap pixmap="skin_default/buttons/green.png" position="350,650" size="140,40" alphatest="on"/>
        <ePixmap pixmap="skin_default/buttons/yellow.png" position="600,650" size="140,40" alphatest="on"/>
        <ePixmap pixmap="skin_default/buttons/blue.png" position="850,650" size="140,40" alphatest="on"/>

        <!-- Labels for each button -->
        <widget name="red_label" position="100,690" size="140,40" font="Bold;24" halign="center" foregroundColor="white" transparent="1"/>
        <widget name="green_label" position="350,690" size="140,40" font="Bold;24" halign="center" foregroundColor="white" transparent="1"/>
        <widget name="yellow_label" position="600,690" size="140,40" font="Bold;24" halign="center" foregroundColor="white" transparent="1"/>
        <widget name="blue_label" position="850,690" size="140,40" font="Bold;24" halign="center" foregroundColor="white" transparent="1"/>
    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.dir_index = PANEL_DIRS.index(load_last_dir())
        self.current_dir = PANEL_DIRS[self.dir_index]

        # Custom title
        self["title_custom"] = Label("Panel Manager")

        # Static label
        self["dir_label"] = Label("Default Folder Path:")

        # Dynamic current directory
        self["dir"] = Label(self.current_dir)

        # Button labels
        self["red_label"] = Label("Apply")
        self["green_label"] = Label("Browse")
        self["yellow_label"] = Label("Cycle")
        self["blue_label"] = Label("Exit")

        # Actions
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "DirectionActions"],
            {
                "ok": self.apply_dir,
                "red": self.apply_dir,       # Apply directory
                "green": self.browse_dir,    # Browse folder
                "yellow": self.cycle_right,  # Yellow cycles forward
                "blue": self.close,          # Exit
                "cancel": self.close,
                "left": self.cycle_left,     # Left = cycle backward
                "right": self.cycle_right    # Right = cycle forward
            }, -1
        )

    # --- Apply / create directory ---
    def apply_dir(self):
        try:
            if not os.path.exists(self.current_dir):
                os.makedirs(self.current_dir)
            save_last_dir(self.current_dir)
            self.session.open(MessageBox, f"Directory applied:\n{self.current_dir}", MessageBox.TYPE_INFO)
        except Exception as e:
            self.session.open(MessageBox, f"Failed to create folder:\n{e}", MessageBox.TYPE_ERROR)
        self.close()

    # --- Browse directory ---
    def browse_dir(self):
        try:
            from Screens.FileBrowser import FileBrowser
            if os.path.exists(self.current_dir):
                self.session.openWithCallback(self.folder_selected, FileBrowser, directory=self.current_dir, type=FileBrowser.TYPE_DIR)
            else:
                self.session.open(MessageBox, f"Directory does not exist:\n{self.current_dir}", MessageBox.TYPE_ERROR)
        except Exception as e:
            self.session.open(MessageBox, f"Cannot browse folder:\n{e}", MessageBox.TYPE_ERROR)

    # --- Cycle directories left ---
    def cycle_left(self):
        self.dir_index = (self.dir_index - 1) % len(PANEL_DIRS)
        self.current_dir = PANEL_DIRS[self.dir_index]
        self["dir"].setText(self.current_dir)

    # --- Cycle directories right ---
    def cycle_right(self):
        self.dir_index = (self.dir_index + 1) % len(PANEL_DIRS)
        self.current_dir = PANEL_DIRS[self.dir_index]
        self["dir"].setText(self.current_dir)

    # --- Callback after folder selection ---
    def folder_selected(self, selected):
        if selected:
            self.current_dir = selected
            self["dir"].setText(self.current_dir)

# ---------------- MAIN PANEL ----------------
class EliesatPanel(Screen):
    skin = ""

    def __init__(self, session):
        # Detect screen width
        screen_width = 1280
        try:
            screen_width = getDesktop(0).size().width()
        except Exception:
            pass

        # Load skin file
        base_skin_path = "/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/skin/"
        hd_skin = os.path.join(base_skin_path, "eliesatpanel_hd.xml")
        fhd_skin = os.path.join(base_skin_path, "eliesatpanel_fhd.xml")
        skin_file = hd_skin
        if screen_width >= 1920 and os.path.exists(fhd_skin):
            skin_file = fhd_skin
        elif os.path.exists(hd_skin):
            skin_file = hd_skin
        else:
            skin_file = os.path.join(base_skin_path, "eliesatpanel.xml")

        # Read skin
        try:
            with open(skin_file, "r") as f:
                self.skin = f.read()
        except Exception:
            self.skin = """<screen name="ElieSatPanel" position="center,center" size="1280,720" title="ElieSatPanel">
                <eLabel text="Eliesat Panel - Skin Missing" position="center,center" size="400,50"
                    font="Regular;30" halign="center" valign="center" />
            </screen>"""

        Screen.__init__(self, session)

        # --- Widgets ---
        self["menu"] = FlexibleMenu([])
        self["description"] = Label("")
        self["pageinfo"] = Label("")
        self["pagelabel"] = Label("")

        # --- Color buttons ---
        self["red"] = Label("IPTV Adder")
        self["green"] = Label("Cccam Adder")
        self["yellow"] = Label("News")
        self["blue"] = Label("Scripts")

        # --- System info ---
        self["image_name"] = Label("Image: " + get_image_name())
        self["local_ip"] = Label("IP: " + get_local_ip())
        self["StorageInfo"] = Label(get_storage_info())
        self["RAMInfo"] = Label(get_ram_info())
        self["python_ver"] = Label("Python: " + get_python_version())
        self["net_status"] = Label("Net: " + check_internet())

        # Start update timer
        t = Timer(0.5, self.update_me)
        t.start()

        # --- Panel version / side bars ---
        vertical_left = "\n".join(list("Version " + Version))
        vertical_right = "\n".join(list("By ElieSat"))
        self["left_bar"] = Label(vertical_left)
        self["right_bar"] = Label(vertical_right)

        # --- Menu list ---
        self.menuList = [
            ("Addons", "Manage and install plugins"),
            ("Display", "Change your image bootlogos and spinners"),
            ("Feeds", "Update and install feeds"),
            ("Images-download", "Download new images"),
            ("Images-backup", "Enjoy images updated backups"),
            ("Picons", "Install and manage channel picons"),
            ("Settings", "Try new channels and frequencies"),
            ("Skins", "Choose and apply skins"),
            ("Softcams", "Manage softcams"),
            ("Tools", "Useful tools and extras"),
            ("Tools-panel", "Explore eliesatpanel tools"),
            ("About", "About"),
            ("Extra1", "Extra menu slot 1"),
            ("Extra2", "Extra menu slot 2"),
            ("Extra3", "Extra menu slot 3"),
            ("Extra4", "Extra menu slot 4"),
            ("Extra5", "Extra menu slot 5"),
            ("Extra6", "Extra menu slot 6"),
        ]
        self["menu"].setList(self.menuList)

        # --- Description & page info ---
        self["menu"].onSelectionChanged.append(self.updateDescription)
        self["menu"].onSelectionChanged.append(self.updatePageInfo)
        self.updateDescription()
        self.updatePageInfo()

        # --- Actions ---
        self["setupActions"] = ActionMap(
            ["OkCancelActions", "DirectionActions", "ColorActions", "MenuActions"],
            {
                "cancel": self.close,
                "red": self.openIptvadder,
                "green": self.openCccamadder,
                "yellow": self.openNews,
                "blue": self.openScripts,
                "ok": self.ok,
                "left": self.left,
                "right": self.right,
                "up": self.up,
                "down": self.down,
                "menu": self.open_directory_selector,  # Open directory selector
            },
            -1,
        )

    # --- Navigation ---
    def left(self): self["menu"].left()
    def right(self): self["menu"].right()
    def up(self): self["menu"].up()
    def down(self): self["menu"].down()

    # --- OK press ---
    def ok(self):
        current = self["menu"].getCurrent()
        if current:
            name = current[0]
            submenu_map = {
                "Addons": Addons,
                "Display": Display,
                "Feeds": Feeds,
                "Images-download": Imagesdownload,
                "Images-backup": Imagesbackup,
                "Picons": Picons,
                "Settings": Settings,
                "Skins": Skins,
                "Softcams": Softcams,
                "Tools": Tools,
                "Tools-panel": Toolsp,
                "About": Abt,
            }
            if name in submenu_map:
                self.session.open(submenu_map[name])
            else:
                self.session.open(MessageBox, f"{name} - Coming Soon", type=MessageBox.TYPE_INFO, timeout=5)

    # --- Color button methods ---
    def openIptvadder(self):
        try: self.session.open(Iptvadder)
        except: self.session.open(MessageBox, "Cannot open Iptvadder.", type=MessageBox.TYPE_ERROR, timeout=5)

    def openCccamadder(self):
        try: self.session.open(Cccamadder)
        except: self.session.open(MessageBox, "Cannot open Cccamadder.", type=MessageBox.TYPE_ERROR, timeout=5)

    def openNews(self):
        try: self.session.open(News)
        except: self.session.open(MessageBox, "Cannot open News.", type=MessageBox.TYPE_ERROR, timeout=5)

    def openScripts(self):
        try: self.session.open(Scripts)
        except: self.session.open(MessageBox, "Cannot open Scripts.", type=MessageBox.TYPE_ERROR, timeout=5)

    # --- Menu button ---
    def open_directory_selector(self):
     self.session.open(PanelManager)

    # --- Description / Page info updates ---
    def updateDescription(self):
        current = self["menu"].getCurrent()
        if current:
            self["description"].setText(current[1] if len(current) > 1 else "")

    def updatePageInfo(self):
        currentPage = self["menu"].getCurrentPage()
        totalPages = self["menu"].total_pages
        self["pageinfo"].setText(f"Page {currentPage}/{totalPages}")
        dots = " ".join(["●" if i == currentPage else "○" for i in range(1, totalPages + 1)])
        self["pagelabel"].setText(dots)

    # --- Update handler ---
    def update_me(self):
        try:
            remote_version = '0.0'
            remote_changelog = ''
            req = compat_Request(installer, headers={'User-Agent': 'Mozilla/5.0'})
            page = compat_urlopen(req).read()
            data = page.decode("utf-8") if PY3 else page.encode("utf-8")

            if data:
                for line in data.split("\n"):
                    if line.startswith("version"):
                        remote_version = line.split("'")[1]
                    if line.startswith("changelog"):
                        remote_changelog = line.split("'")[1]
                        break

            if float(Version) < float(remote_version):
                self.session.openWithCallback(
                    self.install_update,
                    MessageBox,
                    _("New version %s is available.\n%s\n\nDo you want to install it now?" %
                      (remote_version, remote_changelog)),
                    MessageBox.TYPE_YESNO
                )
        except Exception as e:
            print("[ElieSatPanel] update_me error:", e)

    def install_update(self, answer=False):
        if answer:
            self.session.open(
                Console,
                title='Updating please wait...',
                cmdlist=['wget -q "--no-check-certificate" ' + installer + ' -O - | /bin/sh'],
                finishedCallback=self.myCallback,
                closeOnSuccess=False
            )

    def myCallback(self, result):
        print("[ElieSatPanel] Update finished:", result)

# ---------------- PLUGIN ENTRY POINTS ----------------
def main(session, **kwargs):
    session.open(EliesatPanel)

def menuHook(menuid, **kwargs):
    if menuid == "mainmenu":
        return [("ElieSatPanel", main, "eliesat_panel", 46)]
    return []

def Plugins(**kwargs):
    return [
        PluginDescriptor(
            name="ElieSatPanel",
            description="enigma2 addons panel",
            where=PluginDescriptor.WHERE_PLUGINMENU,
            icon="assets/icon/panel_logo.png",
            fnc=main,
        ),
        PluginDescriptor(
            name="ElieSatPanel",
            description="enigma2 addons panel",
            where=PluginDescriptor.WHERE_MENU,
            fnc=menuHook,
        ),
        PluginDescriptor(
            name="ElieSatPanel",
            description="enigma2 addons panel",
            where=PluginDescriptor.WHERE_EXTENSIONSMENU,
            fnc=main,
        ),
    ]
