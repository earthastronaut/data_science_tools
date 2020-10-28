""" Tools for jupyter notebooks.
"""

EXTRA_JUPYTER_HTML = """<!-- EXTRA HTML TO INJECT INTO JUPYTER --!>

<!-- Limits the size of the output --!>
<style>
    .jp-Cell-outputWrapper {
        max-height: 500px;
    }
</style>
"""


def _hack_style_jupyter_lab():
    """Hack style format the jupyter notebook.

    This is a hack for formatting the jupyter notebook. It adds some
    utilities to the jupyter lab.

    Eventually these should be turned into some sort of jupyter lab extension.

    """
    from IPython.core.display import (  # pylint: disable=import-outside-toplevel
        display_html,
    )

    display_html(EXTRA_JUPYTER_HTML, raw=True)
