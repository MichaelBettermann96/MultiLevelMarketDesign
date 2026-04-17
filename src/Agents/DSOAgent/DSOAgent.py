from ...Agents.DSOAgent import GridDataProvider as gdp
from ...Agents.DSOAgent import NetworkSimulator as ns

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning) # This disables all warning! Only done, because the future warnings came within the package
import aiomas

class DSOAgent(aiomas.Agent):
    def __init__(self,
                 container,
                 ID: int,
                 grid_data_provider,
                 grid_data_provider_kwargs,
                 network_simulator,
                 network_simulator_kwargs,
                 ):
        super().__init__(container=container)
        self.ID = ID

        # current timestep of the simulation
        self.__timestep = None
        # current round of the simulation
        self.__round = None

        # The network simulator simulates the underlying network. It is the one determining line_loading etc.
        self.network_simulator = self.__initialise_network_simulator(model=network_simulator, network_simulator_kwargs=network_simulator_kwargs)

        # The grid_data_provider determines the price for infrastructure usage in the power network used by the Prosumer agents
        self.__grid_data_provider = self.__initialise_grid_data_provider(model=grid_data_provider, grid_data_provider_kwargs=grid_data_provider_kwargs)

        # A dictionary of general infrastructure information
        self.infrastructure_information = None

        # Address of the Coordinator
        self.CoordinatorAddr = None

        # Buffer the results of the last Coordination approach
        self.coordination_result_storage = None

        return

    ## Initialisation Phase ##
    async def initialise_DSOAgent(self, timestep, round):
        """
        initialise Coordinator agent every timestep
        :param: timestep: Current timestep of the Simulation
                round: current round of the simulation
        :return:
        """

        self.__round = round
        self.__simulation_timestep = timestep

        self.network_simulator.simulation_timestep = timestep
        self.__grid_data_provider.simulation_timestep = timestep

        self.network_simulator.simulation_round = round
        self.__grid_data_provider.simulation_round = round
        return


    def __initialise_grid_data_provider(self, model, grid_data_provider_kwargs):
        """
        this function determines which grid_data_provider model is chosen and builds it
        :param model: this is the model of the price setter
        :return:
        """
        # TODO: Refactor this
        if model == "Static":
            return gdp.Static()
        if model == "Linear_Line_Load":
            return gdp.Linear_Line_Load_dependent()
        if model == "Simple_Forwarder":
            return gdp.Simple_Forwarder()
        else:
            raise Exception("The model of the grid_data_provider was not found")

        return

    def __initialise_network_simulator(self, model, network_simulator_kwargs):
        """
        this function determines which Network Simulation model is chosen and builds it
        :param model: this is the model of the Network Simulator
        :return:
        """
        if model == "Pandapower_OPF":
            return ns.Pandapower_OPF(ID=self.ID,
                                     kwargs=network_simulator_kwargs)
        else:
            raise Exception("The model of the network simulator was not found")
        return

    async def register_infrastructure_agent_at_coordinator(self, CoordinatorAddr):
        """
        send the initial data to the Coordinator such that it can initialise the coordination scheme.
        :param: CoordinatorAddr: Address of the Coordinator
        :return:
        """
        Coordinator = await self.container.connect(CoordinatorAddr)
        await Coordinator.initialise_infrastructure_agent(addr=self.addr)
        return

    ## Coordination Phase ##
    # Update the Coordinator with the infrastructure agent information.
    async def update_infrastructure_agent_at_coordinator(self, CoordinatorAddr):
        """
        send the initial data to the Coordinator such that it can initialise the coordination scheme.
        :param: CoordinatorAddr: Address of the Coordinator
        :return:
        """
        Coordinator = await self.container.connect(CoordinatorAddr)

        if self.infrastructure_information != None:
            network_data = self.network_simulator.update_network_simulator(data=self.infrastructure_information)
        else:
            network_data = self.network_simulator.get_infrastructure_information()

        coordinator_data = self.__grid_data_provider.get_grid_related_information(data=network_data)

        await Coordinator.update_infrastructure_agent(data=coordinator_data)
        return

    # store coordination data at grid data provider
    @aiomas.expose
    def coordination_result(self, result):
        self.infrastructure_information = self.__grid_data_provider.process_coordination_data(result)

        return
