# -*- coding: utf-8 -*-
import os
from Screens.Screen import Screen
from Components.Label import Label
from Components.ActionMap import ActionMap
from Plugins.Extensions.ElieSatPanel.__init__ import Version
from Plugins.Extensions.ElieSatPanel.menus.Helpers import (
    get_local_ip,
    check_internet,
    get_image_name,
    get_python_version,
    get_storage_info,
    get_ram_info,
)

class blankm(Screen):
    def __init__(self, session):
        # -------- Load appropriate skin (FHD preferred) --------
        base_skin_path = "/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/skin/"
        hd_skin = os.path.join(base_skin_path, "eliesatpanel_hd.xml")
        fhd_skin = os.path.join(base_skin_path, "eliesatpanel_fhd.xml")

        if os.path.exists(fhd_skin):
            skin_file = fhd_skin
        elif os.path.exists(hd_skin):
            skin_file = hd_skin
        else:
            skin_file = None

        if skin_file:
            try:
                with open(skin_file, "r") as f:
                    self.skin = f.read()
            except Exception:
                self.skin = None

        if not getattr(self, "skin", None):
            self.skin = """<screen name="ElieSatPanel" position="center,center" size="1280,720" title="ElieSatPanel">
                <eLabel text="Eliesat Panel - Skin Missing" position="center,center" size="400,50"
                    font="Regular;30" halign="center" valign="center" />
            </screen>"""

        Screen.__init__(self, session)

        # -------- Vertical Text for Version & Custom --------
        vertical_left = "\n".join(list("Version " + Version))
        vertical_right = "\n".join(list("By ElieSat"))
        self["left_bar"] = Label(vertical_left)
        self["right_bar"] = Label(vertical_right)

        # -------- Labels --------
        self["image_name"] = Label(get_image_name())
        self["local_ip"] = Label(get_local_ip())
        self["StorageInfo"] = Label(get_storage_info())
        self["RAMInfo"] = Label(get_ram_info())
        self["python_ver"] = Label(f"Python {get_python_version()}")
        self["net_status"] = Label("Online" if check_internet() else "Offline")
        self["menu"] = Label("")  # Replace with actual menu widget if needed
        self["description"] = Label("")
        self["pagelabel"] = Label("●")
        self["pageinfo"] = Label("Page 1/1")
        self["red"] = Label("IPTV Adder")
        self["green"] = Label("Cccam Adder")
        self["yellow"] = Label("News")
        self["blue"] = Label("Scripts")
        self["version"] = Label(f"ElieSatPanel {Version}")

        # -------- Actions --------
        self["setupActions"] = ActionMap(
            ["OkCancelActions", "DirectionActions", "ColorActions", "MenuActions"],
            {
                "cancel": self.close,
                "red": lambda: None,
                "green": lambda: None,
                "yellow": lambda: None,
                "blue": lambda: None,
                "ok": lambda: None,
                "left": lambda: None,
                "right": lambda: None,
                "up": lambda: None,
                "down": lambda: None,
                "menu": lambda: None,
            },
            -1
        )

