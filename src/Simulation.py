

from .utils.Aggregation_Unit import Aggregation_Unit
import asyncio
import aiomas

class Simulation():
    def __init__(self):

        # Eventloop of the simulation --> enables asynchronous running of the simulation
        self.__simulation_loop = None
        # Inherits all information about the aggregation unit --> needed to start the Eventloop simultanously
        self.__aggregation_unit_dict = {}
        # Dictory of all added agents --> only used by external agents --> added later to enable connections to Proxies
        self.__agent_dict = {}

        return


    def __simulation_close(self):
        for aggregation_unit in self.__aggregation_unit_dict.values():
            aggregation_unit.close()

        return

    # Add the Aggregation unit. It still needs coordinator, prosumer agent etc.
    def add_aggregation_unit(self, containeraddress, ID, rounds=1,):
        aggregation_unit = Aggregation_Unit(
            containeraddress=containeraddress,
            ID=ID,
            rounds=rounds,
            loop=self.__simulation_loop
        )

        # check if ID already taken
        if ID in self.__agent_dict.keys():
            raise Exception("Each agent must have a unique ID. {} is already taken".format(ID))
        # add aggregation unit to the aggregation unit dictionary
        self.__aggregation_unit_dict[ID] = aggregation_unit

        # The first container provides the eventloop for the asynchronous implementation
        if self.__simulation_loop == None:
            self.__simulation_loop = aggregation_unit.container.loop
        return

    # add a coordinator, i.e., the way the Aggregation unit is coordinating the prosumer agents
    def add_coordinator(self,
                        aggregation_unit_ID,
                        coordinator,
                        ID,
                        coordinator_kwargs = {},
                        ):

        # check if ID already taken
        if ID in self.__agent_dict.keys():
            raise Exception("Each agent must have a unique ID. {} is already taken".format(ID))

        # add description of agent to agent dict
        self.__agent_dict[ID] = {"agent_type": "coordinator_agent",
                               "aggregation_unit_ID": aggregation_unit_ID,
                               "coordinator": coordinator,
                                "coordinator_kwargs": coordinator_kwargs
                                 }

        self.__aggregation_unit_dict[aggregation_unit_ID].add_CoordinatorAgent(coordinator=coordinator, coordinator_kwargs=coordinator_kwargs, ID=ID)
        return

    # add a prosumer agent, i.e., the represenation of your energy system. Different prosumer models and energy data provider are possible
    def add_prosumer(self,
                     aggregation_unit_ID,
                     ID,
                     prosumer_model,
                     energy_data_provider,
                     prosumer_model_kwargs={},
                     energy_data_provider_kwargs={}
                     ):

        # check if ID already taken
        if ID in self.__agent_dict.keys():
            raise Exception("Each agent must have a unique ID. {} is already taken".format(ID))

        # add description of agent to agent dict
        self.__agent_dict[ID] = {"agent_type": "prosumer_agent",
                               "aggregation_unit_ID": aggregation_unit_ID,
                               "prosumer_model": prosumer_model,
                               "energy_data_provider": energy_data_provider,
                               "prosumer_model_kwargs": prosumer_model_kwargs,
                               "energy_data_provider_kwargs": energy_data_provider_kwargs
                                 }

        self.__aggregation_unit_dict[aggregation_unit_ID].add_ProsumerAgent(ID=ID,
                                                                            energy_data_provider=energy_data_provider,
                                                                            energy_data_provider_kwargs=energy_data_provider_kwargs,
                                                                            prosumer_model=prosumer_model,
                                                                            prosumer_model_kwargs=prosumer_model_kwargs,
                                                                            )
        return

    # add infrastructure provider i.e., the agent representing and handling the powergrid below
    def add_infrastructure_provider(self,
                                    aggregation_unit_ID,
                                    ID,
                                    grid_data_provider,
                                    grid_data_provider_kwargs,
                                    network_simulator,
                                    network_simulator_kwargs
                                    ):

        # check if ID already taken
        if ID in self.__agent_dict.keys():
            raise Exception("Each agent must have a unique ID. {} is already taken".format(ID))

        # add description of agent to agent dict
        self.__agent_dict[ID] = {
            "agent_type": "infrastructure_agent",
            "aggregation_unit_ID": aggregation_unit_ID,
            "grid_data_provider": grid_data_provider,
            "network_simulator": network_simulator,
            "grid_data_provider_kwargs": grid_data_provider_kwargs,
            "network_simulator_kwargs": network_simulator_kwargs
                                 }

        self.__aggregation_unit_dict[aggregation_unit_ID].add_InfrasturctureAgent(ID=ID,
                                                                                  grid_data_provider=grid_data_provider,
                                                                                  grid_data_provider_kwargs=grid_data_provider_kwargs,
                                                                                  network_simulator=network_simulator,
                                                                                  network_simulator_kwargs=network_simulator_kwargs
                                                                                  )
        return

    # Add external connection i.e., the agent responsible for inter Aggregation unit communication.
    def add_external_connection(self,
                                aggregation_unit_ID,
                                ID,
                                external_connection,
                                external_connection_kwargs={},
                                ):

        # Check whether external connection and container are in the kwargs. If they are raise an exception
        if "external_connection" in external_connection_kwargs.keys() or "container" in external_connection_kwargs.keys():
            raise Exception("'external_connection' and 'container' keys are not allowed in the external_connection_kwargs, since they are resorved for Proxy connections")

        # add description of agent to agent dict
        self.__agent_dict[ID] = {"agent_type": "external_agent",
                               "aggregation_unit_ID": aggregation_unit_ID,
                               "external_connection": external_connection,
                               "external_connection_kwargs": external_connection_kwargs
                                 }

        return

    # build the external agent after the connection and everything is set.
    def __build_simulation(self):

        # check the agent dict for exteranl agents. Add them to the aggregation_unit_dict
        for ID, agent in self.__agent_dict.items():
            if agent["agent_type"] == "external_agent":
                self.__aggregation_unit_dict[agent["aggregation_unit_ID"]].add_ExternalAgent(ID=ID,
                                                                                             external_connection=agent["external_connection"],
                                                                                             external_connection_kwargs=agent["external_connection_kwargs"]
                                                                                             )

        return

    def connect(self,
                prosumer_ID,
                external_ID):

        # get prosumer aggregation unit ID of the prosumer agent in the agent dict
        prosumer_aggregation_unit_ID = self.__agent_dict[prosumer_ID]["aggregation_unit_ID"]
        # get the external address i.e. the address of the prosumer agent proxy, such that the external connection agent can connect.
        external_address = self.__aggregation_unit_dict[prosumer_aggregation_unit_ID].ProsumerAgentList[prosumer_ID].addr
        # get the container of the aggregation unit to be able to connect
        container = self.__aggregation_unit_dict[prosumer_aggregation_unit_ID].container
        # add it to external connection kwargs, such that the external agent has the necessary information for the communication between external connection agent and prosumer agent (proxy)
        self.__agent_dict[external_ID]["external_connection_kwargs"]["external_address"] = external_address
        self.__agent_dict[external_ID]["external_connection_kwargs"]["container"] = container
        return

    # run the simulation asynchronously, such that the aggregation unit run (almost) in parallel
    def run_Simulation(self, timesteps=1):

        # build the rest of the agents (external)
        self.__build_simulation()

       # function to asynchronoulsy start the simulation.
        async def __start_Simulation(data):
            await asyncio.gather(*data)
            return

        for timestep in range(timesteps):
            print("Simulation running: Timestep {}".format(timestep))
            # get all aggregation units and asyncronously start them at the same time
            processlist = [aggregation_unit.run(timestep=timestep) for aggregation_unit in self.__aggregation_unit_dict.values()]
            # run until all aggregation units are finished.
            self.__simulation_loop.run_until_complete(__start_Simulation(data=processlist))

        return

    def close_simulation(self):
        for aggregation_unit in self.__aggregation_unit_dict.values():
            aggregation_unit.close_aggregation_unit()

