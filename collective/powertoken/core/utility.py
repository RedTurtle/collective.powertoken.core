# -*- coding: utf-8 -*-

import uuid

from persistent.list import PersistentList
from persistent.dict import PersistentDict

from zope.interface import implements, alsoProvides, noLongerProvides
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError

from collective.powertoken.core.interfaces import IPowerTokenUtility, IPowerTokenizedContent
from collective.powertoken.core.interfaces import IPowerActionProvider
from collective.powertoken.core.tokenaction import TokenActionConfiguration
from collective.powertoken.core.exceptions import PowerTokenSecurityError, PowerTokenConfigurationError
from collective.powertoken.core import config

from AccessControl.User import SimpleUser, UnrestrictedUser
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager, getSecurityManager

from Products.CMFCore.utils import getToolByName

class UnrestrictedUser(UnrestrictedUser):
    """Unrestricted user that still has an id."""

    def getId(self):
        """Return the ID of the user."""
        return self.getUserName()


class PowerTokenUtility(object):
    """ Utility for manage power tokens on contents
    """

    implements(IPowerTokenUtility)
    
    def _generateNewToken(self):
        return str(uuid.uuid4())

    def enablePowerToken(self, content, type, roles=[], oneTime=True, unrestricted=False,
                         username=None, **kwargs):
        annotations = IAnnotations(content)
        
        if not annotations.get(config.MAIN_TOKEN_NAME):
            annotations[config.MAIN_TOKEN_NAME] = PersistentDict()
            alsoProvides(content, IPowerTokenizedContent)
            content.reindexObject(idxs=['object_provides'])
        powertokens = annotations[config.MAIN_TOKEN_NAME]

        token = self._generateNewToken()

        if powertokens.get(token) is not None:
            raise KeyError('Token %s already stored in object %s' % (token,
                                                                     '/'.join(content.getPhysicalPath())))
        
        powertokens[token] = PersistentList()
        self.addAction(content, token, type, roles=roles, oneTime=oneTime, unrestricted=unrestricted,
                       username=username, **kwargs)
        return token

    def addAction(self, content, token, type, roles=[], oneTime=True, unrestricted=False,
                  username=None, **kwargs):
        self.verifyToken(content, token, True)
        annotations = IAnnotations(content)
        powertokens = annotations[config.MAIN_TOKEN_NAME]
        actions = powertokens[token]
        action = TokenActionConfiguration(type, roles=roles, oneTime=oneTime,
                                          unrestricted=unrestricted, username=username, **kwargs)
        actions.append(action)
        return action

    def verifyToken(self, content, token, raiseOnError=True):
        if not IPowerTokenizedContent.providedBy(content):
            raise PowerTokenConfigurationError("Content %s isn't an IPowerTokenizedContent" % '/'.join(content.getPhysicalPath()))
        annotations = IAnnotations(content)
        try:
            powertokens = annotations[config.MAIN_TOKEN_NAME]
        except KeyError:
            raise KeyError("Content %s doesn't provide tokens" % '/'.join(content.getPhysicalPath()))

        if not token or powertokens.get(token) is None:
            if raiseOnError:
                raise PowerTokenSecurityError('Token verification failed')
            return False
        return True

    def disablePowerTokens(self, content):
        annotations = IAnnotations(content)
        del annotations[config.MAIN_TOKEN_NAME]
        noLongerProvides(content, IPowerTokenizedContent)
        content.reindexObject(idxs=['object_provides'])

    def consumeToken(self, content, token):
        self.verifyToken(content, token, True)
        annotations = IAnnotations(content)
        powertokens = annotations[config.MAIN_TOKEN_NAME]
        results = []
        for action in powertokens[token][:]:
            if action.oneTime:
                powertokens[token].remove(action)
            if len(powertokens[token])==0:
                del powertokens[token]
            if len(powertokens)==0:
                self.disablePowerTokens(content)
            results.append(action)
        return results

    def removeToken(self, content, token):
        self.verifyToken(content, token, True)
        annotations = IAnnotations(content)
        powertokens = annotations[config.MAIN_TOKEN_NAME]
        del powertokens[token]
        if len(powertokens)==0:
            self.disablePowerTokens(content)

    def consumeActions(self, content, token, **kwargs):
        self.verifyToken(content, token)
        actions = self.consumeToken(content, token)
        results = []

        for action in actions:
            action_type = action.type
            
            try:
                adapter = getMultiAdapter((content, content.REQUEST), IPowerActionProvider, name=action_type)
            except ComponentLookupError:
                raise ComponentLookupError('Cannot find a provider for performing action "%s" on %s' % (action_type,
                                                                                                        '/'.join(content.getPhysicalPath())))
            try:
                if action.roles or action.unrestricted:
                    acl_users = getToolByName(content, 'acl_users')
                    old_sm = getSecurityManager()
                    Cls = SimpleUser
                    if action.unrestricted:
                        Cls = UnrestrictedUser                        
                    tmp_user = Cls(action.username or old_sm.getUser().getId() or '', '', action.roles, '')
                    tmp_user = tmp_user.__of__(acl_users)
                    newSecurityManager(None, tmp_user)
                results.append(adapter.doAction(action, **kwargs))
            finally:
                if action.roles:
                    setSecurityManager(old_sm)
        return results
