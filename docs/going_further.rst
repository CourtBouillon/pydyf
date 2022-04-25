Going Further
=============


Why pydyf?
-------------

pydyf has been created to replace Cairo_ PDF generation in WeasyPrint_.

Indeed, there were some bugs in WeasyPrint caused by Cairo, and new versions of
Cairo can take a long time to be released. There are also many features that
are easier to implement with more control on the PDF generation.

So we created pydyf.

.. _WeasyPrint: https://www.courtbouillon.org/weasyprint
.. _Cairo: https://www.cairographics.org/

Why Python?
-----------

Python is a really good language to design a small, OS-agnostic library. As it
is object-oriented, it gives the possibility to follow the PDF specification
with high-level classes and a small amount of very simple code.

And of course, WeasyPrint is written in Python too, giving an obvious reason
for this choice.

Speed is not pydyf’s main goal. Code simplicity, maintainability and
flexibility are more important goals for this library, as they give the ability
to stay really close to the specification and to fix bugs easily.
