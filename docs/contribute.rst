Contribute
==========

You want to add some code to pydyf, launch its tests or improve its
documentation? Thank you very much! Here are some tips to help you play with
pydyf in good conditions.

The first step is to clone the repository, create a virtual environment and
install pydyf dependencies.

.. code-block:: shell

   git clone https://github.com/CourtBouillon/pydyf.git
   cd pydyf
   python -m venv venv
   venv/bin/pip install .[doc,test]

You can then let your terminal in the current directory and launch Python to
test your changes. ``import pydyf`` will then import the working directory
code, so that you can modify it and test your changes.

.. code-block:: shell

   venv/bin/python


Code & Issues
-------------

If you’ve found a bug in pydyf, it’s time to report it, and to fix it if you
can!

You can report bugs and feature requests on GitHub_. If you want to add or
fix some code, please fork the repository and create a pull request, we’ll be
happy to review your work.

.. _GitHub: https://github.com/CourtBouillon/pydyf


Tests
-----

Tests are stored in the ``tests`` folder at the top of the repository. They use
the pytest_ library.

Launching tests require to have Ghostscript_ installed and available in
``PATH``.

You can launch tests (with code coverage and lint) using the following command::

  venv/bin/pytest

.. _pytest: https://docs.pytest.org/
.. _Ghostscript: https://www.ghostscript.com/


Documentation
-------------

Documentation is stored in the ``docs`` folder at the top of the repository. It
relies on the Sphinx_ library.

You can build the documentation using the following command::

  venv/bin/sphinx-build docs docs/_build

The documentation home page can now be found in the ``docs/_build/index.html``
file. You can open this file in a browser to see the final rendering.

.. _Sphinx: https://www.sphinx-doc.org/
