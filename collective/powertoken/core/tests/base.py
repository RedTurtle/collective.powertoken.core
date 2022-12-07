# -*- coding: utf-8 -*-

import unittest
from collective.powertoken.core.testing import INTEGRATION_TESTING

class TestCase(unittest.TestCase):
    """Base class used for test cases
    """
    layer = INTEGRATION_TESTING


#class FunctionalTestCase(ptc.FunctionalTestCase):
    #"""Test case class used for functional (doc-)tests
    #"""
