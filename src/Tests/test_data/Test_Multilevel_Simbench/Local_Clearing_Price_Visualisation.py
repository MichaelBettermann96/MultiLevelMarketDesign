import os
from ast import literal_eval
import pandas as pd
import math
import statistics as st
import matplotlib.pyplot as plt

plt.rcParams["figure.figsize"] = (14,8)
plt.rcParams.update({'font.size': 11})

Test_date = "/17.04.2026"

path = os.getcwd() + "/data/" + Test_date

MeritOrdertypes = [
    "/LowLevelMeritOrder",
    "/MediumLevelMeritOrder",
    "/HighLevelMeritOrder"
]

MeritOrdertype_Results = {
    "Low": {
        "price_distribution": None,
        "Median_price": None

    },
    "Medium": {
        "price_distribution": None,
        "median_price": None
    },
    "High": {
    }
}


for MeritOrdertype in MeritOrdertypes:
    print("MeritOrderType: {}".format(MeritOrdertype))
    print("")

    # Read global price information
    df_global = pd.DataFrame()
    for Coordinator_name in os.listdir(path+MeritOrdertype):
        df_temp = pd.read_csv(path + MeritOrdertype + "/" + Coordinator_name + "/global_clearing_price.csv")
        #print(df_temp)
        df_global[Coordinator_name] = df_temp["clearing_price"]



    if MeritOrdertype == "/HighLevelMeritOrder":
        for coordinator in df_global:
            temp = df_global[coordinator].tolist()
            # transform entries from strings to lists
            temp = [literal_eval(value) for value in temp]
            # only get the minimum prices of the Clearing Price List
            temp = [min(prices) for prices in temp]

            print("High Level")
            # Determine price range of the simulation day
            print("The Daily price range is between {} and {}".format(min(temp),max(temp)))
            # Determine the median price of the simulation day
            print("The Daily Median price is {} ".format(st.median(temp)))
            # Determine the mean price of the simulation day
            print("The Daily Mean price  is {} ".format(st.mean(temp)))
            # Determine the standard deviation of the prices of the simulation day
            print("The Daily STD price  is {} ".format(st.stdev(temp)))

            MeritOrdertype_Results["High"]= temp

    else:
        # Read local price information
        df_local = pd.DataFrame()
        for Coordinator_name in os.listdir(path+MeritOrdertype):
            df_temp = pd.read_csv(path + MeritOrdertype + "/" + Coordinator_name + "/local_clearing_price.csv")
            df_local[Coordinator_name] = df_temp["0"]

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
                "std_price": st.stdev(minimum_prices)
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
        elif MeritOrdertype == "/MediumLevelMeritOrder":
            MeritOrdertype_Results["Medium"]["price_distribution"] = price_distribution_per_timestep
            MeritOrdertype_Results["Medium"]["median_price"] = aggregated_median_price_list


        print("The Daily price range is between {} and {}".format(min(aggregated_minimum_price_list), max(aggregated_maximum_price_list)))
        print("The Daily Median price range is between {} and {}".format(min(aggregated_median_price_list), max(aggregated_median_price_list)))
        print("The Daily Mean price range is between {} and {}".format(min(aggregated_mean_price_list), max(aggregated_mean_price_list)))
        print("The Daily STD price range is between {} and {}".format(min(aggregated_std_price_list), max(aggregated_std_price_list)))
        print("The STD of Daily Mean prices between AUs of the same level is: {}".format(st.stdev(aggregated_mean_price_list)))
        print("The STD of Daily Median prices between AUs of the same level is: {}".format(st.stdev(aggregated_median_price_list)))


Low_df_price_distribution = pd.DataFrame.from_dict(MeritOrdertype_Results["Low"]["price_distribution"])
Medium_df_price_distribution = pd.DataFrame.from_dict(MeritOrdertype_Results["Medium"]["price_distribution"])
High_df_prices = pd.DataFrame(MeritOrdertype_Results["High"], )

fig, ax = plt.subplots(nrows=3, ncols=1, layout="constrained")
fig.supxlabel("15 Minute Time Interval")
fig.supylabel("Price in €ct per kWh")

# Get the median of the prices between the AUs of the same level
Low_df_median_price = Low_df_price_distribution.median(axis=0)
Medium_df_median_price = Medium_df_price_distribution.median(axis=0)

# Create the boxplot for each interval of the Low level AUs
High_df_prices.plot.line(ax=ax[0], grid=True, color="black")
Low_df_price_distribution.boxplot(column=list(range(1,96,1)), ax=ax[0])

# Create the boxplot for each interval of the Medium Level Aus
High_df_prices.plot.line(ax=ax[1], grid=True, color="black")
Medium_df_price_distribution.boxplot(column=list(range(1,96,1)), ax=ax[1])

# Plot the line of the medians of the low and medium level AU as well as the High-Level/Uniform AU
Low_df_median_price.plot.line(ax=ax[2], grid=True, color="blue")
Medium_df_median_price.plot.line(ax=ax[2], grid=True, color="red")
High_df_prices.plot.line(ax=ax[2], grid=True, color="green")

ax[0].set_xticks(list(range(0,96,5)))
ax[0].set_title("Boxplot Distribution of Low-Voltage Level Prices for each Time Interval")
ax[0].legend(["Uniform"])

ax[1].set_xticks(list(range(0,96,5)))
ax[1].set_title("Boxplot Distribution of Medium-Voltage Level Prices for each Time Interval")
ax[1].legend(["Uniform"])

ax[2].set_xticks(list(range(0,96,5)))
ax[2].set_title("Median prices of Low- , Medium-, and High-Voltage Level Prices for each Time Interval")
ax[2].legend(["Low", "Medium", "High/Uniform"])

#plt.savefig(fname="Clearing_Price.pdf")
plt.show()




