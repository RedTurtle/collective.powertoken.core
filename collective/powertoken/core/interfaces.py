# -*- coding: utf-8 -*-

from zope.interface import Interface, Attribute

class IPowerTokenizedContent(Interface):
    """Marker interface for flagging content provided with a power token"""


class IPowerTokenUtility(Interface):
    """Interface for the Power Token utility"""
    
    def enablePowerToken(content, type, roles=[], oneTime=True, unrestricted=False, username=None, **kwargs):
        """
        Enable a Power Token on the content, registering an action type.
        
        Additional keyword arguments provided are stored in the action.
        
        Return the generated token.
        """

    def addAction(content, token, type, roles=[], oneTime=True, unrestricted=False, username=None, **kwargs):
        """
        Add another action to an existing Power Token enabled content
        
        Returns the new action IPowerActionConfiguration object
        """

    def disablePowerTokens(self, content):
        """Disable the Power Token feature on the object"""

    def verifyToken(content, token, raiseOnError=False):
        """
        Check if the content provide actions for the given token
        """
    
    def removeToken(content, token):
        """
        Remove a token from the object, not consuming it
        """
    
    def consumeToken(content, token):
        """
        Delete the given token action from the list
        
        Return the action deleted
        """
    
    def consumeActions(content, token):
        """
        Execute what to do on the content for a given token
        
        Returns the list of results of all actions in order (if any)
        """


class IPowerActionProvider(Interface):
    """Marker interface for an object able to perform action on a content"""
    
    def doAction(action):
        """Execute the action.
        
        Action is an object providing IPowerActionConfiguration interface
        """


class IPowerActionConfiguration(Interface):
    """An action configuration, taken from a Power Token"""

    type = Attribute("Kind on action")
    roles = Attribute("Run this action with those roles")
    oneTime = Attribute("True if the action can be executed one time, then is consumed. "
                        "False for action that not really consume the token")
    unrestricted = Attribute("For use UnrestrictedUser or not")
    username = Attribute("A custom userid to use for the temp user")
    params = Attribute("Additional parameters, used for performing the action")


