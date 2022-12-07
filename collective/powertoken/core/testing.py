# -*- coding: utf-8 -*-

from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
)
from plone.testing import z2

#
from zope.publisher.interfaces.browser import IHTTPRequest
from collective.powertoken.core.interfaces import IPowerActionProvider
from zope.component import provideAdapter
from zope.interface import implementer
from Products.CMFCore.interfaces import IContentish


@implementer(IPowerActionProvider)
class TestPowerActionProvider(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def doAction(self, action, **kwargs):
        return self.context.absolute_url(), action.type, action.params, kwargs


@implementer(IPowerActionProvider)
class AdvancedTestPowerActionProvider(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def doAction(self, action, **kwargs):
        member = self.context.portal_membership.getAuthenticatedMember()
        return (member.has_role('Abc', self.context), member.getId())



class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import collective.powertoken.core
        self.loadZCML(package=collective.powertoken.core)

        provideAdapter(
                TestPowerActionProvider,
                (IContentish,
                IHTTPRequest),
                provides=IPowerActionProvider,
                name='foo'
            )

        provideAdapter(
                AdvancedTestPowerActionProvider,
                (IContentish,
                IHTTPRequest),
                provides=IPowerActionProvider,
                name='viewfoo'
            )


FIXTURE = Fixture()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='CollectivePowertokenCoreLayer:Integration',
)
