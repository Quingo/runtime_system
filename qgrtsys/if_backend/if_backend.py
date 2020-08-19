class If_backend():
    """The interface class for Quingo backends.

    Any actual backend (including hardware such as CCLight, simulators)
    should inherit from this interface.
    """

    def __init__(self, name):
        self.__name__ = name

    def name(self):
        return self.__name__

    def available(self):
        return False

    def execute(self):

        raise NotImplementedError

    def read_result(self):
        raise NotImplementedError

    def upload_program(self, program):
        raise NotImplementedError
