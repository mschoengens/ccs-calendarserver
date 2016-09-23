##
# Copyright (c) 2014-2016 Apple Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##
from __future__ import print_function

from calendarserver.tools.diagnose import (
    runCommand, FileNotFound
)
from twisted.trial.unittest import TestCase


class DiagnoseTestCase(TestCase):

    def test_runCommand(self):
        code, stdout, stderr = runCommand(
            "/bin/ls", "-al", "/"
        )
        self.assertEquals(code, 0)
        self.assertEquals(stderr, "")
        self.assertTrue("total" in stdout)

    def test_runCommand_nonExistent(self):
        self.assertRaises(FileNotFound, runCommand, "/xyzzy/plugh/notthere")
