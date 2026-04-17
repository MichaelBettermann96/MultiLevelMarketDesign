from pandapower.control import ConstControl
from .....utils.Logger import Warning, Info, Fail, Print_Values
from pandapower.timeseries import DFData

# Enhancmenet of the pandapower ConstContoller to allow to change the datasource for the next simulation
class Controller(ConstControl):
    def __init__(self,
                 net,
                 element,
                 variable,
                 element_index,
                 data_source,
                 profile_name):
        # this is Dataframe before converting it to DFData. This is so the data_source can be changed.
        # it is essentially a copy of data_source, but in a different format to handle an update
        self.element = element
        self.data = data_source
        print("OG_datasource")
        print(data_source)

        super().__init__(net=net, element=element, variable=variable, element_index=element_index,
             data_source=DFData(data_source), profile_name=profile_name, order=1, level=1)

        return

    def update_datasource(self, datasource, node_ID):
        """
        Update the datasource to allow for the simulation in the next timestep
        :param datasource: data that needs to be updated
        :param node_ID: Identifier of the node that needs to be updated
        :return:
        """
        # first update self.data, so it can be updated and allows us to replace the data_source
        #if self.element == "load":
        #    Fail("Controller datasource before for Client {}:".format(node_ID))
        #    Warning("self.data")
        #    Print_Values(self.data)
        #    Warning("self.datasource")
        #    Print_Values(self.data_source.get_time_step_value(time_step=1, profile_name=node_ID))

        if node_ID in self.data.columns:
            self.data[node_ID] = datasource
            self.data_source = DFData(self.data)
        else:
            raise Exception("the proposed node_ID ({}) is not in the data_source".format(node_ID))

        #if self.element == "sgen":
            #Fail("Controller datasource after for Client {}:".format(node_ID))
            #self.data[24][2] = 5
            #Warning("self.data")
            #Print_Values(self.data)
            #Warning("self.datasource")
            #Print_Values(self.data_source.get_time_step_value(time_step=0, profile_name=[node_ID]))
        #if node_ID == 1:
        #    print("Updated Data of the Controller")
        #    print(self.data)

        return

