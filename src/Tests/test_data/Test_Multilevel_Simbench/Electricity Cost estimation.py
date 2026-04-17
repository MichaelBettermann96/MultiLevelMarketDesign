import os
import pandas as pd
import math
import statistics as st
from ast import literal_eval
from operator import add, mul, sub

timesteps = list(range(0,96,1))

path = os.getcwd() + "/data"

MeritOrdertypes = [
    "/LowLevelMeritOrder",
    "/MediumLevelMeritOrder",
    "/HighLevelMeritOrder"
]

MeritOrdertype_Results = {
    "Low": {
        "price_distribution": None,
        "median_price": None,
        "quantity": None,
        "consumer_Cost": None

    },
    "Medium": {
        "price_distribution": None,
        "median_price": None,
        "quantity": None,
        "consumer_cost":None,
    },
    "High": {
        "quantity": None,
        "consumer_cost": None,
    }
}

for MeritOrdertype in MeritOrdertypes:
    print("")
    print("MeritOrderType: {}".format(MeritOrdertype))


    # Read global price information
    df_global = pd.DataFrame()
    for Coordinator_name in os.listdir(path+MeritOrdertype):
        df_temp = pd.read_csv(path + MeritOrdertype + "/" + Coordinator_name + "/global_clearing_price.csv", index_col=0)
        df_global[Coordinator_name] = df_temp["clearing_price"]


    if MeritOrdertype == "/HighLevelMeritOrder":
        for coordinator in df_global:
            temp = df_global[coordinator].tolist()
            # transform entries from strings to lists
            temp = [literal_eval(value) for value in temp]

            temp = [min(prices) for prices in temp]

            quantity = []
            for timestep in timesteps:
                df_quantity = pd.read_csv(path + MeritOrdertype + "/" + Coordinator_name + "/timestep_" + str(timestep) + ".csv", index_col=0)
                # Quantity is in MWh --> transform to kWh as the prices are set this way
                q = df_quantity["quantity"].tolist()[0] * 1000
                if q > 0:
                    # first value represents the full demand
                    quantity.append(q)
                else:
                    quantity.append(0)

            print("High Level")
            print("The Daily price range is between {} and {}".format(min(temp),max(temp)))
            print("The Daily Median price is {} ".format(st.median(temp)))
            print("The Daily Mean price  is {} ".format(st.mean(temp)))
            print("Aggregated Quantity in High-Level")
            print(quantity)

        MeritOrdertype_Results["High"]["quantity"] = quantity
        MeritOrdertype_Results["High"]["price_distribution"] = temp


    else:
        # Read local price information
        df_local = pd.DataFrame()

        # List of all quantity over the entire day for each coordinator
        aggregated_quantity_list = [0]*96

        for Coordinator_name in os.listdir(path+MeritOrdertype):
            df_local[Coordinator_name] = pd.read_csv(path + MeritOrdertype + "/" + Coordinator_name + "/local_clearing_price.csv", index_col=0)["0"]

            quantity = []
            # iterate over every timestep to get the quantity per timestep
            for timestep in timesteps:
                # read the first value of the aggregated demand curves --> full demand of the respective coordinator
                df_quantity = pd.read_csv(path + MeritOrdertype + "/" + Coordinator_name + "/timestep_" + str(timestep) + ".csv", index_col=0)
                # Quantity is in MWh --> transform to kWh as the prices are set this way
                q = df_quantity["quantity"].tolist()[0] * 1000
                if q > 0 :
                    quantity.append(q)
                else:
                    quantity.append(0)

            # first value represents the full demand
            aggregated_quantity_list = list(map(add, aggregated_quantity_list, quantity))

        minimum_price_list_for_each_coordinator = {}

        for coordinator in df_global:
            # transform global price df to list
            global_price_list = df_global[coordinator].tolist()
            # transform entries from strings to lists
            global_price_list = [literal_eval(value) for value in global_price_list]
            # transform local price df to list
            local_price_list = df_local[coordinator].tolist()

            # insert local price information
            final_prices = [global_price_list[i] + [local_price] if (not math.isnan(local_price) and local_price < min(global_price_list[i])) else global_price_list[i] for i, local_price in enumerate(local_price_list)  ]
            final_prices = list(map(sorted, final_prices))

            # only get the minimum
            minimum_prices = [min(prices) for prices in final_prices]

            # put it into a dictionary
            minimum_price_list_for_each_coordinator[coordinator] = {
                "prices": minimum_prices,
                "max_price": max(minimum_prices),
                "min_price": min(minimum_prices),
                "median_price": st.median(minimum_prices),
                "mean_price": st.mean(minimum_prices),
                "std_price": st.stdev(minimum_prices),
                "quantity": quantity
                                                                    }




        # List of all minimum prices over the entire day for each coordinator
        aggregated_minimum_price_list  = []
        # List of all maximum prices over the entire day for each coordinator
        aggregated_maximum_price_list  = []
        # List of all median prices over the entire day for each coordinator
        aggregated_median_price_list  = []
        # List of all mean prices over the entire day for each coordinator
        aggregated_mean_price_list  = []
        # List of all std prices over the entire day for each coordinator
        aggregated_std_price_list  = []


        # list for price distribution over a day
        price_distribution_per_timestep = {i: [] for i in range(0,96)}
        # fill the list to see the ranges of prices

        for coordinator in minimum_price_list_for_each_coordinator.values():
            aggregated_minimum_price_list.append(coordinator["min_price"])
            aggregated_maximum_price_list.append(coordinator["max_price"])
            aggregated_median_price_list.append(coordinator["median_price"])
            aggregated_mean_price_list.append(coordinator["mean_price"])
            aggregated_std_price_list.append(coordinator["std_price"])






        # For each timstep fill in the respective price for the respective Network
        for coordinator in minimum_price_list_for_each_coordinator.values():
            for index, price in enumerate(coordinator["prices"]):
                price_distribution_per_timestep[index].append(price)


        if MeritOrdertype == "/LowLevelMeritOrder":
            MeritOrdertype_Results["Low"]["price_distribution"] = price_distribution_per_timestep
            MeritOrdertype_Results["Low"]["median_price"] = aggregated_median_price_list
            MeritOrdertype_Results["Low"]["mean_price"] = aggregated_mean_price_list
            MeritOrdertype_Results["Low"]["quantity"] = aggregated_quantity_list
        elif MeritOrdertype == "/MediumLevelMeritOrder":
            MeritOrdertype_Results["Medium"]["price_distribution"] = price_distribution_per_timestep
            MeritOrdertype_Results["Medium"]["median_price"] = aggregated_median_price_list
            MeritOrdertype_Results["Medium"]["mean_price"] = aggregated_mean_price_list
            MeritOrdertype_Results["Medium"]["quantity"] = aggregated_quantity_list

        print("The Daily price range is between {} and {}".format(min(aggregated_minimum_price_list), max(aggregated_maximum_price_list)))
        print("The Daily Median price range is between {} and {}".format(min(aggregated_median_price_list), max(aggregated_median_price_list)))
        print("The Daily Mean price range is between {} and {}".format(min(aggregated_mean_price_list), max(aggregated_mean_price_list)))
        print("The Daily STD price range is between {} and {}".format(min(aggregated_std_price_list), max(aggregated_std_price_list)))
        print("The Daily STD of Mean prices range is: {}".format(st.stdev(aggregated_mean_price_list)))
        print("The Daily STD of Median prices range is: {}".format(st.stdev(aggregated_median_price_list)))
        print("The Aggregated Quantity is: {}".format(aggregated_quantity_list))


print("End Results Multi-Level")
print("Low")
print("Median Price Distribution")
print([st.mean(t) for t in MeritOrdertype_Results["Low"]["price_distribution"].values()])
print("Quantity Distribution")
print(MeritOrdertype_Results["Low"]["quantity"])
print("Median Low Level Cost Distribution")
low_cost_distribution = list(map(mul, [st.mean(t) for t in MeritOrdertype_Results["Low"]["price_distribution"].values()], MeritOrdertype_Results["Low"]["quantity"] ))
print(low_cost_distribution)
print("Sum of Mean Low Level Cost")
print(sum(low_cost_distribution))
print("")

print("Medium")
print("Median Price Distribution")
print([st.mean(t) for t in MeritOrdertype_Results["Medium"]["price_distribution"].values()])
print("Quantity Distribution")
print(list(map(sub, MeritOrdertype_Results["Medium"]["quantity"], MeritOrdertype_Results["Low"]["quantity"])))
print("Median Mean Level Cost Distribution")
medium_cost_distribution = list(map(mul, [st.mean(t) for t in MeritOrdertype_Results["Medium"]["price_distribution"].values()], list(map(sub, MeritOrdertype_Results["Medium"]["quantity"], MeritOrdertype_Results["Low"]["quantity"]))))
print(medium_cost_distribution)
print("Sum of Mean Medium Level Cost ")
print(sum(medium_cost_distribution))
print("")

print("High")
print("Price Distribution")
print(MeritOrdertype_Results["High"]["price_distribution"])
print("Quantity Distribution")
print(list(map(sub, MeritOrdertype_Results["High"]["quantity"], MeritOrdertype_Results["Medium"]["quantity"]   )))
print("Sum of Quantity")
print(sum(list(map(sub, MeritOrdertype_Results["High"]["quantity"], MeritOrdertype_Results["Medium"]["quantity"]   ))))

print("High Level Cost Distribution")
high_cost_distribution = list(map(mul, MeritOrdertype_Results["High"]["price_distribution"], list(map(sub, MeritOrdertype_Results["High"]["quantity"], MeritOrdertype_Results["Medium"]["quantity"]   ))))
print(high_cost_distribution)
print("Sum of High Level Cost")
print(sum(high_cost_distribution))
print("")

print("Final Results:")
print("Final Uniform Pricing Cost: {} ".format(sum(list(map(mul, MeritOrdertype_Results["High"]["price_distribution"],MeritOrdertype_Results["High"]["quantity"])))))
print("Final Multi-Level Pricing Cost: {} ".format(sum(low_cost_distribution) + sum(medium_cost_distribution) + sum(high_cost_distribution)))