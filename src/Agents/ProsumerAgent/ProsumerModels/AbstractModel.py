from abc import ABC, abstractmethod

class AbstractModel(ABC):
    def __init__(self,ID):
        self.ID = ID
        self.__simulation_timestep = None
        self.__simulation_round
        return

    @property
    def simulation_timestep(self):
        return self.__simulation_timestep

    @simulation_timestep.setter
    def simulation_timestep(self, timestep):
        self.__simulation_timestep = timestep

    @property
    def simulation_round(self):
        return self.__simulation_round

    @simulation_round.setter
    def simulation_round(self, r):
        self.__simulation_round = r


    @abstractmethod
    async def update_model(self):
        """
        update the model. The vendor tries to gain as much profit as possible out of the local energy market. Therefore,
        it will change the expected electricity and the injection prices, which the model should take as input to optimise
        its operation
        :return:
        """
        return

