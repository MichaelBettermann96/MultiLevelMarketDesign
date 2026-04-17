from ....utils.Logger import Warning, Info, Fail, Print_Values

from .AbstractCoordinator import AbstractCoordinator
import os
from pathlib import Path
import pandas as pd

class HighLevelMeritOrder(AbstractCoordinator):
    def __init__(self, ID):
        self.ID = ID

        return

    # if there are single bids, transform them into a prosumption function
    def __transform_bid_to_prosumption_function(self, data):

        for agent_id, bid in data.items():
            # if the key "prosumption_function" not in the sent bids it needs to be transformed
            if "prosumption_function" not in bid.keys():
                #Filtering bids
                prosumption_function = {"prosumption_function": {}}
                for timestep, _ in enumerate(bid["quantity"]):
                    # Seller
                    if bid["quantity"][timestep] < 0:
                        prosumption_function["prosumption_function"][str(timestep)] = [
                            {"price_interval": ['-inf', bid["price"][timestep]], "quantity": 0},
                            {"price_interval": [bid["price"][timestep], 'inf'], "quantity": bid["quantity"][timestep]},
                        ]
                    # Buyer
                    else:
                        prosumption_function["prosumption_function"][str(timestep)] = [
                            {"price_interval": ['-inf', "inf"], "quantity": bid["quantity"][timestep]},
                        ]

                data[agent_id] = prosumption_function

        return



    def solve(self, data):
        """
        Coordinate the entities that send information to you
        :param data: information from the prosumer agents, external agent and the infrastructure agent
        :return:
        """

        # get IDs of all prosumers sending information
        prosumer_agent_list = [ID for ID in data["prosumer_agent"].keys()]
        # the function determining the amount of load/generation activated depending on the cleared price
        aggregated_prosumption_function = {}

        # if there are bids (not prosumption functions!) transform them into prosumption functions
        self.__transform_bid_to_prosumption_function(data["prosumer_agent"])

        # Interval is day ahead therefore it is 0-95
        for timestep in range(0, 96):
            # Filter out all the boundaries introduced by the bidder to determine the intervals of the aggregated prosumption function
            boundaries = []
            # iterate through every prosumer agent
            for prosumer_agent_ID in prosumer_agent_list:
                # iterate through every interval of each prosumer agent
                for interval in data["prosumer_agent"][prosumer_agent_ID]["prosumption_function"][str(timestep)]:
                    #if timestep == 0:
                        #print("timestep {} : {}".format(timestep, interval))
                    # check for infinite values --> only add the non-infinite values
                    # if the left interval is not "-inf", then add the left boundary ...
                    if interval["price_interval"][0] != "-inf":
                        # ... if it is not in boundaries yet
                        if interval["price_interval"][0] not in boundaries:
                            boundaries.append(interval["price_interval"][0])
                    # if the right interval is not "inf", then add the right boundary ...
                    if interval["price_interval"][1] != "inf":
                        # ... if it is not in boundaries yet
                        if interval["price_interval"][1] not in boundaries:
                            boundaries.append(interval["price_interval"][1])

            # sort the boundaries, so it is rising e.g., [3,1,2] --> [1,2,3]
            sorted_boundaries = sorted(boundaries)
            # insert infinite values again at the beginning and at the end of the interval
            if not sorted_boundaries:
                aggregated_prosumption_function[timestep] = [{"price_interval": ["-inf", "inf"], "quantity": 0}]
            else:
                # insert the values of the intervals --> intervals of aggregated function, quantity still missing
                aggregated_prosumption_function[timestep] = [
                    {"price_interval": ["-inf", sorted_boundaries[0]], "quantity": 0}]
                for i, bound in enumerate(sorted_boundaries):
                    if i != len(sorted_boundaries) - 1:
                        aggregated_prosumption_function[timestep].append({"price_interval": [sorted_boundaries[i], sorted_boundaries[i + 1]], "quantity": 0})
                aggregated_prosumption_function[timestep].append({"price_interval": [sorted_boundaries[len(sorted_boundaries) - 1], "inf"], "quantity": 0})

            # Determine the respective cumulated quantity values
            for prosumer_agent_ID in prosumer_agent_list:
                # iterate over all intervals of all bidders
                for interval in data["prosumer_agent"][prosumer_agent_ID]["prosumption_function"][str(timestep)]:
                    # iterate over all aggregated_prosumption_function intervals
                    for aggregated_intervals in aggregated_prosumption_function[timestep]:

                        # if both interval and aggregated_intervals are on the border --> add quantity to aggregated_intervals
                        if (interval["price_interval"][0] == "-inf" and aggregated_intervals["price_interval"][0] == "-inf") or \
                                (interval["price_interval"][1] == "inf" and aggregated_intervals["price_interval"][1] == "inf"):
                            aggregated_intervals["quantity"] = aggregated_intervals["quantity"] + interval["quantity"]

                        # if the right side of the interval is bigger than the left border of aggregated_intervals --> add quantity to aggregated_intervals
                        elif (interval["price_interval"][0] == "-inf" and aggregated_intervals["price_interval"][0] != "-inf"):
                            # if interval spans the entire aggregated_interval --> add quantity to aggregated intervals
                            if interval["price_interval"][1] == "inf":
                                aggregated_intervals["quantity"] = aggregated_intervals["quantity"] + interval[
                                    "quantity"]
                            elif (aggregated_intervals["price_interval"][0] < interval["price_interval"][1]):
                                aggregated_intervals["quantity"] = aggregated_intervals["quantity"] + interval[
                                    "quantity"]

                        # if the left side of the interval is smaller than the right border of aggregated_intervals --> add quantity to aggregated_intervals
                        elif (interval["price_interval"][1] == "inf" and aggregated_intervals["price_interval"][1] != "inf"):
                            # if interval spans the entire aggregated_interval --> add quantity to aggregated intervals
                            if interval["price_interval"][0] == "-inf":
                                aggregated_intervals["quantity"] = aggregated_intervals["quantity"] + interval[
                                    "quantity"]
                            elif (aggregated_intervals["price_interval"][1] > interval["price_interval"][0]):
                                aggregated_intervals["quantity"] = aggregated_intervals["quantity"] + interval[
                                    "quantity"]

                        # if neither boundary is inifinte
                        # if the left side of the interval is smaller than the right border of aggregated_intervals --> add quantity to aggregated_intervals
                        elif not (interval["price_interval"][0] == "-inf" or interval["price_interval"][1] == "inf") and \
                                not (aggregated_intervals["price_interval"][0] == "-inf" or aggregated_intervals["price_interval"][1] == "inf"):
                            # the left side of the interval is smaller than the right border of x and
                            # the right border of the interval has to be bigger or the same as the right border of aggregated_intervals --> add quantity
                            if (interval["price_interval"][0] < aggregated_intervals["price_interval"][1]) and \
                                    (interval["price_interval"][1] >= aggregated_intervals["price_interval"][1]):
                                aggregated_intervals["quantity"] = aggregated_intervals["quantity"] + interval["quantity"]

        # save the prosumption interval in the Coordinator output folder
        self.__save_prosumption_interval(aggregated_prosumption_function)

        # Determine the clearing price
        local_clearing_price = []
        for prosumption_interval in aggregated_prosumption_function.values():
            clearing_point = True
            # iterate over the intervals per timestep
            for interval in prosumption_interval:
                # when for the first time the quantity is negative --> that is the price where more supply than demand is there.
                if interval["quantity"] <= 0 and clearing_point == True:
                    # if the first interval is already 0 --> no demand in AU --> price == 0
                    if interval["price_interval"][0] == "-inf":
                        local_clearing_price.append([0])
                    else:
                        local_clearing_price.append([interval["price_interval"][0]])

                    clearing_point = False
            if clearing_point:
                local_clearing_price.append(None)

        Info("The global clearing price (Clearing Price List) of Global Level at Coordinator {}:".format(self.ID))
        print(local_clearing_price)

        self.__save_global_clearing_price(global_clearing_price={"clearing_price": local_clearing_price})



        return {"prosumer_agent": {ID: {"clearing_price": local_clearing_price} for ID, _ in data["prosumer_agent"].items()},
                "external_agent": None,
                "DSO_agent": None, }


    # saving the global clearing price to the folder CoordinatorAgent/output/HighLevelMeritOrder/Coordinator
    def __save_global_clearing_price(self, global_clearing_price):
        df = pd.DataFrame(data=global_clearing_price)
        Path(os.getcwd() + "/Agents/CoordinatorAgent/output/HighLevelMeritOrder/Coordinator_" + str(self.ID)).mkdir(
            parents=True, exist_ok=True)
        path = os.getcwd() + "/Agents/CoordinatorAgent/output/HighLevelMeritOrder/Coordinator_" + str(
            self.ID) + "/global_clearing_price.csv"
        df.to_csv(path)

        return

    # saving the prosumption interval to the folder CoordinatorAgent/output/HighLevelMeritOrder/Coordinator
    def __save_prosumption_interval(self, aggregated_prosumption_function):
        for timestep, prosumption_interval in aggregated_prosumption_function.items():
            data = {}
            # build the Dataframe and save it
            for interval in prosumption_interval:
                data[interval["price_interval"][0]] = interval["quantity"]

            intervals = [str(x["price_interval"][0]) for x in prosumption_interval]
            intervals.append("inf")
            data = [{"quantity": x["quantity"]} for x in prosumption_interval]
            data.append({"quantity": data[len(data) - 1]["quantity"]})
            df = pd.DataFrame(data=data, index=intervals)

            Path(os.getcwd() + "/Agents/CoordinatorAgent/output/HighLevelMeritOrder/Coordinator_" + str(
                self.ID)).mkdir(parents=True, exist_ok=True)
            path = os.getcwd() + "/Agents/CoordinatorAgent/output/HighLevelMeritOrder/Coordinator_" + str(
                self.ID) + "/timestep_" + str(timestep) + ".csv"
            df.to_csv(path)