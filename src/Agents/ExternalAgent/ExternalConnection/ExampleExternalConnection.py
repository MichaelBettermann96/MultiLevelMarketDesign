from ....utils.Logger import Warning, Info, Fail, Print_Values
from .AbstractExternalConnection import AbstractExternalConnection

class ExampleExternalConnection(AbstractExternalConnection):
    def __init__(self):
        return

    def get_external_connection_information(self):
        """
        Provide the external information for the coordination process
        :return:
        """
        return

    async def update_external_connection_information(self, data):
        return