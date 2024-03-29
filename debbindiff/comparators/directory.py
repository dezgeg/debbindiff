# -*- coding: utf-8 -*-
#
# debbindiff: highlight differences between two builds of Debian packages
#
# Copyright © 2015 Jérémy Bobbio <lunar@debian.org>
#
# debbindiff is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# debbindiff is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with debbindiff.  If not, see <http://www.gnu.org/licenses/>.

import os.path
import re
import subprocess
from debbindiff import logger, tool_required, RequiredToolNotFound
from debbindiff.difference import Difference
import debbindiff.comparators
from debbindiff.comparators.utils import returns_details, Command


def ls(path):
    return '\n'.join(sorted(subprocess.check_output(['ls', path], shell=False).decode('utf-8').splitlines()))


class Stat(Command):
    @tool_required('stat')
    def cmdline(self):
        return ['stat', self.path]

    FILE_RE = re.compile(r'^\s*File:.*$')
    DEVICE_RE = re.compile(r'Device: [0-9a-f]+h/[0-9]+d')
    INODE_RE = re.compile(r'Inode: [0-9]+')
    ACCESS_TIME_RE = re.compile(r'^Access: [0-9]{4}-[0-9]{2}-[0-9]{2}.*$')

    def filter(self, line):
        line = Stat.FILE_RE.sub('', line)
        line = Stat.DEVICE_RE.sub('', line)
        line = Stat.INODE_RE.sub('', line)
        line = Stat.ACCESS_TIME_RE.sub('', line)
        return line


@tool_required('lsattr')
def lsattr(path):
    try:
        output = subprocess.check_output(['lsattr', '-d', path], shell=False, stderr=subprocess.STDOUT).decode('utf-8')
        return output.split()[0]
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            # filesystem doesn't support xattrs
            return ''


class Getfacl(Command):
    @tool_required('getfacl')
    def cmdline(self):
        return ['getfacl', '-p', '-c', self.path]


def compare_meta(path1, path2):
    logger.debug('compare_meta(%s, %s)' % (path1, path2))
    differences = []

    try:
        difference = Difference.from_command(Stat, path1, path2)
        if difference:
            differences.append(difference)
    except RequiredToolNotFound:
        logger.warn("'stat' not found! Is PATH wrong?")

    try:
        lsattr1 = lsattr(path1)
        lsattr2 = lsattr(path2)
        difference = Difference.from_unicode(
                         lsattr1, lsattr2, path1, path2, source="lattr")
        if difference:
            differences.append(difference)
    except RequiredToolNotFound:
        logger.info("Unable to find 'lsattr'.")

    try:
        difference = Difference.from_command(Getfacl, path1, path2)
        if difference:
            differences.append(difference)
    except RequiredToolNotFound:
        logger.info("Unable to find 'getfacl'.")
    return differences


@tool_required('ls')
@returns_details
def compare_directories(path1, path2, source=None):
    differences = []
    logger.debug('path1 files: %s' % sorted(set(os.listdir(path1))))
    logger.debug('path2 files: %s' % sorted(set(os.listdir(path2))))
    for name in sorted(set(os.listdir(path1)).intersection(set(os.listdir(path2)))):
        logger.debug('compare %s' % name)
        in_path1 = os.path.join(path1, name)
        in_path2 = os.path.join(path2, name)
        in_difference = debbindiff.comparators.compare_files(
                            in_path1, in_path2, source=name)
        if not os.path.isdir(in_path1):
            if in_difference:
                in_difference.add_details(compare_meta(in_path1, in_path2))
            else:
                details = compare_meta(in_path1, in_path2)
                if details:
                    d = Difference(None, path1, path2, source=name)
                    d.add_details(details)
                    in_difference = d
        differences.append(in_difference)
    ls1 = ls(path1)
    ls2 = ls(path2)
    differences.append(Difference.from_unicode(ls1, ls2, path1, path2, source="ls"))
    differences.extend(compare_meta(path1, path2))
    return differences
