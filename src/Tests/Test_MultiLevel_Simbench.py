
from src.utils import Logger as lg
import random
from src.utils.Logger import Info, Warning
from src.Simulation import Simulation
import simbench as sb




"""
Operational Cost in EUROcents/kWh depending on type:
    PV: [4.1  -  14.4] 
    PV + Battery: [6.0 - 22.5]  --> PV average 13.2
    Wind onshore: [4.3 - 9.2] 
    Bio: [11.5 - 32.5] 
    Coal: [15.1 - 29.3]
    Water: [5.50 - 17.82]
"""

electricity_price = {
    # Prices for Generation profiles in Eurocents per MWh
    "Hydro1": {"low": 5.50,"high": 17.8},
    "Hydro2": {"low": 5.50,"high": 17.8},
    "Hydro3": {"low": 5.50,"high": 17.8},
    "PV1": {"low": 4.1,"high": 14.4},
    "PV2": {"low": 4.1,"high": 14.4},
    "PV3": {"low": 4.1,"high": 14.4},
    "PV4": {"low": 4.1,"high": 14.4},
    "PV5": {"low": 4.1,"high": 14.4},
    "PV6": {"low": 4.1,"high": 14.4},
    "PV7": {"low": 4.1,"high": 14.4},
    "PV8": {"low": 4.1,"high": 14.4},
    "WP1": {"low": 4.3,"high": 9.2},
    "WP2": {"low": 4.3,"high": 9.2},
    "WP3": {"low": 4.3,"high": 9.2},
    "WP4": {"low": 4.3,"high": 9.2},
    "WP5": {"low": 4.3,"high": 9.2},
    "WP6": {"low": 4.3,"high": 9.2},
    "WP7": {"low": 4.3,"high": 9.2},
    "WP8": {"low": 4.3,"high": 9.2},
    "WP9": {"low": 4.3,"high": 9.2},
    "WP10": {"low": 4.3,"high": 9.2},
    "WP11": {"low": 4.3,"high": 9.2},
    "WP12": {"low": 4.3,"high": 9.2},
    "BM1": {"low": 11.5,"high": 23.5},
    "BM2": {"low": 11.5,"high": 23.5},
    "BM3": {"low": 11.5,"high": 23.5},
    "BM4": {"low": 11.5,"high": 23.5},
    "BM5": {"low": 11.5,"high": 23.5},
    "Coal": 25,

    # Demand of networks which are aggregated
    # for mv grids the price is between the lowest PV and the highest Biomass powerplant,as they are typically in the MV grid (according to simbench documentation)
    "mv_add1": {"low": 4.1,"high": 23.5},
    "mv_add2": {"low": 4.1,"high": 23.5},
    # for lv grids the price for PV is assumed, since they are the only generators according to the simbench documentation
    "lv_semiurb4": {"low": 4.1,"high": 14.4},
    "lv_urban6": {"low": 4.1,"high": 14.4},

}


ID_dict = {

    "prosumer_agent_ID": 0,
    "coordinator_agent_ID": 100000,
    "external_agent_ID": 200000,
    "infrastructure_agent_ID": 300000,
    "aggregation_unit_ID": 400000,
    # not used as of right now

}


simbench_profiles = sb.get_all_simbench_profiles(scenario=0)


profiles = {
   "network": {
       "lv_rural1": "1-LV-rural1--0-no_sw",
       "lv_rural2": "1-LV-rural2--0-no_sw",
       "lv_rural3": "1-LV-rural3--0-no_sw ",
       #"lv_semiurb4": "1-LV-semiurb4--0-no_sw",
       "lv_semiurb5": "1-LV-semiurb5--0-no_sw",
       #"lv_urban6": "1-LV-urban6--0-no_sw",
       "mv_rural":  "1-MV-rural--0-no_sw",
       "mv_semiurb":  "1-MV-semiurb--0-no_sw",
       "mv_urban": "1-MV-urban--0-no_sw",
       "mv_comm": "1-MV-comm--0-no_sw",
   },
    "SLP": {
        # SLPs
        "G0-A": simbench_profiles["load"][["time", "G0-A_pload"]].set_index("time"),
        "G0-M": simbench_profiles["load"][["time", "G0-M_pload"]].set_index("time"),
        "G1-A": simbench_profiles["load"][["time", "G1-A_pload"]].set_index("time"),
        "G1-B": simbench_profiles["load"][["time", "G1-B_pload"]].set_index("time"),
        "G1-C": simbench_profiles["load"][["time", "G1-C_pload"]].set_index("time"),
        "G2-A": simbench_profiles["load"][["time", "G2-A_pload"]].set_index("time"),
        "G3-A": simbench_profiles["load"][["time", "G3-A_pload"]].set_index("time"),
        "G3-M": simbench_profiles["load"][["time", "G3-M_pload"]].set_index("time"),
        "G4-A": simbench_profiles["load"][["time", "G4-A_pload"]].set_index("time"),
        "G4-B": simbench_profiles["load"][["time", "G4-B_pload"]].set_index("time"),
        "G4-M": simbench_profiles["load"][["time", "G4-M_pload"]].set_index("time"),
        "G5-A": simbench_profiles["load"][["time", "G5-A_pload"]].set_index("time"),
        "G6-A": simbench_profiles["load"][["time", "G6-A_pload"]].set_index("time"),
        #"G6-B": simbench_profiles["load"][["time", "G6-B_pload"]].set_index("time"), # does not exist
        "BL-H": simbench_profiles["load"][["time", "BL-H_pload"]].set_index("time"),
        "G3-H": simbench_profiles["load"][["time", "G3-H_pload"]].set_index("time"),
        "WB-H": simbench_profiles["load"][["time", "WB-H_pload"]].set_index("time"),
        "L0-A": simbench_profiles["load"][["time", "L0-A_pload"]].set_index("time"),
        "L2-M": simbench_profiles["load"][["time", "L2-M_pload"]].set_index("time"),

        # Demand of networks which are aggregated
        "mv_add1": simbench_profiles["load"][["time", "mv_add1_pload"]].set_index("time"),
        "mv_add2": simbench_profiles["load"][["time", "mv_add2_pload"]].set_index("time"),
        "lv_semiurb4": simbench_profiles["load"][["time", "lv_semiurb4_pload"]].set_index("time"),
        "lv_urban6": simbench_profiles["load"][["time", "lv_urban6_pload"]].set_index("time"),
    },

"Generation":
    {
       # Generation profiles
        "Hydro1": simbench_profiles["renewables"][["time", "Hydro1"]].set_index("time"),
        "Hydro2": simbench_profiles["renewables"][["time", "Hydro2"]].set_index("time"),
        "Hydro3": simbench_profiles["renewables"][["time", "Hydro3"]].set_index("time"),
        "PV1": simbench_profiles["renewables"][["time", "PV1"]].set_index("time"),
        "PV2": simbench_profiles["renewables"][["time", "PV2"]].set_index("time"),
        "PV3": simbench_profiles["renewables"][["time", "PV3"]].set_index("time"),
        "PV4": simbench_profiles["renewables"][["time", "PV4"]].set_index("time"),
        "PV5": simbench_profiles["renewables"][["time", "PV5"]].set_index("time"),
        "PV6": simbench_profiles["renewables"][["time", "PV6"]].set_index("time"),
        "PV7": simbench_profiles["renewables"][["time", "PV7"]].set_index("time"),
        "PV8": simbench_profiles["renewables"][["time", "PV8"]].set_index("time"),
        "WP1": simbench_profiles["renewables"][["time", "WP1"]].set_index("time"),
        "WP2": simbench_profiles["renewables"][["time", "WP2"]].set_index("time"),
        "WP3": simbench_profiles["renewables"][["time", "WP3"]].set_index("time"),
        "WP4": simbench_profiles["renewables"][["time", "WP4"]].set_index("time"),
        "WP5": simbench_profiles["renewables"][["time", "WP5"]].set_index("time"),
        "WP6": simbench_profiles["renewables"][["time", "WP6"]].set_index("time"),
        "WP7": simbench_profiles["renewables"][["time", "WP7"]].set_index("time"),
        "WP8": simbench_profiles["renewables"][["time", "WP8"]].set_index("time"),
        "WP9": simbench_profiles["renewables"][["time", "WP9"]].set_index("time"),
        "WP10": simbench_profiles["renewables"][["time", "WP10"]].set_index("time"),
        "WP11": simbench_profiles["renewables"][["time", "WP11"]].set_index("time"),
        "WP12": simbench_profiles["renewables"][["time", "WP12"]].set_index("time"),
        "BM1": simbench_profiles["renewables"][["time", "BM1"]].set_index("time"),
        "BM2": simbench_profiles["renewables"][["time", "BM2"]].set_index("time"),
        "BM3": simbench_profiles["renewables"][["time", "BM3"]].set_index("time"),
        "BM4": simbench_profiles["renewables"][["time", "BM4"]].set_index("time"),
        "BM5": simbench_profiles["renewables"][["time", "BM5"]].set_index("time"),

        # Generation of aggregated networks
        "mv_add1": simbench_profiles["renewables"][["time", "mv_add1"]].set_index("time"),
        "mv_add2": simbench_profiles["renewables"][["time", "mv_add2"]].set_index("time"),
        "lv_semiurb4": simbench_profiles["renewables"][["time", "lv_semiurb4"]].set_index("time"),
        "lv_urban6": simbench_profiles["renewables"][["time", "lv_urban6"]].set_index("time"),

    }


}

testing_days = {        # testing days picked at random
    0: "22.01.2016",
    1: "15.02.2016",
    2: "15.03.2016",
    3: "11.04.2016",
    4: "07.06.2016",
    5: "15.07.2016",
    6: "14.08.2016",
    7: "19.09.2016",
    8: "25.11.2016",
    9: "17.12.2016",

}





# build an aggregation unit and connect them to the upper level, unless it is bottom level
def build_aggregation_unit(
                           network: str, # sb code of the respective network in simbench
                           ID_counter_dict: dict, # ID of the respective agent or aggregation unit
                           simulation,
                           level: int,
                           proxy_ID = None
                           ):
    
    level_dict = {
        0: "LowLevelMeritOrder",
        1: "MediumLevelMeritOrder",
        2: "HighLevelMeritOrder" #2
    }


    if level == 0:
        print("Building network: {} on level {}".format(network, level))
        Info("Building Lowlevel aggregation unit {} with coordinator ID {}".format(ID_counter_dict["aggregation_unit_ID"], ID_counter_dict["coordinator_agent_ID"]))
        aggregation_unit_ID = ID_counter_dict["aggregation_unit_ID"]
        # increase the aggregation unit ID dict number by one, since it was used
        ID_counter_dict["aggregation_unit_ID"] = ID_counter_dict["aggregation_unit_ID"] + 1
        # add aggregation unit
        simulation.add_aggregation_unit(rounds=2,  # 2
                                        containeraddress=('localhost', 5555 + aggregation_unit_ID - 400000),
                                        ID=aggregation_unit_ID,
                                        )
        # add coordinator
        simulation.add_coordinator(aggregation_unit_ID=aggregation_unit_ID, coordinator=level_dict[level],
                                   ID=ID_counter_dict["coordinator_agent_ID"])
        ID_counter_dict["coordinator_agent_ID"] = ID_counter_dict["coordinator_agent_ID"] + 1


        Network = sb.get_simbench_net(network)
        testing_day = testing_days[random.randint(a=0, b=9)]
        starting_time_Network = testing_day + " 00:00"
        ending_time_Network = testing_day + " 23:45"
        # get the consumption data from simbench of the respective timeframe
        consumption_data = sb.get_absolute_profiles_from_relative_profiles(net=Network,
                                                                             element="load",
                                                                             multiplying_column="p_mw",
                                                                             time_as_index=True).loc[starting_time_Network:ending_time_Network]
        # calculate the number of loads
        number_of_loads = consumption_data.shape[1]

        # get the generation data from simbench of the respective timeframe
        generation_data = sb.get_absolute_profiles_from_relative_profiles(net=Network,
                                                                            element="sgen",
                                                                            multiplying_column="p_mw",
                                                                            time_as_index=True).loc[starting_time_Network:ending_time_Network] * (-1)  # generation is notated as negative
        # calculate the number of sgens
        number_of_sgen = generation_data.shape[1]

        # for each load
        for index in range(0, number_of_loads):
            #Info("Adding consuming Prosumer Agent {} of Aggregation Unit {}".format(index + ID_counter_dict["prosumer_agent_ID"], aggregation_unit_ID))
            simulation.add_prosumer(aggregation_unit_ID=aggregation_unit_ID,
                                    ID=index + ID_counter_dict["prosumer_agent_ID"], # give ID of index [0-number of loads] +  the base prosumer agent ID
                                    prosumer_model="Simple_Consumer",
                                    energy_data_provider="StaticBidder",
                                    energy_data_provider_kwargs={},
                                    prosumer_model_kwargs={"quantity": consumption_data[index].values.tolist()}
                                    )
        # increase the dict entry with the number of loads just added
        ID_counter_dict["prosumer_agent_ID"] = ID_counter_dict["prosumer_agent_ID"] + number_of_loads
        # for each sgen
        for sgen in Network.sgen.iterrows():
            # extract prosumer agent ID
            prosumer_agent_ID = ID_counter_dict["prosumer_agent_ID"]
            if sgen[1]["profile"] in profiles["Generation"].keys():
                # get the selling price of the generating prosumer agent
                selling_price = round(random.uniform(a=electricity_price[sgen[1]["profile"]]["low"],b=electricity_price[sgen[1]["profile"]]["high"]), 2)
                Info("Adding generating Prosumer Agent {} with profile {} and selling price {} to Aggregation Unit {}".format(prosumer_agent_ID, sgen[1]["profile"], selling_price, aggregation_unit_ID))
                # increase prosumcer_agent_ID by one and save it since it was used
                ID_counter_dict["prosumer_agent_ID"] = ID_counter_dict["prosumer_agent_ID"] + 1
                # read standard generation profiles from the profiles[Generation] dictionary
                generation_data = profiles["Generation"][sgen[1]["profile"]].loc[starting_time_Network:ending_time_Network] * (-1)
                # transform from [[x],[y],[z]] --> [x,y,z]
                generation_data = [item for row in generation_data.values.tolist() for item in row]
                simulation.add_prosumer(aggregation_unit_ID=aggregation_unit_ID,
                                        ID=prosumer_agent_ID,
                                        # give ID of index [0-number of sgens] +  the base prosumer agent ID
                                        prosumer_model="Simple_Producer",
                                        energy_data_provider="StaticBidder",
                                        energy_data_provider_kwargs={
                                            #"selling_price": [prosumer_agent_ID] * 96 # TODO: Change so it reflects actual prices
                                            "selling_price": [selling_price] * 96
                                        },
                                        prosumer_model_kwargs={"quantity": generation_data},
                                        )
        
        # if there is a proxy (so a connection from the external agent to an upper level prosumer agent)
        # create an external agent and connect with the upper prosumer agent
        if proxy_ID != None:
            Warning("adding Externalagent {}".format(ID_counter_dict["external_agent_ID"]))
            # add external connection as proxy
            external_agent_ID = ID_counter_dict["external_agent_ID"]
            # increase the dict entry of the external agent ID by one, since it was used
            ID_counter_dict["external_agent_ID"] = ID_counter_dict["external_agent_ID"] + 1
            simulation.add_external_connection(aggregation_unit_ID=aggregation_unit_ID,
                                               ID=external_agent_ID,
                                               external_connection="Proxy_Connection",
                                               external_connection_kwargs={}
                                               )
            # connect external connection with the prosumer agent functioning as proxy
            simulation.connect(prosumer_ID=proxy_ID, external_ID=external_agent_ID)

    elif level == 1:
        print("Building network: {} on level {}".format(network, level))
        Info("Building Medium Level aggregation unit {} with coordinator ID {}".format(ID_counter_dict["aggregation_unit_ID"], ID_counter_dict["coordinator_agent_ID"]))
        aggregation_unit_ID = ID_counter_dict["aggregation_unit_ID"]
        # increase the aggregation unit ID dict number by one, since it was used
        ID_counter_dict["aggregation_unit_ID"] = ID_counter_dict["aggregation_unit_ID"] + 1
        # add aggregation unit
        simulation.add_aggregation_unit(rounds=2,
                                        containeraddress=('localhost', 5555 + aggregation_unit_ID - 400000),
                                        ID=aggregation_unit_ID, )
        # add coordinator
        simulation.add_coordinator(aggregation_unit_ID=aggregation_unit_ID, coordinator=level_dict[level],
                                   ID=ID_counter_dict["coordinator_agent_ID"])
        ID_counter_dict["coordinator_agent_ID"] = ID_counter_dict["coordinator_agent_ID"] + 1

        # for each load in the network, add a prosumer agent.
        # separate between profiles (load profiles or sgen) and profiles representing another lower level voltage grid
        Network = sb.get_simbench_net(network)
        testing_day = testing_days[random.randint(a=0, b=9)]
        starting_time_Network = testing_day + " 00:00"
        ending_time_Network = testing_day + " 23:45"

        for load in Network.load.iterrows():
            # extract prosumer agent ID
            prosumer_agent_ID = ID_counter_dict["prosumer_agent_ID"]
            if load[1]["profile"] in profiles["network"].keys():
                print("Building recursively a new AU according to network code: {}".format(load[1]["profile"]))

                # increase it by one and save it since it was used
                ID_counter_dict["prosumer_agent_ID"] = ID_counter_dict["prosumer_agent_ID"] + 1

                simulation.add_prosumer(aggregation_unit_ID=aggregation_unit_ID,
                                        ID=prosumer_agent_ID,
                                        prosumer_model="Empty_Prosumer_Model",
                                        energy_data_provider="EDP_Proxy",
                                        energy_data_provider_kwargs={},
                                        prosumer_model_kwargs={}
                                        )

                build_aggregation_unit(
                    network=profiles["network"][load[1]["profile"]],
                    ID_counter_dict=ID_counter_dict,  # ID of the respective agent or aggregation unit
                    simulation=simulation,
                    level=level - 1,
                    proxy_ID=prosumer_agent_ID,

                )

            elif load[1]["profile"] in profiles["SLP"].keys():
                print("Building a consumer model according to SLP code: {}".format(load[1]["profile"]))

                # increase prosumcer_agent_ID by one and save it since it was used
                ID_counter_dict["prosumer_agent_ID"] = ID_counter_dict["prosumer_agent_ID"] + 1
                # read standard load profiles from the profiles[SLP] dictionary
                consumption_data = profiles["SLP"][load[1]["profile"]].loc[starting_time_Network:ending_time_Network]
                # transform from [[x],[y],[z]] --> [x,y,z]
                consumption_data = [item for row in consumption_data.values.tolist() for item in row]
                simulation.add_prosumer(aggregation_unit_ID=aggregation_unit_ID,
                                        ID=prosumer_agent_ID,
                                        # give ID of index [0-number of loads] +  the base prosumer agent ID
                                        prosumer_model="Simple_Consumer",
                                        energy_data_provider="StaticBidder",
                                        energy_data_provider_kwargs={},
                                        prosumer_model_kwargs={"quantity": consumption_data}
                                        )
            else:
                print("This SLP or network code: {} is not in the list (yet)".format(load[1]["profile"]))

        # Add sgen
        # for each sgen
        for sgen in Network.sgen.iterrows():
            # extract prosumer agent ID
            prosumer_agent_ID = ID_counter_dict["prosumer_agent_ID"]
            if sgen[1]["profile"] in profiles["Generation"].keys():
                # get the selling price of the generating prosumer agent
                selling_price = round(random.uniform(a=electricity_price[sgen[1]["profile"]]["low"],b=electricity_price[sgen[1]["profile"]]["high"]), 2)
                Info("Adding generating Prosumer Agent {} with profile {} and selling price {} to Aggregation Unit {}".format(prosumer_agent_ID, sgen[1]["profile"], selling_price, aggregation_unit_ID))
                # increase prosumcer_agent_ID by one and save it since it was used
                ID_counter_dict["prosumer_agent_ID"] = ID_counter_dict["prosumer_agent_ID"] + 1
                # read standard generation profiles from the profiles[Generation] dictionary
                generation_data = profiles["Generation"][sgen[1]["profile"]].loc[starting_time_Network:ending_time_Network] * (-1)
                # transform from [[x],[y],[z]] --> [x,y,z]
                generation_data = [item for row in generation_data.values.tolist() for item in row]
                simulation.add_prosumer(aggregation_unit_ID=aggregation_unit_ID,
                                        ID=prosumer_agent_ID,
                                        # give ID of index [0-number of sgens] +  the base prosumer agent ID
                                        prosumer_model="Simple_Producer",
                                        energy_data_provider="StaticBidder",
                                        energy_data_provider_kwargs={
                                            #"selling_price": [prosumer_agent_ID] * 96 # TODO: Change so it reflects actual prices
                                            "selling_price": [selling_price] * 96
                                        },
                                        prosumer_model_kwargs={"quantity": generation_data},
                                        )
            else:
                print("This Generation Code: {} of network {} is not in the list (yet) or will be ignored (if not semiurb4 and urban6)".format(sgen[1]["profile"], network))

        # add proxy to higher level AU
        if proxy_ID != None:
            Warning("adding Externalagent {}".format(ID_counter_dict["external_agent_ID"]))
            # add external connection as proxy
            external_agent_ID = ID_counter_dict["external_agent_ID"]
            # increase the dict entry of the external agent ID by one, since it was used
            ID_counter_dict["external_agent_ID"] = ID_counter_dict["external_agent_ID"] + 1
            simulation.add_external_connection(aggregation_unit_ID=aggregation_unit_ID,
                                               ID=external_agent_ID,
                                               external_connection="Proxy_Connection",
                                               external_connection_kwargs={}
                                               )
            # connect external connection with the prosumer agent functioning as proxy
            simulation.connect(prosumer_ID=proxy_ID, external_ID=external_agent_ID)

    elif level == 2:
        print("Building network: {} on level {}".format(network, level))
        Info("Building High Level aggregation unit {} with coordinator ID {}".format(ID_counter_dict["aggregation_unit_ID"], ID_counter_dict["coordinator_agent_ID"]))

        aggregation_unit_ID = ID_counter_dict["aggregation_unit_ID"]
        # increase the aggregation unit ID dict number by one, since it was used
        ID_counter_dict["aggregation_unit_ID"] = ID_counter_dict["aggregation_unit_ID"] + 1
        # add aggregation unit
        simulation.add_aggregation_unit(rounds=1,
                                        containeraddress=('localhost', 5555 + aggregation_unit_ID - 400000),
                                        ID=aggregation_unit_ID, )
        # add coordinator
        simulation.add_coordinator(aggregation_unit_ID=aggregation_unit_ID, coordinator=level_dict[level],
                                   ID=ID_counter_dict["coordinator_agent_ID"])
        ID_counter_dict["coordinator_agent_ID"] = ID_counter_dict["coordinator_agent_ID"] + 1

        ## add artificial generation (Coal). apparently at least 60MW is needed. This is the last resort, so it has to clear
        # TODO: Check out the coal generator, they are only used in the Highest level to ensure feasibility
        for coal_generator in range(0,1):
            # extract prosumer agent ID
            prosumer_agent_ID = ID_counter_dict["prosumer_agent_ID"]
            # get the selling price of the generating prosumer agent
            selling_price = electricity_price["Coal"]
            Info("Adding generating Prosumer Agent {} with profile {} and selling price {} to Aggregation Unit {}".format(prosumer_agent_ID, "Coal", selling_price, aggregation_unit_ID))
            # increase prosumcer_agent_ID by one and save it since it was used
            ID_counter_dict["prosumer_agent_ID"] = ID_counter_dict["prosumer_agent_ID"] + 1
            # read standard generation profiles from the profiles[Generation] dictionary (just standard 700kWh per time unit)
            generation_data = [-500]*96
            simulation.add_prosumer(aggregation_unit_ID=aggregation_unit_ID,
                                    ID=prosumer_agent_ID,
                                    # give ID of index [0-number of sgens] +  the base prosumer agent ID
                                    prosumer_model="Simple_Producer",
                                    energy_data_provider="StaticBidder",
                                    energy_data_provider_kwargs={
                                        "selling_price": [selling_price] * 96
                                    },
                                    prosumer_model_kwargs={"quantity": generation_data},
                                    )






        # for each load in the network, add a prosumer agent.
        # separate between profiles (load profiles or sgen) and profiles representing another lower level voltage grid
        Network = sb.get_simbench_net(network)
        testing_day = testing_days[random.randint(a=0, b=9)]
        starting_time_Network = testing_day + " 00:00"
        ending_time_Network = testing_day + " 23:45"

        for load in Network.load.iterrows():
            # extract prosumer agent ID
            prosumer_agent_ID = ID_counter_dict["prosumer_agent_ID"]
            if load[1]["profile"] in profiles["network"].keys():
                print("Building recursively a new AU according to network code: {}".format(load[1]["profile"]))
                print("Building network: {}".format(profiles["network"][load[1]["profile"]]))
                # increase it by one and save it since it was used
                ID_counter_dict["prosumer_agent_ID"] = ID_counter_dict["prosumer_agent_ID"] + 1

                simulation.add_prosumer(aggregation_unit_ID= aggregation_unit_ID,
                                        ID=prosumer_agent_ID,
                                        prosumer_model="Empty_Prosumer_Model",
                                        energy_data_provider="EDP_Proxy",
                                        energy_data_provider_kwargs={},
                                        prosumer_model_kwargs={}
                                        )

                build_aggregation_unit(
                    network= profiles["network"][load[1]["profile"]],
                    ID_counter_dict=ID_counter_dict,  # ID of the respective agent or aggregation unit
                    simulation=simulation,
                    level=level-1,
                    proxy_ID=prosumer_agent_ID,

                )

            elif load[1]["profile"] in profiles["SLP"].keys():
                print("Building a consumer model according to SLP code: {}".format(load[1]["profile"]))

                # increase prosumcer_agent_ID by one and save it since it was used
                ID_counter_dict["prosumer_agent_ID"] = ID_counter_dict["prosumer_agent_ID"] + 1
                # read standard load profiles from the profiles[SLP] dictionary
                consumption_data = profiles["SLP"][load[1]["profile"]].loc[starting_time_Network:ending_time_Network]
                # transform from [[x],[y],[z]] --> [x,y,z]
                consumption_data = [item for row in consumption_data.values.tolist() for item in row]
                simulation.add_prosumer(aggregation_unit_ID=aggregation_unit_ID,
                                        ID=prosumer_agent_ID,
                                        # give ID of index [0-number of loads] +  the base prosumer agent ID
                                        prosumer_model="Simple_Consumer",
                                        energy_data_provider="StaticBidder",
                                        energy_data_provider_kwargs={},
                                        prosumer_model_kwargs={"quantity": consumption_data}
                                        )


            else:
                print("This SLP or network code: {} is not in the list (yet) ".format(load[1]["profile"]))

        # Add sgen
        # for each sgen
        for sgen in Network.sgen.iterrows():
            # extract prosumer agent ID
            prosumer_agent_ID = ID_counter_dict["prosumer_agent_ID"]
            if sgen[1]["profile"] in profiles["Generation"].keys():
                # get the selling price of the generating prosumer agent
                selling_price = round(random.uniform(a=electricity_price[sgen[1]["profile"]]["low"],b=electricity_price[sgen[1]["profile"]]["high"]), 2)
                Info("Adding generating Prosumer Agent {} with profile {} and selling price {} to Aggregation Unit {}".format(prosumer_agent_ID, sgen[1]["profile"], selling_price, aggregation_unit_ID))
                # increase prosumcer_agent_ID by one and save it since it was used
                ID_counter_dict["prosumer_agent_ID"] = ID_counter_dict["prosumer_agent_ID"] + 1
                # read standard generation profiles from the profiles[Generation] dictionary
                generation_data = profiles["Generation"][sgen[1]["profile"]].loc[starting_time_Network:ending_time_Network] * (-1)
                # transform from [[x],[y],[z]] --> [x,y,z]
                generation_data = [item for row in generation_data.values.tolist() for item in row]
                simulation.add_prosumer(aggregation_unit_ID=aggregation_unit_ID,
                                        ID=prosumer_agent_ID,
                                        # give ID of index [0-number of sgens] +  the base prosumer agent ID
                                        prosumer_model="Simple_Producer",
                                        energy_data_provider="StaticBidder",
                                        energy_data_provider_kwargs={
                                            #"selling_price": [prosumer_agent_ID] * 96# TODO: Change so it reflects actual prices
                                            "selling_price": [selling_price] * 96
                                        },
                                        prosumer_model_kwargs={"quantity": generation_data},
                                        )
            else:
                print("This Generation Code: {} is not in the list (yet) or will be ignored (if not semiurb4 and urban6)".format(sgen[1]["profile"]))
    else:
        raise Exception("Level does not exist")


def Test_MultiLevel_Simbench_main():

    simulation = Simulation()
    build_aggregation_unit(
        network="1-HV-urban--2-no_sw",
        ID_counter_dict = ID_dict,  # ID of the respective agent or aggregation unit
        simulation=simulation,
        level= 2,
        proxy_ID = None,
    )

    simulation.run_Simulation()
    simulation.close_simulation()
