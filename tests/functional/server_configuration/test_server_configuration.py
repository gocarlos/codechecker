#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------
#                     The CodeChecker Infrastructure
#   This file is distributed under the University of Illinois Open Source
#   License. See LICENSE.TXT for details.
# -----------------------------------------------------------------------------

"""
server_configuration function test.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import base64
import os
import unittest

from shared.ttypes import Permission
from shared.ttypes import RequestFailed

from libtest import env


class ConfigTests(unittest.TestCase):

    _ccClient = None

    def setUp(self):
        """
        Setup Configuration for tests.
        """

        # TEST_WORKSPACE is automatically set by test package __init__.py .
        self._test_workspace = os.environ['TEST_WORKSPACE']

        test_class = self.__class__.__name__
        print('Running ' + test_class + ' tests in ' + self._test_workspace)

        # Setup a viewer client to test viewer API calls.
        self._cc_client = env.setup_viewer_client(self._test_workspace)
        self.assertIsNotNone(self._cc_client)

        self.auth_client = env.setup_auth_client(self._test_workspace,
                                                 session_token='_PROHIBIT')

        self.config_client = env.setup_config_client(self._test_workspace,
                                                     session_token='_PROHIBIT')

    def test_noauth_notification_edit(self):
        """
        Test for editing the notification text on a non authenting server.
        """

        # A non-authenticated session should return an empty user.
        user = self.auth_client.getLoggedInUser()
        self.assertEqual(user, "")

        # Server without authentication should allow notification setting.
        self.config_client.setNotificationBannerText(base64.b64encode(
            'noAuth notif'))
        self.assertEqual(base64.b64decode(
            self.config_client.getNotificationBannerText()), 'noAuth notif')

    def test_auth_su_notification_edit(self):
        """
        Test that SUPERADMINS can edit the notification text.
        """
        # Create a SUPERUSER login.
        self.sessionToken = self.auth_client.performLogin("Username:Password",
                                                          "root:root")

        ret = self.auth_client.addPermission(Permission.SUPERUSER,
                                             "root",
                                             False,
                                             "")
        self.assertTrue(ret)
        # we got the permission

        su_auth_client = \
            env.setup_auth_client(self._test_workspace,
                                  session_token=self.sessionToken)

        su_config_client = \
            env.setup_config_client(self._test_workspace,
                                    session_token=self.sessionToken)

        user = su_auth_client.getLoggedInUser()
        self.assertEqual(user, "root")
        # we are root

        su_config_client.setNotificationBannerText(
                base64.b64encode('su notification'))
        self.assertEqual(base64.b64decode(
            su_config_client.getNotificationBannerText()),
                'su notification')

    def test_auth_non_su_notification_edit(self):
        """
        Test that non SUPERADMINS can't edit the notification text.
        """
        self.sessionToken = self.auth_client.performLogin("Username:Password",
                                                          "cc:test")

        authd_auth_client = \
            env.setup_auth_client(self._test_workspace,
                                  session_token=self.sessionToken)

        authd_config_client = \
            env.setup_config_client(self._test_workspace,
                                    session_token=self.sessionToken)

        user = authd_auth_client.getLoggedInUser()
        self.assertEqual(user, "cc")

        with self.assertRaises(RequestFailed):
            authd_config_client.setNotificationBannerText(
                    base64.b64encode('non su notification'))

            print("You are not authorized to modify notifications!")

    def test_unicode_string(self):
        """
        Test for non ascii strings. Needed because the used Thrift
        version won't eat them.
        """

        # A non-authenticated session should return an empty user.
        user = self.auth_client.getLoggedInUser()
        self.assertEqual(user, "")

        # Check if utf-8 encoded strings are okay.
        self.config_client.setNotificationBannerText(
                base64.b64encode('árvíztűrő tükörfúrógép'))
        self.assertEqual(base64.b64decode(
            self.config_client.getNotificationBannerText()),
            'árvíztűrő tükörfúrógép')
