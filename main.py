#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
SPDW Mappolo v4.0 - "Definitivo"
SPDW Factory | Sector K

Modifiche v4.0:
- Mapping istantaneo (senza cooldown)
- Data Map: A = dettagli tasto (scrollabile), poi A = rimappa, B = indietro
- L/R navigano schede dettaglio tra tasti precedente/successivo
- Icone nella legenda al posto di testo B: A:
- Fix colori settings (testo leggibile)
- Scroll nella lista tasti Data Map
- Auto-save log alla fine della mappatura
"""

import pygame
import os
import sys
import time
import json

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from mappolo_engine import (init_display, ThemeManager, FontManager, IconManager,
                             DrawSurface, Box, ProgressBar, MenuItem, BootAnimation,
                             SCREEN_W, SCREEN_H)

APP_NAME = "SPDW Mappolo"
APP_VERSION = "v4.0"

CONFIG_PATH = "/home/retrofw/rspdw_lab/settings_mappolo.json"
LOG_DIR = "/home/retrofw/rspdw_lab/black_box/"
MAP_DATA_PATH = "/home/retrofw/rspdw_lab/black_box/mappolo_data.json"
AUTO_LOG_PATH = "/home/retrofw/rspdw_lab/black_box/mappolo_auto.log"

# =============================================================================
# TASTI DA MAPPARE
# =============================================================================
DEFAULT_BUTTONS = [
    ("DPAD_UP", "up", "D-Pad Su", "key"),
    ("DPAD_DOWN", "down", "D-Pad Giu", "key"),
    ("DPAD_LEFT", "left", "D-Pad Sinistra", "key"),
    ("DPAD_RIGHT", "right", "D-Pad Destra", "key"),
    ("BTN_A", "a", "Tasto A", "key"),
    ("BTN_B", "b", "Tasto B", "key"),
    ("BTN_X", "x", "Tasto X", "key"),
    ("BTN_Y", "y", "Tasto Y", "key"),
    ("BTN_L", "l", "Tasto L (dorsale)", "key"),
    ("BTN_R", "r", "Tasto R (dorsale)", "key"),
    ("BTN_START", "start", "Tasto START", "key"),
    ("BTN_SELECT", "select", "Tasto SELECT", "key"),
    ("ANA_UP", "stick", "Analogica Su", "axis"),
    ("ANA_DOWN", "stick", "Analogica Giu", "axis"),
    ("ANA_LEFT", "stick", "Analogica Sinistra", "axis"),
    ("ANA_RIGHT", "stick", "Analogica Destra", "axis"),
    ("BRIGHTNESS", "brightness", "Tasto Luminosita", "key"),
    ("POWER", "cpu", "Tasto Power", "key"),
    ("VOL_UP", "vol+", "Rotella Volume +", "key"),
    ("VOL_DOWN", "vol-", "Rotella Volume -", "key"),
]

# =============================================================================
# KEY NAME MAP
# =============================================================================
KEY_NAME_MAP = {
    pygame.K_UP: "UP", pygame.K_DOWN: "DOWN",
    pygame.K_LEFT: "LEFT", pygame.K_RIGHT: "RIGHT",
    pygame.K_RETURN: "RETURN", pygame.K_SPACE: "SPACE",
    pygame.K_BACKSPACE: "BACKSPACE", pygame.K_TAB: "TAB",
    pygame.K_ESCAPE: "ESCAPE", pygame.K_LCTRL: "LCTRL",
    pygame.K_LALT: "LALT", pygame.K_LSHIFT: "LSHIFT",
    pygame.K_a: "a", pygame.K_b: "b", pygame.K_c: "c",
    pygame.K_d: "d", pygame.K_e: "e", pygame.K_f: "f",
    pygame.K_g: "g", pygame.K_h: "h", pygame.K_i: "i",
    pygame.K_j: "j", pygame.K_k: "k", pygame.K_l: "l",
    pygame.K_m: "m", pygame.K_n: "n", pygame.K_o: "o",
    pygame.K_p: "p", pygame.K_q: "q", pygame.K_r: "r",
    pygame.K_s: "s", pygame.K_t: "t", pygame.K_u: "u",
    pygame.K_v: "v", pygame.K_w: "w", pygame.K_x: "x",
    pygame.K_y: "y", pygame.K_z: "z",
    pygame.K_0: "0", pygame.K_1: "1", pygame.K_2: "2",
    pygame.K_3: "3", pygame.K_4: "4", pygame.K_5: "5",
    pygame.K_6: "6", pygame.K_7: "7", pygame.K_8: "8",
    pygame.K_9: "9",
    pygame.K_PERIOD: "PERIOD", pygame.K_COMMA: "COMMA",
    pygame.K_SLASH: "SLASH", pygame.K_MINUS: "MINUS",
    pygame.K_EQUALS: "EQUALS", pygame.K_SEMICOLON: "SEMICOLON",
    pygame.K_QUOTE: "QUOTE", pygame.K_LEFTBRACKET: "LEFTBRACKET",
    pygame.K_RIGHTBRACKET: "RIGHTBRACKET",
}

# =============================================================================
# EVENT TYPE NAMES
# =============================================================================
EVENT_TYPE_NAMES = {
    pygame.KEYDOWN: "KEYDOWN",
    pygame.KEYUP: "KEYUP",
    pygame.JOYBUTTONDOWN: "JOYBUTTONDOWN",
    pygame.JOYBUTTONUP: "JOYBUTTONUP",
    pygame.JOYAXISMOTION: "JOYAXISMOTION",
    pygame.JOYHATMOTION: "JOYHATMOTION",
}

# =============================================================================
# CONFIG MANAGER
# =============================================================================
class ConfigManager:
    def __init__(self, path=CONFIG_PATH):
        self.path = path
        self.config = {
            'theme': 'phantom',
            'font_size': 1,
            'audio_enabled': True,
            'show_scancode': True,
            'show_keycode': True,
            'show_event_type': True,
            'show_joy_details': True,
            'version': '4.0',
            'auto_save_log': True,
        }
        self._ensure_dir()
        self._load()

    def _ensure_dir(self):
        try:
            os.makedirs(os.path.dirname(self.path))
        except:
            pass

    def _load(self):
        try:
            if os.path.exists(self.path):
                with open(self.path, "r") as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
        except:
            pass

    def save(self):
        try:
            with open(self.path, "w") as f:
                json.dump(self.config, f, indent=2)
        except:
            pass

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save()

# =============================================================================
# MAP DATA MANAGER
# =============================================================================
class MapDataManager:
    def __init__(self, path=MAP_DATA_PATH):
        self.path = path
        self.data = {}
        self._ensure_dir()
        self._load()

    def _ensure_dir(self):
        try:
            os.makedirs(os.path.dirname(self.path))
        except:
            pass

    def _load(self):
        try:
            if os.path.exists(self.path):
                with open(self.path, "r") as f:
                    self.data = json.load(f)
        except:
            self.data = {}

    def save(self):
        try:
            with open(self.path, "w") as f:
                json.dump(self.data, f, indent=2)
        except:
            pass

    def set_mapping(self, button_id, press_data, release_data, raw_events):
        self.data[button_id] = {
            'press': press_data,
            'release': release_data,
            'raw_events': raw_events,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.save()

    def get_mapping(self, button_id):
        return self.data.get(button_id)

    def has_mapping(self, button_id):
        return button_id in self.data

    def clear_all(self):
        self.data = {}
        self.save()

    def delete_mapping(self, button_id):
        if button_id in self.data:
            del self.data[button_id]
            self.save()

    def get_all(self):
        return self.data

    def find_duplicates(self):
        keycode_to_buttons = {}
        for btn_id, info in self.data.items():
            press = info.get('press', {})
            kc = press.get('key', 0)
            if kc not in keycode_to_buttons:
                keycode_to_buttons[kc] = []
            keycode_to_buttons[kc].append(btn_id)

        duplicates = {}
        for kc, buttons in keycode_to_buttons.items():
            if len(buttons) > 1:
                duplicates[kc] = buttons
        return duplicates

    def export_log(self):
        lines = []
        lines.append("=" * 60)
        lines.append("SPDW Mappolo %s - Log Mapping Tasti RS-97+" % APP_VERSION)
        lines.append("Data: %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
        lines.append("=" * 60)
        lines.append("")

        for btn_id, info in sorted(self.data.items()):
            lines.append("-" * 60)
            lines.append("TASTO: %s" % btn_id)
            desc = btn_id
            for bid, ic, d, t in DEFAULT_BUTTONS:
                if bid == btn_id:
                    desc = d
                    break
            lines.append("Descrizione: %s" % desc)

            press = info.get('press', {})
            event_type = press.get('event_type_name', 'key')
            lines.append("Tipo: %s" % event_type)
            lines.append("STATO: MAPPATO")
            lines.append("")

            if press:
                lines.append("  --- PRESSIONE ---")
                lines.append("  type: %s" % press.get('type_name', '?'))
                lines.append("  type_id: %s" % press.get('type', '?'))
                if 'key' in press:
                    lines.append("  key_id: %s" % press['key'])
                    lines.append("  key_name: %s" % press.get('key_name', '?'))
                    lines.append("  key_hex: 0x%04X" % press['key'])
                if 'mod' in press:
                    lines.append("  mod: %s" % press['mod'])
                if 'scancode' in press:
                    lines.append("  scancode: %s" % press['scancode'])
                if 'unicode' in press and press['unicode'] is not None:
                    lines.append("  unicode: %s" % repr(press['unicode']))
                if 'joy' in press:
                    lines.append("  joy_id: %s" % press['joy'])
                if 'button' in press:
                    lines.append("  joy_button: %s" % press['button'])
                if 'axis' in press:
                    lines.append("  joy_axis: %s" % press['axis'])
                if 'value' in press:
                    lines.append("  joy_value: %s" % press['value'])
                if 'hat' in press:
                    lines.append("  joy_hat: %s" % press['hat'])
                lines.append("")

            release = info.get('release', {})
            if release:
                lines.append("  --- RILASCIO ---")
                lines.append("  type: %s" % release.get('type_name', '?'))
                lines.append("  type_id: %s" % release.get('type', '?'))
                if 'key' in release:
                    lines.append("  key_id: %s" % release['key'])
                    lines.append("  key_name: %s" % release.get('key_name', '?'))
                    lines.append("  key_hex: 0x%04X" % release['key'])
                if 'mod' in release:
                    lines.append("  mod: %s" % release['mod'])
                if 'scancode' in release:
                    lines.append("  scancode: %s" % release['scancode'])
                if 'unicode' in release and release['unicode'] is not None:
                    lines.append("  unicode: %s" % repr(release['unicode']))
                if 'joy' in release:
                    lines.append("  joy_id: %s" % release['joy'])
                if 'button' in release:
                    lines.append("  joy_button: %s" % release['button'])
                if 'axis' in release:
                    lines.append("  joy_axis: %s" % release['axis'])
                if 'value' in release:
                    lines.append("  joy_value: %s" % release['value'])
                if 'hat' in release:
                    lines.append("  joy_hat: %s" % release['hat'])
                lines.append("")

            raw_events = info.get('raw_events', [])
            if raw_events:
                lines.append("  --- RAW EVENTS (%s) ---" % len(raw_events))
                for ev in raw_events:
                    lines.append("  %s" % str(ev))
                lines.append("")

        lines.append("")
        lines.append("=" * 60)
        lines.append("FINE LOG")
        return "\n".join(lines)

# =============================================================================
# EVENT TO DICT
# =============================================================================
def event_to_dict(ev):
    d = {"type": ev.type, "type_name": EVENT_TYPE_NAMES.get(ev.type, "UNKNOWN(%s)" % ev.type)}

    if ev.type == pygame.KEYDOWN or ev.type == pygame.KEYUP:
        d["key"] = ev.key
        d["key_name"] = KEY_NAME_MAP.get(ev.key, pygame.key.name(ev.key).upper() if ev.key else "UNKNOWN")
        d["mod"] = ev.mod
        d["scancode"] = getattr(ev, "scancode", None)
        d["unicode"] = getattr(ev, "unicode", None)
    elif ev.type == pygame.JOYBUTTONDOWN or ev.type == pygame.JOYBUTTONUP:
        d["joy"] = ev.joy
        d["button"] = ev.button
    elif ev.type == pygame.JOYAXISMOTION:
        d["joy"] = ev.joy
        d["axis"] = ev.axis
        d["value"] = ev.value
    elif ev.type == pygame.JOYHATMOTION:
        d["joy"] = ev.joy
        d["hat"] = ev.hat
        d["value"] = ev.value

    return d

# =============================================================================
# MAIN APP
# =============================================================================
class MappoloApp:
    def __init__(self):
        self.screen = init_display()
        self.dsurf = DrawSurface(self.screen)

        self.config = ConfigManager()
        self.map_data = MapDataManager()

        self.theme = ThemeManager(self.config.get('theme', 'phantom'))
        self.fonts = FontManager(self.config.get('font_size', 1))
        self.icons = IconManager()

        self.ftitle, self.fcontent, self.fsmall, self.flarge, self.ftiny, self.fmedium = self.fonts.get_all()

        self.boot = BootAnimation(self.theme, self.fonts, self.icons)
        self.boot.start()

        self.state = "boot"
        self.running = True
        self.flash_msg = ""
        self.flash_time = 0

        # Menu
        self.menu_items = [
            MenuItem("Let's Map!", "stick", "map", "Inizia mapping da zero"),
            MenuItem("Data Map", "file", "datamap", "Controlla e modifica mappatura"),
            MenuItem("Settings", "menu", "settings", "Personalizza grafica"),
            MenuItem("About", "manual", "about", "Info app"),
            MenuItem("Esci", "go-up", "exit", "Chiudi applicazione"),
        ]
        self.menu_selected = 0

        # Mapping state (istantaneo, senza cooldown)
        self.mapping_index = 0
        self.mapping_buttons = list(DEFAULT_BUTTONS)
        self.mapping_active = False
        self.mapping_captured = False
        self.mapping_skipped = []
        self.mapping_done = False
        self.mapping_raw_events = []
        self.mapping_press_event = None
        self.mapping_release_event = None

        # Data Map
        self.datamap_scroll = 0
        self.datamap_selected = 0
        self.datamap_items = []
        self.datamap_mode = "view"  # view, detail, remap, confirm_delete
        self.datamap_detail_button = None
        self.datamap_detail_scroll = 0
        self.datamap_detail_lines = []

        # Settings
        self.settings_selected = 0
        self.settings_items = [
            ("Tema", "theme", ['phantom', 'matrix', 'amber']),
            ("Font Size", "font_size", [0, 1, 2]),
            ("Audio", "audio_enabled", [True, False]),
            ("Mostra Scancode", "show_scancode", [True, False]),
            ("Mostra Keycode", "show_keycode", [True, False]),
            ("Mostra Event Type", "show_event_type", [True, False]),
            ("Mostra Joy Details", "show_joy_details", [True, False]),
            ("Auto-Save Log", "auto_save_log", [True, False]),
        ]

        # About
        self.about_scroll = 0

        # Joystick
        self.joystick = None
        try:
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
        except:
            self.joystick = None

    def _reload_fonts(self):
        self.ftitle, self.fcontent, self.fsmall, self.flarge, self.ftiny, self.fmedium = self.fonts.get_all()

    def _flash(self, msg):
        self.flash_msg = msg
        self.flash_time = time.time()

    def _is_flashing(self):
        return self.flash_msg and time.time() - self.flash_time < 2.0

    # ==================== INPUT ====================
    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            # Durante mapping attivo: cattura TUTTI gli eventi
            if self.state == "mapping" and self.mapping_active and not self.mapping_captured:
                self._process_mapping_event(event)
                return

            if event.type == pygame.KEYDOWN:
                key = event.key
                self._handle_keydown(key, event)

    def _process_mapping_event(self, event):
        ev_dict = event_to_dict(event)
        self.mapping_raw_events.append(ev_dict)

        if not self.mapping_captured:
            if event.type == pygame.KEYDOWN:
                self.mapping_press_event = ev_dict
                self.mapping_captured = True
                self.mapping_active = False
                keyname = ev_dict.get('key_name', 'UNKNOWN')
                self._flash("CATTURATO: %s" % keyname)
                return
            elif event.type == pygame.JOYBUTTONDOWN:
                self.mapping_press_event = ev_dict
                self.mapping_captured = True
                self.mapping_active = False
                self._flash("CATTURATO: JOY_BTN_%d" % event.button)
                return
            elif event.type == pygame.JOYAXISMOTION:
                if abs(event.value) > 0.5:
                    self.mapping_press_event = ev_dict
                    self.mapping_captured = True
                    self.mapping_active = False
                    self._flash("CATTURATO: JOY_AXIS_%d" % event.axis)
                    return
            elif event.type == pygame.JOYHATMOTION:
                if event.value != (0, 0):
                    self.mapping_press_event = ev_dict
                    self.mapping_captured = True
                    self.mapping_active = False
                    self._flash("CATTURATO: JOY_HAT_%d" % event.hat)
                    return
        else:
            if event.type == pygame.KEYUP:
                if self.mapping_press_event and event.key == self.mapping_press_event.get('key'):
                    self.mapping_release_event = ev_dict
            elif event.type == pygame.JOYBUTTONUP:
                if self.mapping_press_event and event.button == self.mapping_press_event.get('button'):
                    self.mapping_release_event = ev_dict

    def _handle_keydown(self, key, event):
        if self.state == "boot":
            if key == pygame.K_LCTRL or key == pygame.K_RETURN:
                self.boot.done = True
                self.state = "menu"
            return

        if self.state == "menu":
            if key == pygame.K_UP:
                self.menu_selected = max(0, self.menu_selected - 1)
            elif key == pygame.K_DOWN:
                self.menu_selected = min(len(self.menu_items) - 1, self.menu_selected + 1)
            elif key == pygame.K_LCTRL:
                self._menu_select()
            return

        if self.state == "mapping":
            if self.mapping_done:
                if key == pygame.K_LCTRL:
                    self.state = "datamap"
                    self._update_datamap_items()
                elif key == pygame.K_LALT:
                    self.state = "menu"
                return

            if self.mapping_captured:
                if key == pygame.K_LCTRL:
                    self._confirm_mapping()
                elif key == pygame.K_LALT:
                    self._retry_mapping()
                elif key == pygame.K_SPACE:
                    self.state = "menu"
                    self._reset_mapping_state()
                    self._flash("Menu")
                return
            else:
                if key == pygame.K_LCTRL:
                    self._start_mapping_next()
                elif key == pygame.K_LALT:
                    self._skip_current()
                elif key == pygame.K_SPACE:
                    self.state = "menu"
                    self._reset_mapping_state()
                    self._flash("Menu")
            return

        if self.state == "datamap":
            self._handle_datamap_key(key)
            return

        if self.state == "settings":
            if key == pygame.K_UP:
                self.settings_selected = max(0, self.settings_selected - 1)
            elif key == pygame.K_DOWN:
                self.settings_selected = min(len(self.settings_items) - 1, self.settings_selected + 1)
            elif key == pygame.K_LEFT:
                self._settings_change(-1)
            elif key == pygame.K_RIGHT:
                self._settings_change(1)
            elif key == pygame.K_LALT:
                self.state = "menu"
            return

        if self.state == "about":
            if key == pygame.K_LALT:
                self.state = "menu"
            return

    def _handle_datamap_key(self, key):
        if self.datamap_mode == "confirm_delete":
            if key == pygame.K_LCTRL:
                self.map_data.delete_mapping(self.datamap_detail_button)
                self._update_datamap_items()
                self.datamap_mode = "view"
                self.datamap_detail_button = None
                self._flash("Cancellato!")
            elif key == pygame.K_LALT:
                self.datamap_mode = "detail"
                self._flash("Annullato")
            return

        if self.datamap_mode == "remap":
            scancode = 0
            keyname = KEY_NAME_MAP.get(key, pygame.key.name(key).upper() if key else "UNKNOWN")
            press_data = {
                'type': pygame.KEYDOWN,
                'type_name': 'KEYDOWN',
                'key': key,
                'key_name': keyname,
                'mod': 0,
                'scancode': scancode,
                'unicode': None,
            }
            release_data = {
                'type': pygame.KEYUP,
                'type_name': 'KEYUP',
                'key': key,
                'key_name': keyname,
                'mod': 0,
                'scancode': scancode,
                'unicode': None,
            }
            self.map_data.set_mapping(self.datamap_detail_button, press_data, release_data, [press_data, release_data])
            self._update_datamap_items()
            self.datamap_mode = "detail"
            self._build_detail_lines()
            self._flash("Rimappato!")
            return

        if self.datamap_mode == "detail":
            # Navigazione dettaglio tasto
            if key == pygame.K_LALT or key == pygame.K_BACKSPACE:
                self.datamap_mode = "view"
                self.datamap_detail_button = None
                self.datamap_detail_scroll = 0
                return
            elif key == pygame.K_LCTRL:
                # Da dettaglio, A = rimappa
                self.datamap_mode = "remap"
                self._flash("Premi tasto nuovo")
                return
            elif key == pygame.K_TAB:
                # L = tasto precedente
                self._navigate_detail(-1)
                return
            elif key == pygame.K_BACKSPACE:
                # R = tasto successivo (ma BACKSPACE e' gia' B...)
                # Usiamo LSHIFT per R
                pass
            elif key == pygame.K_LSHIFT:
                # R = tasto successivo
                self._navigate_detail(1)
                return
            elif key == pygame.K_UP:
                self.datamap_detail_scroll = max(0, self.datamap_detail_scroll - 1)
            elif key == pygame.K_DOWN:
                max_scroll = max(0, len(self.datamap_detail_lines) - 15)
                self.datamap_detail_scroll = min(max_scroll, self.datamap_detail_scroll + 1)
            return

        # View mode
        items = self.datamap_items
        if not items:
            if key == pygame.K_LALT:
                self.state = "menu"
            return

        if key == pygame.K_UP:
            self.datamap_selected = max(0, self.datamap_selected - 1)
            # Auto-scroll
            if self.datamap_selected < self.datamap_scroll:
                self.datamap_scroll = self.datamap_selected
        elif key == pygame.K_DOWN:
            self.datamap_selected = min(len(items) - 1, self.datamap_selected + 1)
            visible = 8
            if self.datamap_selected >= self.datamap_scroll + visible:
                self.datamap_scroll = self.datamap_selected - visible + 1
        elif key == pygame.K_LALT:
            self.state = "menu"
        elif key == pygame.K_LCTRL:
            # A = apre dettaglio tasto
            if self.datamap_selected < len(items):
                btn_id = items[self.datamap_selected][0]
                self.datamap_detail_button = btn_id
                self.datamap_detail_scroll = 0
                self._build_detail_lines()
                self.datamap_mode = "detail"
        elif key == pygame.K_LSHIFT:
            # Y = cancella
            if self.datamap_selected < len(items):
                btn_id = items[self.datamap_selected][0]
                self.datamap_detail_button = btn_id
                self.datamap_mode = "confirm_delete"
                self._flash("A=Cancella B=Annulla")

    def _build_detail_lines(self):
        """Costruisce le linee di testo per la schermata dettaglio"""
        self.datamap_detail_lines = []
        if not self.datamap_detail_button:
            return

        info = self.map_data.get_mapping(self.datamap_detail_button)
        if not info:
            return

        # Trova descrizione
        desc = self.datamap_detail_button
        for bid, ic, d, t in DEFAULT_BUTTONS:
            if bid == self.datamap_detail_button:
                desc = d
                break

        self.datamap_detail_lines.append("TASTO: %s" % self.datamap_detail_button)
        self.datamap_detail_lines.append("Descrizione: %s" % desc)
        self.datamap_detail_lines.append("")

        press = info.get('press', {})
        if press:
            self.datamap_detail_lines.append("--- PRESSIONE ---")
            self.datamap_detail_lines.append("type: %s" % press.get('type_name', '?'))
            self.datamap_detail_lines.append("type_id: %s" % press.get('type', '?'))
            if 'key' in press:
                self.datamap_detail_lines.append("key_id: %s" % press['key'])
                self.datamap_detail_lines.append("key_name: %s" % press.get('key_name', '?'))
                self.datamap_detail_lines.append("key_hex: 0x%04X" % press['key'])
            if 'mod' in press:
                self.datamap_detail_lines.append("mod: %s" % press['mod'])
            if 'scancode' in press:
                self.datamap_detail_lines.append("scancode: %s" % press['scancode'])
            if 'unicode' in press and press['unicode'] is not None:
                self.datamap_detail_lines.append("unicode: %s" % repr(press['unicode']))
            if 'joy' in press:
                self.datamap_detail_lines.append("joy_id: %s" % press['joy'])
            if 'button' in press:
                self.datamap_detail_lines.append("joy_button: %s" % press['button'])
            if 'axis' in press:
                self.datamap_detail_lines.append("joy_axis: %s" % press['axis'])
            if 'value' in press:
                self.datamap_detail_lines.append("joy_value: %s" % press['value'])
            if 'hat' in press:
                self.datamap_detail_lines.append("joy_hat: %s" % press['hat'])
            self.datamap_detail_lines.append("")

        release = info.get('release', {})
        if release:
            self.datamap_detail_lines.append("--- RILASCIO ---")
            self.datamap_detail_lines.append("type: %s" % release.get('type_name', '?'))
            self.datamap_detail_lines.append("type_id: %s" % release.get('type', '?'))
            if 'key' in release:
                self.datamap_detail_lines.append("key_id: %s" % release['key'])
                self.datamap_detail_lines.append("key_name: %s" % release.get('key_name', '?'))
                self.datamap_detail_lines.append("key_hex: 0x%04X" % release['key'])
            if 'mod' in release:
                self.datamap_detail_lines.append("mod: %s" % release['mod'])
            if 'scancode' in release:
                self.datamap_detail_lines.append("scancode: %s" % release['scancode'])
            if 'unicode' in release and release['unicode'] is not None:
                self.datamap_detail_lines.append("unicode: %s" % repr(release['unicode']))
            if 'joy' in release:
                self.datamap_detail_lines.append("joy_id: %s" % release['joy'])
            if 'button' in release:
                self.datamap_detail_lines.append("joy_button: %s" % release['button'])
            if 'axis' in release:
                self.datamap_detail_lines.append("joy_axis: %s" % release['axis'])
            if 'value' in release:
                self.datamap_detail_lines.append("joy_value: %s" % release['value'])
            if 'hat' in release:
                self.datamap_detail_lines.append("joy_hat: %s" % release['hat'])
            self.datamap_detail_lines.append("")

        raw_events = info.get('raw_events', [])
        if raw_events:
            self.datamap_detail_lines.append("--- RAW EVENTS (%s) ---" % len(raw_events))
            for ev in raw_events:
                self.datamap_detail_lines.append(str(ev))
            self.datamap_detail_lines.append("")

        self.datamap_detail_lines.append("Timestamp: %s" % info.get('timestamp', '?'))

    def _navigate_detail(self, direction):
        """Naviga tra i tasti nella schermata dettaglio (L/R)"""
        if not self.datamap_items or not self.datamap_detail_button:
            return

        # Trova indice attuale
        current_idx = -1
        for i, (btn_id, _) in enumerate(self.datamap_items):
            if btn_id == self.datamap_detail_button:
                current_idx = i
                break

        if current_idx < 0:
            return

        new_idx = current_idx + direction
        if 0 <= new_idx < len(self.datamap_items):
            self.datamap_detail_button = self.datamap_items[new_idx][0]
            self.datamap_detail_scroll = 0
            self._build_detail_lines()
            self.datamap_selected = new_idx
            # Aggiorna scroll lista
            visible = 8
            if new_idx < self.datamap_scroll:
                self.datamap_scroll = new_idx
            elif new_idx >= self.datamap_scroll + visible:
                self.datamap_scroll = new_idx - visible + 1

    def _menu_select(self):
        item = self.menu_items[self.menu_selected]
        if item.action_id == "map":
            self.state = "mapping"
            self.mapping_index = 0
            self._reset_mapping_state()
            self.mapping_done = False
            self.mapping_skipped = []
            self.map_data.clear_all()
        elif item.action_id == "datamap":
            self.state = "datamap"
            self.datamap_selected = 0
            self.datamap_scroll = 0
            self.datamap_mode = "view"
            self.datamap_detail_button = None
            self.datamap_detail_scroll = 0
            self._update_datamap_items()
        elif item.action_id == "settings":
            self.state = "settings"
            self.settings_selected = 0
        elif item.action_id == "about":
            self.state = "about"
            self.about_scroll = 0
        elif item.action_id == "exit":
            self.running = False

    def _update_datamap_items(self):
        self.datamap_items = sorted(self.map_data.data.items())

    def _start_mapping_next(self):
        if self.mapping_index >= len(self.mapping_buttons):
            self.mapping_done = True
            self._flash("MAPPING COMPLETO!")
            self._auto_save_log()
            return
        self.mapping_active = True
        self.mapping_captured = False
        self.mapping_press_event = None
        self.mapping_release_event = None
        self.mapping_raw_events = []

    def _skip_current(self):
        if self.mapping_index < len(self.mapping_buttons):
            btn_id, icon_name, desc, tipo = self.mapping_buttons[self.mapping_index]
            self.mapping_skipped.append(btn_id)
            self.mapping_index += 1
            self._reset_mapping_state()
            self._flash("Saltato: %s" % btn_id)
            if self.mapping_index >= len(self.mapping_buttons):
                self.mapping_done = True
                self._flash("COMPLETO! (con salti)")
                self._auto_save_log()

    def _confirm_mapping(self):
        if not self.mapping_press_event:
            return

        btn_id, icon_name, desc, tipo = self.mapping_buttons[self.mapping_index]

        if not self.mapping_release_event:
            self.mapping_release_event = dict(self.mapping_press_event)
            self.mapping_release_event['type'] = pygame.KEYUP if self.mapping_press_event.get('type') == pygame.KEYDOWN else pygame.JOYBUTTONUP
            self.mapping_release_event['type_name'] = 'KEYUP' if self.mapping_press_event.get('type_name') == 'KEYDOWN' else 'JOYBUTTONUP'

        self.map_data.set_mapping(
            btn_id,
            self.mapping_press_event,
            self.mapping_release_event,
            self.mapping_raw_events
        )

        self.mapping_index += 1
        self._reset_mapping_state()

        if self.mapping_index >= len(self.mapping_buttons):
            self.mapping_done = True
            self._flash("COMPLETO!")
            self._auto_save_log()
        else:
            self._flash("OK - Prossimo tasto")

    def _retry_mapping(self):
        self.mapping_captured = False
        self.mapping_press_event = None
        self.mapping_release_event = None
        self.mapping_raw_events = []
        self.mapping_active = True
        self._flash("Riprova - premi il tasto")

    def _reset_mapping_state(self):
        self.mapping_active = False
        self.mapping_captured = False
        self.mapping_press_event = None
        self.mapping_release_event = None
        self.mapping_raw_events = []

    def _auto_save_log(self):
        if not self.config.get('auto_save_log', True):
            return
        try:
            log_text = self.map_data.export_log()
            with open(AUTO_LOG_PATH, "w") as f:
                f.write(log_text)
            self._flash("LOG SALVATO!")
        except Exception as e:
            self._flash("ERRORE LOG: %s" % str(e)[:20])

    def _settings_change(self, direction):
        if self.settings_selected >= len(self.settings_items):
            return
        label, key, options = self.settings_items[self.settings_selected]
        current = self.config.get(key)
        if current in options:
            idx = options.index(current)
            new_idx = max(0, min(idx + direction, len(options) - 1))
            self.config.set(key, options[new_idx])
        else:
            if options:
                self.config.set(key, options[0])

        if key == 'theme':
            self.theme.set_theme(self.config.get('theme', 'phantom'))
        elif key == 'font_size':
            self.fonts.set_size(self.config.get('font_size', 1))
            self._reload_fonts()

    # ==================== DRAWING ====================
    def _draw(self):
        if self.state == "boot":
            self.boot.update()
            self.boot.draw(self.dsurf)
            if self.boot.done:
                self.state = "menu"
        elif self.state == "menu":
            self._draw_menu()
        elif self.state == "mapping":
            self._draw_mapping()
        elif self.state == "datamap":
            self._draw_datamap()
        elif self.state == "settings":
            self._draw_settings()
        elif self.state == "about":
            self._draw_about()

    def _draw_icon_legend(self, x, y, icon_name, text, color):
        """Disegna icona + testo nella legenda"""
        if self.icons.has(icon_name):
            self.icons.draw(self.dsurf.surf, icon_name, x, y)
            self.dsurf.text(self.ftiny, text, x + 18, y + 1, color)
        else:
            self.dsurf.text(self.ftiny, text, x, y + 1, color)

    def _draw_menu(self):
        self.dsurf.fill(self.theme.BG)

        try:
            title = self.ftitle.render("SPDW MAPPolo", True, self.theme.ACCENT)
            self.dsurf.blit(title, (80, 10))
            ver = self.ftiny.render(APP_VERSION, True, self.theme.DIM)
            self.dsurf.blit(ver, (230, 18))
        except:
            pass

        y = 50
        for i, item in enumerate(self.menu_items):
            box_h = 32
            x = 20
            w = 280

            if i == self.menu_selected:
                self.dsurf.fill(self.theme.MENU_SEL, (x, y, w, box_h))
                text_color = self.theme.BG
            else:
                self.dsurf.fill(self.theme.MENU_BG, (x, y, w, box_h))
                text_color = self.theme.MENU_TEXT

            if self.icons.has(item.icon_name):
                self.icons.draw(self.dsurf.surf, item.icon_name, x + 6, y + 8)
                tx = x + 32
            else:
                tx = x + 10

            self.dsurf.text(self.fcontent, item.label, tx, y + 6, text_color)

            if i == self.menu_selected:
                self.dsurf.text(self.ftiny, item.desc, tx, y + 20, self.theme.DIM)

            y += box_h + 4

        self._draw_footer()

    def _draw_footer(self):
        y = 220
        self.dsurf.fill(self.theme.DIM, (0, y, 320, 20))

        # Icone nella legenda
        self._draw_icon_legend(4, y + 2, 'a', "Seleziona", self.theme.TEXT)
        self._draw_icon_legend(90, y + 2, 'b', "Annulla", self.theme.TEXT)
        self._draw_icon_legend(170, y + 2, 'select', "Menu", self.theme.TEXT)

    def _draw_mapping(self):
        self.dsurf.fill(self.theme.BG)

        self.dsurf.text(self.ftitle, "MAPPING", 10, 8, self.theme.ACCENT)
        progress = self.mapping_index
        total = len(self.mapping_buttons)
        self.dsurf.text(self.ftiny, "%d/%d" % (progress, total), 260, 12, self.theme.DIM)

        if self.mapping_done:
            self._draw_mapping_done()
            return

        if self.mapping_index >= len(self.mapping_buttons):
            self.mapping_done = True
            self._draw_mapping_done()
            return

        btn_id, icon_name, desc, tipo = self.mapping_buttons[self.mapping_index]

        # Current button box
        box = Box(20, 36, 280, 90, self.theme, desc)
        box.draw(self.dsurf, self.fcontent, self.fcontent, [
            "ID: %s" % btn_id,
            "Tipo: %s" % tipo,
            "",
        ], icon=self.icons if self.icons.has(icon_name) else None)

        if self.icons.has(icon_name):
            try:
                big_icon = pygame.transform.scale(self.icons.get(icon_name), (48, 48))
                self.dsurf.blit(big_icon, (136, 50))
            except:
                pass

        # Status area - MAPPING ISTANTANEO (senza cooldown)
        if self.mapping_active:
            self.dsurf.text(self.flarge, "PREMI TASTO!", 55, 130, self.theme.ACCENT)
            self.dsurf.text(self.fsmall, "Premi il tasto da mappare ora", 50, 165, self.theme.WARN)
            self.dsurf.text(self.ftiny, "(qualsiasi tasto della console)", 70, 185, self.theme.DIM)

        elif self.mapping_captured:
            data = self.mapping_press_event
            self.dsurf.text(self.flarge, "CATTURATO!", 70, 120, self.theme.ACCENT)

            y_info = 150
            if 'key' in data:
                self.dsurf.text(self.fsmall, "Keycode: %d" % data['key'], 60, y_info, self.theme.TEXT)
                y_info += 14
                self.dsurf.text(self.fsmall, "Keyname: %s" % data.get('key_name', '?'), 60, y_info, self.theme.TEXT)
                y_info += 14
                self.dsurf.text(self.fsmall, "Hex: 0x%04X" % data['key'], 60, y_info, self.theme.TEXT)
                y_info += 14
            if 'scancode' in data and data['scancode'] is not None:
                self.dsurf.text(self.fsmall, "Scancode: %d" % data['scancode'], 60, y_info, self.theme.TEXT)
                y_info += 14
            if 'joy' in data:
                self.dsurf.text(self.fsmall, "Joy ID: %d" % data['joy'], 60, y_info, self.theme.TEXT)
                y_info += 14
            if 'button' in data:
                self.dsurf.text(self.fsmall, "Joy Button: %d" % data['button'], 60, y_info, self.theme.TEXT)
                y_info += 14
            if 'axis' in data:
                self.dsurf.text(self.fsmall, "Joy Axis: %d" % data['axis'], 60, y_info, self.theme.TEXT)
                y_info += 14

            self.dsurf.text(self.fsmall, "A=Conferma  B=Rifare  X=Menu", 40, 200, self.theme.ACCENT)

        else:
            self.dsurf.text(self.fcontent, "A = Inizia mapping", 60, 125, self.theme.TEXT)
            self.dsurf.text(self.fcontent, "B = Salta tasto", 60, 148, self.theme.TEXT)
            self.dsurf.text(self.fcontent, "X = Torna al menu", 60, 171, self.theme.TEXT)

            if self.map_data.has_mapping(btn_id):
                info = self.map_data.get_mapping(btn_id)
                press = info.get('press', {})
                kn = press.get('key_name', '?')
                kc = press.get('key', 0)
                self.dsurf.text(self.ftiny, "Gia: %s (kc:%d)" % (kn, kc), 60, 196, self.theme.ACCENT)

        # Flash message
        if self._is_flashing():
            self.dsurf.fill(self.theme.BG, (20, 200, 280, 30))
            self.dsurf.text(self.fcontent, self.flash_msg, 30, 205, self.theme.ACCENT2)

        self._draw_mini_progress()
        self._draw_mapping_footer()

    def _draw_mapping_done(self):
        box = Box(20, 40, 280, 140, self.theme, "COMPLETATO")

        lines = ["Tutti i tasti mappati!"]
        if self.mapping_skipped:
            lines.append("Saltati: %d" % len(self.mapping_skipped))

        dups = self.map_data.find_duplicates()
        if dups:
            lines.append("")
            lines.append("[!] TASTI DOPPI:")
            for kc, buttons in sorted(dups.items()):
                lines.append("  %s" % ", ".join(buttons))
        else:
            lines.append("Nessun doppio rilevato.")

        lines.append("")
        lines.append("A = Data Map")
        lines.append("B = Menu")

        box.draw(self.dsurf, self.fcontent, self.fsmall, lines)
        self._draw_mapping_footer()

    def _draw_mini_progress(self):
        y = 230
        done = self.mapping_index
        total = len(self.mapping_buttons)
        bar_w = 300
        fill_w = int(bar_w * done / total) if total > 0 else 0
        self.dsurf.fill(self.theme.DIM, (10, y, bar_w, 6))
        if fill_w > 0:
            self.dsurf.fill(self.theme.ACCENT, (10, y, fill_w, 6))

    def _draw_mapping_footer(self):
        y = 220
        self.dsurf.fill(self.theme.DIM, (0, y, 320, 20))

        if self.mapping_done:
            self._draw_icon_legend(10, y + 2, 'a', "Data Map", self.theme.TEXT)
            self._draw_icon_legend(120, y + 2, 'b', "Menu", self.theme.TEXT)
        elif self.mapping_active:
            self.dsurf.text(self.ftiny, "PREMI IL TASTO ORA!", 10, y + 4, self.theme.WARN)
        elif self.mapping_captured:
            self._draw_icon_legend(10, y + 2, 'a', "Conferma", self.theme.TEXT)
            self._draw_icon_legend(100, y + 2, 'b', "Rifare", self.theme.TEXT)
            self._draw_icon_legend(180, y + 2, 'x', "Menu", self.theme.TEXT)
        else:
            self._draw_icon_legend(10, y + 2, 'a', "Map", self.theme.TEXT)
            self._draw_icon_legend(70, y + 2, 'b', "Skip", self.theme.TEXT)
            self._draw_icon_legend(130, y + 2, 'x', "Menu", self.theme.TEXT)

    def _draw_datamap(self):
        if self.datamap_mode == "detail":
            self._draw_datamap_detail()
            return

        self.dsurf.fill(self.theme.BG)
        self.dsurf.text(self.ftitle, "DATA MAP", 10, 8, self.theme.ACCENT)

        if self.datamap_mode == "remap":
            self.dsurf.text(self.fsmall, "[RIMappa - premi tasto]", 140, 12, self.theme.WARN)
        elif self.datamap_mode == "confirm_delete":
            self.dsurf.text(self.fsmall, "[Cancella? A=Si B=No]", 140, 12, self.theme.ACCENT2)

        if not self.datamap_items:
            box = Box(20, 40, 280, 100, self.theme, "NESSUN DATO")
            box.draw(self.dsurf, self.fcontent, self.fcontent, [
                "Nessun tasto mappato.",
                "",
                "Vai a 'Let's Map!' per iniziare.",
            ])
            self._draw_datamap_footer()
            return

        dups = self.map_data.find_duplicates()
        dup_buttons = set()
        for btns in dups.values():
            dup_buttons.update(btns)

        # Table header
        self.dsurf.fill(self.theme.DIM, (10, 32, 300, 18))
        self.dsurf.text(self.ftiny, "TASTO", 14, 33, self.theme.BG)
        if self.config.get('show_keycode', True):
            self.dsurf.text(self.ftiny, "KC", 100, 33, self.theme.BG)
        if self.config.get('show_event_type', True):
            self.dsurf.text(self.ftiny, "TYPE", 130, 33, self.theme.BG)
        self.dsurf.text(self.ftiny, "NAME", 170, 33, self.theme.BG)
        if self.config.get('show_scancode', True):
            self.dsurf.text(self.ftiny, "SC", 260, 33, self.theme.BG)

        # Rows
        y = 54
        visible_count = 0
        for i, (btn_id, info) in enumerate(self.datamap_items):
            if y > 200:
                break
            if i < self.datamap_scroll:
                continue

            visible_count += 1
            is_dup = btn_id in dup_buttons
            press = info.get('press', {})

            if i == self.datamap_selected:
                self.dsurf.fill(self.theme.MENU_SEL, (10, y, 300, 16))
                tc = self.theme.BG
            else:
                if is_dup:
                    self.dsurf.fill((40, 10, 10), (10, y, 300, 16))
                    tc = self.theme.WARN
                else:
                    tc = self.theme.TEXT

            name = btn_id[:10]
            self.dsurf.text(self.ftiny, name, 14, y + 1, tc)

            if self.config.get('show_keycode', True):
                self.dsurf.text(self.ftiny, str(press.get('key', 0)), 100, y + 1, tc)

            if self.config.get('show_event_type', True):
                et = press.get('type_name', 'KEY')[:4]
                self.dsurf.text(self.ftiny, et, 130, y + 1, tc)

            self.dsurf.text(self.ftiny, press.get('key_name', '?')[:8], 170, y + 1, tc)

            if self.config.get('show_scancode', True):
                self.dsurf.text(self.ftiny, str(press.get('scancode', 0)), 260, y + 1, tc)

            if is_dup:
                self.dsurf.text(self.ftiny, "DUP", 290, y + 1, self.theme.WARN)

            y += 18

        if dups:
            self.dsurf.text(self.ftiny, "[DUP] = Tasto condiviso", 10, 210, self.theme.WARN)

        self._draw_datamap_footer()

    def _draw_datamap_detail(self):
        """Schermata dettaglio tasto con scroll"""
        self.dsurf.fill(self.theme.BG)

        # Titolo
        self.dsurf.text(self.ftitle, "DETTAGLIO", 10, 8, self.theme.ACCENT)
        if self.datamap_detail_button:
            self.dsurf.text(self.ftiny, self.datamap_detail_button, 200, 12, self.theme.DIM)

        # Contenuto scrollabile
        y = 32
        line_h = 12
        for i, line in enumerate(self.datamap_detail_lines):
            if i < self.datamap_detail_scroll:
                continue
            if y > 210:
                break

            # Colori diversi per sezioni
            if line.startswith("---"):
                self.dsurf.text(self.fsmall, line, 20, y, self.theme.ACCENT)
            elif line.startswith("TASTO:") or line.startswith("Descrizione:"):
                self.dsurf.text(self.fsmall, line, 20, y, self.theme.ACCENT2)
            elif line.startswith("Timestamp:"):
                self.dsurf.text(self.ftiny, line, 20, y, self.theme.DIM)
            else:
                self.dsurf.text(self.ftiny, line, 30, y, self.theme.TEXT)

            y += line_h

        # Scrollbar
        total_lines = len(self.datamap_detail_lines)
        visible_lines = 15
        if total_lines > visible_lines:
            sb_h = int((float(visible_lines) / total_lines) * 170)
            sb_y = 32 + int((float(self.datamap_detail_scroll) / total_lines) * 170)
            self.dsurf.fill(self.theme.DIM, (314, sb_y, 4, sb_h))

        self._draw_datamap_detail_footer()

    def _draw_datamap_footer(self):
        y = 220
        self.dsurf.fill(self.theme.DIM, (0, y, 320, 20))

        if self.datamap_mode == "remap":
            self.dsurf.text(self.ftiny, "Premi un tasto per rimappare", 10, y + 4, self.theme.WARN)
        elif self.datamap_mode == "confirm_delete":
            self._draw_icon_legend(10, y + 2, 'a', "Cancella", self.theme.ACCENT2)
            self._draw_icon_legend(120, y + 2, 'b', "Annulla", self.theme.ACCENT2)
        else:
            self._draw_icon_legend(4, y + 2, 'b', "Indietro", self.theme.TEXT)
            self._draw_icon_legend(90, y + 2, 'a', "Dettaglio", self.theme.TEXT)
            self._draw_icon_legend(180, y + 2, 'y', "Canc", self.theme.TEXT)

    def _draw_datamap_detail_footer(self):
        y = 220
        self.dsurf.fill(self.theme.DIM, (0, y, 320, 20))

        self._draw_icon_legend(4, y + 2, 'b', "Indietro", self.theme.TEXT)
        self._draw_icon_legend(90, y + 2, 'a', "Rimappa", self.theme.TEXT)
        self._draw_icon_legend(180, y + 2, 'l', "Prec", self.theme.TEXT)
        self._draw_icon_legend(240, y + 2, 'r', "Succ", self.theme.TEXT)

    def _draw_settings(self):
        self.dsurf.fill(self.theme.BG)
        self.dsurf.text(self.ftitle, "SETTINGS", 10, 8, self.theme.ACCENT)

        y = 40
        for i, (label, key, options) in enumerate(self.settings_items):
            box_h = 20
            if i == self.settings_selected:
                self.dsurf.fill(self.theme.MENU_SEL, (20, y, 280, box_h))
                tc = self.theme.BG  # Testo scuro su sfondo chiaro (selezione)
            else:
                self.dsurf.fill(self.theme.MENU_BG, (20, y, 280, box_h))
                tc = self.theme.MENU_TEXT  # Testo chiaro su sfondo scuro

            val = self.config.get(key)
            if isinstance(val, bool):
                val_str = "ON" if val else "OFF"
            else:
                val_str = str(val)

            self.dsurf.text(self.fsmall, label, 30, y + 2, tc)
            self.dsurf.text(self.fsmall, "< %s >" % val_str, 180, y + 2, self.theme.ACCENT)
            y += box_h + 2

        self.dsurf.text(self.fsmall, "Anteprima:", 20, y + 6, self.theme.TEXT)
        self.dsurf.fill(self.theme.ACCENT, (100, y + 6, 40, 18))
        self.dsurf.rect(self.theme.TEXT, (100, y + 6, 40, 18), 1)

        self._draw_footer()

    def _draw_about(self):
        self.dsurf.fill(self.theme.BG)
        self.dsurf.text(self.ftitle, "ABOUT", 10, 8, self.theme.ACCENT)

        lines = [
            "",
            "SPDW Mappolo %s" % APP_VERSION,
            "SPDW Factory | Sector K",
            "",
            "Tool definitivo per mapping",
            "tasti su RS-97+ RetroFW 2.3",
            "",
            "Raccolta dati COMPLETA:",
            "- Pressione e Rilascio",
            "- key_id, key_hex, key_name",
            "- scancode, unicode, mod",
            "- type_id, type_name",
            "- Raw events (tutti)",
            "- Joy button/axis/hat",
            "",
            "Mapping istantaneo:",
            "- Premi il tasto, catturato!",
            "",
            "Data Map dettagliata:",
            "- A = vedi dettaglio tasto",
            "- A = rimappa dal dettaglio",
            "- L/R = naviga schede",
            "",
            "Auto-save log alla fine",
            "",
            "SPDW Factory 2026",
        ]

        y = 36
        for line in lines:
            self.dsurf.text(self.fsmall, line, 20, y, self.theme.TEXT)
            y += 12

        self._draw_footer()

    # ==================== MAIN LOOP ====================
    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            self._handle_input()
            self._draw()
            pygame.display.flip()
            clock.tick(30)
        pygame.quit()

if __name__ == "__main__":
    try:
        app = MappoloApp()
        app.run()
    except Exception as e:
        try:
            with open(LOG_DIR + "mappolo.log", "a") as f:
                f.write("[FATAL] %s\n" % str(e))
        except:
            pass
        raise
