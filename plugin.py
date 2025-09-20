# -*- coding: utf-8 -*-
from Plugins.Extensions.ElieSatPanel.__init__ import Version
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
import os
import socket
import sys
import math
import subprocess

from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Plugins.Plugin import PluginDescriptor
from sys import version_info
from Components.GUIComponent import GUIComponent
from Components.MultiContent import (
    MultiContentEntryText,
    MultiContentEntryPixmap,
    MultiContentEntryPixmapAlphaTest,
)
from enigma import (
    eListboxPythonMultiContent,
    eListbox,
    ePixmap,
    eLabel,
    eSize,
    ePoint,
    gFont,
    BT_SCALE,
    BT_KEEP_ASPECT_RATIO,
    BT_ALIGN_CENTER,
    RT_HALIGN_CENTER,
    RT_VALIGN_CENTER,
)
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, fileExists
from skin import parseColor
from threading import Timer
from .menus.Console import Console

try:
    # Python 3
    from urllib.request import Request as compat_Request, urlopen as compat_urlopen
except ImportError:
    # Python 2
    from urllib2 import Request as compat_Request, urlopen as compat_urlopen

PY3 = version_info[0] == 3
installer = 'https://raw.githubusercontent.com/eliesat/beta/main/installer1.sh'

# ---------------- NETWORK HELPERS ----------------
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "No IP"


def check_internet():
    try:
        subprocess.check_call(
            ["ping", "-c", "1", "-W", "1", "8.8.8.8"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return "Online"
    except Exception:
        return "Offline"


# ---------------- IMAGE / PYTHON HELPERS ----------------
def get_image_name():
    """
    Return clean image name (e.g. 'openATV').
    Priority:
      1. /etc/image-version -> creator=...
      2. /etc/image-version -> imagename= or image=
      3. fallback to first non-empty line's last word in /etc/image-version
      4. /etc/issue -> first word
    Returns: raw string (no "Image:" prefix)
    """
    try:
        path = "/etc/image-version"
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    lines = [ln.strip() for ln in f if ln.strip()]
                    # explicit keys
                    for line in lines:
                        lower = line.lower()
                        if lower.startswith("creator="):
                            return line.split("=", 1)[1].strip().strip('"').strip("'")
                        if lower.startswith("imagename=") or lower.startswith("image="):
                            return line.split("=", 1)[1].strip().strip('"').strip("'")
                    # fallback: last word of first non-empty line
                    if lines:
                        return lines[0].split()[-1]
            except Exception:
                pass

        issue = "/etc/issue"
        if os.path.exists(issue):
            try:
                with open(issue, "r") as f:
                    first = f.readline().strip()
                    if first:
                        return first.split()[0]
            except Exception:
                pass
    except Exception:
        pass
    return "Unknown"


def get_python_version():
    """
    Return human-readable Python version (e.g. '3.13.7').
    """
    try:
        vi = sys.version_info
        return "%d.%d.%d" % (vi.major, vi.minor, vi.micro)
    except Exception:
        return "Unknown"

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


# ---------------- MAIN PANEL ----------------
class EliesatPanel(Screen):
    skin = ""

    def __init__(self, session):
        Screen.__init__(self, session)

        # Load skin file
        skin_file = "/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/skin/eliesatpanel.xml"
        if os.path.exists(skin_file):
            try:
                with open(skin_file, "r") as f:
                    self.skin = f.read()
            except Exception:
                self.skin = ""
        if not self.skin:
            self.skin = """<screen name="ElieSatPanel" position="center,center" size="1280,720" title="ElieSatPanel">
                <eLabel text="Eliesat Panel - Skin Missing" position="center,center" size="400,50"
                    font="Regular;30" halign="center" valign="center" />
            </screen>"""

        # Menu widget (expects list of (name, description) tuples)
        self["menu"] = FlexibleMenu([])
        if getattr(self["menu"], "skinAttributes", None) is None:
            self["menu"].skinAttributes = []

        # Color labels
        self["red"] = Label("Exit")
        self["green"] = Label("")
        self["yellow"] = Label("")
        self["blue"] = Label("Scripts")

        vertical_left = "\n".join(list("Version " + Version))
        vertical_right = "\n".join(list("By ElieSat"))
        # Network / System info labels (single prefix only)
        self["local_ip"] = Label("IP: " + get_local_ip())
        self["net_status"] = Label("Net: " + check_internet())
        self["image_name"] = Label("Image: " + get_image_name())
        self["python_ver"] = Label("Python: " + get_python_version())
        self["left_bar"] = Label(vertical_left)
        self["right_bar"] = Label(vertical_right)
        t = Timer(0.5, self.update_me)
        t.start()

        # Menu list with descriptions
        self.menuList = [
            ("Addons", "Manage and install plugins"),
            ("Display", "Change your image bootlogos and spinners"),
            ("Feeds", "Update and install feeds"),
            ("Images-download", "Download new images"),
            ("Images-backup", "Enjoy images updated backups "),
            ("Picons", "Install and manage channel picons"),
            ("Settings", "Try new channels and frequencies"),
            ("Skins", "Choose and apply skins"),
            ("Softcams", "Manage softcams"),
            ("Tools", "Useful tools and extras"),
            ("Tools-panel", "Explore eliesatpanel tools"),
            ("About", "About"),
            # extras to test multiple pages
            ("Extra1", "Extra menu slot 1"),
            ("Extra2", "Extra menu slot 2"),
            ("Extra3", "Extra menu slot 3"),
            ("Extra4", "Extra menu slot 4"),
            ("Extra5", "Extra menu slot 5"),
            ("Extra6", "Extra menu slot 6"),
        ]
        self["menu"].setList(self.menuList)

        # Description label
        self["description"] = Label("")
        self["StorageInfo"] = Label(self.getStorageInfo())
        self["RAMInfo"] = Label(self.getRAMInfo())
        self["panel_version"] = Label("ElieSatPanel v" + Version)


        def updateDescription():
            current = self["menu"].getCurrent()
            if current:
                try:
                    self["description"].setText(current[1])
                except Exception:
                    self["description"].setText("")

        self["menu"].onSelectionChanged.append(updateDescription)
        updateDescription()

        # Actions
        self["setupActions"] = ActionMap(
            ["OkCancelActions", "DirectionActions", "ColorActions"],
            {
                "cancel": self.close,
                "red": self.openIptvadder,   # 🔹 red button
                "green": self.openCccamadder,   # 🔹 green button
                "yellow": self.openNews,   # 🔹 yellow button
                "blue": self.openScripts,   # 🔹 blue button
                "ok": self.ok,
                "left": self.left,
                "right": self.right,
                "up": self.up,
                "down": self.down,
            },
            -1,
        )

    # Movement handling
    def left(self):
        self["menu"].left()

    def right(self):
        self["menu"].right()

    def up(self):
        self["menu"].up()

    def down(self):
        self["menu"].down()

    # OK press
    def ok(self):
        current = self["menu"].getCurrent()
        if current:
            try:
                name = current[0]
            except Exception:
                name = str(current)

            # 🔹 Mapping menu names to their submenu classes
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
                # Open the submenu screen instead of MessageBox
                self.session.open(submenu_map[name])
            else:
                # Fallback for extras or undefined
                self.session.open(
                    MessageBox,
                    f"{name} - Coming Soon",
                    type=MessageBox.TYPE_INFO,
                    timeout=5,
                )

    def getStorageInfo(self):
        info = []
        mounts = {
            'Hdd': '/media/hdd'
        }
        
        for name, path in mounts.items():
            if os.path.ismount(path):
                try:
                    stat = os.statvfs(path)
                    total = (stat.f_blocks * stat.f_frsize) / (1024**3)
                    free = (stat.f_bfree * stat.f_frsize) / (1024**3)
                    used = total - free
                    info.append(f"{name}: {used:.1f}GB / {total:.1f}GB")
                except:
                    info.append(f"{name}: Error")
            else:
                info.append(f"{name}: Not Available")
        
        return "\n".join(info)

    def getRAMInfo(self):
        try:
            with open("/proc/meminfo") as f:
                mem = {line.split(':')[0]: line.split(':')[1].strip() for line in f}
            total = int(mem["MemTotal"].split()[0]) // 1024
            free = int(mem["MemAvailable"].split()[0]) // 1024
            used = total - free
#            return f"Ram: {total}MB used: {used}MB Free: {free}MB"
            return f"Ram: {used}MB / {total}MB"
        except:
            return "Ram: Not Available"

    # Red press
    def openIptvadder(self):
        """Open the Iptvadder submenu (triggered by red key)."""
        try:
            self.session.open(Iptvadder)
        except Exception:
            # optional: fallback MessageBox if Iptvadder cannot be opened
            self.session.open(MessageBox, "Cannot open Iptvadder.", type=MessageBox.TYPE_ERROR, timeout=5)

    # Green press
    def openCccamadder(self):
        """Open the Cccamadder submenu (triggered by green key)."""
        try:
            self.session.open(Cccamadder)
        except Exception:
            # optional: fallback MessageBox if Scripts cannot be opened
            self.session.open(MessageBox, "Cannot open Cccamadder.", type=MessageBox.TYPE_ERROR, timeout=5)

    # News press
    def openNews(self):
        """Open the News submenu (triggered by blue key)."""
        try:
            self.session.open(News)
        except Exception:
            # optional: fallback MessageBox if News cannot be opened
            self.session.open(MessageBox, "Cannot open News.", type=MessageBox.TYPE_ERROR, timeout=5)

    # Blue press
    def openScripts(self):
        """Open the Scripts submenu (triggered by blue key)."""
        try:
            self.session.open(Scripts)
        except Exception:
            # optional: fallback MessageBox if Scripts cannot be opened
            self.session.open(MessageBox, "Cannot open Scripts.", type=MessageBox.TYPE_ERROR, timeout=5)

    # ---------------- UPDATE HANDLING ----------------
    def update_me(self):
        remote_version = '0.0'
        remote_changelog = ''
        req = compat_Request(installer, headers={'User-Agent': 'Mozilla/5.0'})
        page = compat_urlopen(req).read()

        if PY3:
            data = page.decode("utf-8")
        else:
            data = page.encode("utf-8")

        if data:
            lines = data.split("\n")
            for line in lines:
                if line.startswith("version"):
                    remote_version = line.split("'")[1]
                if line.startswith("changelog"):
                    remote_changelog = line.split("'")[1]
                    break

        try:
            if float(Version) < float(remote_version):
                new_version = remote_version
                new_changelog = remote_changelog
                self.session.openWithCallback(
                    self.install_update,
                    MessageBox,
                    _("New version %s is available.\n%s\n\nDo you want to install it now?" %
                      (new_version, new_changelog)),
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
        return

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

