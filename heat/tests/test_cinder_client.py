#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""Tests for :module:'heat.engine.clients.os.cinder'."""

import mock
import uuid

from heat.common import exception
from heat.engine.clients.os import cinder
from heat.tests import common
from heat.tests import utils


class CinderClientPluginTests(common.HeatTestCase):
    """
    Basic tests for the helper methods in
    :module:'heat.engine.clients.os.cinder'.
    """
    def setUp(self):
        super(CinderClientPluginTests, self).setUp()
        self.cinder_client = self.m.CreateMockAnything()
        con = utils.dummy_context()
        c = con.clients
        self.cinder_plugin = c.client_plugin('cinder')
        self.cinder_plugin._client = self.cinder_client

    def test_get_volume(self):
        """Tests the get_volume function."""
        volume_id = str(uuid.uuid4())
        my_volume = self.m.CreateMockAnything()
        self.cinder_client.volumes = self.m.CreateMockAnything()
        self.cinder_client.volumes.get(volume_id).MultipleTimes().\
            AndReturn(my_volume)
        self.m.ReplayAll()

        self.assertEqual(my_volume, self.cinder_plugin.get_volume(volume_id))

        self.m.VerifyAll()


class VolumeConstraintTest(common.HeatTestCase):

    def setUp(self):
        super(VolumeConstraintTest, self).setUp()
        self.ctx = utils.dummy_context()
        self.mock_get_volume = mock.Mock()
        self.ctx.clients.client_plugin(
            'cinder').get_volume = self.mock_get_volume
        self.constraint = cinder.VolumeConstraint()

    def test_validation(self):
        self.mock_get_volume.return_value = None
        self.assertTrue(self.constraint.validate("foo", self.ctx))

    def test_validation_error(self):
        self.mock_get_volume.side_effect = exception.VolumeNotFound(
            volume='bar')
        self.assertFalse(self.constraint.validate("bar", self.ctx))
