#!/usr/bin/env python3
# Builds the release packages of NewVirtualKeyBoard from the repository:
#   enigma2-plugin-systemplugins-newvirtualkeyboard_<version>_all.ipk  (OE images:
#       openATV, OpenPLi, OpenViX, ... - opkg)
#   enigma2-plugin-systemplugins-newvirtualkeyboard_<version>_all.deb  (DreamOS - dpkg)
#   NewVirtualKeyBoard-<version>.zip   (usr/ tree to copy to the box by hand)
#   SHA256SUMS
# ipk and deb are the same ar container (debian-binary, control.tar.gz,
# data.tar.gz); written with the standard library only, so it runs anywhere.
# Translation sources (.po/.pot, updateallpo.sh) and compiled Python files are
# left out - the box needs the .mo files only.
# usage: python3 CI/build_packages.py [--out dist]
import argparse
import gzip
import hashlib
import io
import os
import re
import stat
import tarfile
import time
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN_REL = 'usr/lib/enigma2/python/Plugins/SystemPlugins/NewVirtualKeyBoard'
PACKAGE = 'enigma2-plugin-systemplugins-newvirtualkeyboard'

# leftovers of versions installed with installer.sh before 13.9 (the prerm
# script is CI/prerm.sh)
POSTINST = """#!/bin/sh
P=/usr/lib/enigma2/python/Plugins/SystemPlugins/NewVirtualKeyBoard
rm -rf $P/language $P/language_config.py* $P/compat.py* $P/skins/NewVirtualKeyBoard*.py* $P/skins/__init__.py* $P/skins/icons/vk
echo "NewVirtualKeyBoard installed - restart enigma2 and select the new keyboard in Menu > System > NewVirtualKeyBoard setup"
exit 0
"""


def read(path, mode='r'):
    with open(os.path.join(REPO, path), mode) as f:
        return f.read()


def version():
    return re.search(r'^version=(\S+)', read(os.path.join(PLUGIN_REL, 'version')), re.M).group(1)


def changelog():
    # the "What is NEW" lines of installer.sh (also shown by the update check)
    m = re.search(r'description="\n(.*?)\n"', read('installer.sh'), re.S)
    return m.group(1).strip() if m else ''


def plugin_files():
    base = os.path.join(REPO, PLUGIN_REL)
    for root, dirs, files in os.walk(base):
        dirs[:] = sorted(d for d in dirs if d != '__pycache__')
        for name in sorted(files):
            if name.endswith(('.pyc', '.pyo', '.po', '.pot')) or name == 'updateallpo.sh':
                continue
            full = os.path.join(root, name)
            yield full, os.path.relpath(full, REPO).replace(os.sep, '/')


def tar_gz(members, mtime):
    # members: [(archive name, bytes or None for a directory, mode)]
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode='wb', mtime=mtime) as gz:
        with tarfile.open(fileobj=gz, mode='w', format=tarfile.GNU_FORMAT) as tar:
            for name, data, mode in members:
                info = tarfile.TarInfo(name)
                info.uid = info.gid = 0
                info.uname = info.gname = 'root'
                info.mtime = mtime
                info.mode = mode
                if data is None:
                    info.type = tarfile.DIRTYPE
                    tar.addfile(info)
                else:
                    info.size = len(data)
                    tar.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def ar(members, mtime):
    out = [b'!<arch>\n']
    for name, data in members:
        header = '%-16s%-12d%-6d%-6d%-8s%-10d`\n' % (name, mtime, 0, 0, '100644', len(data))
        out.append(header.encode('ascii'))
        out.append(data)
        if len(data) % 2:
            out.append(b'\n')
    return b''.join(out)


def data_members(files):
    dirs = set()
    members = []
    for full, rel in files:
        parts = rel.split('/')
        for i in range(1, len(parts)):
            d = '/'.join(parts[:i])
            if d not in dirs:
                dirs.add(d)
                members.append(('./' + d + '/', None, 0o755))
        mode = 0o755 if rel.endswith('.sh') else 0o644
        members.append(('./' + rel, read(full, 'rb'), mode))
    return [('./', None, 0o755)] + members


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(REPO, 'dist'))
    a = ap.parse_args()
    a.out = os.path.abspath(a.out)
    ver = version()
    mtime = int(os.environ.get('SOURCE_DATE_EPOCH', time.time()))
    os.makedirs(a.out, exist_ok=True)
    files = list(plugin_files())
    installed_kb = (sum(os.path.getsize(f) for f, r in files) + 1023) // 1024
    desc = ['NewVirtualKeyBoard - virtual keyboard with all Windows keyboard layouts',
            ' Replacement virtual keyboard for enigma2 by mfaraj57 & RAED (fairbird),',
            ' based on the E2iPlayer keyboard.']
    for line in changelog().splitlines():
        line = line.strip()
        if line.startswith('-'):
            desc.append(' ' + line)
    control = '\n'.join([
        'Package: %s' % PACKAGE,
        'Version: %s' % ver,
        'Architecture: all',
        'Section: extra',
        'Priority: optional',
        'Maintainer: RAED - fairbird <rrrr53@hotmail.com>',
        'Homepage: https://github.com/fairbird/NewVirtualKeyBoard',
        'Installed-Size: %d' % installed_kb,
        'Description: ' + desc[0],
    ] + desc[1:]) + '\n'
    control_tgz = tar_gz([('./', None, 0o755), ('./control', control.encode('utf-8'), 0o644),
                          ('./postinst', POSTINST.encode(), 0o755), ('./prerm', read('CI/prerm.sh', 'rb'), 0o755)], mtime)
    data_tgz = tar_gz(data_members(files), mtime)
    package = ar([('debian-binary', b'2.0\n'), ('control.tar.gz', control_tgz), ('data.tar.gz', data_tgz)], mtime)
    outputs = []
    for ext in ('ipk', 'deb'):
        path = os.path.join(a.out, '%s_%s_all.%s' % (PACKAGE, ver, ext))
        with open(path, 'wb') as f:
            f.write(package)
        outputs.append(path)
    zpath = os.path.join(a.out, 'NewVirtualKeyBoard-%s.zip' % ver)
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for full, rel in files:
            info = zipfile.ZipInfo(rel, time.gmtime(mtime)[:6])
            info.external_attr = (stat.S_IFREG | (0o755 if rel.endswith('.sh') else 0o644)) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, read(full, 'rb'))
    outputs.append(zpath)
    with open(os.path.join(a.out, 'SHA256SUMS'), 'w') as f:
        for path in outputs:
            f.write('%s  %s\n' % (hashlib.sha256(read(path, 'rb')).hexdigest(), os.path.basename(path)))
    print('version %s, %d files, installed %d KB' % (ver, len(files), installed_kb))
    for path in outputs:
        print('  %-70s %8d bytes' % (os.path.basename(path), os.path.getsize(path)))


if __name__ == '__main__':
    main()
