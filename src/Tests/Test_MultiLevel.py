import os

from src.utils import Logger as lg

from src.utils.Logger import Info
from src.Simulation import Simulation




"""
Operational Cost in EUROcents/kWh depending on type:
    PV: [4.1  -  14.4] 
    PV + Battery: [6.0 - 22.5]
    Wind onshore: [4.3 - 9.2] 
    Bio: [11.5 - 32.5] 
    Coal: [15.1 - 29.3]

    TODO: 
        Which price should be assumed? The right border or the average?
"""


def Test_MultiLevel_main():

    simulation = Simulation()

    # High
    simulation.add_aggregation_unit(rounds=1,
                                    containeraddress=('localhost', 5555),
                                    ID=1000,)

    # Lower and Medium AU have to run atleast thrice in order to fully get all the updates. This is due to the layout of the MAS
    # Medium
    simulation.add_aggregation_unit(rounds=2,
                                    containeraddress=('localhost', 5556),
                                    ID=1001,)
    #Medium
    simulation.add_aggregation_unit(rounds=2,
                                    containeraddress=('localhost', 5557),
                                    ID=1002,)
    # Low
    simulation.add_aggregation_unit(rounds=2,
                                    containeraddress=('localhost', 5558),
                                    ID=1003,)
    # Low
    simulation.add_aggregation_unit(rounds=2,
                                    containeraddress=('localhost', 5559),
                                    ID=1004,)
    # Low
    simulation.add_aggregation_unit(rounds=2,
                                    containeraddress=('localhost', 5560),
                                    ID=1005,)
    # Low
    simulation.add_aggregation_unit(rounds=2,
                                    containeraddress=('localhost', 5561),
                                    ID=1006,)

    # Adding the Coordinator
    # HighLevel
    simulation.add_coordinator(aggregation_unit_ID=1000, coordinator="HighLevelMeritOrder", ID=5001)
    # MediumLevel
    simulation.add_coordinator(aggregation_unit_ID=1001, coordinator="MediumLevelMeritOrder", ID=5002)
    simulation.add_coordinator(aggregation_unit_ID=1002,coordinator="MediumLevelMeritOrder", ID=5003)
    # LowLevel
    simulation.add_coordinator(aggregation_unit_ID=1003, coordinator="LowLevelMeritOrder", ID=5004)
    simulation.add_coordinator(aggregation_unit_ID=1004,coordinator="LowLevelMeritOrder", ID=5005)
    simulation.add_coordinator(aggregation_unit_ID=1005,coordinator="LowLevelMeritOrder", ID=5006)
    simulation.add_coordinator(aggregation_unit_ID=1006,coordinator="LowLevelMeritOrder", ID=5007)

    # first LowLevelAggregation unit
    simulation.add_prosumer(aggregation_unit_ID=1003,
                            ID=1,
                            prosumer_model="Simple_Producer",
                            energy_data_provider="StaticBidder",
                            energy_data_provider_kwargs={"selling_price": [1] * 96},
                            prosumer_model_kwargs={"quantity": [-2] * 96}
                            )

    simulation.add_prosumer(aggregation_unit_ID=1003,
                            ID=2,
                            prosumer_model="Simple_Producer",
                            energy_data_provider="StaticBidder",
                            energy_data_provider_kwargs={"selling_price": [4] * 96},
                            prosumer_model_kwargs={"quantity": [-1] * 96}
                            )


    simulation.add_prosumer(aggregation_unit_ID=1003,
                            ID=4,
                            prosumer_model="Simple_Consumer",
                            energy_data_provider="StaticBidder",
                            energy_data_provider_kwargs={},
                            prosumer_model_kwargs={"quantity": [3] * 96}
                            )



    # Second LowLevel_Aggregation_unit
    simulation.add_prosumer(aggregation_unit_ID=1004,
                            ID=5,
                            prosumer_model="Simple_Producer",
                            energy_data_provider="StaticBidder",
                            energy_data_provider_kwargs={"selling_price": [1] * 96},
                            prosumer_model_kwargs={"quantity": [-1] * 96}
                            )

    simulation.add_prosumer(aggregation_unit_ID=1004,
                            ID=6,
                            prosumer_model="Simple_Producer",
                            energy_data_provider="StaticBidder",
                            energy_data_provider_kwargs={"selling_price": [3] * 96},
                            prosumer_model_kwargs={"quantity": [-1] * 96}
                            )

    simulation.add_prosumer(aggregation_unit_ID=1004,
                            ID=7,
                            prosumer_model="Simple_Producer",
                            energy_data_provider="StaticBidder",
                            energy_data_provider_kwargs={"selling_price": [4] * 96},
                            prosumer_model_kwargs={"quantity": [-1] * 96}
                            )


    simulation.add_prosumer(aggregation_unit_ID=1004,
                            ID=8,
                            prosumer_model="Simple_Consumer",
                            energy_data_provider="StaticBidder",
                            energy_data_provider_kwargs={},
                            prosumer_model_kwargs={"quantity": [1] * 96}
                            )

    # Third LowLevel_Aggregation_unit
    simulation.add_prosumer(aggregation_unit_ID=1005,
                            ID=9,
                            prosumer_model="Simple_Producer",
                            energy_data_provider="StaticBidder",
                            energy_data_provider_kwargs={"selling_price": [1] * 96},
                            prosumer_model_kwargs={"quantity": [-2] * 96}
                            )

    simulation.add_prosumer(aggregation_unit_ID=1005,
                            ID=12,
                            prosumer_model="Simple_Consumer",
                            energy_data_provider="StaticBidder",
                            energy_data_provider_kwargs={},
                            prosumer_model_kwargs={"quantity": [4] * 96}
                            )


    # Fourth LowLevel_Aggregation_unit
    simulation.add_prosumer(aggregation_unit_ID=1006,
                            ID=13,
                            prosumer_model="Simple_Producer",
                            energy_data_provider="StaticBidder",
                            energy_data_provider_kwargs={"selling_price": [5] * 96},
                            prosumer_model_kwargs={"quantity": [-1] * 96}
                            )

    simulation.add_prosumer(aggregation_unit_ID=1006,
                            ID=16,
                            prosumer_model="Simple_Consumer",
                            energy_data_provider="StaticBidder",
                            energy_data_provider_kwargs={},
                            prosumer_model_kwargs={"quantity": [1] * 96}
                            )

    # First MediumLevel_Aggregation_unit
    simulation.add_prosumer(aggregation_unit_ID=1001,
                            ID=17,
                            prosumer_model="Simple_Consumer",
                            energy_data_provider="StaticBidder",
                            energy_data_provider_kwargs={},
                            prosumer_model_kwargs={"quantity": [1] * 96}
                            )
    simulation.add_prosumer(aggregation_unit_ID=1001,
                            ID=18,
                            prosumer_model="Simple_Producer",
                            energy_data_provider="StaticBidder",
                            energy_data_provider_kwargs={"selling_price": [2] * 96},
                            prosumer_model_kwargs={"quantity": [-2] * 96}
                            )


    # Second MediumLevel_Aggregation_unit
    simulation.add_prosumer(aggregation_unit_ID=1002,
                            ID=20,
                            prosumer_model="Simple_Consumer",
                            energy_data_provider="StaticBidder",
                            energy_data_provider_kwargs={},
                            prosumer_model_kwargs={"quantity": [2] * 96}
                            )
    simulation.add_prosumer(aggregation_unit_ID=1002,
                            ID=21,
                            prosumer_model="Simple_Producer",
                            energy_data_provider="StaticBidder",
                            energy_data_provider_kwargs={"selling_price": [2] * 96},
                            prosumer_model_kwargs={"quantity": [-2] * 96}
                            )
    simulation.add_prosumer(aggregation_unit_ID=1002,
                            ID=22,
                            prosumer_model="Simple_Producer",
                            energy_data_provider="StaticBidder",
                            energy_data_provider_kwargs={"selling_price": [4] * 96},
                            prosumer_model_kwargs={"quantity": [-1] * 96}
                            )

    ### finished setting up non-Proxy Prosumer Agents

    # Add Proxies
    # High AU
    simulation.add_prosumer(aggregation_unit_ID=1000,
                            ID=2001,
                            prosumer_model="Empty_Prosumer_Model",
                            energy_data_provider="EDP_Proxy",
                            energy_data_provider_kwargs={},
                            prosumer_model_kwargs={}
                            )

    simulation.add_prosumer(aggregation_unit_ID=1000,
                            ID=2002,
                            prosumer_model="Empty_Prosumer_Model",
                            energy_data_provider="EDP_Proxy",
                            energy_data_provider_kwargs={},
                            prosumer_model_kwargs={}
                            )

    # Medium AU 1
    simulation.add_prosumer(aggregation_unit_ID=1001,
                            ID=2003,
                            prosumer_model="Empty_Prosumer_Model",
                            prosumer_model_kwargs={},
                            energy_data_provider="EDP_Proxy",
                            energy_data_provider_kwargs={},
                            )

    simulation.add_prosumer(aggregation_unit_ID=1001,
                            ID=2004,
                            prosumer_model="Empty_Prosumer_Model",
                            energy_data_provider="EDP_Proxy",
                            energy_data_provider_kwargs={},
                            prosumer_model_kwargs={}
                            )


    # Medium AU 2
    simulation.add_prosumer(aggregation_unit_ID=1002,
                            ID=2005,
                            prosumer_model="Empty_Prosumer_Model",
                            energy_data_provider="EDP_Proxy",
                            energy_data_provider_kwargs={},
                            prosumer_model_kwargs={}
                            )

    simulation.add_prosumer(aggregation_unit_ID=1002,
                            ID=2006,
                            prosumer_model="Empty_Prosumer_Model",
                            energy_data_provider="EDP_Proxy",
                            energy_data_provider_kwargs={},
                            prosumer_model_kwargs={}
                            )



    # Adding External Agents
    # Connect Medium 1 & 2 --> to High
    simulation.add_external_connection(aggregation_unit_ID=1001,
                                       ID=4003,
                                       external_connection="Proxy_Connection",
                                       external_connection_kwargs={}
                                       )
    simulation.connect(prosumer_ID=2001, external_ID=4003)


    simulation.add_external_connection(aggregation_unit_ID=1002,
                                       ID=4004,
                                       external_connection="Proxy_Connection",
                                       external_connection_kwargs={}
                                       )
    simulation.connect(prosumer_ID=2002, external_ID=4004)

    # Connect Low 1 & 2 --> to Medium 1
    simulation.add_external_connection(aggregation_unit_ID=1003,
                                       ID=4005,
                                       external_connection="Proxy_Connection",
                                       external_connection_kwargs={}
                                       )
    simulation.connect(prosumer_ID=2003, external_ID=4005)


    simulation.add_external_connection(aggregation_unit_ID=1004,
                                       ID=4006,
                                       external_connection="Proxy_Connection",
                                       external_connection_kwargs={}

                                       )
    simulation.connect(prosumer_ID=2004, external_ID=4006)

    # Connect Low 3 & 4 --> to Medium 2
    simulation.add_external_connection(aggregation_unit_ID=1005,
                                       ID=4007,
                                       external_connection="Proxy_Connection",
                                       external_connection_kwargs={}
                                       )
    simulation.connect(prosumer_ID=2005, external_ID=4007)

    simulation.add_external_connection(aggregation_unit_ID=1006,
                                       ID=4008,
                                       external_connection="Proxy_Connection",
                                       external_connection_kwargs={}
                                       )
    simulation.connect(prosumer_ID=2006, external_ID=4008)

    simulation.run_Simulation()

