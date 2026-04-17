from ...utils.Logger import Warning, Fail, Info,Print_Values
import aiomas
from ..CoordinatorAgent import Coordinator as coord
from .Coordinator import AbstractCoordinator as abstractcoord

class CoordinatorAgent(aiomas.Agent):
    def __init__(self,
                 ID,
                 container,
                 coordinator,
                 coordinator_kwargs={},
                 ):
        super().__init__(container)
        self.ID = ID
        # current timestep of the simulation
        self.__simulation_timestep = None
        # current round of the simulation
        self.__round = None

        # Dictionary of prosumer agents with their respective information (e.g. address, current_information)
        self.__prosumer_agent_information = {}

        # Dictionary with infrastructure Provider information
        self.__DSO_agent_information = {"address": None,
                                        "current_information": None,
                                        }

        # Dictionary with external agent information
        self.__external_agent_information = {}

        if type(coordinator) == str:
            self.coordinator = self.__initialise_coordinator(model=coordinator, coordinator_kwargs=coordinator_kwargs)
        elif isinstance(coordinator, coord.AbstractCoordinator):
            self.coordinator = coordinator
        else:
            raise Exception("The format of the Coordinator parameter is either of string (for predefined Coordinator or of type )")

        return

    async def initialise_Coordinatoragent(self, timestep, round):
        """
        initialise Coordinator agent every timestep
        :param: timestep: Current timestep of the Simulation
                round: current round of the simulation
        :return:
        """
        self.__simulation_timestep = timestep
        self.__round = round
        self.coordinator.simulation_timestep = timestep
        self.coordinator.simulation_round = round
        return

    def __initialise_coordinator(self, model, coordinator_kwargs):
        """
        this function determines which coordinator is chosen and builds it
        :param model: this is the model of the coordinator
        :return:
        """
        if model == "CongestionAwareLEM":
            return coord.CongestionAwareLEM(ID=self.ID, kwargs=coordinator_kwargs)
        if model == "LowLevelMeritOrder":
            return coord.LowLevelMeritOrder(ID=self.ID)
        if model == "MediumLevelMeritOrder":
            return coord.MediumLevelMeritOrder(ID=self.ID)
        if model == "HighLevelMeritOrder":
            return coord.HighLevelMeritOrder(ID=self.ID)
        else:
            raise Exception("Coordinator model was not found")
        return

    # initialise the infrastructure agent
    @aiomas.expose
    def initialise_infrastructure_agent(self,
                                        #data,
                                        addr):
        """
        Initialise the DSO, save the address to the DSO to later provide him with information about the coordination process
        :param data: Data about the infrastructure (line congestion etc.)
        :param addr: address of the DSO agent
        :return:
        """
        self.__DSO_agent_information["address"] = addr
        return

    # incoming message 2b
    @aiomas.expose
    def update_infrastructure_agent(self, data):
        """
        :param data:
        :return:
        """
        self.__DSO_agent_information["current_information"] = data
        return

    # allowing the coordinator to initialise the prosumer agents before the coordination process started.
    # Registration of prosumer address e.g.
    @aiomas.expose
    def initialise_prosumer_agent(self, ID, addr):
        """
        Registration of the Prosumer agent. Save the address to later provide the Prosumer agent with information
        about the coordination process
        :param ID: ID of the ProsumerAgent
        :param addr: Address of the ProsumerAgent
        :return:
        """
        self.__prosumer_agent_information[ID] = {"current_information": None, "Address": addr}
        return


    # incoming message 3a
    @aiomas.expose
    def update_prosumer_agent(self, ID, data):
        """
        Registration of the Prosumer agent. Save the address to later provide the Prosumer agent with information
        about the coordination process
        :param ID: ID of the ProsumerAgent
        :param initial_bid: Initial bid used for the first clearing process
        :param addr: Address of the Prosumer Agent
        :return:
        """
        self.__prosumer_agent_information[ID]["current_information"] = data
        return

    # initialise the external agent at the coordinator. E.g., saving the address of the external connection
    @aiomas.expose
    def initialise_external_agent(self, ID,
                                   addr):
        """
        initialisation of the external connection point of the power grid. The external connection provides information
        about the injection prices and the prices for consumption
        :param ID: ID of the ExternalAgent
        :param data: Data regarding feed in tarriffs and external consumption price
        :param addr: Address of the External Agent
        :return:
        """
        Info("registering External Agent {}".format(ID))
        self.__external_agent_information[ID] = {}
        self.__external_agent_information[ID]["address"] = addr
        self.__external_agent_information[ID]["current_information"] = []
        return

    # update the external agent at the coordinator. E.g., update of change of external energy prices
    @aiomas.expose
    def update_external_agent(self, ID, data):
        """
        :param data:
        :return:
        """
        self.__external_agent_information[ID]["current_information"] = data
        return

    # start the coordination process in the simulation
    async def start_coordination_process(self):
        """
        Provide the market clearer with the bid information of the Customer Agent and let him solve the market clearing
        process.
        Then provide the involved Agents with the results of the market clearing process
        :return:
        """
        prosumer_information = {}
        for ID, agent in self.__prosumer_agent_information.items():
            prosumer_information[ID] = agent["current_information"]

        external_information = {}
        for ID, agent in self.__external_agent_information.items():
            external_information[ID] = agent["current_information"]

        # give the coordinator module all the information buffered in the Coordinator agent
        data = {"prosumer_agent": prosumer_information,
                "external_agent": external_information,
                "DSO_agent": self.__DSO_agent_information["current_information"]}

        # Coordination process --> provide prosumer agent information bundeled
        results = self.coordinator.solve(data=data)

        # Send the coordinator information to the respective prosumer agent
        for ID, customer in self.__prosumer_agent_information.items():
            # if the result is set to None, then do not send the message --> its unnecessary
            if results["prosumer_agent"][ID] != None:
                Customer_Agent = await self.container.connect(customer["Address"])
                await Customer_Agent.coordination_result(result=results["prosumer_agent"][ID])

        # send information about external consumption and injection to the External Agent
        # only send information if external agent exists
        if self.__external_agent_information:
            for ID, external_agent in self.__external_agent_information.items():
            # if the result is set to None, then do not send the message --> its unnecessary
                if results["external_agent"] != None:
                    External_Agent = await self.container.connect(external_agent["address"])
                    await External_Agent.coordination_result(result=results["external_agent"][ID])
                else:
                    External_Agent = await self.container.connect(external_agent["address"])
                    await External_Agent.coordination_result(result=None)

        # send information of consumption and generation of the Customer agents and the external agent to the DSO
        # only send information if infrastructure agent exists
        if self.__DSO_agent_information["address"] != None:
            # if the result is set to None, then do not send the message --> its unnecessary
            if results["DSO_agent"] != None:
                DSO_Agent = await self.container.connect(self.__DSO_agent_information["address"])
                await DSO_Agent.coordination_result(result=results["DSO_agent"])

        return
