from .AbstractEnergyDataProvider import AbstractEnergyDataProvider
import asyncio
from ....utils.Logger import Warning, Fail, Info, Print_Values


class EDP_Proxy(AbstractEnergyDataProvider):
    def __init__(self,
                 ID,
                 kwargs: dict = {}
                 ):
        super().__init__(ID=ID)

        self.__coordinator_results = {}

        self.__lower_coordinator_not_updated = True
        self.__upper_coordinator_not_updated = True
        self.__round_one = True

    @property
    def coordinator_results(self):
        return self.__coordinator_results

    @coordinator_results.setter
    def coordinator_results(self, value):
        self.__coordinator_results = value
        self.__upper_coordinator_not_updated = False
        return

    async def proxy_connection(self, data):
        # Take the information from the connected external agent and give it to the coordinator results
        self.__coordinator_results = data

        self.__lower_coordinator_not_updated = False


        while self.__upper_coordinator_not_updated:
            await asyncio.sleep(0)


        # After getting the information set everything to initial settings
        if (self.__lower_coordinator_not_updated == False) and (self.__upper_coordinator_not_updated == False):
            if self.__round_one == True:
                self.__round_one = False
               # reset to original state
            else:
                self.__round_one = True
                self.__upper_coordinator_not_updated = True
                self.__lower_coordinator_not_updated = True
                self.__coordinator_results = {}


        return self.__coordinator_results

    async def get_energy_data_provider_information(self):
        """
        Function that uses the results of the coordinator to preprocess the information and send it to the prosumer agent.
        The prosumer model uses this information.
        :param coordinator_results: Results of the Coordinator
        :return: Some information that is sent to the prosumer model
        """

        while self.__lower_coordinator_not_updated:
            await asyncio.sleep(0)

        return self.__coordinator_results

    def form_coordinator_information(self, prosumer_model_information):
        """
        This methods purpose is to form the prosumer_model_information so the coordinator understands the message
        :param prosumer_model_information: information of the prosumer model.
        :return:
        """
        return self.__coordinator_results