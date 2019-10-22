from django.contrib import admin
from .models import *
from django_matplotlib.fields import MatplotlibFigureField
from django_matplotlib.forms import MatplotlibWidget

# Register your models here.
class MyModelAdmin(admin.ModelAdmin):
    pass

admin.site.register(MyModel, MyModelAdmin)


