from abc import ABC, abstractmethod

# Abstract GridDataProvider provides a blueprint on what methods a GridDataProvider has to implement
class AbstractGridDataProvider(ABC):
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
    def get_grid_related_information(self, data):
        """
        Implements a function that has to calculate on how to price each of the lines.
        :return:
        """
        return
