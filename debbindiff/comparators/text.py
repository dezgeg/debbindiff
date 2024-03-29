# -*- coding: utf-8 -*-
#
# debbindiff: highlight differences between two builds of Debian packages
#
# Copyright © 2014-2015 Jérémy Bobbio <lunar@debian.org>
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

import codecs
from debbindiff.comparators.binary import compare_binary_files
from debbindiff.difference import Difference


def compare_text_files(path1, path2, encoding=None, source=None):
    if encoding is None:
        encoding = 'utf-8'
    try:
        file1 = codecs.open(path1, 'r', encoding=encoding)
        file2 = codecs.open(path2, 'r', encoding=encoding)
        return Difference.from_file(file1, file2, path1, path2, source)
    except (LookupError, UnicodeDecodeError):
        # unknown or misdetected encoding
        return compare_binary_files(path1, path2, source)
