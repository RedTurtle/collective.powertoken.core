# -*- coding: utf-8 -*-

from zExceptions import BadRequest

from zope.component import getUtility

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from collective.powertoken.core.interfaces import IPowerTokenUtility

class ConsumePowerTokenView(BrowserView):
    
    def __call__(self, *args, **kw):
        form = self.request.form
        if not form.get('token') or not form.get('path'):
            raise BadRequest('You need to provide the token and the content path')
        
        path = form['path']
        token = form['token']
        
        target = self._getTarget(path)
        
        utility = getUtility(IPowerTokenUtility)
        return utility.consumeAction(target, token)
        
    def _getTarget(self, path):
        """
        Path must be always "folder/foo" or "/folder/foo", not including portal object id
        """
        
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        
        if path.startswith('/'):
            path = path[1:]
        
        return portal.unrestrictedTraverse(path)

        