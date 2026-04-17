from .AbstractEnergyDataProvider import AbstractEnergyDataProvider
import asyncio
class ExampleEnergyDataProvider(AbstractEnergyDataProvider):
    def __init__(self,
                 ID,
                 kwargs: dict = {}
                 ):
        super().__init__(ID=ID)

        self.__coordinator_results = {}

    @property
    def coordinator_results(self):
        return self.__coordinator_results

    @coordinator_results.setter
    def coordinator_results(self, value):
        self.__coordinator_results = value
        return
    async def get_energy_data_provider_information(self):
        """
        Function that uses the results of the coordinator to preprocess the information and send it to the prosumer agent.
        The prosumer model uses this information.
        :param coordinator_results: Results of the Coordinator
        :return: Some information that is sent to the prosumer model
        """
        return

    def form_coordinator_information(self, prosumer_model_information):
        """
        This methods purpose is to form the prosumer_model_information so the coordinator understands the message
        :param prosumer_model_information: information of the prosumer model.
        :return:
        """
        return