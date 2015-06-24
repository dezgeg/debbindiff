#!/usr/bin/env python
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

import codecs
import os.path
import shutil
import pytest
from debbindiff.comparators.deb import compare_deb_files

TEST_FILE1_PATH = os.path.join(os.path.dirname(__file__), '../data/test1.deb')
TEST_FILE2_PATH = os.path.join(os.path.dirname(__file__), '../data/test2.deb')

def test_no_differences():
    differences = compare_deb_files(TEST_FILE1_PATH, TEST_FILE1_PATH)
    assert len(differences) == 0

@pytest.fixture
def differences():
    return compare_deb_files(TEST_FILE1_PATH, TEST_FILE2_PATH)[0].details # skip container with path

def test_compressed_files(differences):
    assert differences[0].source1 == 'control.tar.gz'
    assert differences[1].source1 == 'data.tar.gz'

def test_metadata(differences):
    expected_diff = open(os.path.join(os.path.dirname(__file__), '../data/deb_metadata_expected_diff')).read()
    assert differences[-1].unified_diff == expected_diff

