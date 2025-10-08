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
    - getList() accessor added
    - Defensive normalization of incoming list
    - HD/FHD dynamic defaults now actually take effect
    - Pager uses simple printable bullets
    - Added HD-specific text positions (8 MultiContentEntryText total)
    - Optimized for smoother performance on Hisilicon CPUs
    """
    _cached_logos = {}

    def __init__(self, list_=None):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.list = list_ or []
        self._normalize_list()
        self.entries = dict()
        self.onSelectionChanged = []
        self.current = 0
        self.total_pages = 1

        # HD/FHD dynamic defaults
        if getDesktop(0).size().width() >= 1920:
            self.normalFont = gFont("Bold", 30)
            self.selFont = gFont("Bold", 30)
            self.boxwidth = 240
            self.boxheight = 240
            self.activeboxwidth = 285
            self.activeboxheight = 285
            self.margin = 30
            self.panelheight = 570
            self.itemPerPage = 18
            self.columns = 6
        else:
            self.normalFont = gFont("Bold", 20)
            self.selFont = gFont("Bold", 20)
            self.boxwidth = 160
            self.boxheight = 180
            self.activeboxwidth = 210
            self.activeboxheight = 210
            self.margin = 10
            self.panelheight = 380
            self.itemPerPage = 12
            self.columns = 4

        self.selectedicon = "●"
        self.unselectedicon = "○"

        # Preload pager pixmaps once
        self.ptr_pagerleft = self._loadPixmapSafe("Extensions/ElieSatPanel/assets/icon/pager_left.png")
        self.ptr_pagerright = self._loadPixmapSafe("Extensions/ElieSatPanel/assets/icon/pager_right.png")

        self.itemPixmap = None
        self.selPixmap = None
        self.listWidth = 0
        self.listHeight = 0

    def _loadPixmapSafe(self, path):
        try:
            return LoadPixmap(resolveFilename(SCOPE_PLUGINS, path))
        except Exception:
            return None

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
                continue
        self.list = normalized

    def getList(self):
        return self.list

    def applySkin(self, desktop, parent):
        attribs = []
        for (attrib, value) in getattr(self, "skinAttributes", []):
            try:
                if attrib == "itemPerPage":
                    self.itemPerPage = int(value)
                    self.columns = max(1, self.itemPerPage // 2)
                elif attrib == "panelheight":
                    self.panelheight = int(value)
                elif attrib == "margin":
                    self.margin = int(value)
                elif attrib == "boxSize":
                    if "," in value:
                        self.boxwidth, self.boxheight = [int(v) for v in value.split(",")]
                    else:
                        self.boxwidth = self.boxheight = int(value)
                elif attrib == "activeSize":
                    if "," in value:
                        self.activeboxwidth, self.activeboxheight = [int(v) for v in value.split(",")]
                    else:
                        self.activeboxwidth = self.activeboxheight = int(value)
                elif attrib == "size":
                    self.listWidth, self.listHeight = [int(v) for v in value.split(",")]
                    if self.instance:
                        self.instance.resize(eSize(self.listWidth, self.listHeight))
                elif attrib == "itemPixmap":
                    self.itemPixmap = LoadPixmap(value)
                elif attrib == "selPixmap":
                    self.selPixmap = LoadPixmap(value)
                else:
                    attribs.append((attrib, value))
            except Exception:
                continue

        self.l.setFont(0, self.normalFont)
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
        if self.ptr_pagerleft:
            self.pager_left.setPixmap(self.ptr_pagerleft)
        if self.ptr_pagerright:
            self.pager_right.setPixmap(self.ptr_pagerright)
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
        self.list = list_ or []
        self._normalize_list()
        if self.current >= len(self.list):
            self.current = max(0, len(self.list) - 1)
        if self.instance:
            self.setL(True)

    def buildEntry(self):
        self.entries.clear()
        if len(self.list) == 0:
            return

        width = self.boxwidth + self.margin
        height = self.boxheight + self.margin
        xoffset = (self.activeboxwidth - self.boxwidth) // 2
        yoffset = (self.activeboxheight - self.boxheight) // 2
        isFHD = getDesktop(0).size().width() >= 1920
        self.total_pages = int(math.ceil(float(len(self.list)) / self.itemPerPage)) if self.itemPerPage > 0 else 1

        # Preload logo only once
        if "addons" not in self._cached_logos:
            logoPath = resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/assets/icons/display.png")
            if not fileExists(logoPath):
                logoPath = resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/assets/icons/default.png")
            self._cached_logos["addons"] = LoadPixmap(logoPath) if fileExists(logoPath) else None
        logo = self._cached_logos.get("addons")

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
                active_height = self.activeboxheight
                inactive_height = self.boxheight
                page = page_index + 1
                text_width = self.activeboxwidth
                text_x = x + xoffset + (self.boxwidth - text_width) // 2

                # Active / inactive entries
                active_texts = (
                    MultiContentEntryText(pos=(x, y + self.activeboxheight - (60 if isFHD else 65)),
                                          size=(text_width, 30), font=0, text=name,
                                          flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                          color=0x00FF8C00),
                    MultiContentEntryText(pos=(x, y + self.activeboxheight - (30 if isFHD else 45)),
                                          size=(text_width, 30), font=0, text=version,
                                          flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                          color=0x00FF8C00),
                )
                inactive_texts = (
                    MultiContentEntryText(pos=(text_x, y + yoffset + self.boxheight - (60 if isFHD else 65)),
                                          size=(text_width, 30), font=0, text=name,
                                          flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER),
                    MultiContentEntryText(pos=(text_x, y + yoffset + self.boxheight - (30 if isFHD else 45)),
                                          size=(text_width, 30), font=0, text=version,
                                          flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER),
                )

                self.entries[key] = {
                    "active": (
                        MultiContentEntryPixmap(pos=(x - 5, y - 5), size=(self.activeboxwidth + 10, active_height + 10),
                                                png=self.selPixmap, flags=BT_SCALE),
                        MultiContentEntryPixmapAlphaTest(pos=(x, y), size=(self.activeboxwidth, active_height - 60),
                                                         png=logo, flags=BT_SCALE | BT_ALIGN_CENTER | BT_KEEP_ASPECT_RATIO),
                    ) + active_texts,
                    "u_active": (
                        MultiContentEntryPixmap(pos=(x + xoffset, y + yoffset), size=(self.boxwidth, inactive_height),
                                                png=self.itemPixmap, flags=BT_SCALE),
                        MultiContentEntryPixmapAlphaTest(pos=(x + xoffset, y + yoffset),
                                                         size=(self.boxwidth, inactive_height - 60),
                                                         png=logo, flags=BT_SCALE | BT_ALIGN_CENTER | BT_KEEP_ASPECT_RATIO),
                    ) + inactive_texts,
                    "page": page
                }

                x += width
                if (idx % self.columns) == (self.columns - 1):
                    x = 0
                    y += height
        self.setL()

    # --------------------- LIST DISPLAY ---------------------
    def setL(self, refresh=False):
        if refresh:
            self.entries.clear()
            self.buildEntry()
            return
        if len(self.entries) > 0 and len(self.list) > 0:
            res = [None]
            if self.current > (len(self.list) - 1):
                self.current = (len(self.list) - 1)
            try:
                current_key = self.list[self.current][0]
                current = self.entries.get(current_key)
            except Exception:
                current = None
                if len(self.entries):
                    first_key = next(iter(self.entries))
                    current = self.entries[first_key]
                    self.current = 0

            current_page = current.get("page") if current else 1
            page_items = []
            for _, value in self.entries.items():
                if value["page"] == current_page:
                    page_items.extend(value["active"] if value == current else value["u_active"])

            try:
                self.l.setList([res + page_items])
            except Exception:
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

    # --------------------- PAGER ---------------------
    def setpage(self):
        if self.total_pages > 1:
            self.pagetext = ""
            if len(self.list) > 0:
                for i in range(1, self.total_pages + 1):
                    self.pagetext += " " + (self.selectedicon if i == self.getCurrentPage() else self.unselectedicon)
                self.pagetext += " "
            self.pagelabel.setText(self.pagetext)
            try:
                w = int(self.pagelabel.calculateSize().width() / 2)
            except Exception:
                w = 100
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

    # --------------------- MOVEMENT ---------------------
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
            self.current = (self.current - step if direction == "backwards" else self.current + step) % len(self.list)
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

        # ---------------- Skin selection ----------------
        base_skin_path = "/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/skin/"
        skin_files = {
            "hd": os.path.join(base_skin_path, "eliesatpanel_hd.xml"),
            "fhd": os.path.join(base_skin_path, "eliesatpanel_fhd.xml"),
            "default": os.path.join(base_skin_path, "eliesatpanel.xml"),
        }

        skin_file = (
            skin_files["fhd"] if screen_width >= 1920 and os.path.exists(skin_files["fhd"])
            else skin_files["hd"] if os.path.exists(skin_files["hd"])
            else skin_files["default"]
        )

        try:
            with open(skin_file, "r", encoding="utf-8") as f:
                self.skin = f.read()
        except FileNotFoundError:
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
        self.submenu_indices = {}

        # ---------------- Load Icon ----------------
        try:
            icon_path = resolveFilename(
                SCOPE_PLUGINS, "Extensions/ElieSatPanel/assets/icons/addons.png"
            )
            if not fileExists(icon_path):
                icon_path = resolveFilename(
                    SCOPE_PLUGINS, "Extensions/ElieSatPanel/assets/icons/default.png"
                )
            self.iconPixmap = LoadPixmap(icon_path)
        except Exception:
            self.iconPixmap = None

        # ---------------- UI Components ----------------
        self["menu"] = FlexibleMenu([])
        self["menu"].itemPixmap = self.iconPixmap
        self["description"] = Label("")
        self["pageinfo"] = Label("")
        self["pagelabel"] = Label("")
        self["image_name"] = Label(f"Image: {get_image_name()}")
        self["local_ip"] = Label(f"IP: {get_local_ip()}")
        self["StorageInfo"] = Label(get_storage_info())
        self["RAMInfo"] = Label(get_ram_info())
        self["python_ver"] = Label(f"Python: {get_python_version()}")
        self["net_status"] = Label(f"Net: {check_internet()}")

        vertical_left = "\n".join(list("Version " + Version))
        vertical_right = "\n".join(list("By ElieSat"))
        self["left_bar"] = Label(vertical_left)
        self["right_bar"] = Label(vertical_right)

        # ---------------- Colored buttons ----------------
        self["red"] = Label("IPTV Adder")
        self["green"] = Label("Cccam Adder")
        self["yellow"] = Label("News")
        self["blue"] = Label("Scripts")

        # ---------------- Key Actions ----------------
        self["setupActions"] = ActionMap(
            ["OkCancelActions", "DirectionActions", "ColorActions", "MenuActions"],
            {
                "cancel": self.go_back_or_exit,
                "red": self.openIptvadder,
                "green": self.openCccamadder,
                "yellow": self.openNews,
                "blue": self.openScripts,
                "ok": self.ok,
                "left": lambda: self["menu"].left(),
                "right": lambda: self["menu"].right(),
                "up": lambda: self["menu"].up(),
                "down": lambda: self["menu"].down(),
            },
            -1,
        )

        # ---------------- Initialization ----------------
        self.onLayoutFinish.append(self.load_main_menu)

        # Menu selection callbacks
        try:
            self["menu"].onSelectionChanged.append(self.updateDescription)
            self["menu"].onSelectionChanged.append(self.updatePageInfo)
        except Exception:
            pass

        # Background tasks
        Timer(1, self.update_extensions_from_github).start()
        Timer(2, self.check_plugin_update).start()

    # ---------------- Main menu ----------------
    def load_main_menu(self):
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

        # Restore previous main menu index
        idx = min(int(getattr(self, "previous_index", 0)), len(categories_display) - 1)
        self["menu"].setIndex(idx)
        self.updateDescription()
        self.updatePageInfo()

    # ---------------- OK Button ----------------
    def ok(self):
        current = self["menu"].getCurrent()
        if not current:
            return

        # Store previous main menu index
        if not self.in_submenu:
            self.previous_index = self["menu"].getSelectedIndex() or 0

        for cat in self.main_categories:
            if current[0] == cat[0]:
                return self.load_sub_menu(cat[2], current[0])

        self.run_selected_script()

    # ---------------- Submenu ----------------
    def load_sub_menu(self, status, title):
        self.in_submenu = True
        packages = []

        # Restore previous submenu index if revisiting
        submenu_index = self.submenu_indices.get(title, 0)

        try:
            if not os.path.exists(LOCAL_EXTENSIONS):
                raise FileNotFoundError(f"extensions file not found: {LOCAL_EXTENSIONS}")

            with open(LOCAL_EXTENSIONS, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()

            name = version = desc = st = ""
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("Package:"):
                    name = line.split(":", 1)[1].strip()
                elif line.startswith("Version:"):
                    ver_line = line.split(":", 1)[1].strip()
                    parts = ver_line.split(None, 1)
                    version = parts[0]
                    desc = parts[1] if len(parts) > 1 else ""
                elif line.startswith("Status:"):
                    st = line.split(":", 1)[1].strip()
                    if st.lower() == status.lower():
                        packages.append((f"{name}-{version}", desc))
                    name = version = desc = st = ""

            if not packages:
                packages.append((f"No packages with Status: {status}", ""))

        except Exception as e:
            packages.append((f"Error reading extensions: {e}", ""))

        self.submenu_title = title
        self["menu"].setList(packages)

        # Restore scroll index if available
        if submenu_index < len(packages):
            self["menu"].setIndex(submenu_index)
        else:
            self["menu"].setIndex(0)

        self.updateDescription()
        self.updatePageInfo()

    # ---------------- Run Script ----------------
    def run_selected_script(self):
        try:
            selected = self["menu"].getCurrent()
            if not selected:
                return
            selected_label = selected[0]
            pkg_name = selected_label.rsplit("-", 1)[0] if "-" in selected_label else selected_label

            if not os.path.exists(LOCAL_EXTENSIONS):
                print("[Display] extensions file missing")
                return

            script_url = self._find_script_url(pkg_name)
            if not script_url:
                print("[Display] No script found for", selected_label)
                return

            # Save submenu index before running script
            submenu_index = self["menu"].getSelectedIndex()
            submenu_title = self.submenu_title

            def restore_submenu(result=None):
                if submenu_title:
                    for cat in self.main_categories:
                        if cat[0] == submenu_title:
                            self.load_sub_menu(cat[2], cat[0])
                            self["menu"].setIndex(submenu_index)
                            break

            self.session.open(
                Console,
                title=f"Running {selected_label}...",
                cmdlist=[f'wget -q --no-check-certificate "{script_url}" -O - | /bin/sh'],
                closeOnSuccess=True,
                finishedCallback=restore_submenu,
            )

        except Exception as e:
            print("[Display] run_selected_script error:", e)

    def _find_script_url(self, pkg_name):
        """Helper to extract .sh script URL for given package"""
        try:
            with open(LOCAL_EXTENSIONS, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
            block = {}
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("Package:"):
                    if block and block.get("Package") == pkg_name:
                        return next((v for v in block.values() if isinstance(v, str) and v.endswith(".sh")), None)
                    block = {"Package": line.split(":", 1)[1].strip()}
                elif "=" in line:
                    key, val = line.split("=", 1)
                    block[key.strip()] = val.strip().strip("'\"")
            return None
        except Exception as e:
            print("[Display] _find_script_url error:", e)
            return None

    # ---------------- Colored Buttons ----------------
    def openIptvadder(self): self._safe_open(Iptvadder, "IPTV Adder")
    def openCccamadder(self): self._safe_open(Cccamadder, "Cccam Adder")
    def openNews(self): self._safe_open(News, "News")
    def openScripts(self): self._safe_open(Scripts, "Scripts")

    def _safe_open(self, screen, name):
        try:
            self.session.open(screen)
        except Exception as e:
            print(f"[Display] {name} error:", e)

    # ---------------- Exit / Back ----------------
    def go_back_or_exit(self):
        if self.in_submenu:
            self.submenu_indices[self.submenu_title] = self["menu"].getSelectedIndex() or 0
            self.load_main_menu()
        else:
            self.close()

    # ---------------- Description & Page Info ----------------
    def updateDescription(self):
        current = self["menu"].getCurrent()
        desc_text = current[1] if current and len(current) > 1 else ""
        self["description"].setText(desc_text or "")

    def updatePageInfo(self):
        try:
            currentPage = int(self["menu"].getCurrentPage())
        except Exception:
            currentPage = 1
        try:
            totalPages = int(self["menu"].total_pages) if hasattr(self["menu"], "total_pages") else 1
        except Exception:
            totalPages = 1
        try:
            self["pageinfo"].setText(f"Page {currentPage}/{totalPages}")
        except Exception:
            pass
        try:
            dots = " ".join(["●" if i == currentPage else "○" for i in range(1, totalPages + 1)])
            self["pagelabel"].setText(dots)
        except Exception:
            try: self["pagelabel"].setText("")
            except Exception: pass

    # ---------------- GitHub Update ----------------
    def update_extensions_from_github(self):
        try:
            response = requests.get(EXTENSIONS_URL, timeout=10)
            if response.status_code != 200:
                print(f"[Display] Failed to fetch extensions: {response.status_code}")
                return False

            new_hash = hashlib.md5(response.content).hexdigest()
            local_hash = None
            if os.path.exists(LOCAL_EXTENSIONS):
                with open(LOCAL_EXTENSIONS, "rb") as f:
                    local_hash = hashlib.md5(f.read()).hexdigest()

            if local_hash == new_hash:
                print("[Display] Extensions already up-to-date")
                return False

            with open(LOCAL_EXTENSIONS, "wb") as f:
                f.write(response.content)
            print("[Display] Extensions file updated from GitHub")

            # Refresh current view
            if not self.in_submenu:
                self.load_main_menu()
            else:
                for cat in self.main_categories:
                    if cat[0] == self.submenu_title:
                        self.load_sub_menu(cat[2], cat[0])
                        break

            return True
        except Exception as e:
            print("[Display] update_extensions_from_github error:", e)
            return False

    # ---------------- Plugin Update ----------------
    def check_plugin_update(self):
        try:
            req = requests.get(INSTALLER_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if req.status_code != 200:
                print("[Display] Failed to fetch installer for update check")
                return

            remote_version, remote_changelog = None, ""
            for line in req.text.splitlines():
                if line.startswith("version"):
                    remote_version = line.split("=", 1)[1].strip().strip("'\"")
                elif line.startswith("changelog"):
                    remote_changelog = line.split("=", 1)[1].strip().strip("'\"")
                    break

            if remote_version and float(Version) < float(remote_version):
                self.session.openWithCallback(
                    self.install_plugin_update,
                    MessageBox,
                    f"New version {remote_version} available.\n{remote_changelog}\nInstall now?",
                    MessageBox.TYPE_YESNO,
                )
        except Exception as e:
            print("[Display] check_plugin_update error:", e)

    def install_plugin_update(self, answer=False):
        if not answer:
            return
        self.session.open(
            Console,
            title="Updating ElieSatPanel...",
            cmdlist=[f'wget -q --no-check-certificate {INSTALLER_URL} -O - | /bin/sh'],
            finishedCallback=lambda r: print("[Display] Plugin update finished:", r),
            closeOnSuccess=True,
        )
