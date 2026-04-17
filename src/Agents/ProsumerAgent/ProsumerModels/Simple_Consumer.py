from .AbstractModel import AbstractModel
import os
from pathlib import Path

class SimpleConsumer(AbstractModel):
    def __init__(self, ID, kwargs):
        # Initialise the model. Here the initial parameter of the model can be defined
        # If you have to read some data from e.g., a csv file. Save this information under input --> YOURCLASSNAME --> your data
        self.ID = ID

        if "quantity" in kwargs.keys():
            self.quantity = kwargs["quantity"]
        else:
            self.quantity = [5] * 96

        return

    # This function is only needed if your prosumer model is a proxy for a lower level Aggregation unit

    async def update_model(self, updates):
        """
        update the model. The information from the energy data identifier, is saved in data. Based on this information
        the local Energy Management System, can adjust its consumption accordingly.
        data: Information of energy data provider --> check for semantics and syntax in the ontology of the energy data identifier
        :return:
        """

        return {"quantity": self.quantity}

