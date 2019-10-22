from django_matplotlib.fields import MatplotlibFigureField
from django.db import models


class CompositeModel(models.Model):
    
    # Plot piecewise line
    line_plot = MatplotlibFigureField(figure='plot_line',
                                      verbose_name='Line', silent=True)
    # Plot sine function
    sine_plot = MatplotlibFigureField(figure='plot_sine',
                                      verbose_name='Sine', silent=True)
    #                                      
    imshow_demo = MatplotlibFigureField(figure='plot_sine',
                                        verbose_name='Sine', silent=True)


