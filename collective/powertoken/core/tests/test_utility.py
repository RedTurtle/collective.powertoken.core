# -*- coding: utf-8 -*-

from zope.component import getUtility, ComponentLookupError
from zope.annotation.interfaces import IAnnotations

from zope.component import provideAdapter
from zope.component import getGlobalSiteManager

from zope.publisher.interfaces.browser import IHTTPRequest
from Products.CMFCore.interfaces import IContentish

from collective.powertoken.core import config
from collective.powertoken.core.exceptions import PowerTokenSecurityError, PowerTokenConfigurationError
from collective.powertoken.core.interfaces import IPowerTokenUtility, IPowerTokenizedContent 
from collective.powertoken.core.interfaces import IPowerActionProvider
from collective.powertoken.core.tests.base import TestCase, TestPowerActionProvider

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

    def test_enableToken(self):
        token = self.utility.enablePowerToken(self.doc, 'foo')
        configuration = IAnnotations(self.doc)[config.MAIN_TOKEN_NAME]
        self.assertTrue(IPowerTokenizedContent.providedBy(self.doc))
        self.assertEquals(configuration.keys()[0], token)

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
        token2 = self.utility.enablePowerToken(self.doc, 'foo')
        configuration = IAnnotations(self.doc)[config.MAIN_TOKEN_NAME]
        self.assertEquals(len(configuration), 2)
        self.utility.consumeToken(self.doc, token1)
        self.assertEqual(len(configuration), 1)
        self.utility.consumeToken(self.doc, token2)
        self.assertEqual(IAnnotations(self.doc).get(config.MAIN_TOKEN_NAME), None)
    
    def test_consumePermanentToken(self):
        """When oneTime is False"""
        token = self.utility.enablePowerToken(self.doc, 'foo', oneTime=False)
        configuration = IAnnotations(self.doc)[config.MAIN_TOKEN_NAME]
        self.assertEquals(len(configuration), 1)
        self.utility.consumeToken(self.doc, token)
        self.utility.consumeToken(self.doc, token)
        self.assertEquals(len(configuration), 1)

    def test_removeToken(self):
        token1 = self.utility.enablePowerToken(self.doc, 'foo')
        token2 = self.utility.enablePowerToken(self.doc, 'foo')
        configuration = IAnnotations(self.doc)[config.MAIN_TOKEN_NAME]
        self.assertEquals(len(configuration), 2)
        self.utility.removeToken(self.doc, token1)
        self.assertEqual(len(configuration), 1)
        self.utility.removeToken(self.doc, token2)
        self.assertEqual(IAnnotations(self.doc).get(config.MAIN_TOKEN_NAME), None)

    def test_consumeAction(self):
        token = self.utility.enablePowerToken(self.doc, 'foo')
        self.assertEqual(self.utility.consumeAction(self.doc, token),
                         (self.doc.absolute_url(), 'foo', {}))
        token = self.utility.enablePowerToken(self.doc, 'foo', aaa=5)
        self.assertEqual(self.utility.consumeAction(self.doc, token),
                         (self.doc.absolute_url(), 'foo', {'aaa': 5}))
        token = self.utility.enablePowerToken(self.doc, 'fake', aaa=5)
        self.assertRaises(ComponentLookupError, self.utility.consumeAction, self.doc, token)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestToken))
    return suite
