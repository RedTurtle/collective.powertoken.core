from setuptools import setup, find_packages
import os, sys

version = '0.3.0'

install_requires=['setuptools',]
tests_require = ['interlude', 'plone.app.testing', 'plone.app.robotframework']
#install_requires.extends(tests_require)

if sys.version_info < (2, 6):
    install_requires.append('uuid')

setup(name='collective.powertoken.core',
      version=version,
      description="A mechanism for bypass Plone security, performing "
                  "operations normally unauthorized, if a secret token is know (core package)",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "Framework :: Zope3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python 3.8",        
        ],
      keywords='plone security token plonegov',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/collective.powertoken.core',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.powertoken'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
