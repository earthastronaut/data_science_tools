""" General python utilities.
"""

from .types import Any

__all__ = ["DotDict"]

# %% DotDict


class DotDict(dict):
    """ dot.notation access to dictionary attributes """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__.update(self)

    def __hasattr__(self, name: str):
        return super().__contains__(name)

    def __getitem__(self, name: str):
        try:
            return super().__getitem__(name)
        except KeyError as error:
            names = list(self.keys())
            error.args = (f"'{name}' not in {names}",)
            raise error

    def __getattr__(self, name: str):
        try:
            return self.__getitem__(name)
        except KeyError as error:
            raise AttributeError from error

    def __setitem__(self, name: str, value: Any):
        self.__dict__[name] = value
        return super().__setitem__(name, value)

    def __setattr__(self, name: str, value: Any):
        return self.__setitem__(name, value)

    def __delitem__(self, name: str):
        del self.__dict__[name]
        return super().__delitem__(name)

    def __delattr__(self, name: str):
        return self.__delitem__(name)


# %%
