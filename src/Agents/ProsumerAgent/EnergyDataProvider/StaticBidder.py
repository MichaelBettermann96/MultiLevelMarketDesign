import pandas as pd

from .AbstractEnergyDataProvider import AbstractEnergyDataProvider
import os
from pathlib import Path


class StaticBidder(AbstractEnergyDataProvider):
    def __init__(self,
                 ID,
                 kwargs: dict = {}
                 ):
        super().__init__(ID=ID)
        self.__coordinator_results = {}

        if "selling_price" in kwargs:
            self.__injection_price = kwargs["selling_price"]
        else:
            self.__injection_price = [-1] * 96

        if "buying_price" in kwargs:
            self.__consumption_price = kwargs["buying_price"]
        else:
            self.__consumption_price = [-1] * 96

    @property
    def coordinator_results(self):
        return self.__coordinator_results

    @coordinator_results.setter
    def coordinator_results(self, value):
        self.__coordinator_results = value
        # if coordinator_results are not None, save the results
        if self.__coordinator_results:
            self.__save_results(results=self.__coordinator_results)
        return

    async def get_energy_data_provider_information(self):
        """
        Function that uses the results of the coordinator to preprocess the information and send it to the prosumer agent.
        The prosumer model uses this information.
        :param coordinator_results: Results of the Coordinator
        :return: Some information that is sent to the prosumer model
        """


        # If there is no response yet from the coordinator --> send your bid
        if not self.__coordinator_results:
            return {"consumption_prices": self.__consumption_price, "injection_prices": self.__injection_price}
        # if there is a response save the results and provide to the prosumer model the response of the coordinator
        else:
            return {"clearing_price": self.__coordinator_results}

    def __save_results(self, results):
        path = str(Path(os.path.dirname(__file__)).parents[0])
        Path(path + "/EnergyDataProvider/output/StaticBidder/Client_" + str(self.ID)).mkdir(parents=True, exist_ok=True)
        path = path + "/EnergyDataProvider/output/StaticBidder/Client_" + str(self.ID) + "/Client_" + str(self.ID) + ".csv"
        df = pd.DataFrame(data={"costs": results})
        df.to_csv(path)

        return



    def form_coordinator_information(self, prosumer_model_information):
        """
        This methods purpose is to form the prosumer_model_information so the coordinator understands the message
        :param prosumer_model_information: information of the prosumer model.
        :return:
        """
        self.__quantity = prosumer_model_information["quantity"]

        bids = {"quantity": prosumer_model_information["quantity"],
                "price": [self.__consumption_price[i] if q >= 0
                else self.__injection_price[i] for i, q in
                enumerate(prosumer_model_information["quantity"])] }



        return bids