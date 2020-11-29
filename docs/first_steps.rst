First Steps
===========


Installation
------------

The easiest way to use pydyf is to install it in a Python `virtual
environment`_. When your virtual environment is activated, you can then install
pydyf with pip_::

    pip install pydyf

.. _virtual environment: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
.. _pip: https://pip.pypa.io/


Create a PDF
------------

.. code-block:: python

   import pydyf

   document = pydyf.PDF()

   # Add an empty page
   document.add_page(pydyf.Dictionary({
       'Type': '/Page',
       'Parent': document.pages.reference,
       'MediaBox': pydyf.Array([0, 0, 200, 200]),
   }))

   # Write to document.pdf
   with open('document.pdf', 'wb') as f:
       document.write(f)
