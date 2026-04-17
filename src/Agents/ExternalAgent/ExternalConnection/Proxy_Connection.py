
import aiomas
from ....utils.Logger import Warning, Info, Fail, Print_Values
from .AbstractExternalConnection import AbstractExternalConnection

class Proxy_Connection(AbstractExternalConnection):
    def __init__(self,
                 ID,
                 EC_kwargs = {}):
        self.ID = ID

        if "container" not in EC_kwargs.keys():
            raise Exception("For a Proxy Connection the container needs to be known. Please use the connect function with simulation.connect(prosumer_ID='', external_ID='')")
        else:
            self.proxy_container = EC_kwargs["container"]

        if "external_address" not in EC_kwargs.keys():
            raise Exception("For a Proxy Connection the address of the Prosumer Agent of the upper level Aggregation unit has to be given. Please use the connect function with simulation.connect(prosumer_ID='', external_ID='') ")
        else:
            self.external_address = EC_kwargs["external_address"]


        self.external_information = None

        return

    def get_external_connection_information(self):
        """
        Provide the external information for the coordination process
        :return:
        """
        message = {}
        message["type"] = "Proxy"
        message["content"] = self.external_information
        return message

    # When getting response from the lower coordinator --> update upper prosumer agent and wait for update from upper coordinator
    async def update_external_connection_information(self, data):
        if data:
            Prosumer_Agent_Proxy = await self.proxy_container.connect(self.external_address)
            proxy_response = await Prosumer_Agent_Proxy.proxy_connection(data=data)
            self.external_information = proxy_response
        return