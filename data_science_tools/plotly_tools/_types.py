""" For all common types. DO NOT IMPORT OTHER PACKAGE MODULES INTO THIS ONE
"""
# pylint: disable=missing-function-docstring
from abc import ABCMeta, abstractmethod
from typing import Union, List

from plotly.subplots import SubplotXY, SubplotDomain

__all__ = [
    "TScene",
    "TFigure",
]


class TScene(metaclass=ABCMeta):
    """plotly.graph_objects.layout.Scene"""


class TFigure(metaclass=ABCMeta):
    """Type for plotly.graph_objects.Figure"""

    _grid_ref: List

    @abstractmethod
    def get_subplot(
        self, row: int, col: int, secondary_y: bool = False
    ) -> Union[None, TScene, SubplotXY, SubplotDomain]:
        pass
