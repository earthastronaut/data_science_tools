""" General python utilities.
"""

__all__ = [
    'DotDict'
]

# %% DotDict

class DotDict(dict):
    """ dot.notation access to dictionary attributes """

    def __hasattr__(self, name):
        return super().__contains__(name)

    def __getitem__(self, name):
        try:
            return super().__getitem__(name)
        except KeyError as error:
            names = list(self.keys())
            error.args = (f"'{name}' not in {names}",)
            raise error

    def __getattr__(self, name):
        try:
            return self.__getitem__(name)
        except KeyError as error:
            raise AttributeError(*error.args)

    def __setitem__(self, name, value):
        self.__dict__[name] = value
        return super().__setitem__(name, value)

    def __setattr__(self, name, value):
        return self.__setitem__(name, value)

    def __delitem__(self, name):
        del self.__dict__[name]
        return super().__delitem__(name)

    def __delattr__(self, name):
        return self.__delitem__(name)


# %%
