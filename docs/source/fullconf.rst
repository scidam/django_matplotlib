
Default settings for MatplotlibFigureField
==========================================

Below are default configuration parameters for :class:`DjangoMatplotlibField`.

Parameters `DJANGO_MATPLOTLIB_TMP` and `DJANGO_MATPLOTLIB_MODULE`
can be overridden on per-project basis in the project's settings file.

Parameters presented in `DJANGO_MATPLOTLIB_FIG_DEFAULTS` dictionary
are used as defaults when a new matplotlib field is created. These parameters
could be overridden on per-field basis.

.. literalinclude:: ../../django_matplotlib/conf.py

