# -*- coding: utf-8 -*-
import os
import sys
import math
import socket
import subprocess
from sys import version_info
from threading import Timer
import requests
import hashlib

from Plugins.Plugin import PluginDescriptor
from skin import parseColor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.InputBox import InputBox
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, fileExists
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

from Plugins.Extensions.ElieSatPanel.__init__ import Version
from Plugins.Extensions.ElieSatPanel.menus.Console import Console
from Plugins.Extensions.ElieSatPanel.menus.Iptvadder import Iptvadder
from Plugins.Extensions.ElieSatPanel.menus.Cccamadder import Cccamadder
from Plugins.Extensions.ElieSatPanel.menus.News import News
from Plugins.Extensions.ElieSatPanel.menus.Scripts import Scripts
from Plugins.Extensions.ElieSatPanel.menus.Helpers import (
    get_local_ip,
    check_internet,
    get_image_name,
    get_python_version,
    get_storage_info,
    get_ram_info,
)

PY3 = version_info[0] == 3
try:
    from urllib.request import Request as compat_Request, urlopen as compat_urlopen
except ImportError:
    from urllib2 import Request as compat_Request, urlopen as compat_urlopen

installer = 'https://raw.githubusercontent.com/eliesat/beta/main/installer1.sh'

# ---------------- FLEXIBLE MENU ----------------
class FlexibleMenu(GUIComponent):
    """A grid-like flexible menu that accepts a list of (title, description) pairs.

    Fixes applied:
    - Reliable selection callbacks via onSelectionChanged
    - getList() accessor added (avoids undefined getlist errors)
    - Printable pager icons (bullets) to avoid non-printable char issues
    - Defensive normalization of incoming list
    - Preserves stable behavior for selection/page calculations
    """
    def __init__(self, list_=None):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.list = list_ or []
        # normalize list to list of tuples (title, desc)
        self._normalize_list()
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

        # pager icons --- use printable bullets to avoid font/icon issues
        self.selectedicon = "●"
        self.unselectedicon = "○"

        # try to load fancier icons but don't replace printable ones if fails
        try:
            from html import unescape
            s = unescape("&#xe837;")
            u = unescape("&#xe836;")
            # only use them if they are printable (len>0 and not control)
            if s and ord(s[0]) >= 32:
                self.selectedicon = s
            if u and ord(u[0]) >= 32:
                self.unselectedicon = u
        except Exception:
            pass

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

    def _normalize_list(self):
        normalized = []
        for item in (self.list or []):
            try:
                if isinstance(item, (list, tuple)) and len(item) >= 1:
                    title = str(item[0])
                    desc = str(item[1]) if len(item) > 1 else ""
                    normalized.append((title, desc))
                else:
                    normalized.append((str(item), ""))
            except Exception:
                # Skip bad entries
                continue
        self.list = normalized

    def getList(self):
        """Return the normalized internal list (for callers that expect a getter)."""
        return self.list

    def applySkin(self, desktop, parent):
        attribs = []
        for (attrib, value) in getattr(self, "skinAttributes", []):
            if attrib == "itemPerPage":
                try:
                    self.itemPerPage = int(value)
                    # keep sensible columns based on itemPerPage
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

        # Font and height for the content
        self.l.setFont(0, gFont("Bold", 30))
        self.l.setItemHeight(self.panelheight)
        self.skinAttributes = attribs
        # Build entries for the first time
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
        # accept list of strings or tuples
        self.list = list_ or []
        self._normalize_list()
        # clamp current index
        if self.current >= len(self.list):
            self.current = max(0, len(self.list) - 1)
        if self.instance:
            self.setL(True)

    def buildEntry(self):
        # rebuild entries (does not modify self.list)
        self.entries.clear()
        if len(self.list) > 0:
            width = self.boxwidth + self.margin
            height = self.boxheight + self.margin
            xoffset = (self.activeboxwidth - self.boxwidth) // 2 if self.activeboxwidth > self.boxwidth else 0
            yoffset = (self.activeboxheight - self.boxheight) // 2 if self.activeboxheight > self.boxheight else 0

            self.total_pages = int(math.ceil(float(len(self.list)) / self.itemPerPage)) if self.itemPerPage > 0 else 1

            for page_index in range(self.total_pages):
                x = 0
                y = 0
                for idx in range(page_index * self.itemPerPage, min((page_index + 1) * self.itemPerPage, len(self.list))):
                    elem = self.list[idx]
                    try:
                        full_text = elem[0]
                        desc = elem[1] if len(elem) > 1 else ""
                    except Exception:
                        continue

                    if "-" in full_text:
                        name, version = full_text.rsplit("-", 1)
                    else:
                        name = full_text
                        version = ""

                    key = full_text

                    # Load logo (fallback to default icon)
                    logo = None
                    try:
                        logoPath = resolveFilename(
                            SCOPE_PLUGINS,
                            "Extensions/ElieSatPanel/assets/icons/display.png",
                        )
                        if not fileExists(logoPath):
                            logoPath = resolveFilename(
                                SCOPE_PLUGINS,
                                "Extensions/ElieSatPanel/assets/icons/default.png",
                            )
                        if fileExists(logoPath):
                            logo = LoadPixmap(logoPath)
                    except Exception:
                        logo = None

                    active_height = self.activeboxheight
                    inactive_height = self.boxheight

                    page = page_index + 1

                    # Compute text_x to center name under icon for unselected
                    text_width = self.activeboxwidth
                    text_x = x + xoffset + (self.boxwidth - text_width) // 2

                    # Build entries for this item
                    try:
                        active_entries = (
                            MultiContentEntryPixmap(
                                pos=(x - 5, y - 5),
                                size=(self.activeboxwidth + 10, active_height + 10),
                                png=self.selPixmap,
                                flags=BT_SCALE,
                            ),
                            MultiContentEntryPixmapAlphaTest(
                                pos=(x, y),
                                size=(self.activeboxwidth, active_height - 60),
                                png=logo,
                                flags=BT_SCALE | BT_ALIGN_CENTER | BT_KEEP_ASPECT_RATIO,
                            ),
                            MultiContentEntryText(
                                pos=(x, y + self.activeboxheight - 60),
                                size=(text_width, 30),
                                font=0,
                                text=name,
                                flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                color=0x00FF8C00,
                            ),
                            MultiContentEntryText(
                                pos=(x, y + self.activeboxheight - 30),
                                size=(text_width, 30),
                                font=0,
                                text=version,
                                flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                color=0x00FF8C00,
                            ),
                        )

                        inactive_entries = (
                            MultiContentEntryPixmap(
                                pos=(x + xoffset, y + yoffset),
                                size=(self.boxwidth, inactive_height),
                                png=self.itemPixmap,
                                flags=BT_SCALE,
                            ),
                            MultiContentEntryPixmapAlphaTest(
                                pos=(x + xoffset, y + yoffset),
                                size=(self.boxwidth, inactive_height - 60),
                                png=logo,
                                flags=BT_SCALE | BT_ALIGN_CENTER | BT_KEEP_ASPECT_RATIO,
                            ),
                            MultiContentEntryText(
                                pos=(text_x, y + yoffset + self.boxheight - 60),
                                size=(text_width, 30),
                                font=0,
                                text=name,
                                flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                            ),
                            MultiContentEntryText(
                                pos=(text_x, y + yoffset + self.boxheight - 30),
                                size=(text_width, 30),
                                font=0,
                                text=version,
                                flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                            ),
                        )

                        self.entries[key] = {
                            "active": active_entries,
                            "u_active": inactive_entries,
                            "page": page,
                        }

                    except Exception:
                        # skip problematic item but continue building rest
                        continue

                    x += width
                    if (idx % self.columns) == (self.columns - 1):
                        x = 0
                        y += height

        # After building entries update the visual list
        self.setL()

    def setL(self, refresh=False):
        # refresh rebuilds entries and repopulates the visible list
        if refresh:
            self.entries.clear()
            self.buildEntry()
            return
        if len(self.entries) > 0 and len(self.list) > 0:
            res = [None]
            if self.current > (len(self.list) - 1):
                self.current = (len(self.list) - 1)
            # safely get current key
            try:
                current_key = self.list[self.current][0]
                current = self.entries.get(current_key)
            except Exception:
                current = None
                # fallback to first available
                if len(self.entries):
                    first_key = next(iter(self.entries))
                    current = self.entries[first_key]
                    self.current = 0

            current_page = current.get("page") if current else 1
            page_items = []
            for _, value in self.entries.items():
                if value["page"] == current_page:
                    if value == current:
                        page_items.extend(value["active"])
                    else:
                        page_items.extend(value["u_active"])

            # eListbox expects a list of records; pack into a single-line record
            try:
                self.l.setList([res + page_items])
            except Exception:
                # last-resort: send empty list
                try:
                    self.l.setList([])
                except Exception:
                    pass

            self.setpage()
        else:
            try:
                self.l.setList([])
            except Exception:
                pass

    def setpage(self):
        if self.total_pages > 1:
            self.pagetext = ""
            if len(self.list) > 0:
                for i in range(1, self.total_pages + 1):
                    if i == self.getCurrentPage():
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
                try:
                    self.pager_left.show()
                    self.pager_right.show()
                    self.pager_center.show()
                    self.pagelabel.show()
                except Exception:
                    pass
        else:
            try:
                self.pager_left.hide()
                self.pager_right.hide()
                self.pager_center.hide()
                self.pagelabel.hide()
            except Exception:
                pass

    def getCurrentPage(self):
        # return a 1-based page index; if items exist always return at least 1
        if len(self.entries) > 0 and len(self.list) > 0:
            if self.current > (len(self.list) - 1):
                self.current = (len(self.list) - 1)
            try:
                current_key = self.list[self.current][0]
                current = self.entries.get(current_key, None)
                if current:
                    return current["page"]
            except Exception:
                pass
            return 1
        return 1

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
            try:
                return self.list[self.current]
            except Exception:
                return self.list[0]
        return None

    def getSelectedIndex(self):
        return self.current

    def setIndex(self, index):
        try:
            self.current = int(index)
        except Exception:
            self.current = 0
        if self.instance:
            self.setL()

INSTALLER_URL = "https://raw.githubusercontent.com/eliesat/beta/main/installer1.sh"
EXTENSIONS_URL = "https://raw.githubusercontent.com/eliesat/eliesatpanel/refs/heads/main/sub/display"
LOCAL_EXTENSIONS = "/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/data/display"

# ---------------- DISPLAY CLASS ----------------
class Display(Screen):
    skin = ""

    def __init__(self, session):
        screen_width = 1280
        try:
            screen_width = getDesktop(0).size().width()
        except Exception:
            pass

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

        try:
            with open(skin_file, "r") as f:
                self.skin = f.read()
        except Exception:
            self.skin = (
                '<screen name="Display" position="center,center" size="1280,720">'
                '<eLabel text="Skin Missing" position="center,center" size="400,50" '
                'font="Regular;30" halign="center" valign="center"/>'
                '</screen>'
            )

        Screen.__init__(self, session)
        self.session = session
        self.in_submenu = False
        self.submenu_title = None
        self.previous_index = 0

        # Load Addons icon
        try:
            icon_path = resolveFilename(
                SCOPE_PLUGINS,
                "Extensions/ElieSatPanel/assets/icons/addons.png",
            )
            if not fileExists(icon_path):
                icon_path = resolveFilename(
                    SCOPE_PLUGINS,
                    "Extensions/ElieSatPanel/assets/icons/default.png",
                )
            self.iconPixmap = LoadPixmap(icon_path)
        except Exception:
            self.iconPixmap = None

        # ---------------- Components ----------------
        self["menu"] = FlexibleMenu([])
        self["menu"].itemPixmap = self.iconPixmap
        self["description"] = Label("")
        self["pageinfo"] = Label("")
        self["pagelabel"] = Label("")
        self["image_name"] = Label("Image: " + str(get_image_name()))
        self["local_ip"] = Label("IP: " + str(get_local_ip()))
        self["StorageInfo"] = Label(get_storage_info())
        self["RAMInfo"] = Label(get_ram_info())
        self["python_ver"] = Label("Python: " + str(get_python_version()))
        self["net_status"] = Label("Net: " + str(check_internet()))

        vertical_left = "Version\n" + str(Version)
        vertical_right = "By ElieSat"
        self["left_bar"] = Label(vertical_left)
        self["right_bar"] = Label(vertical_right)

        # Colored buttons
        self["red"] = Label("IPTV Adder")
        self["green"] = Label("Cccam Adder")
        self["yellow"] = Label("News")
        self["blue"] = Label("Scripts")

        # ---------------- Actions ----------------
        self["setupActions"] = ActionMap(
            ["OkCancelActions", "DirectionActions", "ColorActions", "MenuActions"],
            {
                "cancel": self.go_back_or_exit,
                "red": self.openIptvadder,
                "green": self.openCccamadder,
                "yellow": self.openNews,
                "blue": self.openScripts,
                "ok": self.ok,
                "left": self.left,
                "right": self.right,
                "up": self.up,
                "down": self.down,
            },
            -1,
        )

        # Load main menu after screen finish
        self.onLayoutFinish.append(self.load_main_menu)

        # Selection change callbacks
        try:
            self["menu"].onSelectionChanged.append(self.updateDescription)
            self["menu"].onSelectionChanged.append(self.updatePageInfo)
        except Exception:
            pass

        # Update extensions from GitHub
        Timer(1, self.update_extensions_from_github).start()
        # Check plugin version
        Timer(2, self.check_plugin_update).start()

    # --- Navigation ---
    def left(self): self["menu"].left()
    def right(self): self["menu"].right()
    def up(self): self["menu"].up()
    def down(self): self["menu"].down()

    # --- Main menu ---
    def load_main_menu(self, restore_index=False):
        self.in_submenu = False
        self.main_categories = [
            ("Bootvideos", "Bootvideos", "Bvi"),
            ("Bootlogos-Images", "Bootlogos-Images", "Bli"),
            ("Bootlogos-Neutral", "Bootlogos-Neutral", "Ble"),
            ("Bootlogos-Novaler", "Bootlogos-Novaler", "Blno"),
            ("LcdSkins", "LcdSkins", "Lcd"),
            ("Radio-logos", "Radio-logos", "Rdl"),
            ("Spinners", "Spinners", "Spn"),
        ]
        categories_display = [(x[0], x[1]) for x in self.main_categories]
        self["menu"].setList(categories_display)

        idx = 0
        try:
            if restore_index:
                idx = self.previous_index
            elif hasattr(self, "previous_index"):
                idx = self.previous_index
        except Exception:
            idx = 0
        if idx >= len(categories_display):
            idx = 0
        try: self["menu"].setIndex(idx)
        except Exception: pass
        self.updateDescription()
        self.updatePageInfo()

    # --- OK button ---
    def ok(self):
        current = self["menu"].getCurrent()
        if not current: return
        try: self.previous_index = self["menu"].getSelectedIndex()
        except Exception: self.previous_index = 0

        status_code = None
        for cat in self.main_categories:
            if current[0] == cat[0]:
                status_code = cat[2]
                break

        if status_code:
            self.load_sub_menu(status_code, current[0])
        else:
            self.run_selected_script()

    # --- Load submenu ---
    def load_sub_menu(self, status, title):
        self.in_submenu = True
        packages = []
        try:
            if not os.path.exists(LOCAL_EXTENSIONS):
                raise IOError("extensions file not found: %s" % LOCAL_EXTENSIONS)
            with open(LOCAL_EXTENSIONS, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()

            name, version, desc, st = "", "", "", ""
            for line in lines:
                line = line.strip()
                if not line: continue
                if line.startswith("Package:"): name = line.split(":", 1)[1].strip()
                elif line.startswith("Version:"):
                    ver_line = line.split(":", 1)[1].strip()
                    parts = ver_line.split(None, 1)
                    version = parts[0]
                    desc = parts[1] if len(parts) > 1 else ""
                elif line.startswith("Status:"):
                    st = line.split(":", 1)[1].strip()
                    if st.lower() == status.lower():
                        packages.append((f"{name}-{version}", desc))
                    name, version, desc, st = "", "", "", ""

            if not packages: packages.append((f"No packages with Status: {status}", ""))

        except Exception as e:
            packages.append((f"Error reading extensions: {e}", ""))

        self.submenu_title = title
        self["menu"].setList(packages)
        try: self["menu"].setIndex(0)
        except Exception: pass
        self.updateDescription()
        self.updatePageInfo()

    # --- Run selected script ---
    def run_selected_script(self):
        try:
            selected = self["menu"].getCurrent()
            if not selected: return
            selected_label = selected[0]
            selected_pkg_name = selected_label.rsplit("-", 1)[0] if "-" in selected_label else selected_label

            if not os.path.exists(LOCAL_EXTENSIONS):
                print("[Display] extensions file missing when running script")
                return

            with open(LOCAL_EXTENSIONS, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()

            blocks = []
            current_block = {}
            for line in lines:
                line = line.strip()
                if not line: continue
                if line.startswith("Package:"):
                    if current_block: blocks.append(current_block)
                    current_block = {"Package": line.split(":", 1)[1].strip()}
                elif "=" in line and current_block:
                    key, value = line.split("=", 1)
                    current_block[key.strip()] = value.strip().strip("'\"")
                elif line.startswith("Version:") and current_block:
                    current_block["Version"] = line.split(":", 1)[1].strip()
                elif line.startswith("Status:") and current_block:
                    current_block["Status"] = line.split(":", 1)[1].strip()
            if current_block: blocks.append(current_block)

            script_url = None
            for blk in blocks:
                if blk.get("Package") == selected_pkg_name:
                    for key, val in blk.items():
                        if key not in ["Package", "Version", "Status"] and isinstance(val, str) and val.endswith(".sh"):
                            script_url = val
                            break
                    break

            if not script_url:
                print("[Display] No script found for", selected_label)
                return

            # Save submenu index before running script
            submenu_index = self["menu"].getSelectedIndex()
            submenu_title = self.submenu_title

            def restore_submenu(result=None):
                # Restore submenu after script finishes
                if submenu_title:
                    status_code = None
                    for cat in self.main_categories:
                        if cat[0] == submenu_title:
                            status_code = cat[2]
                            break
                    if status_code:
                        self.load_sub_menu(status_code, submenu_title)
                        try:
                            self["menu"].setIndex(submenu_index)
                        except Exception:
                            self["menu"].setIndex(0)
                        self.submenu_title = None

            # Run script in Console
            self.session.open(
                Console,
                title="Running %s..." % selected_label,
                cmdlist=['wget -q "--no-check-certificate" %s -O - | /bin/sh' % script_url],
                closeOnSuccess=True,
                finishedCallback=restore_submenu
            )

        except Exception as e:
            print("[Display] run_selected_script error:", e)

    # --- Colored buttons ---
    def openIptvadder(self):
        try: self.session.open(Iptvadder)
        except Exception as e: print("[Display] IPTV Adder error:", e)

    def openCccamadder(self):
        try: self.session.open(Cccamadder)
        except Exception as e: print("[Display] Cccam Adder error:", e)

    def openNews(self):
        try: self.session.open(News)
        except Exception as e: print("[Display] News error:", e)

    def openScripts(self):
        try: self.session.open(Scripts)
        except Exception as e: print("[Display] Scripts error:", e)

    # --- Cancel / Exit ---
    def go_back_or_exit(self):
        if self.in_submenu:
            self.load_main_menu()
        else:
            self.close()

    # --- Update description & page info ---
    def updateDescription(self):
        current = self["menu"].getCurrent()
        if current:
            desc_text = current[1] if len(current) > 1 else ""
            try: self["description"].setText(desc_text)
            except Exception: pass

    def updatePageInfo(self):
        try: currentPage = int(self["menu"].getCurrentPage())
        except Exception: currentPage = 1
        try: totalPages = int(self["menu"].total_pages) if hasattr(self["menu"], "total_pages") else 1
        except Exception: totalPages = 1
        try: self["pageinfo"].setText(f"Page {currentPage}/{totalPages}")
        except Exception: pass
        try:
            dots = " ".join(["●" if i == currentPage else "○" for i in range(1, totalPages + 1)])
            self["pagelabel"].setText(dots)
        except Exception:
            try: self["pagelabel"].setText("")
            except Exception: pass

    # --- Update extensions from GitHub ---
    def update_extensions_from_github(self):
        try:
            response = requests.get(EXTENSIONS_URL, timeout=10)
            if response.status_code != 200:
                print('[Display] Failed to download extensions from GitHub: status', response.status_code)
                return False

            update_needed = True
            if os.path.exists(LOCAL_EXTENSIONS):
                try:
                    with open(LOCAL_EXTENSIONS, 'rb') as f:
                        local_hash = hashlib.md5(f.read()).hexdigest()
                    new_hash = hashlib.md5(response.content).hexdigest()
                    if local_hash == new_hash:
                        update_needed = False
                except Exception: update_needed = True

            if update_needed:
                try:
                    with open(LOCAL_EXTENSIONS, 'wb') as f: f.write(response.content)
                    print('[Display] Extensions file updated from GitHub')
                    if not self.in_submenu:
                        self.load_main_menu()
                    else:
                        for cat in self.main_categories:
                            if cat[0] == self.submenu_title:
                                self.load_sub_menu(cat[2], cat[0])
                                break
                except Exception as e:
                    print('[Display] Error writing extensions file:', e)
            else:
                print('[Display] Extensions file already up to date')
            return update_needed

        except Exception as e:
            print(f'[Display] Error updating extensions: {e}')
            return False

    # --- Check plugin version ---
    def check_plugin_update(self):
        try:
            req = requests.get(INSTALLER_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if req.status_code != 200:
                print('[Display] Failed to fetch installer for update check')
                return
            data = req.text
            remote_version = None
            remote_changelog = ""
            for line in data.split("\n"):
                l = line.strip()
                if l.startswith("version"):
                    parts = l.split("=", 1)
                    if len(parts) > 1: remote_version = parts[1].strip().strip("'\"")
                elif l.startswith("changelog"):
                    parts = l.split("=", 1)
                    if len(parts) > 1:
                        remote_changelog = parts[1].strip().strip("'\"")
                        break
            try:
                if remote_version and float(str(Version)) < float(remote_version):
                    self.session.openWithCallback(
                        self.install_plugin_update,
                        MessageBox,
                        f"""New version {remote_version} available.\n{remote_changelog}\nInstall now?""",
                        MessageBox.TYPE_YESNO,
                    )
            except Exception:
                pass
        except Exception as e:
            print("[Display] Plugin update check error:", e)

    # --- Install plugin update ---
    def install_plugin_update(self, answer=False):
        if answer:
            self.session.open(
                Console,
                title='Updating ElieSatPanel...',
                cmdlist=['wget -q "--no-check-certificate" ' + INSTALLER_URL + ' -O - | /bin/sh'],
                finishedCallback=lambda result: print("[Display] Plugin update finished:", result),
                closeOnSuccess=True,
            )