# -*- coding: utf-8 -*-
#
# debbindiff: highlight differences between two builds of Debian packages
#
# Copyright © 2014 Jérémy Bobbio <lunar@debian.org>
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
from zipfile import ZipFile, BadZipfile
from debbindiff import logger
from debbindiff.difference import Difference
import debbindiff.comparators
from debbindiff import tool_required
from debbindiff.comparators.utils import binary_fallback, returns_details, make_temp_directory, Command


class Zipinfo(Command):
    @tool_required('zipinfo')
    def cmdline(self):
        return ['zipinfo', self.path]

    def filter(self, line):
        # we don't care about the archive file path
        if re.match('^Archive:.*', line):
            return ''
        return line


class ZipinfoVerbose(Zipinfo):
    @tool_required('zipinfo')
    def cmdline(self):
        return ['zipinfo', '-v', self.path]


@binary_fallback
@returns_details
def compare_zip_files(path1, path2, source=None):
    differences = []
    try:
        with ZipFile(path1, 'r') as zip1:
            with ZipFile(path2, 'r') as zip2:
                # look up differences in content
                with make_temp_directory() as temp_dir1:
                    with make_temp_directory() as temp_dir2:
                        for name in sorted(set(zip1.namelist())
                                           .intersection(zip2.namelist())):
                            # skip directories
                            if name.endswith('/'):
                                continue
                            logger.debug('extract member %s', name)
                            in_path1 = zip1.extract(name, temp_dir1)
                            in_path2 = zip2.extract(name, temp_dir2)
                            differences.append(
                                debbindiff.comparators.compare_files(
                                    in_path1, in_path2,
                                    source=name))
                            os.unlink(in_path1)
                            os.unlink(in_path2)
                # look up differences in metadata
                difference = Difference.from_command(Zipinfo, path1, path2)
                if not difference:
                    # search harder
                    difference = Difference.from_command(ZipinfoVerbose, path1, path2)
                differences.append(difference)
    except BadZipfile:
        logger.debug('Either %s or %s is not a zip file.' % (path1, path2))
        # we'll fallback on binary comparison
    return differences
