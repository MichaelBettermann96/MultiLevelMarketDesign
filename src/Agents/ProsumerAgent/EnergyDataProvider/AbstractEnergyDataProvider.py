from abc import ABC, abstractmethod

class AbstractEnergyDataProvider(ABC):
    def __init__(self, ID):
        self.ID = ID
        self.__simulation_timestep = None
        self.__simulation_round = None
        self.__coordinator_results = None
        return

    # timestep within the simulation
    @property
    def simulation_timestep(self):
        return self.__simulation_timestep

    @simulation_timestep.setter
    def simulation_timestep(self, timestep):
        self.__simulation_timestep = timestep

    # Current round within one simulation timestep
    @property
    def simulation_round(self):
        return self.__simulation_round

    @simulation_round.setter
    def simulation_round(self, r):
        self.__simulation_round = r

    @property
    @abstractmethod
    def coordinator_results(self):
        return self.__coordinator_results

    @coordinator_results.setter
    def coordinator_results(self, value):
        self.__coordinator_results = value
        return
    @abstractmethod
    async def get_energy_data_provider_information(self):
        """
        function that determines the prices for injection and consumption for the model to process.
        Format of the output:
        :return: ConsumptionPrice -> list, InjectionPrice -> list
        """
        return

    @abstractmethod
    def form_coordinator_information(self, prosumer_model_information):
        """
        This methods purpose is to form the prosumer_model_information so the coordinator understands the message
        :param prosumer_model_information: information of the prosumer model.
        :return:
        """
        return
