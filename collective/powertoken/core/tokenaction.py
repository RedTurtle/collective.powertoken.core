# -*- coding: utf-8 -*-

from persistent import Persistent
from zope.interface import implements
from collective.powertoken.core.interfaces import IPowerActionConfiguration

class TokenActionConfiguration(Persistent):
    implements(IPowerActionConfiguration)
    
    def __init__(self, type, roles=[], oneTime=True, unrestricted=False, username=None, **kwargs):
        self.type = type
        self.roles = roles
        self.oneTime = oneTime
        self.unrestricted = unrestricted
        self.username = username
        self.params = kwargs

    def __repr__(self):
        return "<TokenActionConfiguration type='%s', roles=%s (%s), username=%s, oneTime=%s, params=%s>" % (
                    self.type,
                    self.roles,
                    self.unrestricted and 'unrestricted' or 'restricted',
                    self.username,
                    self.oneTime,
                    self.params
                    )
