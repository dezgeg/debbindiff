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

import sys
from debbindiff import logger
from debbindiff.changes import Changes
import debbindiff.comparators
from debbindiff.comparators.utils import binary_fallback, returns_details
from debbindiff.difference import Difference, get_source


DOT_CHANGES_FIELDS = [
    "Format", "Source", "Binary", "Architecture",
    "Version", "Distribution", "Urgency",
    "Maintainer", "Changed-By", "Description",
    "Changes",
    ]


@binary_fallback
@returns_details
def compare_dot_changes_files(path1, path2, source=None):
    try:
        dot_changes1 = Changes(filename=path1)
        dot_changes1.validate(check_signature=False)
        dot_changes2 = Changes(filename=path2)
        dot_changes2.validate(check_signature=False)
    except IOError, e:
        logger.critical(e)
        sys.exit(2)

    differences = []
    for field in DOT_CHANGES_FIELDS:
        differences.append(Difference.from_unicode(
                               dot_changes1[field].lstrip(),
                               dot_changes2[field].lstrip(),
                               path1, path2, source=field))

    files_difference = Difference.from_unicode(
        dot_changes1.get_as_string('Files'),
        dot_changes2.get_as_string('Files'),
        path1, path2,
        source='Files')

    if not files_difference:
        return differences

    differences.append(files_difference)

    # we are only interested in file names
    files1 = dict([(d['name'], d) for d in dot_changes1.get('Files')])
    files2 = dict([(d['name'], d) for d in dot_changes2.get('Files')])

    for filename in sorted(set(files1.keys()).intersection(files2.keys())):
        d1 = files1[filename]
        d2 = files2[filename]
        if d1['md5sum'] != d2['md5sum']:
            logger.debug("%s mentioned in .changes have "
                         "differences", filename)
            differences.append(
                debbindiff.comparators.compare_files(
                    dot_changes1.get_path(filename),
                    dot_changes2.get_path(filename),
                    source=get_source(dot_changes1.get_path(filename),
                                      dot_changes2.get_path(filename))))

    return differences
