from ....utils.Logger import Warning, Info, Fail, Print_Values
from .AbstractCoordinator import AbstractCoordinator

class ExampleCoordinator(AbstractCoordinator):
    def __init__(self, ID):
        self.ID = ID
        return

    # Solving the Coordination Problem. This will be called by the encompassing agent
    def solve(self, data):
        """
        Coordinate the entities that send information to you
        :param data: information from the prosumer agents, external agent and the infrastructure agent
        :return:
        """
        return