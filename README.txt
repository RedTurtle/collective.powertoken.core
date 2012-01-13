.. contents:: Table of Contents

Introduction
============

A product for Plone developers. You will be able to register actions on site's contents, protected
by a *secret token*.

Using an internal utility, or calling a provided view (``@@consume-powertoken``) you can run the action you
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

Registering more that one action
--------------------------------

You can also register (and then run all of theme) more that one action for a token.

>>> token = utility.enablePowerToken(document, 'myMagicAction')
>>> utility.addAction(document, token, 'myMagicAction')
>>> utility.addAction(document, token, 'aDifferentAction')

When you consume the token, all registered actions are executed in order.

>>> result = utility.consumeAction(document, token)

What action is executed?
------------------------

This is only the core package so you need to look for other packages that add possible actions (or develop
your own).

When you call:

>>> token = utility.enablePowerToken(document, 'myMagicAction', parameter1='foo', parameter2=5)

... you are preparing the call for an adapter called *myMagicAction*, saving also additional
parameter provided (in a special ``action`` object, see below). Know that 3rd party adapter can require
specific parameters to works.

When ``consumeAction`` is called, internally a new adapter is called:

>>> from collective.powertoken.core.interfaces import IPowerActionProvider
>>> adapter = getMultiAdapter((document, request),
...                           IPowerActionProvider,
...                           name='myMagicAction')
>>> result = adapter.doAction(action)

What to do with results (you can also don't provide results) is under your control. Result is always a
Python list with all results from all executed actions. 

A `list of all know action providers`__ is available online (feel free to contribute and update this page
with your own).

__ https://github.com/RedTurtle/collective.powertoken.core/blob/master/docs/KNOW-ACTION-PROVIDERS.txt

Special parameters
------------------

When calling ``enablePowerToken`` and you give additional parameters, they are stored in the ``action``
object:

``roles``
    Default to empty list. Commonly when you call ``consumeAction`` you are performing an action keeping user's
    privileges. Providing there a list of Zope roles will give you *those* roles instead. In this way,
    knowing a token, you can commonly perform unauthorized actions.
``oneTime``
    Default to True. When you call ``consumeAction``  you commonly execute the action and remove the action
    from the action list.
    Instead you can configure an action that never expire the token when executed, so you can call it many
    times as you want (using the same token every time).
``params``
    Default is an empty dict, automatically filled with every other keyword argument passed,
    commonly used by adapters.

Additional advanced, parameters:

``unrestricted``
    Defaut: False. Use an unrestricted user, that always pass security check. Please note that
    *you commonly don't need this*, just configure well ``roles``.
``username``
    Defaut: None. When using a different security context, like when using the ``roles`` parameter, instead
    of the current user's id (or an empty string when anonymous) you can choose a new one.

Final security note
===================

This product play with Zope security, potentially giving great power to users, simply knowing the secret token.

**Be careful!**

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/
