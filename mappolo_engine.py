#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
SPDW Mappolo v4.0 - Engine Grafico
SPDW Factory | Sector K
"""

import pygame
import os
import time

SCREEN_W = 320
SCREEN_H = 240

THEMES = {
    'phantom': {
        'name': 'PHANTOM',
        'BG': (10, 10, 20), 'TEXT': (255, 255, 255), 'DIM': (100, 100, 120),
        'ACCENT': (0, 255, 200), 'ACCENT2': (255, 0, 128), 'WARN': (255, 200, 0),
        'MENU_BG': (20, 20, 40), 'MENU_SEL': (0, 255, 200), 'MENU_TEXT': (255, 255, 255),
        'BOX_BG': (15, 15, 30), 'BOX_BORDER': (0, 200, 180),
        'PROG_BG': (40, 40, 40), 'PROG_FILL': (0, 255, 200), 'PROG_BORDER': (100, 100, 100),
        'BOOT_GLOW': (0, 255, 200),
    },
    'matrix': {
        'name': 'MATRIX',
        'BG': (0, 5, 0), 'TEXT': (0, 255, 0), 'DIM': (0, 100, 0),
        'ACCENT': (0, 255, 0), 'ACCENT2': (0, 200, 0), 'WARN': (255, 255, 0),
        'MENU_BG': (0, 20, 0), 'MENU_SEL': (0, 255, 0), 'MENU_TEXT': (0, 255, 0),
        'BOX_BG': (0, 15, 0), 'BOX_BORDER': (0, 200, 0),
        'PROG_BG': (0, 30, 0), 'PROG_FILL': (0, 255, 0), 'PROG_BORDER': (0, 128, 0),
        'BOOT_GLOW': (0, 255, 0),
    },
    'amber': {
        'name': 'AMBER',
        'BG': (20, 10, 0), 'TEXT': (255, 176, 0), 'DIM': (128, 80, 0),
        'ACCENT': (255, 200, 0), 'ACCENT2': (255, 140, 0), 'WARN': (255, 100, 0),
        'MENU_BG': (40, 20, 0), 'MENU_SEL': (255, 180, 0), 'MENU_TEXT': (255, 200, 0),
        'BOX_BG': (30, 15, 0), 'BOX_BORDER': (255, 160, 0),
        'PROG_BG': (40, 25, 0), 'PROG_FILL': (255, 176, 0), 'PROG_BORDER': (160, 100, 0),
        'BOOT_GLOW': (255, 200, 0),
    },
}

class ThemeManager:
    def __init__(self, theme_name='phantom'):
        self.theme_name = theme_name
        self._apply()

    def set_theme(self, name):
        if name in THEMES:
            self.theme_name = name
            self._apply()
            return True
        return False

    def _apply(self):
        t = THEMES.get(self.theme_name, THEMES['phantom'])
        for k, v in t.items():
            setattr(self, k, v)

    def list_themes(self):
        return [(k, v['name']) for k, v in THEMES.items()]

FONT_SIZES = {
    'tiny': 10, 'small': 12, 'medium': 14, 'content': 16,
    'title': 20, 'large': 24, 'huge': 28,
}

class FontManager:
    def __init__(self, base_size=1):
        self.base_size = base_size
        self.fonts = {}
        self._load_all()

    def _sz(self, name):
        s = FONT_SIZES[name]
        if self.base_size == 0:
            return max(8, s - 2)
        elif self.base_size == 2:
            return min(32, s + 4)
        return s

    def _load_all(self):
        for name in FONT_SIZES:
            try:
                self.fonts[name] = pygame.font.Font(None, self._sz(name))
            except:
                self.fonts[name] = pygame.font.Font(None, 14)

    def set_size(self, base_size):
        self.base_size = max(0, min(2, base_size))
        self._load_all()

    def get(self, name):
        return self.fonts.get(name, self.fonts.get('content'))

    def get_all(self):
        return (self.get('title'), self.get('content'), self.get('small'),
                self.get('large'), self.get('tiny'), self.get('medium'))

ICON_PATH = "/home/retrofw/rspdw_lab/icons/"
ICON_SIZE = 16

class IconManager:
    def __init__(self):
        self.icons = {}
        self._load_icons()

    def _load_icons(self):
        icon_files = {
            'a': 'a.png', 'b': 'b.png', 'x': 'x.png', 'y': 'y.png',
            'l': 'l.png', 'r': 'r.png',
            'start': 'start.png', 'select': 'select.png',
            'up': 'up.png', 'down': 'down.png', 'left': 'left.png', 'right': 'right.png',
            'stick': 'stick.png', 'brightness': 'brightness.png',
            'file': 'file.png', 'folder': 'folder.png',
            'menu': 'menu.png', 'manual': 'manual.png',
            'go-up': 'go-up.png', 'cpu': 'cpu.png',
            'vol+': 'vol+.png', 'vol-': 'vol-.png', 'volume': 'volume.png', 'mute': 'mute.png',
            'sectionl': 'sectionl.png', 'sectionr': 'sectionr.png',
            'sd': 'sd.png',
        }
        for key, filename in icon_files.items():
            path = os.path.join(ICON_PATH, filename)
            try:
                if os.path.exists(path):
                    img = pygame.image.load(path)
                    img = pygame.transform.scale(img, (ICON_SIZE, ICON_SIZE))
                    self.icons[key] = img
            except:
                pass

    def get(self, name):
        return self.icons.get(name)

    def has(self, name):
        return name in self.icons

    def draw(self, surf, name, x, y):
        icon = self.icons.get(name)
        if icon:
            surf.blit(icon, (x, y))
            return True
        return False

    def draw_scaled(self, surf, name, x, y, size):
        icon = self.icons.get(name)
        if icon:
            try:
                scaled = pygame.transform.scale(icon, (size, size))
                surf.blit(scaled, (x, y))
                return True
            except:
                pass
        return False

class DrawSurface:
    def __init__(self, physical_surface):
        self.surf = physical_surface
        self.w = SCREEN_W
        self.h = SCREEN_H

    def fill(self, color, rect=None):
        if rect is None:
            self.surf.fill(color)
        else:
            self.surf.fill(color, rect)

    def rect(self, color, rect, width=0):
        pygame.draw.rect(self.surf, color, rect, width)

    def text(self, font, text, x, y, color, max_chars=None):
        if max_chars and len(text) > max_chars:
            text = text[:max_chars-1] + ".."
        try:
            s = font.render(text, True, color)
            self.surf.blit(s, (x, y))
        except:
            pass

    def line(self, color, p1, p2, width=1):
        pygame.draw.line(self.surf, color, p1, p2, width)

    def circle(self, color, center, radius, width=0):
        pygame.draw.circle(self.surf, color, center, radius, width)

    def blit(self, source, dest):
        self.surf.blit(source, dest)

class Box:
    def __init__(self, x, y, w, h, theme, title=""):
        self.rect = (x, y, w, h)
        self.theme = theme
        self.title = title
        self.padding = 4

    def draw(self, dsurf, font_title, font_content, content_lines=None, icon=None):
        x, y, w, h = self.rect
        dsurf.fill(self.theme.BOX_BG, self.rect)
        dsurf.rect(self.theme.BOX_BORDER, self.rect, 2)

        if self.title:
            title_h = font_title.get_height() + 4
            dsurf.fill(self.theme.BOX_BORDER, (x, y, w, title_h))
            tx = x + 4
            if icon and icon.has(self.title.lower()):
                icon.draw(dsurf.surf, self.title.lower(), tx, y + 2)
                tx += ICON_SIZE + 4
            dsurf.text(font_title, self.title, tx, y + 2, self.theme.BG)
            content_y = y + title_h + self.padding
        else:
            content_y = y + self.padding

        if content_lines and font_content:
            line_h = font_content.get_height()
            for i, line in enumerate(content_lines):
                ly = content_y + i * line_h
                if ly + line_h > y + h - self.padding:
                    break
                dsurf.text(font_content, line, x + self.padding, ly, self.theme.TEXT)

class ProgressBar:
    def __init__(self, x, y, w, h, theme):
        self.rect = (x, y, w, h)
        self.theme = theme
        self.value = 0.0
        self.label = ""

    def set(self, value, label=""):
        self.value = max(0.0, min(1.0, value))
        self.label = label

    def draw(self, dsurf, font):
        x, y, w, h = self.rect
        dsurf.fill(self.theme.PROG_BG, self.rect)
        dsurf.rect(self.theme.PROG_BORDER, self.rect, 1)
        fill_w = int((w - 4) * self.value)
        if fill_w > 0:
            dsurf.fill(self.theme.PROG_FILL, (x + 2, y + 2, fill_w, h - 4))
        pct = "%d%%" % int(self.value * 100)
        txt = "%s %s" % (self.label, pct) if self.label else pct
        dsurf.text(font, txt, x + 4, y + 1, self.theme.TEXT)

class MenuItem:
    def __init__(self, label, icon_name, action_id, desc=""):
        self.label = label
        self.icon_name = icon_name
        self.action_id = action_id
        self.desc = desc

class BootAnimation:
    def __init__(self, theme, fonts, icons):
        self.theme = theme
        self.fonts = fonts
        self.icons = icons
        self.phase = 0
        self.start_time = 0
        self.done = False
        self.letters = []
        for c in "SPDW MAPPolo":
            self.letters.append({'char': c, 'visible': False, 'time': 0})

    def start(self):
        self.start_time = time.time()
        self.phase = 0
        self.done = False

    def update(self):
        elapsed = time.time() - self.start_time
        if elapsed < 2.0:
            self.phase = 0
            for i, letter in enumerate(self.letters):
                if elapsed > 0.5 + i * 0.08:
                    letter['visible'] = True
        elif elapsed < 3.5:
            self.phase = 1
        elif elapsed < 5.0:
            self.phase = 2
        else:
            self.done = True

    def draw(self, dsurf):
        dsurf.fill(self.theme.BG)

        if self.phase == 0:
            x = 60
            y = 80
            for letter in self.letters:
                if letter['visible']:
                    color = self.theme.BOOT_GLOW
                    try:
                        glow = self.fonts.get('huge').render(letter['char'], True, color)
                        dsurf.blit(glow, (x, y))
                    except:
                        pass
                    x += 18
                else:
                    x += 18

            try:
                sub = self.fonts.get('small').render("FACTORY | SECTOR K", True, self.theme.DIM)
                dsurf.blit(sub, (90, 115))
            except:
                pass

        elif self.phase == 1:
            try:
                logo = self.fonts.get('huge').render("SPDW MAPPolo", True, self.theme.BOOT_GLOW)
                dsurf.blit(logo, (50, 70))
                sub = self.fonts.get('small').render("FACTORY | SECTOR K", True, self.theme.DIM)
                dsurf.blit(sub, (90, 105))
            except:
                pass

            prog = ProgressBar(40, 140, 240, 16, self.theme)
            prog.set(0.3, "LOADING")
            prog.draw(dsurf, self.fonts.get('tiny'))

        elif self.phase == 2:
            try:
                logo = self.fonts.get('huge').render("SPDW MAPPolo", True, self.theme.BOOT_GLOW)
                dsurf.blit(logo, (50, 70))
                sub = self.fonts.get('small').render("FACTORY | SECTOR K", True, self.theme.DIM)
                dsurf.blit(sub, (90, 105))
            except:
                pass

            prog = ProgressBar(40, 140, 240, 16, self.theme)
            prog.set(1.0, "READY")
            prog.draw(dsurf, self.fonts.get('tiny'))

            elapsed = time.time() - self.start_time
            if int(elapsed * 2) % 2 == 0:
                try:
                    prompt = self.fonts.get('large').render("Let's Map!", True, self.theme.ACCENT)
                    dsurf.blit(prompt, (80, 180))
                except:
                    pass

def init_display():
    os.environ["SDL_VIDEODRIVER"] = "fbcon"
    os.environ["SDL_FBDEV"] = "/dev/fb0"
    os.environ["SDL_NOMOUSE"] = "1"
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), 0, 16)
    pygame.mouse.set_visible(False)
    return screen
