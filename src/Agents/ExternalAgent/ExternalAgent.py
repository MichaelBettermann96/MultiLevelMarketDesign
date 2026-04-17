from ...utils.Logger import Warning, Info, Fail, Print_Values
import aiomas
from ..ExternalAgent import ExternalConnection as exCon

class ExternalAgent(aiomas.Agent):
    def __init__(self,
                 container,
                 ID,
                 external_connection: str,
                 external_connection_kwargs: {} = {},
                 ):
        super().__init__(container)

        self.ID = ID
        # current timestep of the simulation
        self.__timestep = None
        # current round of the simulation
        self.__round = None

        # External Connection
        if type(external_connection) == str:
            self.external_connection = self.__initialise_external_connection(model=external_connection,
                                                                             EC_kwargs=external_connection_kwargs)
        elif isinstance(external_connection, exCon.AbstractExternalConnection):
            self.external_connection = external_connection
        else:
            raise Exception(
                "The format of the external_connection parameter is either of string (for predefined external_connection or an object which inherits from the AbstractExternalConnection"
            )
        return

    async def initialise_External_Agent(self, timestep, round):
        """
        initialise Coordinator agent every timestep
        :param: timestep: Current timestep of the Simulation
                round: current round of the simulation
        :return:
        """

        self.__round = round
        self.__simulation_timestep = timestep

        self.external_connection.simulation_timestep = timestep
        self.external_connection.simulation_round = round
        return


    def __initialise_external_connection(self, model, EC_kwargs):
        """
        :param model: name of the model of the external connection, which will be instantiated
        :return: the model of the external connection
        """
        if model == "Proxy_Connection":
            return exCon.Proxy_Connection(ID=self.ID,
                                          EC_kwargs=EC_kwargs)
        else:
            raise Exception("The model was not recognised")
        return

    async def register_external_agent_at_Coordinator(self, Maddr):
        """
        Provide the Local Energy Market with data from the External Agent (Access point to other networks)
        :param Maddr: address of the Local Energy Market
        :return:
        """
        Coordinator = await self.container.connect(Maddr)

        await Coordinator.initialise_external_agent(ID=self.ID,
                                                    addr=self.addr)
        return


    async def update_external_agent_at_coordinator(self, CoordinatorAddr):
        """
        :param Maddr:
        :return:
        """
        Coordinator = await self.container.connect(CoordinatorAddr)
        await Coordinator.update_external_agent(data=self.external_connection.get_external_connection_information(), ID=self.ID)
        return

    @aiomas.expose
    async def coordination_result(self, result):
        """
        :param result:
        :return:
        """

        await self.external_connection.update_external_connection_information(data=result)
        return

