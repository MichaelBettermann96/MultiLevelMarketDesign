from .AbstractGridDataProvider import AbstractGridDataProvider


class Simple_Forwarder(AbstractGridDataProvider):
    def __init__(self):

        self.__coordination_data = None
        return

    def get_grid_related_information(self, data):
        """
        The information of the Network Simulator is used and refined to communicate with the coordinator
        :param data: information from the Network Simulator
        :return:
        """

        print("This ist the Information gathered from the Network Simulator")
        print(data)

        # As of right now do not forward anything
        return #data

    def process_coordination_data(self, coordination_data):
        """
        :param coordination_data: Information provided from the Coordinator after the coordination step
        :return:
        """
        self.__coordination_data = coordination_data
        return coordination_data
