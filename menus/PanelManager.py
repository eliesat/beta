# -*- coding: utf-8 -*-
import os
import re
import uuid

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.Label import Label
from Components.ActionMap import ActionMap

# ---------------- Unlock marker path ----------------
UNLOCK_FLAG = "/etc/eliesat_unlocked.cfg"

# ---------------- Directories (original plugin behavior) ----------------
PANEL_DIRS = [
    "/media/hdd/ElieSatPanel",
    "/media/usb/ElieSatPanel",
    "/media/mmc/ElieSatPanel"
]

def load_last_dir():
    cfg_path = "/etc/panel_dir.cfg"
    if os.path.exists(cfg_path):
        with open(cfg_path, "r") as f:
            path = f.read().strip()
            if os.path.exists(path):
                return path
    return PANEL_DIRS[0]

# ---------------- MAC / Password helpers ----------------
def get_mac_address():
    ifaces = ("eth0", "eth1", "wan0", "wlan0", "wlan1", "lan0")
    for iface in ifaces:
        path = f"/sys/class/net/{iface}/address"
        try:
            if os.path.exists(path):
                with open(path) as f:
                    mac = f.read().strip()
                if mac and mac != "00:00:00:00:00:00":
                    return mac.upper()
        except Exception:
            pass
    try:
        mac_int = uuid.getnode()
        mac_hex = f"{mac_int:012X}"
        mac = ":".join(mac_hex[i:i+2] for i in range(0, 12, 2))
        return mac
    except Exception:
        return None

def make_password_from_mac(mac):
    if not mac:
        return None
    mac = mac.strip().upper()
    if ":" in mac or "-" in mac or "." in mac:
        parts = re.split("[:\-\.]", mac)
    else:
        parts = [mac[i:i+2] for i in range(0, len(mac), 2)]
    if len(parts) < 4:
        return None
    try:
        chars = [parts[i][0] for i in range(4)]
        return "".join(chars)
    except Exception:
        return None

def is_unlocked():
    if not os.path.exists(UNLOCK_FLAG):
        return False
    try:
        with open(UNLOCK_FLAG, "r") as f:
            saved_mac = f.read().strip().upper()
        current_mac = get_mac_address()
        return bool(saved_mac and current_mac and saved_mac == current_mac)
    except Exception:
        return False

def set_unlocked(mac):
    try:
        with open(UNLOCK_FLAG, "w") as f:
            f.write((mac or "").strip().upper())
        return True
    except Exception:
        return False

# ---------------- PANEL MANAGER SCREEN ----------------
class PanelManager(Screen):
    skin = """
    <screen name="PanelManager" position="center,center" size="1280,720" title="">
        <ePixmap position="0,0" zPosition="-1" size="1280,720"
            pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/assets/background/panel_bg.png"/>

        <widget name="title_custom" position="550,0" size="400,50" font="Bold;34"
            backgroundColor="#000000" foregroundColor="yellow" transparent="0" />

        <widget name="username_label" position="40,50" size="400,40" font="Bold;32"
            foregroundColor="yellow" transparent="1"/>
        <widget name="username" position="460,50" size="780,40" font="Bold;32"
            foregroundColor="orange" transparent="1"/>

        <widget name="password_label" position="40,110" size="400,40" font="Bold;32"
            foregroundColor="yellow" transparent="1"/>
        <widget name="password" position="460,110" size="780,40" font="Bold;32"
            foregroundColor="orange" transparent="1"/>

        <widget name="dir_label" position="40,170" size="400,50" font="Bold;32"
            foregroundColor="yellow" transparent="1" />
        <widget name="dir" position="460,170" size="780,50" font="Bold;32"
            foregroundColor="orange" transparent="1" />

        <widget name="device_label" position="40,230" size="400,40" font="Bold;32"
            foregroundColor="yellow" transparent="1"/>
        <widget name="device" position="460,230" size="780,40" font="Bold;32"
            foregroundColor="orange" transparent="1"/>

        <widget name="mac_label" position="40,290" size="400,40" font="Bold;32"
            foregroundColor="yellow" transparent="1"/>
        <widget name="mac_value" position="460,290" size="780,40" font="Bold;32"
            foregroundColor="orange" transparent="1"/>

        <widget name="focus_hint" position="40,560" size="1200,40" font="Bold;30"
            foregroundColor="orange" transparent="1" halign="center"/>

        <ePixmap pixmap="skin_default/buttons/red.png" position="100,620" size="140,40" alphatest="on"/>
        <ePixmap pixmap="skin_default/buttons/green.png" position="350,620" size="140,40" alphatest="on"/>
        <ePixmap pixmap="skin_default/buttons/yellow.png" position="600,620" size="140,40" alphatest="on"/>
        <ePixmap pixmap="skin_default/buttons/blue.png" position="850,620" size="140,40" alphatest="on"/>

        <widget name="red_label" position="100,660" size="140,40" font="Bold;32" halign="center" foregroundColor="yellow" transparent="1"/>
        <widget name="green_label" position="350,660" size="140,40" font="Bold;32" halign="center" foregroundColor="yellow" transparent="1"/>
        <widget name="yellow_label" position="600,660" size="140,40" font="Bold;32" halign="center" foregroundColor="yellow" transparent="1"/>
        <widget name="blue_label" position="850,660" size="140,40" font="Bold;32" halign="center" foregroundColor="yellow" transparent="1"/>
    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session

        self.dir_index = PANEL_DIRS.index(load_last_dir())
        self.current_dir = PANEL_DIRS[self.dir_index]

        self.username_value = "ElieSat"
        self.password_value = ""
        self.mac = get_mac_address() or "Unknown"
        self.device_name = os.uname().nodename  # Device Name
        self.expected_password = make_password_from_mac(self.mac)

        # ---------------- Labels ----------------
        self["title_custom"] = Label("Panel Manager")
        self["username_label"] = Label("Username:")
        self["username"] = Label(self.username_value)
        self["password_label"] = Label("Password:")
        self["password"] = Label("")
        self["dir_label"] = Label("Default Folder Path:")
        self["dir"] = Label(self.current_dir)
        self["device_label"] = Label("Device Name:")
        self["device"] = Label(self.device_name)
        self["mac_label"] = Label("MAC Address:")
        self["mac_value"] = Label(self.mac)
        self["focus_hint"] = Label("")

        self["red_label"] = Label("Unlock")
        self["green_label"] = Label("Apply Path")
        self["yellow_label"] = Label("Cycle")
        self["blue_label"] = Label("Reset")  # Renamed

        self.focus_items = ["username", "password", "dir", "device"]
        self.focus_index = 0
        self._refresh_fields_and_focus()

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "DirectionActions"],
            {
                "ok": self._ok_pressed,
                "red": self.apply_password,
                "green": self.apply_dir,
                "yellow": self.cycle_right,
                "blue": self.reset_password,  # Blue now resets password
                "cancel": self.close,
                "up": self.focus_up,
                "down": self.focus_down,
                "left": self.cycle_left,
                "right": self.cycle_right
            }, -1
        )

        if is_unlocked() and self.expected_password:
            self.password_value = self.expected_password
            self["focus_hint"].setText("Unlocked on this device (saved).")
            self._refresh_fields_and_focus()

    # ---------------- Focus / UI helpers ----------------
    def _refresh_fields_and_focus(self):
        sel = self.focus_items[self.focus_index]
        if sel == "username":
            hint = "Selected: Username (OK to edit)"
        elif sel == "password":
            hint = "Selected: Password (OK to edit, Red = Unlock)"
        elif sel == "dir":
            hint = "Selected: Folder (OK or Green = Apply Path; Left/Right = Cycle)"
        else:
            hint = "Selected: Device Name (OK to edit)"
        self["focus_hint"].setText(hint)

        uname_display = self.username_value
        if sel == "username":
            uname_display = "> " + uname_display
        self["username"].setText(uname_display)

        masked = "*" * len(self.password_value) if self.password_value else ""
        if sel == "password":
            masked = "> " + masked
        self["password"].setText(masked)

        dir_display = self.current_dir
        if sel == "dir":
            dir_display = "> " + dir_display
        self["dir"].setText(dir_display)

        device_display = self.device_name
        if sel == "device":
            device_display = "> " + device_display
        self["device"].setText(device_display)

        self["mac_value"].setText(self.mac)

    # ---------------- Focus navigation ----------------
    def focus_up(self):
        self.focus_index = (self.focus_index - 1) % len(self.focus_items)
        self._refresh_fields_and_focus()

    def focus_down(self):
        self.focus_index = (self.focus_index + 1) % len(self.focus_items)
        self._refresh_fields_and_focus()

    # ---------------- Editing ----------------
    def _ok_pressed(self):
        sel = self.focus_items[self.focus_index]
        if sel == "username":
            self.session.openWithCallback(self._onUsernameEntered, VirtualKeyBoard, title="Enter username", text=self.username_value)
        elif sel == "password":
            self.session.openWithCallback(self._onPasswordEntered, VirtualKeyBoard, title="Enter password", text=self.password_value)
        elif sel == "device":
            self.session.openWithCallback(self._onDeviceEntered, VirtualKeyBoard, title="Enter device name", text=self.device_name)
        else:
            self.apply_dir()

    def _onUsernameEntered(self, result):
        if result is None:
            return
        self.username_value = result.strip()
        self._refresh_fields_and_focus()

    def _onPasswordEntered(self, result):
        if result is None:
            return
        self.password_value = result.strip()
        self._refresh_fields_and_focus()

    def _onDeviceEntered(self, result):
        if result is None:
            return
        self.device_name = result.strip()
        self._refresh_fields_and_focus()

    # ---------------- Unlock only ----------------
    def apply_password(self):
        if is_unlocked():
            self.session.open(MessageBox, "Already unlocked on this device.", MessageBox.TYPE_INFO)
            return

        expected = self.expected_password
        if expected is None:
            self.session.open(MessageBox, "Cannot read MAC address.", MessageBox.TYPE_ERROR)
            return

        if (self.username_value.strip().upper() != "ELIESAT" or
            self.password_value.strip().upper() != expected.strip().upper()):
            self.session.open(MessageBox, "Access denied — wrong username or password.", MessageBox.TYPE_ERROR)
            return

        if set_unlocked(self.mac):
            self.session.open(MessageBox, "✅ Password accepted — device unlocked successfully.", MessageBox.TYPE_INFO)
        else:
            self.session.open(MessageBox, "❌ Failed to save unlock flag in /etc/.", MessageBox.TYPE_ERROR)

    # ---------------- Apply folder only ----------------
    def apply_dir(self):
        try:
            for folder in PANEL_DIRS:
                cfg_file = os.path.join(folder, "panel_dir.cfg")
                if folder != self.current_dir and os.path.exists(cfg_file):
                    os.remove(cfg_file)

            if not os.path.exists(self.current_dir):
                os.makedirs(self.current_dir)

            cfg_file = os.path.join(self.current_dir, "panel_dir.cfg")
            with open(cfg_file, "w") as f:
                f.write(self.current_dir)

            self.session.open(MessageBox, f"📁 Default folder path applied:\n{self.current_dir}", MessageBox.TYPE_INFO)
        except Exception as e:
            self.session.open(MessageBox, f"Failed to apply folder:\n{e}", MessageBox.TYPE_ERROR)

    # ---------------- Reset password ----------------
    def reset_password(self):
        self.password_value = ""
        self._refresh_fields_and_focus()
        self.session.open(MessageBox, "Password has been reset.", MessageBox.TYPE_INFO)

    # ---------------- Folder cycling ----------------
    def cycle_left(self):
        if self.focus_items[self.focus_index] != "dir":
            return
        self.dir_index = (self.dir_index - 1) % len(PANEL_DIRS)
        self.current_dir = PANEL_DIRS[self.dir_index]
        self._refresh_fields_and_focus()

    def cycle_right(self):
        if self.focus_items[self.focus_index] != "dir":
            return
        self.dir_index = (self.dir_index + 1) % len(PANEL_DIRS)
        self.current_dir = PANEL_DIRS[self.dir_index]
        self._refresh_fields_and_focus()

