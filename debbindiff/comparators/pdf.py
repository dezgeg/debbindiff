# -*- coding: utf-8 -*-
#
# debbindiff: highlight differences between two builds of Debian packages
#
# Copyright © 2015-2015 Jérémy Bobbio <lunar@debian.org>
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

import subprocess
from debbindiff import tool_required
from debbindiff.comparators.utils import binary_fallback, returns_details, Command
from debbindiff.difference import Difference, get_source


class Pdftotext(Command):
    @tool_required('pdftotext')
    def cmdline(self):
        return ['pdftotext', self.path, '-']


class Pdftk(Command):
    @tool_required('pdftk')
    def cmdline(self):
        return ['pdftk', self.path, 'output', '-', 'uncompress']

    def filter(self, line):
        return line.decode('latin-1').encode('utf-8')


@binary_fallback
@returns_details
def compare_pdf_files(path1, path2, source=None):
    differences = []
    differences.append(Difference.from_command(Pdftotext, path1, path2))
    differences.append(Difference.from_command(Pdftk, path1, path2))
    return differences
