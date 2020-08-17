""" Configuration
"""
import os

SOURCE_DIR = os.path.dirname(
    __file__
)

DATA_SCIENCE_MPLSTYLE_FILEPATH = os.environ.get(
    'DATA_SCIENCE_MPLSTYLE_FILEPATH',
    os.path.join(SOURCE_DIR, 'visualization/resources/theme.mplstyle')
)

def initialize(config=None):
    """ Initialize the configuration. Called in __init__.py
    """
    # do not import globally so config is top of the import hiearchy.
    import plt  # pylint: disable=import-outside-toplevel, import-error
    config = config or globals()

    plt.style.use(config['DATA_SCIENCE_MPLSTYLE_FILEPATH'])
