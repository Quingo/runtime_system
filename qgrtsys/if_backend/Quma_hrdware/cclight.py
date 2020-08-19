import logging

from qgrtsys.if_backend.if_backend import *


class CCLight(If_backend):
    # 3. if required, assemble the assembly code into binary code
    def __init__(self):
        super.__init__("CCLight")

    def is_available(self):
        # logging.error(
        #     "{}: This backend has not been implemented yet.".format(self.name))
        return False
