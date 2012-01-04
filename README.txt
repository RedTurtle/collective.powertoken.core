.. contents:: Table of Contents

Introduction
============

A product for Plone developers. You will be able to register actions on site's contents, protected
by a *secret token*.

Using an internal utility, or calling a provided view (``consume-powertoken``) raise the action you
have configured previously.

How to use
==========

First of all you need the utility:

>>> from collective.powertoken.core.interfaces import IPowerTokenUtility
>>> utility = getUtility(IPowerTokenUtility)

With this you can register a new action on a site content (for example, a document):

>>> token = utility.enablePowerToken(document, 'myMagicAction')

The *token* must (probably) kept secret, and you must use it has you prefer (for example: develop an
application that send the token by e-mail)

You can then execute the given action using the same utility:

>>> result = utility.consumeAction(document, token)

Or calling the provided view that need ``token`` and ``path`` parameters, for example:

    http://myplonesite/@@consume-powertoken?token=aaaa-bbbb-cccc&path=path/to/the/content

What action is executed?
------------------------

This is only the core package so you need to look for other packages that add possible actions (or develop
your own)

When you call:

>>> token = utility.enablePowerToken(document, 'myMagicAction', parameter1='foo', parameter2=5)

... you are preparing the call for an adapter called *myMagicAction*, saving also additional
parameter provided (in a special ``action`` object, see below)(3rd party adapter can require
specific parameters to works).

When ``consumeAction`` is called, internally a new adapter is called:

>>> from collective.powertoken.core.interfaces import IPowerActionProvider
>>> adapter = getMultiAdapter((document, request),
...                           IPowerActionProvider,
...                           name='myMagicAction')
>>> result = adapter.doAction(action)

That to do with results (you can also don't provide results) is under your control

Special parameters
------------------

When calling ``enablePowerToken`` and you give additional parameters, they are stored in the ``action``
object all but:

``roles``
    Default to empty list. Commonly when you call ``consumeAction`` you are performing an action keeping your
    privileges. Providing there a list of Zope roles will give you *those* roles instead. In this way,
    knowing a token, you can commonly perform unauthorized actions.
``oneTime``
    Default to True. When you call ``consumeAction``  you commonly execute the action and delete the token.
    You can configure an action that never expire the token when executed, so you can call it many times
    as you want (using the same token every time).

