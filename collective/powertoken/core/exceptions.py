# -*- coding: utf-8 -*-

from AccessControl import Unauthorized

class PowerTokenSecurityError(Unauthorized):
    """General error for providing bad token"""

class PowerTokenConfigurationError(Exception):
    """General error for bad configuration of a Power Token object"""