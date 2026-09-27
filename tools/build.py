#!/usr/bin/env python3
"""Builds the MorvaneOS LXQt theme and defaults.

    python tools/build.py [root]

Needs only Python. The argument is the root to read LXQt's own files from ('/' by
default): LXQt's dark theme (lxqt-themes), its default lxqt.conf and session.conf
(lxqt-session), pcmanfm-qt's settings.conf and Openbox's rc.xml. Output goes to
theme/ and config/; commit it, it's what the package installs.

- The LXQt theme morvane-dark (panel, runner, notifications) is LXQt's dark theme
  with the MorvaneOS colours in place of its greys and dark red.
- The defaults are LXQt's, pcmanfm-qt's and Openbox's own files with the MorvaneOS
  settings changed: the theme, a MorvaneOS palette for Qt apps, icons, cursor,
  wallpaper, Openbox's MorvaneOS-Dark window borders (from morvane-gtk-theme), and
  Openbox chosen as the window manager so the first-run chooser doesn't appear.
  Those files belong to their packages, so these go in /etc/xdg/morvaneos, which
  morvane-gtk-theme puts first in XDG_CONFIG_DIRS. Users' own settings still win.
"""

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/')

THEME = 'morvane-dark'
WM_THEME = 'MorvaneOS-Dark'
WALLPAPER = '/usr/share/backgrounds/morvaneos/twilight.png'

# Brand palette (MorvaneOS/assets README), as in morvane-gtk-theme
PASTEL = '#F4A6C6'
LAVENDER = '#B9A3E6'
NIGHT = '#120C16'
PAPER = '#F5EEF3'
SURFACE = '#1A1220'
RAISED = '#221828'
BORDER = '#2A1C32'
SELECTED = '#4A3552'
MUTED = '#A898AC'

# LXQt's dark theme colours and their MorvaneOS replacements. Its accent is a dark red;
# MorvaneOS uses its purples there, keeping the same steps of lightness.
THEME_COLOURS = {
	'#1e1e1e': SURFACE,
	'#3c3c3c': BORDER,
	'#500709': '#3A2845',
	'#640b0c': SELECTED,
	'#870e10': '#5E4368',
	'#880c10': '#5E4368',
	'#6d6d6d': '#8F7F96',
	'#787676': '#8F7F96',
	'#ababab': MUTED,
	'#dedede': PAPER,
	'rgba(50, 50, 50, 80%)': 'rgba(26, 18, 32, 80%)',
}

# Qt apps' colours (lxqt.conf [Palette]); LXQt applies them with the Fusion style
PALETTE = {
	'window_color': SURFACE,
	'window_text_color': PAPER,
	'base_color': NIGHT,
	'text_color': PAPER,
	'highlight_color': PASTEL,
	'highlighted_text_color': NIGHT,
	'link_color': LAVENDER,
	'link_visited_color': '#C9A0D8',
	'tooltip_base_color': RAISED,
	'tooltip_text_color': PAPER,
}


def contrast(a: str, b: str) -> float:
	def lum(c: str) -> float:
		v = [int(c[i : i + 2], 16) / 255 for i in (1, 3, 5)]
		v = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in v]
		return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]

	hi, lo = sorted((lum(a), lum(b)), reverse=True)
	return (hi + 0.05) / (lo + 0.05)


def check() -> list[str]:
	pairs = [
		('window_text_color', 'window_color', 7.0),
		('text_color', 'base_color', 7.0),
		('highlighted_text_color', 'highlight_color', 7.0),
		('tooltip_text_color', 'tooltip_base_color', 7.0),
		('link_color', 'base_color', 4.5),
		('link_visited_color', 'base_color', 4.5),
	]
	problems = [
		f'palette: {fg} {PALETTE[fg]} on {bg} {PALETTE[bg]} is {contrast(PALETTE[fg], PALETTE[bg]):.1f}:1, needs {minimum}'
		for fg, bg, minimum in pairs
		if contrast(PALETTE[fg], PALETTE[bg]) < minimum
	]
	if contrast(PAPER, SELECTED) < 7.0:
		problems.append(f'panel: text on hovered and checked buttons is {contrast(PAPER, SELECTED):.1f}:1, needs 7')
	return problems


def set_ini(text: str, section: str, key: str, value: str) -> str:
	"""Sets key=value in [section], adding the key (or section) if it's missing."""
	lines = text.splitlines()
	start = next((i for i, line in enumerate(lines) if line.strip() == f'[{section}]'), None)
	if start is None:
		return text.rstrip('\n') + f'\n\n[{section}]\n{key}={value}\n'
	end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith('[')), len(lines))
	for i in range(start + 1, end):
		if lines[i].split('=', 1)[0].strip() == key:
			lines[i] = f'{key}={value}'
			break
	else:
		insert = end
		while insert > start + 1 and not lines[insert - 1].strip():
			insert -= 1
		lines.insert(insert, f'{key}={value}')
	return '\n'.join(lines) + '\n'


def source(path: str) -> str:
	file = SRC / path.lstrip('/')
	if not file.is_file():
		sys.exit(f'Not found: {file} (pass the root to read LXQt, pcmanfm-qt and Openbox files from)')
	return file.read_text()


def build_theme() -> None:
	src = SRC / 'usr/share/lxqt/themes/dark'
	if not src.is_dir():
		sys.exit(f"LXQt's dark theme not found: {src}")
	out = ROOT / 'theme'
	shutil.rmtree(out, ignore_errors=True)
	# Some files are links to LXQt's shared artwork. They stay links in the package, but
	# are listed in theme/symlinks rather than kept in the repo (Git for Windows can't
	# read links made on Linux); the PKGBUILD recreates them.
	shutil.copytree(src, out / THEME, symlinks=True)
	links = sorted(f for f in (out / THEME).rglob('*') if f.is_symlink())
	(out / 'symlinks').write_text(''.join(f'{link.relative_to(out)} {link.readlink()}\n' for link in links))
	for link in links:
		link.unlink()
	for file in (out / THEME).rglob('*'):
		if file.suffix in ('.qss', '.svg'):
			text = file.read_text()
			for old, new in THEME_COLOURS.items():
				text = re.sub(re.escape(old), new, text, flags=re.IGNORECASE)
			file.write_text(text)
	(out / THEME / 'wallpaper.cfg').write_text(f'[General]\nwallpaper={WALLPAPER}\n')
	(out / THEME / 'preview.png').unlink(missing_ok=True)  # shows LXQt's colours


def build_config() -> None:
	out = ROOT / 'config' / 'etc/xdg/morvaneos'
	shutil.rmtree(ROOT / 'config', ignore_errors=True)
	header = '# MorvaneOS defaults: {} with the MorvaneOS settings, from morvane-lxqt-theme (tools/build.py).\n'

	lxqt = source('/usr/share/lxqt/lxqt.conf')
	lxqt = set_ini(lxqt, 'General', 'theme', THEME)
	lxqt = set_ini(lxqt, 'General', 'icon_theme', 'candy-icons')
	lxqt = set_ini(lxqt, 'General', 'palette_override', 'true')
	for key, value in PALETTE.items():
		lxqt = set_ini(lxqt, 'Palette', key, value)

	session = source('/usr/share/lxqt/session.conf')
	session = set_ini(session, 'General', 'window_manager', 'openbox')
	session = set_ini(session, 'Mouse', 'cursor_theme', 'sandrone-linux')

	pcmanfm = source('/usr/share/pcmanfm-qt/lxqt/settings.conf')
	pcmanfm = set_ini(pcmanfm, 'Desktop', 'Wallpaper', WALLPAPER)
	pcmanfm = set_ini(pcmanfm, 'Desktop', 'WallpaperMode', 'zoom')

	openbox = source('/etc/xdg/openbox/rc.xml')
	theme_name = re.compile(r'(<theme>\s*<name>)[^<]*(</name>)')
	if not theme_name.search(openbox):
		sys.exit("Openbox's rc.xml no longer starts its <theme> with <name>; update tools/build.py")
	openbox = theme_name.sub(rf'\g<1>{WM_THEME}\g<2>', openbox, count=1)

	files = {
		'lxqt/lxqt.conf': header.format("LXQt's lxqt.conf") + lxqt,
		'lxqt/session.conf': header.format("LXQt's session.conf") + session,
		'pcmanfm-qt/lxqt/settings.conf': header.format("pcmanfm-qt's settings.conf") + pcmanfm,
		# Openbox reads the first rc.xml it finds; LXQt's session also looks for lxqt-rc.xml
		'openbox/rc.xml': openbox,
		'openbox/lxqt-rc.xml': openbox,
	}
	for path, text in files.items():
		(out / path).parent.mkdir(parents=True, exist_ok=True)
		(out / path).write_text(text)


def build() -> None:
	problems = check()
	if problems:
		sys.exit('Contrast too low, nothing written:\n  ' + '\n  '.join(problems))
	build_theme()
	build_config()
	print('Built the LXQt theme and defaults; all contrast checks passed.')


if __name__ == '__main__':
	build()
