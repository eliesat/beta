# -*- coding: utf-8 -*-
from Plugins.Extensions.ElieSatPanel.menus.Helpers import (
    get_local_ip,
    check_internet,
    get_image_name,
    get_python_version,
    get_storage_info,
    get_ram_info,
)

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Plugins.Extensions.ElieSatPanel.__init__ import Version


class Abt(Screen):
    skin = """
    <screen name="About" position="0,0" size="1920,1080" backgroundColor="transparent" flags="wfNoBorder" title="Scripts">
        <ePixmap position="0,0" zPosition="-1" size="1920,1080"
            pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/background/panel_bg.png"/>

        <!-- 🔹 Top black bar -->
        <eLabel position="0,0" size="1920,130" zPosition="10" backgroundColor="#000000" />

        <!-- 🔹 Title -->
        <eLabel text="● Blank Plugin – Linked to Red Button"
            position="350,0" size="1400,50" zPosition="11"
            font="Bold;32" halign="left" valign="center" noWrap="1"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <!-- 🔹 Bottom color button bars + labels -->
        <eLabel position="0,1075" size="480,5" zPosition="2" backgroundColor="red" />
        <widget name="red" position="0,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Red Button"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <eLabel position="480,1075" size="480,5" zPosition="2" backgroundColor="green" />
        <widget name="green" position="480,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Green Button"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <eLabel position="960,1075" size="480,5" zPosition="2" backgroundColor="yellow" />
        <widget name="yellow" position="960,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Yellow Button"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <eLabel position="1440,1075" size="480,5" zPosition="2" backgroundColor="blue" />
        <widget name="blue" position="1440,1000" size="480,75" zPosition="2"
            font="Bold;32" halign="center" valign="center"
            text="Blue Button"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="0" />

        <!-- 🔹 Left vertical black bar -->
        <eLabel position="0,130" size="80,870" zPosition="10" backgroundColor="#000000" />
        <!-- 🔹 Right vertical black bar -->
        <eLabel position="1840,130" size="80,870" zPosition="10" backgroundColor="#000000" />

        <!-- 🔹 Date -->
        <widget source="global.CurrentTime" render="Label"
            position="1350,180" size="500,35" zPosition="12"
            font="Bold;32" halign="center" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="1">
            <convert type="ClockToText">Format %A %d %B</convert>
        </widget>

        <!-- 🔹 Clock -->
        <widget source="global.CurrentTime" render="Label"
            position="1350,220" size="500,35" zPosition="12"
            font="Bold;32" halign="center" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="1">
            <convert type="ClockToText">Format %H:%M:%S</convert>
        </widget>

        <!-- 🔹 Image name -->
        <widget name="image_name"
            position="1470,420" size="500,35" zPosition="12"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="1" />

        <!-- 🔹 Python version -->
        <widget name="python_ver"
            position="1470,460" size="500,35" zPosition="12"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="1" />

        <!-- 🔹 Local IP -->
        <widget name="local_ip"
            position="1470,500" size="500,35" zPosition="12"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="1" />

        <!-- 🔹 Storage Info -->
        <widget name="StorageInfo"
            position="1470,540" size="500,35" zPosition="12"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="1" />

        <!-- 🔹 Ram Info -->
        <widget name="RAMInfo"
            position="1470,580" size="500,35" zPosition="12"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="1" />

        <!-- 🔹 Net Status -->
        <widget name="net_status"
            position="1470,620" size="500,35" zPosition="12"
            font="Bold;32" halign="left" valign="center"
            foregroundColor="yellow" backgroundColor="#000000"
            transparent="1" />

        <!-- 🔹 Panel Version on LEFT bar -->
        <widget name="left_bar"
            position="20,160" size="60,760" zPosition="20"
            font="Regular;26" halign="center" valign="top"
            foregroundColor="yellow" transparent="1" noWrap="1" />
        <!-- 🔹 Custom text on RIGHT bar -->
        <widget name="right_bar"
            position="1850,160" size="60,760" zPosition="20"
            font="Regular;26" halign="center" valign="top"
            foregroundColor="yellow" transparent="1" noWrap="1" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.setTitle(_("Blank Plugin"))

        vertical_left = "\n".join(list("Version " + Version))
        vertical_right = "\n".join(list("By ElieSat"))
        self["left_bar"] = Label(vertical_left)
        self["right_bar"] = Label(vertical_right)

        # System info
        self["image_name"] = Label("Image: " + get_image_name())
        self["local_ip"] = Label("IP: " + get_local_ip())
        self["StorageInfo"] = Label(get_storage_info())
        self["RAMInfo"] = Label(get_ram_info())
        self["python_ver"] = Label("Python: " + get_python_version())
        self["net_status"] = Label("Net: " + check_internet())

        # Buttons
        self["red"] = Label(_("Red"))
        self["green"] = Label(_("Green"))
        self["yellow"] = Label(_("Yellow"))
        self["blue"] = Label(_("Blue"))

        # Actions (placeholders)
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {
                "red": self.dummy,
                "green": self.dummy,
                "yellow": self.dummy,
                "blue": self.dummy,
                "cancel": self.close,
            },
            -1,
        )

    def dummy(self):
        self.session.open(MessageBox, _("This button is not linked yet."), MessageBox.TYPE_INFO, timeout=3)

