from abc import ABC, abstractmethod

class AbstractCoordinator(ABC):
    def __init__(self, ID):
        self.ID = ID
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

    # Main function just trying to solve the Coordination problem implemented
    @abstractmethod
    def solve(self, data):
        """
        solve the optimization problem of the Market clearing process
        :param data: bids of the Customeragents
        :return:
        """
        return