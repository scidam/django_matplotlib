
# This directory will be created within MEDIA_ROOT to store
# temporary files of figures (if output_type='file').
DJANGO_MATPLOTLIB_TMP = 'matplotlib_tmp'

# Default home for matplotlib views (functions
# which return matplotlib.Figure instance)
DJANGO_MATPLOTLIB_MODULE = 'figures.py'


# Matplotlib Field configurations
DJANGO_MATPLOTLIB_FIG_DEFAULTS = {
    
    # if True and error occurs when generating figure
    # it willn't raise an exception, but show error-message
    'silent':        False,  
    
    # output figure width (px)
    'fig_width':     320,

    # output figure height (px)
    'fig_height':    240,

    # either 'string' or 'file'
    # if output_type='file' the figure will be stored
    # to a temporary file in MEDIA_ROOT/DJANGO_MATPLOTLIB_TMP/
    # if output_type='string' the figure will be embedded into
    # html, e.g. <img src="data:image/png;base64,..." />
    'output_type':   'string',

    # either 'png' or 'svg';
    'output_format': 'png',

    # when output_type='file' and cleanup='True' temporary files
    # will be deleted at exit; if cleanup='False' temporary files
    # will not be cleaned up.
    'cleanup':       True
}



