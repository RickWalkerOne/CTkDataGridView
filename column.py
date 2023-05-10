from typing import Callable, Optional, Any, List
from mask import Mask


class Column:
    def __init__(self,
                 name: str,
                 text: Optional[str] = None,
                 mask: Optional[Mask] = None):
        self._name = name
        self._text = name if text is None else text
        self._mask = mask
        self._callbacks = []

        self._mask.trace(self._mask_changed, True)

    def _mask_changed(self, changed_parameters: List[str]):
        for func in self._callbacks:
            func(changed_parameters)

    def cget(self, key):
        return getattr(self, '_' + key)

    def configure(self,
                  name: Optional[str] = None,
                  text: Optional[str] = None,
                  mask: Optional[Mask] = None):
        changed = []
        if name is not None:
            self._name = name
            changed.append('name')
        if text is not None:
            self._text = text
            changed.append('text')
        if mask is not None:
            self._mask = mask
            changed.append('mask')
        for func in self._callbacks:
            func(changed)

    def trace(self, func: Callable[[List[str]], Any], add: Optional[bool] = False):
        if add:
            self._callbacks.append(func)
        else:
            self._callbacks = [func]
