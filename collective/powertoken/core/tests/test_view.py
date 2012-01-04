# -*- coding: utf-8 -*-

from zope.component import getUtility, getMultiAdapter
from zope.annotation.interfaces import IAnnotations

from zope.component import provideAdapter
from zope.component import getGlobalSiteManager

from zope.publisher.interfaces.browser import IHTTPRequest
from Products.CMFCore.interfaces import IContentish

from collective.powertoken.core.tests.base import TestCase
from collective.powertoken.core.interfaces import IPowerTokenUtility
from collective.powertoken.core.exceptions import PowerTokenConfigurationError

class TestTokenView(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))
        portal = self.portal
        portal.invokeFactory(type_name="Document", id="testdoc")
        doc = portal.testdoc
        doc.edit(title="A test document")
        self.utility = getUtility(IPowerTokenUtility)
        self.doc = portal.testdoc
        self.request = self.portal.REQUEST
        self.logout()
        self.setRoles(('Anonymous', ))

    def test_givenParameters(self):
        from zExceptions import BadRequest
        view = getMultiAdapter((self.portal, self.request), name='consume-powertoken')
        self.assertRaises(BadRequest, view)
        self.request.form['token'] = 'foo'
        view = getMultiAdapter((self.portal, self.request), name='consume-powertoken')
        self.assertRaises(BadRequest, view)
        del self.request.form['token']
        self.request.form['path'] = '/foo'
        view = getMultiAdapter((self.portal, self.request), name='consume-powertoken')
        self.assertRaises(BadRequest, view)
        # ***
        self.request.form['token'] = 'foo'
        self.request.form['path'] = '/foo'
        view = getMultiAdapter((self.portal, self.request), name='consume-powertoken')
        self.assertRaises(KeyError, view)
        self.request.form['path'] = 'testdoc'
        view = getMultiAdapter((self.portal, self.request), name='consume-powertoken')
        self.assertRaises(PowerTokenConfigurationError, view)

    def test_powerActionCall(self):
        token = self.utility.enablePowerToken(self.doc, 'foo')
        self.request.form['token'] = token
        self.request.form['path'] = 'testdoc'
        view = getMultiAdapter((self.portal, self.request), name='consume-powertoken')
        self.assertEqual(view(), ('http://nohost/plone/testdoc', 'foo', {}))

    def test_getTarget(self):
        view = getMultiAdapter((self.portal, self.request), name='consume-powertoken')
        self.assertRaises(KeyError, view._getTarget, 'aaa')
        self.assertEqual(view._getTarget('testdoc').absolute_url_path(), '/plone/testdoc')
        self.assertEqual(view._getTarget('/testdoc').absolute_url_path(), '/plone/testdoc')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTokenView))
    return suite