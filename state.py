
class State:
    """
    A functor wrapper of a state including its ability to convert itself to a key
    """
    @property
    def key(self):
        return self._bytes_conversion(self._state)

    @property
    def value(self):
        return self._state

    def __init__(self, state, bytes_conversion):
        self._state = state
        self._bytes_conversion = bytes_conversion