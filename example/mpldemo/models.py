from django_matplotlib.fields import MatplotlibFigureField
from django.db import models


class CompositeModel(models.Model):
    
    # Plot piecewise line
    line_plot = MatplotlibFigureField(figure='plot_line',
                                      verbose_name='Line', silent=True)
    # Plot sine function
    sine_plot = MatplotlibFigureField(figure='plot_sine',
                                      verbose_name='Sine', silent=True)
    # Imshow demo
    imshow_demo = MatplotlibFigureField(figure='image_plot',
                                        verbose_name='Imshow demo', silent=True)

    # Pass arguments to plot
    with_args = MatplotlibFigureField(figure='plot_with_args',
                                      verbose_name="Args passed", silent=True,
                                      plt_args=([1, 4, 2], [5, 2, 1]),
                                      help_text="Arguments are passed to the plot "
                                      "using `plt_args` keyword."
                                    )
    # Countour plot as svg
    countour_plot = MatplotlibFigureField(figure='countour_plot',
                                    verbose_name="Contour plot", silent=True,
                                    plt_kwargs={"custom_title":
                                                "Custom figure title goes here..."
                                                }
                                    )

