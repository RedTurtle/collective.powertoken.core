# -*- coding: utf-8 -*-

from AccessControl import Unauthorized

from zope.component import getUtility, ComponentLookupError
from zope.annotation.interfaces import IAnnotations

from collective.powertoken.core import config
from collective.powertoken.core.exceptions import PowerTokenSecurityError, PowerTokenConfigurationError
from collective.powertoken.core.interfaces import IPowerTokenUtility, IPowerTokenizedContent 
from collective.powertoken.core.tests.base import TestCase

class TestToken(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))
        portal = self.portal
        portal.invokeFactory(type_name="Document", id="testdoc")
        doc = portal.testdoc
        doc.edit(title="A test document")
        self.utility = getUtility(IPowerTokenUtility)
        self.doc = portal.testdoc
        self.request = self.portal.REQUEST

    def test_enablePowerToken(self):
        token = self.utility.enablePowerToken(self.doc, 'foo')
        configuration = IAnnotations(self.doc)[config.MAIN_TOKEN_NAME]
        self.assertTrue(IPowerTokenizedContent.providedBy(self.doc))
        self.assertEquals(configuration.keys()[0], token)

    def test_addAction(self):
        self.assertRaises(PowerTokenConfigurationError, self.utility.addAction, self.doc, 'fooToken', 'fooAction')
        token = self.utility.enablePowerToken(self.doc, 'foo')
        self.utility.addAction(self.doc, token, 'fooAction')
        annotations = IAnnotations(self.doc)
        self.assertEqual(len(annotations[config.MAIN_TOKEN_NAME][token]), 2)
        self.assertEqual(annotations[config.MAIN_TOKEN_NAME][token][0].type, 'foo')
        self.assertEqual(annotations[config.MAIN_TOKEN_NAME][token][1].type, 'fooAction')

    def test_disablePowerTokens(self):
        token1 = self.utility.enablePowerToken(self.doc, 'foo')
        token2 = self.utility.enablePowerToken(self.doc, 'foo')
        self.assertTrue(IPowerTokenizedContent.providedBy(self.doc))
        self.utility.disablePowerTokens(self.doc)
        self.assertFalse(IPowerTokenizedContent.providedBy(self.doc))
        self.assertRaises(PowerTokenConfigurationError, self.utility.verifyToken, self.doc, token1, False)
        self.assertRaises(PowerTokenConfigurationError, self.utility.verifyToken, self.doc, token2, False)
        self.assertEqual(IAnnotations(self.doc).get(config.MAIN_TOKEN_NAME), None)

    def test_verifyToken(self):
        self.assertRaises(PowerTokenConfigurationError, self.utility.verifyToken, self.doc, 'foo', False)
        token = self.utility.enablePowerToken(self.doc, 'foo')
        self.assertFalse(self.utility.verifyToken(self.doc, 'foo', False))
        self.assertRaises(PowerTokenSecurityError, self.utility.verifyToken, self.doc, 'foo')
        self.assertTrue(self.utility.verifyToken(self.doc, token))
        annotations = IAnnotations(self.doc)
        del annotations[config.MAIN_TOKEN_NAME]
        self.assertRaises(KeyError, self.utility.verifyToken, self.doc, 'foo', False)

    def test_consumeToken(self):
        token1 = self.utility.enablePowerToken(self.doc, 'foo')
        self.utility.addAction(self.doc, token1, 'anotherFoo')
        token2 = self.utility.enablePowerToken(self.doc, 'foo')
        configuration = IAnnotations(self.doc)[config.MAIN_TOKEN_NAME]
        self.assertEqual(len(configuration), 2)
        self.assertEqual(len(self.utility.consumeToken(self.doc, token1)), 2)
        self.assertEqual(len(configuration), 1)
        self.utility.consumeToken(self.doc, token2)
        self.assertEqual(IAnnotations(self.doc).get(config.MAIN_TOKEN_NAME), None)
    
    def test_consumePermanentToken(self):
        """When oneTime is False for at leat one action"""
        token = self.utility.enablePowerToken(self.doc, 'foo', oneTime=False)
        configuration = IAnnotations(self.doc)[config.MAIN_TOKEN_NAME]
        self.assertEquals(len(configuration), 1)
        self.assertEquals(len(configuration[token]), 1)
        self.utility.consumeToken(self.doc, token)
        self.utility.consumeToken(self.doc, token)
        self.assertEquals(len(configuration), 1)
        # now add another non-permanent action
        self.utility.addAction(self.doc, token, 'anotherFoo')
        self.assertEquals(len(configuration), 1)
        self.assertEquals(len(configuration[token]), 2)
        self.utility.consumeToken(self.doc, token)
        self.assertEquals(len(configuration), 1)
        self.assertEquals(len(configuration[token]), 1)
        self.utility.consumeToken(self.doc, token)
        self.assertEquals(len(configuration), 1)
        self.assertEquals(len(configuration[token]), 1)

    def test_removeToken(self):
        token1 = self.utility.enablePowerToken(self.doc, 'foo')
        token2 = self.utility.enablePowerToken(self.doc, 'foo')
        configuration = IAnnotations(self.doc)[config.MAIN_TOKEN_NAME]
        self.assertEquals(len(configuration), 2)
        self.utility.removeToken(self.doc, token1)
        self.assertEqual(len(configuration), 1)
        self.utility.removeToken(self.doc, token2)
        self.assertEqual(IAnnotations(self.doc).get(config.MAIN_TOKEN_NAME), None)

    def test_consumeActions(self):
        token = self.utility.enablePowerToken(self.doc, 'foo')
        self.assertEqual(self.utility.consumeActions(self.doc, token),
                         [('http://nohost/plone/testdoc', 'foo', {}, {})])
        self.assertRaises(PowerTokenConfigurationError, self.utility.consumeActions, self.doc, token)
        token = self.utility.enablePowerToken(self.doc, 'foo', aaa=5)
        self.assertEqual(self.utility.consumeActions(self.doc, token),
                         [('http://nohost/plone/testdoc', 'foo', {'aaa': 5}, {})])
        token = self.utility.enablePowerToken(self.doc, 'fake', aaa=5)
        self.assertRaises(ComponentLookupError, self.utility.consumeActions, self.doc, token)
        token = self.utility.enablePowerToken(self.doc, 'foo', aaa=7)
        self.assertEqual(self.utility.consumeActions(self.doc, token, bbb=2),
                         [('http://nohost/plone/testdoc', 'foo', {'aaa': 7}, {'bbb': 2})])

    def test_consumeActionsWithMultipleActions(self):
        token = self.utility.enablePowerToken(self.doc, 'foo', abc='text')
        self.utility.addAction(self.doc, token, 'foo')
        self.assertEqual(self.utility.consumeActions(self.doc, token),
                         [('http://nohost/plone/testdoc', 'foo', {'abc': 'text'}, {}),
                          ('http://nohost/plone/testdoc', 'foo', {}, {}),])
        self.assertRaises(PowerTokenConfigurationError, self.utility.consumeActions, self.doc, token)

    def test_unrestrictedUser(self):
        token = self.utility.enablePowerToken(self.doc, 'viewfoo') 
        has_role, username = self.utility.consumeActions(self.doc, token)[0]
        self.assertEqual(has_role, 0)
        self.logout()
        self.setRoles(('Anonymous', ))
        token = self.utility.enablePowerToken(self.doc, 'viewfoo', unrestricted=True)
        has_role, username = self.utility.consumeActions(self.doc, token)[0]
        self.assertEqual(has_role, 1)

    def test_usernameChange(self):
        token = self.utility.enablePowerToken(self.doc, 'viewfoo', roles='Member') 
        has_role, username = self.utility.consumeActions(self.doc, token)[0]
        self.assertEqual(username, 'test_user_1_')
        token = self.utility.enablePowerToken(self.doc, 'viewfoo', roles='Member', username='Unknow') 
        has_role, username = self.utility.consumeActions(self.doc, token)[0]
        self.assertEqual(username, 'Unknow')
        self.logout()
        self.setRoles(('Anonymous', ))
        token = self.utility.enablePowerToken(self.doc, 'viewfoo', roles='Member') 
        has_role, username = self.utility.consumeActions(self.doc, token)[0]
        self.assertEqual(username, '')
        token = self.utility.enablePowerToken(self.doc, 'viewfoo', roles='Member', username='Unknow') 
        has_role, username = self.utility.consumeActions(self.doc, token)[0]
        self.assertEqual(username, 'Unknow')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestToken))
    return suite
