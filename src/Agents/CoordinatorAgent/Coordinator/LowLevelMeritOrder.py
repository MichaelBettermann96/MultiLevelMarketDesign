from ....utils.Logger import Warning, Info, Fail, Print_Values

from .AbstractCoordinator import AbstractCoordinator
import os
from pathlib import Path
import pandas as pd

class LowLevelMeritOrder(AbstractCoordinator):
    def __init__(self,ID):

        self.ID = ID
        self.prosumption_function = {}
        self.prosumer_bids = None
        return

    def solve(self, data):
        """
        Coordinate the entities that send information to you
        :param data: information from the prosumer agents, external agent and the infrastructure agent
        :return:
        """


        for external_agent_ID, external_agent_info in data["external_agent"].items():
            # Compute the prosumption curves, if there is no higher level clearing price set yet.
            if not external_agent_info["content"]:
                demand = [0] * 96
                supply = {i: [] for i, _ in enumerate(demand)}

                # Read out the consumption bids and the supply bids
                self.prosumer_bids = data["prosumer_agent"]
                for ID, dictionary in data["prosumer_agent"].items():
                    for i, _ in enumerate(demand):
                        # if quantity is positive its demand
                        if dictionary["quantity"][i] >= 0:
                            # Demand will be summed to one quantity
                            demand[i] = demand[i] + dictionary["quantity"][i]
                        # if quantity is negative its supply
                        else:
                            # Supply will be formulated as bids with ID (to identify the seller), quantity (the amount of energy)
                            # , and price (how much the energy costs)
                            supply[i].append({"ID": ID, "quantity": dictionary["quantity"][i], "price": dictionary["price"][i]})
                            # Sort it by price low --> high, to ease the merit order principle latter.
                            supply[i] = sorted(supply[i], key=lambda x: x["price"])

                prosumption_function = {i: None for i, _ in enumerate(demand)}

                for timestep, consuming_bid in enumerate(demand):
                    interval = [{"price_interval": [None, None], "quantity": None} for _ in range(len(supply[timestep])+1)]
                    interval[0]["price_interval"][0] = "-inf"
                    interval[0]["quantity"] = demand[timestep]
                    for bid_it, supplying_bid in enumerate(supply[timestep]):
                        interval[bid_it]["price_interval"][1] = supplying_bid["price"]
                        interval[bid_it+1]["price_interval"][0] = supplying_bid["price"]
                        interval[bid_it+1]["quantity"] = interval[bid_it]["quantity"] + supplying_bid["quantity"]

                    interval[len(supply[timestep])]["price_interval"][1] = "inf"
                    prosumption_function[timestep] = interval

                self.prosumption_function = prosumption_function

                prosumer_agent_data = {}
                for ID, dictionary in data["prosumer_agent"].items():
                    prosumer_agent_data[ID] = []

                external_agent_data = {}
                for ID, dictionary in data["external_agent"].items():
                    external_agent_data[ID] = {"prosumption_function": prosumption_function}


                return {"prosumer_agent": prosumer_agent_data,
                        "external_agent": external_agent_data,
                        "DSO_agent": None}

            # The clearing price of the higher level is set.
            # Therefore, the following can be done:
            # Read the global clearing price (from extern)
            # Determine the local clearing price
            # Determine the costs of consumers
            # Determine the revenue of producer
            else:

                # Read global clearing price
                global_clearing_price = external_agent_info["content"]["clearing_price"]

                # find local clearing price
                local_clearing_price = []
                for timestep, prosumption_interval in self.prosumption_function.items():
                    clearing_point = True
                    # iterate over the intervals per timestep
                    for interval in prosumption_interval:
                        # when for the first time the quantity is negative --> that is the price where more supply than demand is there.
                        if interval["quantity"] <= 0 and clearing_point == True:
                            # if the first interval is already 0 --> no demand in AU --> price == 0
                            if interval["price_interval"][0] == "-inf":
                                local_clearing_price.append(0)
                            else:
                                local_clearing_price.append(interval["price_interval"][0])

                            clearing_point = False
                    if clearing_point:
                        local_clearing_price.append(None)

                Info("The Clearing Price List for the Consumers in the Low Level Coordinator: {} ".format(self.ID))
                print(external_agent_info)
                Info("The local clearing price in the Low Level Coordinator: {}".format(self.ID))
                print(local_clearing_price)

                # Save the information for later evaluation
                self.__save_global_clearing_price(global_clearing_price=global_clearing_price)
                self.__save_prosumption_interval()
                self.__save_local_clearing_price(local_clearing_price=local_clearing_price)


                prosumer_costs = {ID: [] for ID in self.prosumer_bids.keys()}
                for timestep in range(len(global_clearing_price)):
                    # Exception if the global clearing price could not be formed
                    if global_clearing_price[timestep] == None:
                        raise Exception(
                            "The global clearing price is None, therefore in sum there is less generation than consumption this is infeasible --> add more generation at timestep {}".format(timestep))

                    # The AU cannot supply itself at all and is therefore dependent from import. --> no local clearing Price!
                    elif local_clearing_price[timestep] == None:
                        # If that is the case:
                        # Incentivise Production, by providing enough energy for the AU to supply itself --> Merit order (Cheapest first)
                        for prosumer_ID, bids in self.prosumer_bids.items():
                            # What sellers sell
                            if bids["quantity"][timestep] < 0:
                                # if the sellers price is higher than the maximum clearing price --> did not get accepted --> no revenue
                                if bids["price"][timestep] > max(global_clearing_price[timestep]):
                                    prosumer_costs[prosumer_ID].append(0)
                                else:
                                    # the first global price, that is higher than the selling price is the price I get from the clearing process
                                    # check the global price list ...
                                    for global_price in global_clearing_price[timestep]:
                                        # ... until you find one that is bigger or equal to yours
                                        if global_price >= bids["price"][timestep]:
                                            # and take this as your revenue
                                            prosumer_costs[prosumer_ID].append(bids["quantity"][timestep] * global_price)
                                            # break out of this loop
                                            break
                            # What buyers buy
                            else:
                                # Consumers pay the minimum global price.
                                # So if the market was cleared in the mediumLevelMerit order and it is cheaper than the clearing price of th HighLevelMeritOrder
                                # --> the mediumLevelMeritOrder is chosen
                                prosumer_costs[prosumer_ID].append(bids["quantity"][timestep] * min(global_clearing_price[timestep]))
                    # The AU can supply itself and sell energy at its local clearing price. However, a global price might be lower.
                    else:
                        for prosumer_ID, bids in self.prosumer_bids.items():
                            # What sellers sell
                            if bids["quantity"][timestep] < 0:
                                # if the sellers price is higher than the maximum clearing price --> did not get accepted --> no revenue
                                if bids["price"][timestep] > max(global_clearing_price[timestep]):
                                    prosumer_costs[prosumer_ID].append(0)
                                else:
                                    # the first global price, that is higher than the selling price is the price I get from the clearing process
                                    # check the global price list ...
                                    for global_price in global_clearing_price[timestep]:
                                        # ... until you find one that is bigger or equal to yours
                                        if global_price >= bids["price"][timestep]:
                                            # and take this as your revenue
                                            prosumer_costs[prosumer_ID].append(bids["quantity"][timestep] * global_price)
                                            # break out of this loop
                                            break
                            # What buyers buy
                            else:
                                # The consumer pays the minimum of the local clearing price and the entries of the global_clearing_prices
                                prosumer_costs[prosumer_ID].append(bids["quantity"][timestep] * min(local_clearing_price[timestep], *global_clearing_price[timestep]))


                external_agent_data = {}
                for ID, dictionary in data["external_agent"].items():
                    external_agent_data[ID] = {}

                return {"prosumer_agent": {ID: costs for ID, costs in prosumer_costs.items()},
                        "external_agent": external_agent_data,
                        "DSO_agent": None}

    def __save_global_clearing_price(self, global_clearing_price):
        df = pd.DataFrame(data=global_clearing_price)
        Path(os.getcwd() + "/Agents/CoordinatorAgent/output/LowLevelMeritOrder/Coordinator_" + str(self.ID)).mkdir(parents=True, exist_ok=True)
        path = os.getcwd() + "/Agents/CoordinatorAgent/output/LowLevelMeritOrder/Coordinator_" + str(self.ID) + "/global_clearing_price.csv"
        df.to_csv(path, index=False)
        return

    def __save_local_clearing_price(self, local_clearing_price):
        df = pd.DataFrame(data=local_clearing_price)
        Path(os.getcwd() + "/Agents/CoordinatorAgent/output/LowLevelMeritOrder/Coordinator_" + str(self.ID)).mkdir(parents=True, exist_ok=True)
        path = os.getcwd() + "/Agents/CoordinatorAgent/output/LowLevelMeritOrder/Coordinator_" + str(self.ID) + "/local_clearing_price.csv"
        df.to_csv(path, index=False)

        return


    def __save_prosumption_interval(self,):
        for timestep, prosumption_interval in self.prosumption_function.items():
            data = {}
            # build the Dataframe and save it
            for interval in prosumption_interval:
                data[interval["price_interval"][0]] = interval["quantity"]

            intervals = [str(x["price_interval"][0]) for x in prosumption_interval]
            intervals.append("inf")
            data = [{"quantity": x["quantity"]} for x in prosumption_interval]
            data.append({"quantity": data[len(data)-1]["quantity"]})
            df = pd.DataFrame(data=data, index=intervals)

            Path(os.getcwd() + "/Agents/CoordinatorAgent/output/LowLevelMeritOrder/Coordinator_" + str(self.ID)).mkdir(parents=True, exist_ok=True)
            path = os.getcwd() + "/Agents/CoordinatorAgent/output/LowLevelMeritOrder/Coordinator_" + str(self.ID) + "/timestep_" + str(timestep) + ".csv"
            df.to_csv(path)

        return