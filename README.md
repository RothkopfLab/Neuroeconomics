# Neuroeconomics of individual differences in saccadic decisions  
This is the official repository for the paper:
> Thomas, T., Hoppe, D., Rothkopf, C. A. (2022). Neuroeconomics of individual differences in saccadic decisions. [bioRxiv](https://www.biorxiv.org/content/10.1101/2022.06.03.494508v1)

## Content
- **Experiment**: In the [experiment](./experiment) folder, you can find the original experiment script, which was used to conduct the experiment.
*Warining*: Since the experiment was conducted quite a while ago, the code might not work with today's versions of the used packages.
- **Model Estimation**: We also provide code to estimate the models described in the paper.
Installation and Usage is described below.
- **Data**: In the [data](./data) folder, we provide two things.
First, the raw data of our subjects and second, the model parameter posterior samples from our subjects. 
- **Analysis**: Code to analyze our data and produce most of the paper plots (and many more) are in [this](./Analysis.ipynb) jupyter notebook.

## Model Estimation
### Installation
Model code is written in julia (1.7.0).  
It can just be installed by running `using Pkg; Pkg.instantiate()` inside julia and the root folder of this project.

### Usage
NEEM (**N**ero**E**conomics of **E**ye**M**ovements) currently only exports a single function. Its usage is shown below.
```julia
julia> using NEEM, CSV, DataFrames 

julia> decisions = CSV.File("path/to/decisions.csv") |> DataFrame

julia> chain = sample_single_subject_lognormal(decisions, "subject_id")
```
Chain is now a single Hamiltonian Monte Carlo chain of posterior samples over all parameters of this single subject.