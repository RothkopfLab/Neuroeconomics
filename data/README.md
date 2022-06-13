# Data
This data contains experimental and model data.

## Experimental
Experimental data of all subjects is in the [decisions.csv](./decisions.csv) file.
Each line in this file corresponds to one decision / one trial from Fig. 1 of the paper.
Below, explanations for every column:
- `partFile`: unique identifier for the (1 minute block)
- `partName`: unique subject identifier
- `chosenX`, `chosenY`: Screen coordinates (in px) of the chosen 2AFC target
- `notChosenX`, `notChosenY`: Screen coordinates (in px) of the **not** chosen 2AFC target
- `chosenBeforeX`, `chosenBeforeY`: Screen coordinates (in px) of the chosen 2AFC target from the trial before
- `trial`: Trial counter (resetting for each block)
- `ampChosen`, `ampNotChosen`: Amplitude (in px) of the two targets
- `angleChosen`, `angleNotChosen`: Change in direction angle of the two targets
- `angleAbsoluteChosen`, `angleAbsoluteNotChosen`: Direction of the two targets
- `expDate`: unique identifier for the experiment date (first or second)
- `detail_centfix_dur`: Time subjects spent in the center during one trial (in 1/250s timesteps)
- `block_time`: Wall time at the start of the block (mainly to order blocks)

## Model
The posterior chains of the best fitting model (all parameters, lognormal uncertainty) of all subjects are given in the [chains](./chains/) folder. 
They are in `jls` format and be easily read by julia/[Turing](https://github.com/TuringLang/Turing.jl). 
For those only interested in the summary statistics, just see `model_mean_lognormal.csv` and `model_std_lognormal.csv` respectively.