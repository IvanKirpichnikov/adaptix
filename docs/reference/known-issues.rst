*******************
Known Issues
*******************

PyInstaller
=======================

Using Adaptix with PyInstaller may lead to errors such as:
``Type ‹...› is not recognized as model``
even when the class is actually supported.

Adaptix relies on package version information provided by ``importlib.metadata``,
but PyInstaller removes package metadata by default during the build process.

To fix this, you need to preserve the metadata by using the ``--copy-metadata PACKAGE_NAME`` option in PyInstaller.
This flag must be applied to every package integrated with Adaptix, for example:
``--copy-metadata sqlalchemy``, ``--copy-metadata msgspec``.
