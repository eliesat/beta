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

        # pager icons
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

        self.l.setFont(0, gFont("Bold", 30))
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

                    # Load logo
                    logo = None
                    try:
                        logoPath = resolveFilename(
                            SCOPE_PLUGINS,
                            "Extensions/ElieSatPanel/assets/compet/icons/tools-panel.png",
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

                    active_height = self.activeboxheight
                    inactive_height = self.boxheight

                    page = page_index + 1

                    # Compute text_x to center name under icon for unselected
                    text_width = self.activeboxwidth
                    text_x = x + xoffset + (self.boxwidth - text_width) // 2

                    self.entries[key] = {
                        "active": (
                            MultiContentEntryPixmap(
                                pos=(x-5, y-5),
                                size=(self.activeboxwidth+10, active_height+10),
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
                        ),
                        "u_active": (
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
                        ),
                        "page": page,
                    }

                    x += width
                    if (idx % self.columns) == (self.columns - 1):
                        x = 0
                        y += height

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
                first_key = next(iter(self.entries))
                current = self.entries[first_key]
                self.current = 0
            current_page = current["page"]
            for _, value in self.entries.items():
                if value["page"] == current_page:
                    if value == current:
                        res.extend(value["active"])
                    else:
                        res.extend(value["u_active"])
            self.l.setList([res])
            self.setpage()
        else:
            self.l.setList([])

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

# ---------------- MAIN PANEL ----------------
class Toolsp(Screen):
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
            self.skin = """<screen name="ElieSatPanel" position="center,center" size="1280,720" title="ElieSatPanel">
                <eLabel text="Eliesat Panel - Skin Missing" position="center,center" size="400,50"
                    font="Regular;30" halign="center" valign="center" />
            </screen>"""

        Screen.__init__(self, session)

        self["menu"] = FlexibleMenu([])
        self["description"] = Label("")
        self["pageinfo"] = Label("")
        self["pagelabel"] = Label("")

        self["red"] = Label("IPTV Adder")
        self["green"] = Label("Cccam Adder")
        self["yellow"] = Label("News")
        self["blue"] = Label("Scripts")

        self["image_name"] = Label("Image: " + get_image_name())
        self["local_ip"] = Label("IP: " + get_local_ip())
        self["StorageInfo"] = Label(get_storage_info())
        self["RAMInfo"] = Label(get_ram_info())
        self["python_ver"] = Label("Python: " + get_python_version())
        self["net_status"] = Label("Net: " + check_internet())

        Timer(0.5, self.update_me).start()

        vertical_left = "\n".join(list("Version " + Version))
        vertical_right = "\n".join(list("By ElieSat"))
        self["left_bar"] = Label(vertical_left)
        self["right_bar"] = Label(vertical_right)

        # Load panels from file
        self.load_panels()

        self["menu"].onSelectionChanged.append(self.updateDescription)
        self["menu"].onSelectionChanged.append(self.updatePageInfo)
        self.updateDescription()
        self.updatePageInfo()

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
            },
            -1,
        )

        # ----------------- ADDED: Check and update panels on plugin start -----------------
        def start_update_panels():
            if self.update_data():  # Update panels if missing or changed
                self.load_panels()   # Reload menu dynamically

        Timer(1, start_update_panels).start()  # Slight delay to ensure session is ready

    # --- Navigation ---
    def left(self):
       self["menu"].left()

    def right(self):
       self["menu"].right()

    def up(self):
       self["menu"].up()

    def down(self):
       self["menu"].down()

    # --- OK button handler ---
    def ok(self):
       try:
              panels_file = resolveFilename(
                     SCOPE_PLUGINS,
                     "Extensions/ElieSatPanel/assets/data/panels"
              )
              with open(panels_file, "r", encoding="utf-8") as f:
                     lines = f.read().splitlines()

              selected = self["menu"].getCurrent()
              if not selected:
                     return
              selected_label = selected[0]  # full name with version
              
              # Extract exact package name (before the dash-version)
              if "-" in selected_label:
                     selected_pkg_name = selected_label.rsplit("-", 1)[0]
              else:
                     selected_pkg_name = selected_label

              # --- Parse panels file into blocks ---
              blocks = []
              current_block = {}
              for line in lines:
                     line = line.strip()
                     if not line:
                            continue
                     if line.startswith("Package:"):
                            if current_block:
                                   blocks.append(current_block)
                            current_block = {"Package": line.split(":",1)[1].strip()}
                     elif "=" in line and current_block:
                            key, value = line.split("=",1)
                            current_block[key.strip()] = value.strip().strip("'\"")
                     elif line.startswith("Version:") and current_block:
                            current_block["Version"] = line.split(":",1)[1].strip()
              if current_block:
                     blocks.append(current_block)

              # --- Find block with exact package name ---
              script_url = None
              for blk in blocks:
                     if blk.get("Package") == selected_pkg_name:
                            # Find first key with .sh
                            for key, val in blk.items():
                                   if key not in ["Package", "Version"] and val.endswith(".sh"):
                                          script_url = val
                                          break
                            break

              if not script_url:
                     print("[Toolsp ok] No script found for", selected_label)
                     return

              # --- Run script ---
              self.session.open(
                     Console,
                     title="Running %s..." % selected_label,
                     cmdlist=['wget -q "--no-check-certificate" %s -O - | /bin/sh' % script_url],
                     closeOnSuccess=False
              )

       except Exception as e:
              print("[Toolsp ok] Error:", e)

    # --- Description & Page info ---
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

    # ----------------- ADDED METHOD -----------------
    def update_data(self):
        url = 'https://raw.githubusercontent.com/eliesat/beta/refs/heads/main/assets/data/panels'
        file_path = '/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/data/panels'
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print('[Toolsp update_data] Failed to download data file from GitHub')
                return False
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    existing_hash = hashlib.md5(f.read()).hexdigest()
                new_hash = hashlib.md5(response.content).hexdigest()
                if existing_hash == new_hash:
                    print('[Toolsp update_data] Data file already up to date')
                    return False
                else:
                    print('[Toolsp update_data] Data file content changed, updating...')
            else:
                print('[Toolsp update_data] Data file missing, downloading...')
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print('[Toolsp update_data] Data file updated successfully')
            return True
        except Exception as e:
            print(f'[Toolsp update_data] Error: {e}')
            return False

    # ----------------- ADDED METHOD -----------------
    def load_panels(self):
        packages = []
        try:
            panels_file = resolveFilename(
                SCOPE_PLUGINS,
                "Extensions/ElieSatPanel/assets/data/panels"
            )
            with open(panels_file, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
            name, version, desc = "", "", ""
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
                    packages.append((f"{name}-{version}", desc))
            if not packages:
                packages.append(("No packages found.", ""))
        except Exception as e:
            packages.append((f"Error reading panels file: {str(e)}", ""))

        self.menuList = packages
        self["menu"].setList(self.menuList)
        self.updateDescription()
        self.updatePageInfo()
        print("[Toolsp load_panels] Menu reloaded successfully")

    # ----------------- SHORTCUT METHODS -----------------
    def openIptvadder(self):
       try:
              from Plugins.Extensions.ElieSatPanel.Iptvadder import Iptvadder
              self.session.open(Iptvadder)
       except Exception as e:
              print("[Toolsp] Error opening Iptvadder:", e)

    def openCccamadder(self):
       try:
              from Plugins.Extensions.ElieSatPanel.Cccamadder import Cccamadder
              self.session.open(Cccamadder)
       except Exception as e:
              print("[Toolsp] Error opening Cccamadder:", e)

    def openNews(self):
       try:
              from Plugins.Extensions.ElieSatPanel.News import News
              self.session.open(News)
       except Exception as e:
              print("[Toolsp] Error opening News:", e)

    def openScripts(self):
       try:
              from Plugins.Extensions.ElieSatPanel.Scripts import Scripts
              self.session.open(Scripts)
       except Exception as e:
              print("[Toolsp] Error opening Scripts:", e)

