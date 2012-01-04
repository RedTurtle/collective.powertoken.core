# -*- coding: utf-8 -*-

from persistent import Persistent
from zope.interface import implements
from collective.powertoken.core.interfaces import IPowerActionConfiguration

class TokenActionConfiguration(Persistent):
    implements(IPowerActionConfiguration)
    
    def __init__(self, type, roles=[], oneTime=True, **kwargs):
        self.type = type
        self.roles = roles
        self.oneTime = oneTime
        self.params = kwargs
