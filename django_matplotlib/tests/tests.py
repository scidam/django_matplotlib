import itertools
from django.test import TestCase
from django.test import RequestFactory
from django_matplotlib.fields import MatplotlibFigureField
from django.db import models
from django import forms
from django.shortcuts import render
from django.template import Template, Context, Engine
from django.http import HttpResponse
from django.conf import settings
from django_matplotlib.conf import DJANGO_MATPLOTLIB_TMP


#  ------------- test settings -----------------

par_variations ={
    'fig_width': [320], 
    'fig_height': [240],
    'silent': [True, False],
    'output_type': ['string', 'file'],
    'cleanup': [True],
    'output_format': ['png', 'svg'],
    'figure': ['test_figure']
}

test_cases = ( 
                {
                 'update':   {'silent': True},
                 'operation':   'equal',
                 'result': {'variable': 'status_code', 'value': 200}
                 },
                {
                 'update':   {'output_format': 'png',
                              'output_type': 'string'},
                 'operation':   'contains',
                 'result': {'variable': 'content',
                            'value': "data:image/png;base64"}
                },
                {
                 'update':   {'output_format': 'svg',
                              'output_type': 'string'},
                 'operation':   'contains',
                 'result': {'variable': 'content',
                            'value': "data:image/svg+xml;"}
                },
                {
                 'update':   {'output_format': 'svg',
                              'output_type': 'file'},
                 'operation':   'contains',
                 'result': {'variable': 'content',
                            'value': ".svg"}
                },
                {
                 'update':   {'output_format': 'png',
                              'output_type': 'file'},
                 'operation':   'contains',
                 'result': {'variable': 'content',
                            'value': ".png"}
                },
                {
                 'update':   {'figure': 'no_figure_view', 'silent': False},
                 'operation': 'raises',
                 'result': {'variable': '', 
                            'value': AttributeError}
                }
)
#  ---------- end of test settings -------------

def cartesian_helper(dct):
    keys = dct.keys()
    vals = dct.values()
    for instance in itertools.product(*vals):
        yield dict(zip(keys, instance))

def test_view(request, form):
    template = Engine().from_string(b"This is probe {{ form }}")
    ctx = Context({'form': form})
    data = template.render(ctx)
    return HttpResponse(data)


def create_model(name, fields=None, app_label='',
                 module=''):
    class Meta:
        pass
    if app_label:
        setattr(Meta, 'app_label', app_label)
    attrs = {'__module__': module, 'Meta': Meta}
    if fields:
        attrs.update(fields)
    model = type(name, (models.Model,), attrs)
    return model


def test_wrapper(kw, variable, op, value, ind):
    def test_function(self, kw=kw, variable=variable, op=op,
                        value=value, ind=ind):
        
        factory = RequestFactory()
        request = factory.get("/")

        def build_env(request):
            sample_model = create_model('SampleModel%s' % ind,
                                        fields={'figure': MatplotlibFigureField(**kw)},
                                        module='django_matplotlib',
                                        app_label='django_matplotlib')
            class SampleForm(forms.ModelForm):
                class Meta:
                    model = sample_model
                    fields = '__all__'
            response = test_view(request, SampleForm())
            return response

        if op == 'raises':
            self.assertRaises(value, build_env, request)
        else:
            response = build_env(request)
            if op == 'equal':
                self.assertEqual(getattr(response, variable), value)

            if op == 'contains':
                self.assertIn(value, getattr(response, variable).decode('utf-8'))
    return test_function


class VariationalTestMetaclass(type):
    """ Metaclass which generates all test cases """

    def __new__(mcs, name, bases, attrs):
        bases += (TestCase, ) if TestCase not in bases else bases
        cls = super().__new__(mcs, name, bases, attrs)
        ind = 1
        for test_case in test_cases:
            for kw in cartesian_helper(par_variations):
                kw.update(test_case['update'])
                test_f = test_wrapper(kw=kw, variable=test_case['result']['variable'],
                        op=test_case['operation'], value=test_case['result']['value'],
                        ind=ind)
                setattr(cls, 'test_%s_%s' % (test_case['result']['variable'], ind), test_f)
                ind += 1
        return cls


class AutoGeneratedTests(metaclass=VariationalTestMetaclass):
    pass
    







