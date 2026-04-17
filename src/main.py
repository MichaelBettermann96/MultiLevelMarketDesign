import Tests as t

from src.utils import Logger as lg
from src.utils.Logger import Info

if __name__ == "__main__":
    lg.Debug = True  # Turn it off to not get the Debugging messages (Info, Warnings and Values)
    Info("starting simulation")
    #t.Test_MultiLevel_main()
    t.Test_MultiLevel_Simbench_main()
    Info("ending simulation")