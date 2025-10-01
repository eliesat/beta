# -*- coding: utf-8 -*-
import os
import sys
import math
import socket
import subprocess
from sys import version_info
from threading import Timer

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
        self.itemPerPage = 24
        self.columns = 6
        self.margin = 10
        self.boxwidth = 200
        self.boxheight = 240  # enough for 150px icon + text
        self.activeboxwidth = 220
        self.activeboxheight = 260
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
        self.entries.clear()
        if not self.list:
            return

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
            try:
                full_name = elem[0]
                desc = elem[1] if len(elem) > 1 else ""
            except Exception:
                continue

            if "-" in full_name:
                pkg_name, pkg_version = full_name.rsplit("-", 1)
            else:
                pkg_name = full_name
                pkg_version = ""

            if count >= self.itemPerPage:
                count = 0
                page += 1
                y = 0

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

            # Dynamic heights
            icon_size = 150
            text1_height = 30
            text2_height = 30
            padding = 10
            active_height = icon_size + text1_height + text2_height + 3*padding
            inactive_height = active_height - 20

            self.entries[full_name] = {
                "active": (
                    MultiContentEntryPixmap(
                        pos=(x, y),
                        size=(self.activeboxwidth, active_height),
                        png=self.selPixmap,
                        flags=BT_SCALE,
                    ),
                    MultiContentEntryPixmapAlphaTest(
                        pos=(x, y),
                        size=(self.activeboxwidth, icon_size),
                        png=logo,
                        flags=BT_SCALE | BT_ALIGN_CENTER | BT_KEEP_ASPECT_RATIO,
                    ),
                    MultiContentEntryText(
                        pos=(x, y + icon_size + padding),
                        size=(self.activeboxwidth, text1_height),
                        font=0,
                        text=pkg_name,
                        flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                        color=0x00FF8C00
                    ),
                    MultiContentEntryText(
                        pos=(x, y + icon_size + padding + text1_height + padding),
                        size=(self.activeboxwidth, text2_height),
                        font=0,
                        text=pkg_version,
                        flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                        color=0x00FF8C00
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
                        size=(self.boxwidth, icon_size),
                        png=logo,
                        flags=BT_SCALE | BT_ALIGN_CENTER | BT_KEEP_ASPECT_RATIO,
                    ),
                    MultiContentEntryText(
                        pos=(x + xoffset, y + yoffset + icon_size + padding),
                        size=(self.boxwidth, text1_height),
                        font=0,
                        text=pkg_name,
                        flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                    ),
                    MultiContentEntryText(
                        pos=(x + xoffset, y + yoffset + icon_size + padding + text1_height + padding),
                        size=(self.boxwidth, text2_height),
                        font=0,
                        text=pkg_version,
                        flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                    ),
                ),
                "page": page,
                "desc": desc
            }

            x += width
            list_dummy.append(full_name)
            if len(list_dummy) == self.columns:
                list_dummy[:] = []
                x = 0
                y += height
            count += 1

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
                if current_page == value["page"] and value != current:
                    res.extend(value["u_active"])
            res.extend(current["active"])
            self.l.setList([res])
            self.setpage()
        else:
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
            self.current = (self.current - step) if direction == "backwards" else (self.current + step)
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

    def left(self): self["menu"].left()
    def right(self): self["menu"].right()
    def up(self): self["menu"].up()
    def down(self): self["menu"].down()

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
            selected_label = selected[0]

            current_pkg = ""
            script_url = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("Package:"):
                    current_pkg = line.split(":", 1)[1].strip()
                elif "=" in line and current_pkg:
                    pkg_name, url = line.split("=", 1)
                    pkg_name = pkg_name.strip()
                    url = url.strip().strip("'\"")
                    if pkg_name in selected_label and url.endswith(".sh"):
                        script_url = url
                        break
            if script_url:
                self.session.open(
                    Console,
                    title="Running %s..." % selected_label,
                    cmdlist=['wget -q "--no-check-certificate" %s -O - | /bin/sh' % script_url],
                    closeOnSuccess=False
                )
        except Exception as e:
            print("[Toolsp ok] Error:", e)

    # --- Color buttons ---
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

