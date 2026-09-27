# morvane-lxqt-theme

The MorvaneOS look for LXQt: the `morvane-dark` theme for the panel, runner and
notifications, MorvaneOS colours for Qt apps, the `MorvaneOS-Dark` window borders,
candy-icons, the Sandrone cursor and the Twilight wallpaper, as LXQt's defaults.
It also picks Openbox as the window manager, so LXQt's first-run chooser doesn't
appear.

Installs:

- **LXQt theme** `morvane-dark` (`/usr/share/lxqt/themes/morvane-dark`): LXQt's
  `dark` theme with the MorvaneOS colours in place of its greys and dark red.
- **Defaults**, in `/etc/xdg/morvaneos/`: LXQt's `lxqt.conf` (theme, icons, Qt
  palette) and `session.conf` (cursor, window manager), pcmanfm-qt's `settings.conf`
  (wallpaper) and Openbox's `rc.xml` (window theme). The usual copies of those files
  belong to LXQt, pcmanfm-qt and Openbox, so these are theirs with the MorvaneOS
  settings changed, found first because morvane-gtk-theme puts
  `/etc/xdg/morvaneos` first in `XDG_CONFIG_DIRS`. Anything set in LXQt's
  Configuration Center still wins.

The window borders are the Openbox-format theme in
[morvane-gtk-theme](https://github.com/MorvaneOS/morvane-gtk-theme). The MorvaneOS
installer installs this package with LXQt.

## Changing it

Edit `tools/build.py`, then run it with the root to read LXQt's, pcmanfm-qt's and
Openbox's own files from (`/` on a system with LXQt installed):

```
python tools/build.py [root]
```

Needs only Python. Rebuild when those packages change their defaults. Commit the
output, bump `pkgver`, build and publish.

## License

The LXQt theme and settings are derived from LXQt's (LGPL-2.1-or-later); the Openbox
config from Openbox's (GPL-2.0-or-later).
