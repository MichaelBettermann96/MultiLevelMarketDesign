import pandas as pd
import os
import simbench as sb
import pandapower as pp
from pandapower.plotting.plotly import vlevel_plotly
from pandapower.timeseries import OutputWriter
from pandapower.timeseries import run_timeseries
from pandapower import control
from .....utils.Logger import Info, Fail, Print_Values, Warning
from ..Pandapower_OPF.Controller import Controller
from ..AbstractNetworkSimulator import AbstractNetworkSimulator
import pandas as pd
from pathlib import Path


class Pandapower_OPF(AbstractNetworkSimulator):

    def __init__(self,
                 ID: int,
                 kwargs={}
                 ):
        self.ID = ID

        # TODO: utilise this kwargs
        # Allow to provide a separate mapping list between busID and client ID. Such that the client can be mapped to the power network
        if "client_to_bus_mapping" in kwargs.keys():
            self.__client_to_bus_mapping = kwargs["client_to_bus_mapping"]
        # If this is not provided, add a Warning, and assume client_id == bus_ID
        else:
            Warning("No client to bus mapping was provided. It is therefore assumed, that client_id == bus_ID. If you want to add a client to bus mapping enter in the network_simulator_kwargs = {client_to_bus_mapping: {client_id: bus_id}, ...")
            self.__client_to_bus_mapping = None

        # Allows to add permanent static prosumption to the respective bus
        if "permanent_static_prosumption" in kwargs.keys():
            self.__permanent_static_prosumption = kwargs["permanent_static_prosumption"]
        else:
            self.__permanent_static_prosumption = {}

        # TODO: Scale parameter of the Line up or down.
        # Allows to add permanent static prosumption to the respective bus
        if "line_scaling" in kwargs.keys():
            self.__line_scaling = kwargs["line_scaling"]
        else:
            self.__line_scaling = None


        # Determine the timesteps needed for the pandapower timeseries calculation
        if "timeseries_timesteps" in kwargs.keys():
            self.timesteps = kwargs["timeseries_timesteps"]
        else:
            self.timesteps = 96

        if ("simbench_network" in kwargs.keys()) and ("custom_pandapower_network" in kwargs.keys()):
            raise Exception("Cannot declare simultaneously 'simbench_network' and 'custuom_network_path' simulatanously")

        elif "custom_pandapower_network" in kwargs.keys():
            self.powernetwork = kwargs["custom_pandapower_network"]
            # TODO: Maybe the clean powernetwork function needs to be done beforehand
            # In general each bus should have a load and a sgen. Maybe a function needs to be implemented which artificially puts a load and a sgen onto each bus

            # Make artificial datasource --> initialised with all 0s. Will be updated as soon as the prosumer agent updates their consumption/generation for the first time
            # The format is {("load", "p_mw"), ("sgen", "p_mw"), }
            # Maybe more components can be made controllable (e.g., storage) and maybe later more aspects of the component can be updated (e.g., q_var)
            self.__datasource = {}
            load_Dataframe = pd.DataFrame()
            for load in self.powernetwork.load.iterrows():
                load_Dataframe[load[0]] = [0]*self.timesteps
            self.__datasource[("load", "p_mw")] = load_Dataframe

            sgen_Dataframe = pd.DataFrame()
            for sgen in self.powernetwork.sgen.iterrows():
                sgen_Dataframe[sgen[0]] = [0] * self.timesteps
            self.__datasource[("sgen", "p_mw")] = sgen_Dataframe

            #Warning("Printing custom datasource")
            #print(self.__datasource)

        # get the power network from the respective simbench network
        elif "simbench_network" in kwargs.keys():
            self.powernetwork = sb.get_simbench_net(kwargs["simbench_network"])
            # for debugging purposes
            #Warning("Powernetwork: {}".format(kwargs["simbench_network"]))
            #Print_Values(self.powernetwork)
            #pp.plotting.simple_plot(sb.get_simbench_net(kwargs["simbench_network"]), plot_line_switches=True)
            #pf_res_plotly(net=sb.get_simbench_net(kwargs["simbench_network"]))
            #all_simbench_codes = sb.collect_all_simbench_codes()
            #for code in all_simbench_codes:
            #    print(code)

            if "empty_simbench_network" in kwargs.keys():
                if kwargs["empty_simbench_network"] == True:
                    self.__datasource = {}
                    load_Dataframe = pd.DataFrame()
                    sgen_Dataframe = pd.DataFrame()
                    if self.__client_to_bus_mapping:
                        for client_ID, _ in self.__client_to_bus_mapping.items():
                            if client_ID in self.__permanent_static_prosumption.keys():
                                load_Dataframe[client_ID] = [abs(prosumption) if prosumption > 0 else 0 for prosumption in  self.__permanent_static_prosumption[client_ID]["prosumption"]]
                                sgen_Dataframe[client_ID] = [abs(prosumption) if prosumption < 0 else 0 for prosumption in  self.__permanent_static_prosumption[client_ID]["prosumption"]]
                            else:
                                load_Dataframe[client_ID] = [0] * self.timesteps
                                sgen_Dataframe[client_ID] = [0] * self.timesteps
                    else:
                        raise Exception("if an empty_simbench_network is True, you have to provide a client to bus mapping. This can look like this: 'client_to_bus_mapping': {client_ID: bus_ID,  1: 1, 2: 2, 4: 4, 5: 5, 6: 6, 7: 7,}" )


                    self.__datasource[("load", "p_mw")] = load_Dataframe
                    self.__datasource[("sgen", "p_mw")] = sgen_Dataframe
            else:
                # the datasource taken from the simbench dataset. (used for initialising generation and consumption curves)
                self.__datasource = sb.get_absolute_values(self.powernetwork, profiles_instead_of_study_cases=True)

        else:
            Warning("No network was defined, therefore the network used as default '1-MV-semiurb--1-no_sw' from simbench will be used . Here is a list of all simbench networks")
            self.powernetwork = sb.get_simbench_net('1-MV-semiurb--1-no_sw')
            all_simbench_codes = sb.collect_all_simbench_codes()
            for code in all_simbench_codes:
                print(code)
            # the datasource taken from the simbench dataset. (used for initialising generation and consumption curves)
            self.__datasource = sb.get_absolute_values(self.powernetwork, profiles_instead_of_study_cases=True)
            #Warning("Simbench Datasource")
            #print(self.__datasource[("load", "p_mw")][1][:20])




        # initialise the control function of the powernetwork
        control.run_control(self.powernetwork)

        # make variable for the controller
        self.__load_controller = None
        self.__generation_controller = None

        # initialise outputwriter to save the line loading information
        self.number_of_powerflow_analysis = 0
        # only initialise outputwriter if in kwargs
        self.outputwriter = self.__initialise_output_writer(current_round=self.number_of_powerflow_analysis)


        # make dictionary which saves line information
        self.lines = {}

        # intialise lines, save line_loading percentage, line_ID etc.
        self.__initialise_lines()

        #for bus in self.powernetwork.bus.iterrows():
        #    print(bus)

        # Clean powernetwork, by removing sgen and storages, since they will be implemented in the prosumer agent
        if "clean" in kwargs.keys():
            if kwargs["clean"] == True:
                self.__clean_powernetwork()

        # if no client to bus mapping was given, assume bus_Id == client_ID
        if not self.__client_to_bus_mapping:
            for load in self.powernetwork.load.iterrows():
                self.__client_to_bus_mapping[load[0]] = load[0]


        # initialise the Network Simulation
        self.__initialise()

        #print(self.powernetwork)
        #print(self.__client_to_bus_mapping)
        #for load in self.powernetwork.load.iterrows():
        #    print(load)

        #  Run timeseries first time to initialise the network
        self.run_timeseries()

        # Debugging
        #for ext_grid in self.powernetwork.ext_grid.iterrows():
        #    print(ext_grid)

        #for bus in self.powernetwork.bus.iterrows():
        #    print(bus)

        #for trafo in self.powernetwork.trafo.iterrows():
        #    print(trafo)

        #for line in self.powernetwork.line.iterrows():
        #    print(line)

        # print it to csv to get a better overview
        #self.powernetwork.sgen.to_csv(os.getcwd()+"Sgen_information.csv")
        #for load in self.powernetwork.load.iterrows():
        #    print(load)


        return

    def get_infrastructure_information(self):

        infrastructure_information = []
        for line in self.lines.items():
            temp = {"line_id": line[0]}
            infrastructure_information.append({**temp, **line[1]})

        return {"Lines": infrastructure_information}

    def __initialise_lines(self):
        """
        This function initialises the self.lines dictionary. It reads through the self.powernetwork.lines
        fetches the line information and initialieses the respective lines
        Same goes for the trafo. Trafos are also depicted as "lines" or edges to the upper network
        In case different information needs to be provided. It can be added here
        :return: None
        """
        # save the lines and how it is connected between buses, so the graph can be reconstructed
        for line in self.powernetwork.line.iterrows():
            # the switches sitting on the loop lines are all open. Meaning the grid is working in a radial fashion
            if "loop" not in line[1]["name"]:
                self.lines[str(line[0])] = {
                                 "from_bus": line[1]["from_bus"],
                                 "to_bus": line[1]["to_bus"],
                                 "loading_percentage": [0]*96,
                                 #"price": [0]*96,
                                 }
        # for the external connection add a "line" between the buses that the trafo "connects"
        for i, trafo in enumerate(self.powernetwork.trafo.iterrows()):
            self.lines["e_"+str(i)] = {
                                 "from_bus": trafo[1]["hv_bus"],
                                 "to_bus": trafo[1]["lv_bus"],
                                 "loading_percentage": [0]*96,
                                 }
        return


    def __initialise_output_writer(self, current_round):
        """
        Initialise the output writer to write down the results of the OPF at each time step. If more
        data is needed (e.g., res_line: p_mw) add the logging variable below
        :param: current_round. The current round of powerflow analysis
        :return:
        """
        Info("initialise Outputwriter")
        path = str(Path(os.path.dirname(__file__)).parents[0])
        ow = OutputWriter(self.powernetwork,
                          self.timesteps,
                          output_path=path + "\output\PandapowerOPF/ID_" + str(self.ID) + "/" + "round_" + str(current_round),
                          output_file_type=".xlsx",
                          log_variables=list())

        # these variables are saved to the hard disk after / during the time series loop
        ow.log_variable('res_line', 'loading_percent')
        ow.log_variable('res_line', 'i_ka')
        ow.log_variable('res_line', 'pl_mw')
        ow.log_variable('res_trafo', 'loading_percent')
        ow.log_variable('res_load', "p_mw")
        ow.log_variable('res_bus', 'p_mw')
        ow.log_variable('res_sgen', 'p_mw')

        return ow

    def __initialise(self):
        """
        This function initialises the Network Simulator.
        It starts by getting an overview of the lines in the network and how the busses are connected with each other.
        Then the clients are initialised. Every client is a load and a sgen connected to a bus (sgen is initially 0).
        Then the controllers (sgen and load) are initialised which allow for a timeseries simulation
        At last the LEM is sent the graph structure.
        :return:
        """
        # TODO: According to client mapping add loads to the respective bus
        Info("initialise Pandapower Simulator")
        # The loads are prosumers, so for every load add a sgen. Initially it produces 0
        # __initialise is called after the cleaning_powernetwork function --> old sgens are out and new sgens are added for each load
        # Get all clients such that the controller know how many instances are in the network
        client_ids = []
        for client in self.__client_to_bus_mapping.keys():
                client_ids.append(client)

        print("Client IDS")
        print(client_ids)
        # Add some consumption dummies. Controller are generally just updating the values later set onto the components (loads, sgen)
        self.__load_controller = Controller(net=self.powernetwork,
                                            element='load',
                                            variable='p_mw',
                                            element_index=client_ids,
                                            data_source=self.__datasource[("load", "p_mw")][:self.timesteps],

                                            profile_name=client_ids
                                            )

        # Add a generation dummy as of right now from the datasource. This will be changed as soon as the first round began
        self.__generation_controller = Controller(net=self.powernetwork,
                                                  element='sgen',
                                                  variable='p_mw',
                                                  element_index=client_ids,
                                                  data_source=self.__datasource[("sgen", "p_mw")][:self.timesteps],
                                                  profile_name=client_ids
                                                  )

    def run_timeseries(self):
        """
        run the simulation after the consumption and generation has been changed.
        The outputwriter than provides information need for building the line prices
        :return:
        """
        Info("Start timeseries Simulation")

        try:
            # if logging is activated, then start logging for the current round
            self.__initialise_output_writer(current_round=self.number_of_powerflow_analysis)
            run_timeseries(net=self.powernetwork, time_steps=range(0, self.timesteps))
        except:
            Fail("Situation did not resolve the planned process was not feasible")
            raise Exception("It was not feasible, I still need to think about what I should do, if this is the case")
            return False

        Info("Saving updated Network Information")
        self.update_line_loading_percentages(current_round=self.number_of_powerflow_analysis)
        self.number_of_powerflow_analysis = self.number_of_powerflow_analysis + 1
        return

    def update_line_loading_percentages(self, current_round):
        """
        updates the loading percentages of the line. This is/can be necessary when finding the prices for the lines
        :return:
        """
        path = str(Path(os.path.dirname(__file__)).parents[0])
        line_loading_percentages = pd.read_excel(path + "\output\PandapowerOPF/ID_" + str(self.ID) + "/" + "round_" + str(current_round) + "/res_line/loading_percent.xlsx")
        trafo_loading_percentages = pd.read_excel(path + "\output\PandapowerOPF/ID_" + str(self.ID) + "/" + "round_" + str(current_round) + "/res_trafo/loading_percent.xlsx")
        #TODO: This is specific to this one simbench grid a more general solution needs to be found
        for line_ID in self.lines.keys():
            if "e_" in line_ID:
                trafo_ID = line_ID.replace("e_", "")
                self.lines[line_ID]["loading_percentage"] = [round(loading_percentage, 2) for loading_percentage in trafo_loading_percentages[int(trafo_ID)].tolist()]
            else:
                self.lines[line_ID]["loading_percentage"] = [round(loading_percentage, 2) for loading_percentage in line_loading_percentages[int(line_ID)].tolist()]
        return

    def __clean_powernetwork(self):
        """
         remove the old sgen and storage systems, since it is assumed that those are included in the ProsumerAgent
         Maybe they can be added again later
         :return:
         """

        # Drop original load. This will be replaced depending on the prosumer agent
        for load in self.powernetwork.load.iterrows():
            self.powernetwork.load.drop(load[0], inplace=True)

        # Drop original sgen. This will be replaced depending on the prosumer agent
        for sgen in self.powernetwork.sgen.iterrows():
            self.powernetwork.sgen.drop(sgen[0], inplace=True)

        # Drop original storage this will be replaced depending on the prosumer agent
        for storage in self.powernetwork.storage.iterrows():
            self.powernetwork.storage.drop(storage[0], inplace=True)

        print("Before Line Scaling")
        for line in self.powernetwork.line.iterrows():
            print(line)

        if self.__line_scaling:
            for line_ID, line_info in self.__line_scaling.items():
                self.powernetwork.line.loc[line_ID, "max_i_ka"] = self.powernetwork.line.loc[line_ID, "max_i_ka"] * line_info["max_i_ka_scaling"]

        print("After Line Scaling")
        for line in self.powernetwork.line.iterrows():
            print(line)


        # Add a sgen and load object for each load. Initialise with 0 p_mw
        for client in self.__client_to_bus_mapping.keys():
            # if client in static prosumer list add
            if client in self.__permanent_static_prosumption.keys():
                try:
                    pp.create_load(self.powernetwork, index=client,
                                       bus=self.__permanent_static_prosumption[client]["busID"], p_mw=0,
                                       name="static_consumption_" + str(client))
                    pp.create_sgen(self.powernetwork, index=client,
                                       bus=self.__permanent_static_prosumption[client]["busID"], p_mw=0,
                                       name="static_generation_" + str(client))
                except:
                    raise Exception(
                        "setting up the a permanent static prosumption curve as a load/sgen in the network failed. Make sure to deliver the input in the form of: {ID_Y: {busID: X , prosumption: [....] }} ")
            # else: add them with a
            else:
                pp.create_load(self.powernetwork, index=client, bus=self.__client_to_bus_mapping[client], p_mw=0, name="client_" + str(client) + "_consumption")
                pp.create_sgen(self.powernetwork, index=client, bus=self.__client_to_bus_mapping[client], p_mw=0, name="client_" + str(client) + "_generation")


        return

    def update_network_simulator(self, data):
        """
        This function update the controller with the necessary information for the next timeseries simulation.
        :param data: load or generation that needs to be updated for the next timeseries simulation
        :param type: Determine if it is a load or a generation
        :return:
        """

        #Info("Updateing network Simulator with following information: {}".format(data))

        for client in data:
            prosumption = {"Consumption": [], "Generation": []}
            for timestep, value in enumerate(client["quantity"]):
                if value >= 0:
                    prosumption["Consumption"].append(value)
                    prosumption["Generation"].append(0)

                else:
                    prosumption["Consumption"].append(0)
                    prosumption["Generation"].append(-value)

            node_ID = int(client["client_id"])

            #print("Checking whether client_bus mapping works")
            #print("client_id: {}, node_id: {}".format(client["client_id"], node_ID))
            self.__load_controller.update_datasource(datasource=[value / 1000 for value in prosumption["Consumption"]], node_ID=node_ID)
            self.__generation_controller.update_datasource(datasource=[value / 1000 for value in prosumption["Generation"]], node_ID=node_ID)

        self.run_timeseries()

        return self.get_infrastructure_information()