import asyncio
import aiomas

from .Logger import Warning, Info, Fail, Print_Values
from ..Agents.ProsumerAgent.ProsumerAgent import ProsumerAgent
from ..Agents.DSOAgent.DSOAgent import DSOAgent
from ..Agents.ExternalAgent.ExternalAgent import ExternalAgent
from ..Agents.CoordinatorAgent.CoordinatorAgent import CoordinatorAgent

class Aggregation_Unit():
    def __init__(self,
                 ID,
                 infrastructureAgent=None,
                 coordinatorAgent=None,
                 externalAgent=None,
                 containeraddress=('localhost', 5555),
                 rounds=1,
                 loop=None

                 ):

        self.ID = ID
        self.__ProsumerAgentList = {}
        self.InfrastructureAgent = infrastructureAgent
        self.CoordinatorAgent = coordinatorAgent
        self.ExternalAgent = externalAgent
        self.__ExternalAgentList = {}
        self.rounds = rounds


        self.container = aiomas.Container.create(containeraddress, loop=loop)

        return

    @property
    def ProsumerAgentList(self):
        return self.__ProsumerAgentList

    def close_aggregation_unit(self):
        self.container.shutdown()
        return
    # Adding Agents
    def add_ProsumerAgent(self,
                          ID,
                          prosumer_model,
                          energy_data_provider,
                          energy_data_provider_kwargs={},
                          prosumer_model_kwargs={}):

        if ID in self.__ProsumerAgentList.keys():
            raise Exception("The ID is already taken, it is not allowed to register multiple CustomerAgents with the same ID")
        self.__ProsumerAgentList[ID] = ProsumerAgent(container=self.container,
                                                   ID=ID,
                                                   prosumer_model=prosumer_model,
                                                   energy_data_provider=energy_data_provider,
                                                   energy_data_provider_kwargs=energy_data_provider_kwargs,
                                                   prosumer_model_kwargs=prosumer_model_kwargs
                                                   )
        return


    def add_InfrasturctureAgent(self,
                                ID,
                                grid_data_provider,
                                network_simulator,
                                grid_data_provider_kwargs,
                                network_simulator_kwargs,
                                ):

        if self.InfrastructureAgent != None:
            raise Exception("Only one Infrastructure Agent per aggregation unit is allowed as of right now")
        self.InfrastructureAgent = DSOAgent(
                                            ID=ID,
                                            container=self.container,
                                            grid_data_provider=grid_data_provider,
                                            grid_data_provider_kwargs=grid_data_provider_kwargs,
                                            network_simulator=network_simulator,
                                            network_simulator_kwargs=network_simulator_kwargs,
                                            )



    def add_CoordinatorAgent(self,
                             coordinator,
                             coordinator_kwargs,
                             ID):
        if self.CoordinatorAgent != None:
            raise Exception("Only one Corrdinator is allowed as of right now")

        self.CoordinatorAgent = CoordinatorAgent(container=self.container, coordinator=coordinator, coordinator_kwargs=coordinator_kwargs, ID=ID)
        return

    def add_ExternalAgent(self,
                          ID,
                          external_connection="Basic",
                          external_connection_kwargs={}):

        self.__ExternalAgentList[ID] = ExternalAgent(container=self.container,
                                                     ID=ID,
                                                     external_connection=external_connection,
                                                     external_connection_kwargs=external_connection_kwargs
                                                     )
        return

    ### Start the simulation
    async def run(self, timestep):
        # initialisation phase
            # check if CoordinatorAgent was initialised
        if self.CoordinatorAgent == None:
            raise Exception("You can not simulate a local aggregation approach without a CoordinatorAgent."
                            "Please use the add_CoordinatorAgent() function first")

            # Send Network Data to the Coordinator
        if self.InfrastructureAgent != None:
            await self.InfrastructureAgent.register_infrastructure_agent_at_coordinator(CoordinatorAddr=self.CoordinatorAgent.addr)

        # Register External Agent to simulate the external Connection
        external_agents_register_calls = [agent.register_external_agent_at_Coordinator(Maddr=self.CoordinatorAgent.addr) for agent in self.__ExternalAgentList.values()]
        await asyncio.gather(*external_agents_register_calls)

            # Register Prosumer Agents
        prosumer_agents_register_calls = [agent.register_prosumer_model_at_coordinator(CoordinatorAddr=self.CoordinatorAgent.addr) for agent in self.__ProsumerAgentList.values()]
        await asyncio.gather(*prosumer_agents_register_calls)

        # Coordination phase of one day
        for r in range(0, self.rounds):

            print("Round: {} of Aggregation Unit {} started".format(r, self.ID))
            await self.CoordinatorAgent.initialise_Coordinatoragent(timestep=timestep, round=r)
            if self.InfrastructureAgent != None:
                await self.InfrastructureAgent.initialise_DSOAgent(timestep=timestep, round=r)
            for agent in self.__ExternalAgentList.values():
                await agent.initialise_External_Agent(timestep=timestep, round=r)

            for agent in self.__ProsumerAgentList.values():
                await agent.initialise_Prosumer_Agent(timestep=timestep, round=r)


            # update information of the prosumer agent (3a)
            prosumer_agents_update_coordinator_calls = [agent.update_prosumer_agent_at_coordinator(CoordinatorAddr=self.CoordinatorAgent.addr) for agent in self.__ProsumerAgentList.values()]


            # updating the information of the infrastructure agent at the Coordinator (2b)
            if self.InfrastructureAgent != None:
                await self.InfrastructureAgent.update_infrastructure_agent_at_coordinator(CoordinatorAddr=self.CoordinatorAgent.addr)

            # updating the information of the external agent at the Coordinator (1c)
            external_agents_update_coordinator_calls = [agent.update_external_agent_at_coordinator(CoordinatorAddr=self.CoordinatorAgent.addr) for agent in self.__ExternalAgentList.values()]


            await asyncio.gather(*external_agents_update_coordinator_calls)
            await asyncio.gather(*prosumer_agents_update_coordinator_calls)

            # Calculating the coordination --> leading to 3b, 2c and 4a
            await self.CoordinatorAgent.start_coordination_process()

        return

