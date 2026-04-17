from ..ProsumerAgent import ProsumerModels as pm
from ..ProsumerAgent import EnergyDataProvider as edp

from ...utils.Logger import Warning, Info, Fail, Print_Values
import aiomas
import asyncio
"""
The class ProsumerAgent ist the Agent communicating with the coordinator to adjust its prosumption behaviour.
He encapsulates the prosumer module and the energy data provider module.
The workflow is the following: The energy data provider gathers information from previous coordinations (or a heuristic)
The prosumer model then provides model specific information for the coordination process.
The energy data identifier then summarises and forwards the information for the coordinator  
"""

class ProsumerAgent(aiomas.Agent):
    def __init__(self,
                 container,
                 ID: int,
                 prosumer_model,
                 energy_data_provider,
                 energy_data_provider_kwargs: {} = {},
                 prosumer_model_kwargs: {} = {},
                 ):
        super().__init__(container)
        self.ID = ID
        # current timestep of the simulation
        self.__simulation_timestep = None
        # current round of the simulation
        self.__round = None

       # Prosumer model --> reflecting the local energy management system of a houshold, factory, etc.
        if type(prosumer_model) == str:
            self.__prosumer_model = self.__initialise_prosumer_model(prosumer_model=prosumer_model,
                                                                     prosumer_model_kwargs=prosumer_model_kwargs)
        elif isinstance(prosumer_model, pm.AbstractModel):
            self.__prosumer_model = prosumer_model
        else:
            raise Exception(
                "The format of the prosumer_model parameter is either of string (for predefined prosumer_model or an object which inherits from the abstractModel"
            )

        # Energy Data Provider --> enabling the connection point between Coordinator and Prosumer model
        self.__energy_data_provider = self.__initialise_energy_data_provider(EDP_name=energy_data_provider,
                                                                             EDP_kwargs=energy_data_provider_kwargs,
                                                                             )
        return

    async def initialise_Prosumer_Agent(self, timestep, round):
        """
        initialise Coordinator agent every timestep
        :param: timestep: Current timestep of the Simulation
                round: current round of the simulation
        :return:
        """

        self.__round = round
        self.__simulation_timestep = timestep

        self.__prosumer_model.simulation_timestep = timestep
        self.__energy_data_provider.simulation_timestep = timestep

        self.__prosumer_model.simulation_round = round
        self.__energy_data_provider.simulation_round = round
        return


    def __initialise_energy_data_provider(self,
                                          EDP_name,
                                          EDP_kwargs,
                                          ):
        """
        Function that initialises the vendor, the name is given and the parameters necessary for the vendor are provided
        in **kwargs
        :param EDP_name: name of the energy data provider type
        :param kwargs: optional parameters for the specified energy data provider
        :return:
        """
        # TODO: Refactor this
        # if a new vendor needs to be added, you need add the initialisation here and at the imports
        if EDP_name == "StaticBidder":
            return edp.StaticBidder(ID=self.ID,
                                    kwargs=EDP_kwargs)
        elif EDP_name == "EDP_Proxy":
            return edp.EDP_Proxy(ID=self.ID,
                                    kwargs=EDP_kwargs)
        else:
            raise Exception("The model was not recognised")
        return

    def __initialise_prosumer_model(self,
                                    prosumer_model=str,
                                    prosumer_model_kwargs={}):
        """
        Similar to the __initialise_energy_data_provider function the prosumer model is determined.
        :param model_name: name of the model, which will be instantiated
               model_kwargs: Additional, model specific information, which is provided when instatiating the prosumer agent and prosumer model
        :return: model, which is the prosumer model behind the Prosumer Agent.
        """
        if prosumer_model == "Simple_Producer":
            return pm.SimpleProducer(ID=self.ID,
                                    kwargs=prosumer_model_kwargs
                                    )
        elif prosumer_model == "Simple_Consumer":
            return pm.SimpleConsumer(ID=self.ID,
                                    kwargs=prosumer_model_kwargs
                                    )
        elif prosumer_model == "Empty_Prosumer_Model":
            return pm.Empty_Prosumer_Model(ID=self.ID,
                                    kwargs=prosumer_model_kwargs
                                    )
        else:
            raise Exception("The model was not recognised")
        return

    async def register_prosumer_model_at_coordinator(self,
                                                     CoordinatorAddr,
                                                     ):
        """
        Initialisation function that registers the prosumer agent at the coordinator. Initial bids are provided
        for the first bidding round.
        :param CoordinatorAddr: address of the coordinator
        :return:
        """
        Coordinator = await self.container.connect(CoordinatorAddr)
        await Coordinator.initialise_prosumer_agent(ID=self.ID,
                                                    addr=self.addr)
        return

    async def update_prosumer_agent_at_coordinator(self,
                                                   CoordinatorAddr):
        """
        Update function that updates the prosumer agent information at the Coordinator. Initial data are provided
        for the first coordination round.
        :param CoordinatorAddr: address of the coordinator
        :return:
        """

        # Energy data provider calculating the energy data provider information depending on the coordination results
        energy_data_provider_information = await self.__energy_data_provider.get_energy_data_provider_information()
        # updating the model and letting the model solve the problem (1a)
        prosumer_model_information = await self.__prosumer_model.update_model(updates=energy_data_provider_information)
        # get information regarding the quantity (2a) and forward it to the coordinator

        prosumer_agent_data = self.__energy_data_provider.form_coordinator_information(prosumer_model_information=prosumer_model_information)
        Coordinator = await self.container.connect(CoordinatorAddr)
        await Coordinator.update_prosumer_agent(ID=self.ID, data=prosumer_agent_data)
        # (3a) forward information to the coordinator

        return

    # The coordinator calls this function, to provide the results of the coordination process
    @aiomas.expose
    def coordination_result(self, result):
        # Message 4a sending Coordination results to the Prosumer agent
        self.__energy_data_provider.coordinator_results = result

        return

    # In case your prosumer_model is a proxy, it has this function implemented
    # This function connects the external agent of Aggregation_Unit A with a prosumer agent of Aggregation_Unit B
    @aiomas.expose
    async def proxy_connection(self, data):
        proxy_results = await self.__energy_data_provider.proxy_connection(data)
        return proxy_results
