from .AbstractGridDataProvider import AbstractGridDataProvider

class ExampleGridDataProvider(AbstractGridDataProvider):
    def __init__(self):
        return

    def get_grid_related_information(self, data):
        """
        The information of the Network Simulator is used and refined to communicate with the coordinator
        :param data: information from the Network Simulator
        :return:
        """
        return

    def process_coordination_data(self, coordination_data):
        """
        :param coordination_data: Information provided from the Coordinator after the coordination step
        :return:
        """

        return
