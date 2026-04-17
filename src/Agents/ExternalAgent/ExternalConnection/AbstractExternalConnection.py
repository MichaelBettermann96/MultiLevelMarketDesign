from abc import ABC, abstractmethod

class AbstractExternalConnection(ABC):
    def __init__(self):
        self.__simulation_timestep = None
        self.__simulation_round = None
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

    @abstractmethod
    def get_external_connection_information(self):
        """
        Get information from external sources
        :return:
        """
        return

    @abstractmethod
    async def update_external_connection_information(self, data):
        """
        Update the external connection. E.g., update the external agent with the current prosumption information, so
        external entities can "see" what the current status of the local aggregation approach is.
        :return:
        """
        return
