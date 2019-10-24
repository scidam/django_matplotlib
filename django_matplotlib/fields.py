import os
import re
import importlib
import inspect
import string
import random
from base64 import b64encode as b64en
import hashlib
import atexit
from io import BytesIO
from django.db import models
from django_matplotlib.forms import MatplotlibFigure
from django.core import checks
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django_matplotlib import conf as djmpl_conf

try:
    import matplotlib.pyplot as plt
    import matplotlib
except ImportError:
    plt = None

MEDIA_ROOT = getattr(settings, "MEDIA_ROOT", '')
MEDIA_URL = getattr(settings, "MEDIA_URL", '')


# default values of app's settings
defaults = type('settings', tuple(), dict())  
for name in dir(djmpl_conf):
    if not name.startswith('_') and name.isupper():
        setattr(defaults, name,
                getattr(settings, name, getattr(djmpl_conf, name)))


# register with atexit module
def cleanup_file(path):
    try:
        os.remove(path)
    except IOError:
        pass


class FigureObject:
    __slots__ = ('type', 'source', 'path', 'error',
                 'format', '_width', '_height')

    def __init__(self, width=320, height=240,
                 type='string', source='', path=''):
        self._width = width
        self._height = height
        self.type = type
        self.source = source
        self.path = path
        self.error = ''
        self.format = ''

    @property
    def url(self):
        if not self.path or not MEDIA_URL:
            return ''
        path = self.path.replace(MEDIA_ROOT, '')
        return os.path.join('/', MEDIA_URL, path)

    @staticmethod
    def _prepare_size(s):
        if isinstance(s, int):
            return str(s) + "px"
        elif isinstance(s, str):
            if s.lower().endswith("px"):
                return s.lower()
            elif s.isnumeric():
                return s + "px"
        return None

    @property
    def width(self):
        return self._prepare_size(self._width)
    
    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        return self._prepare_size(self._height)
    
    @height.setter
    def height(self, value):
        self._height = value


class MatplotlibFieldBase(models.Field):
    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        self.concrete = False
        cls._meta.add_field(self, private=True)
        setattr(cls, name, self)
    
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # Prevent field from being detected as changed
        # when makemigrations command is ran.
        return name, path, tuple(), dict()


class MatplotlibFigureField(MatplotlibFieldBase):
    """Matplotlib figure field for Django.

    Figures are generated in 'png' (default) or 'svg' formats.
    They can be inserted to html documents as inline objects 
    (e.g. using `<img src="data:image/png;base64,...">`) or saved to 
    temporary files.

    If files are saved on disk, they are automatically cleaned up when the
    program exits using :mod:`atexit` module.

    `MatplotlibFigureField` is compatible with standard Django Admin app. 

    Figures automatically re-render (at any subsequent request) 
    when they code is changed. It uses :func:`hashlib.md5` function to
    check changes in figure's code. If the figure wasn't changed, 
    it would be stored in memory and underlying figure view function (which returns 
    :class:`matplotlib.Figure` instance) not be called for each subsequent
    request.
    
    .. note::

       Model fields created using this class aren't stored in the database 
       and no additional columns for such fields are created.

    """

    def __init__(self, *args, **kwargs):
        """MatplotlibFigureField initializer.

        This field can take any of standard Django's field attributes,
        but forces `required` argument to `False` for corresponding form.

        :param figure: The name of callable within `figures.py` which should 
                       return matplotlib.Figure object.
        :type figure: str
        :param silent: Be silent on exceptions or not (default is `False`). 
        :type figure: bool
        :param plt_args: Positional arguments passed to figure's view 
                         (the function defined by the `figure` parameter).
        :type plt_args: tuple
        :param plt_kwargs: Keyword arguments passed to figure's view 
                           (the function defined by the `figure` parameter).        
        :type plt_kwargs: dict
        :param fig_width: Output figure width in pixels. Default is 320.
        :type fig_width: int
        :param fig_height: Output figure height in pixels. Default is 240.
        :type fig_height: int
        :param output_type: Output type of the figure. Either 'file' or
                            'string'. Default is 'string' (used for inline
                            figure object embedding to html pages).
        :type output_type: str
        :param output_format: Output format of the figure. Either 'svg' or
                              'png' (default).
        :type output_format: str
        :param cleanup: Defines whether created files be cleaned up at program
                        exit or not. Default is True (created files will be
                        erased at exit). Has sense only if `output_type='file'`.
        :type cleanup: bool


        .. note::

            Default parameters for MatplotlibFigureField are defined in the file
            conf.py.


        .. note:: 

            If `output_type='file'`,  MEDIA_ROOT should be defined in your
            project settings file. In this case, the field will 
            save temporary files to the folder `MEDIA_ROOT/DJANGO_MATPLOTLIB_TMP`.
            Default value of `DJANGO_MATPLOTLIB_TMP` is defined in `conf.py` and
            can be overridden in your project settings file.

        """

        defs = defaults.DJANGO_MATPLOTLIB_FIG_DEFAULTS
        self.figure = kwargs.pop('figure', '')
        self.silent = kwargs.pop('silent', defs.get('silent'))
        self.plt_args = kwargs.pop('plt_args', tuple())
        self.plt_kwargs = kwargs.pop('plt_kwargs', dict())
        self.fig_width = kwargs.pop('fig_width', defs.get('fig_width'))
        self.fig_height = kwargs.pop('fig_height', defs.get('fig_height'))
        self.output_type = kwargs.pop('output_type', defs.get('output_type'))
        self.output_format = kwargs.pop('output_format',
                                        defs.get('output_format'))
        self.fig_cleanup = kwargs.pop('cleanup', defs.get('cleanup'))
        self._figure_module = None
        kwargs['null'] = True
        super().__init__(*args,  **kwargs)

    def _get_figure_hash(self, func):
        new_hash = None
        source = inspect.getsource(func)
        if self.plt_args:
            source += ''.join(map(str, self.plt_args))
        if self.plt_kwargs:
            source += ''.join([str(k) + str(v) for k, v in self.plt_kwargs.items()])  # noqa
        if source:
            new_hash = hashlib.md5(source.encode('utf-8')).hexdigest()
        return new_hash

    @property
    def suggest_filename(self):
        tmp_dir = os.path.join(MEDIA_ROOT, defaults.DJANGO_MATPLOTLIB_TMP)
        os.makedirs(tmp_dir, exist_ok=True)
        suggest_fname = ''.join([random.choice(string.ascii_lowercase) for _ in range(10)])  # noqa
        suggest_fname += '.' + self.output_format
        file_path = os.path.join(tmp_dir, suggest_fname)
        while os.path.exists(file_path):
            suggest_fname = ''.join([random.choice(string.ascii_lowercase) for _ in range(10)])  # noqa
            suggest_fname += '.' + self.output_format
            file_path = os.path.join(tmp_dir, suggest_fname)
        return file_path

    def _is_figure_changed(self, func):
        new_hash = self._get_figure_hash(func)
        if not hasattr(self, '_fig_hash'):
            return True
        if new_hash != self._fig_hash:
            return True
        else:
            return False

    def _get_figure(self, func):
        if plt:
            matplotlib.use('Agg')
           
        if self._is_figure_changed(func):
            fig_object, func = self._reload_func_source(func)
            if callable(func):
                fig_object = FigureObject()
                try:
                    fig = func(*self.plt_args, **self.plt_kwargs)
                except Exception as e:             # noqa
                    fig_object.error = e
                    if self.silent:
                        return fig_object
                    else:
                        raise e
                else:
                    if not isinstance(fig, plt.Figure):
                        fig_object.error = "%s should return instance of class"\
                                        " Matplotlib.Figure" % self.figure
                        if self.silent:
                            return fig_object
                        else:
                            raise TypeError(fig_object.error)
                # build fig_object from matplotlib figure
                fig_object.width = self.fig_width
                fig_object.height = self.fig_height
                fig_object.type = self.output_type
                fig_object.format = self.output_format
                if self.output_type == 'file':
                    if not MEDIA_ROOT and self.silent:
                        fig_object.error = "MEDIA_ROOT isn't configured. "
                        "Check your project settings file."
                        return fig_object
                    elif not MEDIA_ROOT:
                        raise ImproperlyConfigured("You need to set up MEDIA_ROOT"
                            " variable in your project sttings file.")
                    fig_object.path = self.suggest_filename
                    fig_object.source = ''
                    fig.savefig(fig_object.path, format=self.output_format,
                                bbox_inches='tight')
                    if self.fig_cleanup:
                        atexit.register(cleanup_file, fig_object.path)
                elif self.output_type == 'string':
                    buffer = BytesIO()
                    fig.savefig(buffer, format=self.output_format,
                                bbox_inches='tight')
                    buffer.seek(0)
                    fig_object.path = ''
                    if self.output_format == 'png':
                        fig_object.source = b64en(buffer.read()).decode('utf-8')
                    else:
                        fig_object.source =buffer.read().decode('utf-8')
                    plt.close(fig)
                else:
                    fig_object.error = "Undefined figure type. "
                    "Check out field's 'output_type' argument."
                if fig_object.path or fig_object.source:
                    self._fig_hash = self._get_figure_hash(func)
                self._figure_object = fig_object
        
            else:
                self._figure_object = fig_object
                self._fig_hash = ''
                return fig_object
        return self._figure_object

    def _reload_func_source(self, owner):
        """ Returns reloaded function """
    
        fig_object = FigureObject()
        func = None
        try:
            current_dir = os.path.dirname(inspect.getsourcefile(owner))
            spec = importlib.util.spec_from_file_location(
                defaults.DJANGO_MATPLOTLIB_MODULE.split('.')[0],
                os.path.join(current_dir,
                                defaults.DJANGO_MATPLOTLIB_MODULE)
                )
            self._figure_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self._figure_module)
        except ImportError:
            fig_object.error = "Couldn't locate '%s' in the"\
            " app directory." % defaults.DJANGO_MATPLOTLIB_MODULE
            if self.silent:
                return (fig_object, func)
            else:
                raise ImportError(fig_object.error)

        if not hasattr(self._figure_module, self.figure):
            fig_object.error = "Couldn't locate callable '%s'"\
            " within module '%s'." % (self.figure,
                defaults.DJANGO_MATPLOTLIB_MODULE
                )
            if self.silent:
                return (fig_object, func)
            else:
                raise AttributeError(fig_object.error)
        return fig_object, getattr(self._figure_module, self.figure)

    def __get__(self, attr, owner=None):
        if owner:
            fig_obj, func = self._reload_func_source(owner)
            if callable(func):
                self._figure_object = self._get_figure(func)
                return self._figure_object
            else:
                self._figure_object = fig_obj
                return fig_obj

    def check(self, **kwargs):
        return [
            *super().check(**kwargs),
            *self._check_figure_attribute(**kwargs),
            *self._check_fig_format(**kwargs),
            *self._check_fig_type(**kwargs),
        ]

    def _check_fig_format(self, **kwargs):
        if self.output_format not in ['svg', 'png']:
            return [
                checks.Error(
                    "Attribute 'fig_format' should be either 'png' or 'svg'.",
                    obj=self,
                    id='django_matplotlib.E003',
                )
            ]
        return []

    def _check_fig_type(self, **kwargs):
        if self.output_type not in ['string', 'file']:
            return [
                checks.Error(
                    "Attribute 'fig_type' should be either 'string' or 'file'.",
                    obj=self,
                    id='django_matplotlib.E004',
                )
            ]
        return []

    def _check_figure_attribute(self, **kwargs):
        if not self.figure:
            return [
                checks.Error(
                    "MatplotlibFigrueField must define "
                    "non-empty 'figure' attribute.",
                    obj=self,
                    id='django_matplotlib.E002',
                )
            ]
        elif not isinstance(self.figure, str):
            return [
                checks.Error(
                    "'figure' must be a non-empty string.",
                    obj=self,
                    id='django_matplotlib.E001',
                )
            ]
        else:
            return []

    def formfield(self, **kwargs):
        self.__get__('', owner=self.model)
        defaults = {'form_class': MatplotlibFigure,
                    'choices_form_class': MatplotlibFigure,
                    'initial': self._figure_object}
        defaults.update(kwargs)
        return super().formfield(**defaults)
