# <p align="center">NewVirtualKeyBoard for Enigma2 (E²)</p>
# <p align="center">![GitHub repo size](https://img.shields.io/github/repo-size/fairbird/NewVirtualKeyBoard.svg) [![Visitors](https://api.visitorbadge.io/api/daily?path=https://github.com/fairbird/NewVirtualKeyBoard&label=Visitors%20Today&countColor=blue&style=flat)](https://visitorbadge.io/status?path=https://github.com/fairbird/NewVirtualKeyBoard)</p>

A replacement for the virtual keyboard of Enigma2 images, based on the
E2iPlayer keyboard (thanks SSS). By mfaraj57 & RAED (fairbird).

---

## Github status
[![checks](https://github.com/fairbird/NewVirtualKeyBoard/actions/workflows/checks.yml/badge.svg)](https://github.com/fairbird/NewVirtualKeyBoard/actions/workflows/checks.yml)
[![release](https://github.com/fairbird/NewVirtualKeyBoard/actions/workflows/release.yml/badge.svg)](https://github.com/fairbird/NewVirtualKeyBoard/actions/workflows/release.yml)
[![buildbot](https://github.com/fairbird/NewVirtualKeyBoard/actions/workflows/buildbot.yml/badge.svg)](https://github.com/fairbird/NewVirtualKeyBoard/actions/workflows/buildbot.yml)
[![translations](https://github.com/fairbird/NewVirtualKeyBoard/actions/workflows/translations.yml/badge.svg)](https://github.com/fairbird/NewVirtualKeyBoard/actions/workflows/translations.yml)

[![Plugin Version](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Ffairbird%2FNewVirtualKeyBoard%2Fmain%2Fusr%2Flib%2Fenigma2%2Fpython%2FPlugins%2FSystemPlugins%2FNewVirtualKeyBoard%2Fversion&search=version%3D(.%2B)&replace=%241&label=Version&color=darkviolet)](https://github.com/fairbird/NewVirtualKeyBoard/blob/main/usr/lib/enigma2/python/Plugins/SystemPlugins/NewVirtualKeyBoard/version)
[![Latest Release](https://img.shields.io/github/v/release/fairbird/NewVirtualKeyBoard?label=Latest%20Release&color=darkviolet)](https://github.com/fairbird/NewVirtualKeyBoard/releases/latest)
[![Release date](https://img.shields.io/github/release-date/fairbird/NewVirtualKeyBoard?label=From&color=darkviolet)](https://github.com/fairbird/NewVirtualKeyBoard/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/fairbird/NewVirtualKeyBoard/total.svg?label=Downloads)](https://github.com/fairbird/NewVirtualKeyBoard/releases)
[![Github last commit](https://img.shields.io/github/last-commit/fairbird/NewVirtualKeyBoard)](https://github.com/fairbird/NewVirtualKeyBoard/commits)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/fairbird/NewVirtualKeyBoard.svg?label=commits)](https://github.com/fairbird/NewVirtualKeyBoard/commits)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-2.7%20%7C%203.9--3.14-darkviolet.svg?style=flat)](https://python.org)
![Platform](https://img.shields.io/badge/Platform-Enigma2-orange.svg)
![Images](https://img.shields.io/badge/Images-openATV%20%7C%20OpenPLi%20%7C%20OpenViX%20%7C%20VTi%20%7C%20DreamOS-orange.svg)
![Resolution](https://img.shields.io/badge/Skin-HD%20%7C%20FHD%20%7C%20WQHD-orange.svg)
![Layouts](https://img.shields.io/badge/Keyboard%20layouts-218-brightgreen.svg)
[![Translations](https://img.shields.io/badge/Translations-10-brightgreen.svg)](usr/lib/enigma2/python/Plugins/SystemPlugins/NewVirtualKeyBoard/locale)
[![GitHub stars](https://img.shields.io/github/stars/fairbird/NewVirtualKeyBoard?style=flat)](https://github.com/fairbird/NewVirtualKeyBoard/stargazers)
[![Pull Requests Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)](https://github.com/fairbird/NewVirtualKeyBoard/pulls)
[![Issues](https://img.shields.io/github/issues/fairbird/NewVirtualKeyBoard?color=blue&style=flat)](https://github.com/fairbird/NewVirtualKeyBoard/issues)
[![Forks](https://img.shields.io/github/forks/fairbird/NewVirtualKeyBoard?style=flat)](https://github.com/fairbird/NewVirtualKeyBoard/forks)

---

## Installation

Online from telnet / SSH (لتثبيت البلجن مباشرة من خلال الإنترنيت بواسطة التلنت بهذا الأمر):
```
wget https://raw.githubusercontent.com/fairbird/NewVirtualKeyBoard/main/installer.sh -O - | /bin/sh
```

Or with a package from the [latest release](https://github.com/fairbird/NewVirtualKeyBoard/releases/latest):

| Image | File | Command |
|---|---|---|
| openATV, OpenPLi, OpenViX, VTi, ... | `.ipk` | `opkg install /tmp/<file>.ipk` |
| DreamOS | `.deb` | `dpkg -i /tmp/<file>.deb` |
| any | `.zip` | copy the `usr` folder to `/usr` on the box |

Restart enigma2, then choose the keyboard in **Menu > System > NewVirtualKeyBoard setup**
(Text input method: New Virtual Keyboard). Removing the package puts the
image's own keyboard back.

## Features

- all **218 Windows keyboard layouts**, drawn like the real keyboard on an
  ISO 48-key grid, with the flag of each language
- search **suggestions** from Google, YouTube, Bing, DuckDuckGo or IMDb, in
  the language of the layout
- **search history**, sorted while typing, with a size limit
- **numeric keypad** for number and PIN fields
- dead keys (accents), AltGr, Shift, Caps Lock, multi-tap input with 0-9,
  USB keyboards
- HD, FHD and WQHD skins; font size, text alignment, flags and background
  adjustable
- translations with gettext, the texts follow the enigma2 language
- online update check in the settings

## Remote control keys

| Key | Function |
|---|---|
| OK | type the selected key / take the selected suggestion or history entry |
| GREEN | Enter: confirm the text and close |
| RED | Backspace |
| YELLOW | AltGr |
| BLUE | Shift |
| TEXT | next installed keyboard layout |
| PVR, PREVIOUS / NEXT | switch between keyboard, suggestions and search history |
| LEFT / RIGHT at the edge | to the suggestions or the search history |
| CH+ / FAST FORWARD | insert space |
| CH- / REWIND | clear the text |
| 0-9 | text input like on a phone (text field selected) |
| MENU | settings, install layouts, clear the search history |
| INFO | key help |
| EXIT | close without taking the text |

## Translations

The texts are in `locale/<language>/LC_MESSAGES/NewVirtualKeyBoard.po`.
After changing texts in the code, run the **Update translation templates**
workflow (Actions tab) - it regenerates the `.pot`, merges it into every
`.po`, rebuilds the `.mo` files and opens a pull request. Translators only
edit the `.po` of their language.

## Development

- `tests/test_keyboard.py` tests the plugin with stubbed enigma2 modules,
  on Python 2.7 and 3: `python tests/test_keyboard.py 1920` (also `1280`,
  `2560`; `--net` queries the real suggestion services)
- every push runs the **checks** workflow: compile on Python 2.7 and
  3.9-3.14, the test for HD / FHD / WQHD, ruff, and the ipk / deb / zip
  packages
- a new version in `usr/.../NewVirtualKeyBoard/version` on main starts the
  **release** workflow: packages and a GitHub release
- `CI/` holds the cleanup bot (chmod, dos2unix, autopep8) and the package
  builder

## Credits

Original code SamSamSam (E2iPlayer). Contributors: mfaraj57 and RAED
(fairbird), madmax88 and the linuxsat-support forum. Skin and amends:
KiddaC. Flags partly from [flag-icons](https://github.com/lipis/flag-icons)
(MIT, see `skins/FLAGS-LICENSE.txt`).

Licensed under the GNU GPL v3, see [LICENSE](LICENSE).
