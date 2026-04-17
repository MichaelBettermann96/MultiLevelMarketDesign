# Towards a Power Grid-Aware Electricity Market System - A Multi-Level Market Design

 *by Michael Betterman and Hermann de Meer*
Submitted to ACM SIGENERGY Energy Informatics Review  


# This repository contains the code and data accompanying the paper:
> **Towards a Power Grid-Aware Electricity Market System - A Multi-Level Market Design**
>
> Accepted at * - *
> [Link to paper]()

 
🚀 **Overview**

This repository provides a simulation tool for the simulation of local aggregation approaches (see [Bettermann25](https://dl.acm.org/doi/abs/10.1145/3757888.3757891)) as well as the implementation of the results shown in the paper *Towards a Power Grid-Aware Electricity Market System - A Multi-Level Market Design*.
The repository contains an implementation of a multi-level market design utilising data from simbench to model consumer, generator and the hierarchy of the network.

## 📂 Repository Structure
### **Agents**
- **`CoordinatorAgent/`**: Contains the implementation of the respective Coordinator and the Coordinator Agent encapsulating the implemented Coordinator
- **`DSOAgent/`**: Contains the implementation of the respective GridDataProvider and NetworkSimulator. 
- - **`DSOAgent/GridDataProvider`**: Contains an implementation of a module forwarding processed powernetwork related information
- - **`DSOAgent/NetworkSimulator`**: Contains an implementation of a module simulating the power grid (allows for Powerflow simulations)
- **`ProsumerAgent/`**: Contains the implementation of the respective Prosumer Model and EnergyDataProvider.
- - **`DSOAgent/GridDataProvider`**: Contains an implementation of a module forwarding processed prosumer model related information
- - **`DSOAgent/NetworkSimulator`**: Contains an implementation of a module simulating the local Energy System
- **`ExternalAgent/`**: Contains the implementation of the respective External Communication. Can be used to establish communication between multiple Aggregation Units 

### **Tests**
- **`Test_Multilevel/`**: Contains the implementation of a simple version a multi-level market design 
- **`Test_Multilevel_Simbench/`**: Contains the implementation of a more sophisticated version utilising a high-voltage grid from the simbench dataset

### **Other Files**
- **`requirements.txt`**: Contains the Python dependencies required to run the project.

---

## 💻 Requirements
The code has been tested with Python 3.9

---

## Changelog
17.04.2025: Upload of the initial version 
---

## 🌟 Contributors
Michael Bettermann

