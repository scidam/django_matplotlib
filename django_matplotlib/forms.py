from django.forms import Widget
from django.forms.fields import Field

__all__ = ("MatplotlibWidget", "MatplotlibFigure")


class MatplotlibWidget(Widget):
    template_name = 'widgets/matplotlib.html'
  
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['figure'] = value
        return context


class MatplotlibFigure(Field):
    widget = MatplotlibWidget

    def __init__(self, **kwargs):
        kwargs.update({'required': False})
        super().__init__(**kwargs)
