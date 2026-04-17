import pandas as pd
import matplotlib.pyplot as plt
import os
plt.rcParams["figure.figsize"] = (10,6)
plt.rcParams.update({'font.size': 16})


timestep = str(40)
#Level = "Low"
Level = "Medium"
#Level = "High"
CoordinatorID = str(5002)

path = os.getcwd() + "/data"
LevelPath = path + '/' + Level + 'LevelMeritOrder/Coordinator_' + CoordinatorID + '/timestep_' + timestep + '.csv'
Global_clearing_price_path = path + '/' + Level + 'LevelMeritOrder/Coordinator_' + CoordinatorID + '/global_clearing_price.csv'

global_clearing_price_df = pd.read_csv(Global_clearing_price_path, index_col=0)
global_clearing_price = str(float(min(global_clearing_price_df["clearing_price"][int(timestep)])))

prosumption_function_df = pd.read_csv(LevelPath, index_col=0)
prosumption_function_df.index = prosumption_function_df.index.map(str)

# insert the global clearing price as an interval into the prosumption function visualization
if global_clearing_price in prosumption_function_df.index:
    pass
else:
    for i, index in enumerate(prosumption_function_df.index):
        if prosumption_function_df.index[i + 1] == "inf":
            entry = pd.DataFrame({"quantity": prosumption_function_df["quantity"][index], "index": global_clearing_price}, index=[global_clearing_price])
            prosumption_function_df = pd.concat([prosumption_function_df.iloc[:i+1], entry, prosumption_function_df.iloc[i+1:]])
            break
        elif index == "-inf":
            pass
        elif index < global_clearing_price and global_clearing_price < prosumption_function_df.index[i + 1]:
            entry = pd.DataFrame({"quantity": prosumption_function_df["quantity"][prosumption_function_df.index[i + 1]], "index": global_clearing_price}, index=[global_clearing_price])
            prosumption_function_df = pd.concat([prosumption_function_df.iloc[:i+2], entry, prosumption_function_df.iloc[i+2:]])
            break


# Needed for the negative and positive infinite horizontal lines
Negative_Infinite = prosumption_function_df.loc["-inf"]["quantity"]
Negative_Infinite_x_value = float(prosumption_function_df.index[1])
print(Negative_Infinite_x_value)

Positive_Infinite = prosumption_function_df.loc["inf"]["quantity"]
Positive_Infinite_x_value = float(prosumption_function_df.index[len(prosumption_function_df.index)-2])
print(Positive_Infinite_x_value)

# Map it such that the x axis are actual float values
prosumption_function_df.index = prosumption_function_df.index.map(float)


flag = True
local_clearing_price = [None, 0]
for index in prosumption_function_df.index:
    if (prosumption_function_df["quantity"][index] <= 0) and (flag == True):
        print("local clearing price is: {}".format(index))
        local_clearing_price = [index, 0]
        flag = False


print(prosumption_function_df)
print("")

# Make new dataframe to produce a scatter plot with the local clearing price and global clearing price in there
local_clearing_price_quantity = [[0] if index == local_clearing_price[0] else [None] for index in prosumption_function_df.index]

global_clearing_price_quantity = [[0] if index == global_clearing_price else [None] for index in prosumption_function_df.index]

local_clearing_price_df = pd.DataFrame(local_clearing_price_quantity, columns=["quantity"], index=prosumption_function_df.index)
local_clearing_price_df["index"] = prosumption_function_df.index
local_clearing_price_df.index = local_clearing_price_df.index.map(str)

global_clearing_price_df = pd.DataFrame(global_clearing_price_quantity, columns=["quantity"], index=prosumption_function_df.index)
global_clearing_price_df["index"] = prosumption_function_df.index
global_clearing_price_df.index = global_clearing_price_df.index.map(str)


print("local clearing price")
print(local_clearing_price_df)
print("")

print("global clearing price")
print(global_clearing_price_df)
print("")


ax = prosumption_function_df.plot(title="Quantity Depending on the Clearing Price", drawstyle="steps-post")
ax.margins(x=0)

ax2 = local_clearing_price_df.plot(kind="scatter", x="index", y="quantity", c="red", ax=ax)
#ax3 = global_clearing_price_df.plot(kind="scatter", x="index", y="quantity",  c="green", ax=ax2)
plt.axhline(y=0, color='black', linestyle='--', linewidth=0.5)
plt.hlines(y=Negative_Infinite, xmin=Negative_Infinite_x_value - 1, xmax=Negative_Infinite_x_value ,)
plt.hlines(y=Positive_Infinite, xmin=Positive_Infinite_x_value, xmax=Positive_Infinite_x_value + 1 )

ax.legend(["Quantity", "Local Clearing Price"])

ax.set_xlabel("Price in €ct")
ax.set_ylabel("Quantity in kWh")


#ax.legend(ncol=4)



#plt.savefig(fname="Price_Curve.pdf")
#plt.savefig(fname="TradingDistribution.png")
plt.show()