from .AbstractNetworkSimulator import AbstractNetworkSimulator

# Abstract GridDataProvider provides a blueprint on what methods a GridDataProvider has to implement
class ExampleNetworkSimulator(AbstractNetworkSimulator):
    def __init__(self, ID, kwargs):
        self.ID = ID
        return

    def get_infrastructure_information(self):
        """
        Implements a function that provides the Coordinator agent with information of the infrastructure.
        :return:
        """

        return

    def update_network_simulator (self, data):
        """
        updates the network simulator.
        :return:
        """
        return