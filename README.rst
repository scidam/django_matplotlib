=================
Django Matplotlib
=================

.. image:: https://travis-ci.com/scidam/django_matplotlib.svg?branch=master
    :target: https://travis-ci.com/scidam/django_matplotlib

Django_matplotlib is a reusable
Django app for embedding matplotlib figures
into Django driven websites. It can be easily integrated with Django
admin app and used in templates via forms.

Documentation: http://django-matplotlib.readthedocs.org/

Requirements
------------

Django 1.11+, <3.0; Python 3.5+, <3.8.


Quick start
-----------

1. Clone git repository to place where Django can find it:
   
.. code-block::

   pip install django-matplotlib

2. Add "django_matplotlib" to your INSTALLED_APPS setting like this:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'django_matplotlib',
        ...
    ]

3. Use MatplotlibField in your `models.py`, e.g.:

.. code-block:: python

    from django.db import models
    from django_matplotlib.fields import MatplotlibFigureField

    class MyModelWithFigure(models.Model):
        # ... other fields 
        # figures.py should be in the same directory where models.py is placed.
        # see  ./django_matplotlib/figures.py for example.
        fig = MatplotlibFigureField(figure='test_figure', verbose_name='figure',
                                    silent=True)
        # ... other fields 


4. Generate and apply migrations.


.. note::

    It is assumed that you have Django installed already. Additionally,
    you will need to install `matplotlib` to use `MatplotlibFigureField`
    in your models.


Author
------

Dmitry E. Kislov

E-mail: kislov@easydan.com


