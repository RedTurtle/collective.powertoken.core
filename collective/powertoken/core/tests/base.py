# -*- coding: utf-8 -*-

from Products.Five import zcml
from Products.Five import fiveconfigure

#from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from zope.interface import implements
from zope.component import provideAdapter
from Products.CMFCore.interfaces import IContentish

from zope.publisher.interfaces.browser import IHTTPRequest
from collective.powertoken.core.interfaces import IPowerActionProvider

@onsetup
def setup_product():
    """Set up additional products and ZCML required to test this product.

    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """

    # Load the ZCML configuration for this package and its dependencies

    fiveconfigure.debug_mode = True
    import collective.powertoken.core
    zcml.load_config('configure.zcml', collective.powertoken.core)
    fiveconfigure.debug_mode = False

    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.

    #ztc.installPackage('collective.powertoken')
    
    provideAdapter(
            TestPowerActionProvider,
            (IContentish,
             IHTTPRequest),
            provides=IPowerActionProvider,
            name='foo'
        )

# The order here is important: We first call the deferred function and then
# let PloneTestCase install it during Plone site setup

setup_product()
#ptc.setupPloneSite(products=['collective.powertoken.core'])
ptc.setupPloneSite()


class TestPowerActionProvider(object):
    implements(IPowerActionProvider)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def doAction(self, action):
        return self.context.absolute_url(), action.type, action.params

class TestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """

class FunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """
