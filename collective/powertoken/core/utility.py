# -*- coding: utf-8 -*-

from zope.interface import implements, alsoProvides, noLongerProvides
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from persistent.dict import PersistentDict
import uuid

from collective.powertoken.core.interfaces import IPowerTokenUtility, IPowerTokenizedContent
from collective.powertoken.core.interfaces import IPowerActionProvider
from collective.powertoken.core.tokenaction import TokenActionConfiguration
from collective.powertoken.core.exceptions import PowerTokenSecurityError, PowerTokenConfigurationError
from collective.powertoken.core import config

from AccessControl.User import SimpleUser
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager, getSecurityManager

from Products.CMFCore.utils import getToolByName

class PowerTokenUtility(object):
    """ Utility for manage power tokens on contents
    """

    implements(IPowerTokenUtility)
    
    def _generateNewToken(self):
        return str(uuid.uuid4())

    def enablePowerToken(self, content, type, roles=[], **kwargs):
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
        
        powertokens[token] = TokenActionConfiguration(type, roles=roles, **kwargs)
        
        return token

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
        action = powertokens[token]
        if action.oneTime:
            del powertokens[token]
        if len(powertokens)==0:
            self.disablePowerTokens(content)
        return action

    def removeToken(self, content, token):
        self.verifyToken(content, token, True)
        annotations = IAnnotations(content)
        powertokens = annotations[config.MAIN_TOKEN_NAME]
        del powertokens[token]
        if len(powertokens)==0:
            self.disablePowerTokens(content)

    def consumeAction(self, content, token):
        self.verifyToken(content, token)
        action = self.consumeToken(content, token)
        action_type = action.type
        
        try:
            adapter = getMultiAdapter((content, content.REQUEST), IPowerActionProvider, name=action_type)
        except ComponentLookupError:
            raise ComponentLookupError('Cannot find a provider for performing action "%s" on %s' % (action_type,
                                                                                                    '/'.join(content.getPhysicalPath())))
        try:
            if action.roles:
                acl_users = getToolByName(content, 'acl_users')
                old_sm = getSecurityManager()
                tmp_user = SimpleUser(old_sm.getUser().getId(), '', action.roles, '')
                tmp_user = tmp_user.__of__(acl_users)
                newSecurityManager(None, tmp_user)
            return adapter.doAction(action)
        finally:
            if action.roles:
                setSecurityManager(old_sm)

