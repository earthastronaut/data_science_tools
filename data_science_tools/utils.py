""" General python utilities.
"""
import logging
from .types import Any

__all__ = ["DotDict", "LoggerContext"]

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


class LoggerContext:
    """Temporary set values for logger """

    def __init__(self, logger=None, **kws):
        if isinstance(logger, str) or logger is None:
            logger = logging.getLogger(logger)
        self.logger = logger
        self.temporary_config = {}

        for param, value in kws.items():
            self._get_setter(param)
            self.temporary_config[param] = value
        self.saved_config = {}

    def _get_setter(self, param):
        method_name = f"set_{param}"
        if not hasattr(self, method_name):
            raise TypeError(f"Missing setter for {param}")
        return getattr(self, method_name)

    def set_level(self, level):
        """Method to set the log level """
        saved = self.logger.level
        self.logger.setLevel(level)
        return saved

    def set_disabled(self, disabled):
        """Method to set disable """
        saved = bool(self.logger.disabled)
        self.logger.disabled = bool(disabled)
        return saved

    def start(self):
        """ Start logging given context """
        for param, value in self.temporary_config.items():
            setter = self._get_setter(param)
            self.saved_config[param] = setter(value)

    def stop(self):
        """ Stop logging and revert to previous context """
        for param, value in self.saved_config.items():
            setter = self._get_setter(param)
            setter(value)

    def __enter__(self):
        self.start()

    def __exit__(self, *_, **__):
        self.stop()
