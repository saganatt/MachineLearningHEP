# pylint: disable=missing-function-docstring, invalid-name
"""
file: run-mlhep-fitter-multitrial.py
brief: Prepare MLHEP database files for different fit configurations for multitrial systematics.
usage: python3 run-mlhep-fitter-multitrial.py
author: Maja Karwowska <mkarwowska@cern.ch>, Warsaw University of Technology
"""

import os
import shutil
import yaml

PERM_PATTERN="prompt"

CONFIG="database_ml_parameters_LcToPKPi_multiclass_fdd"
CONFIG_EXT=f"{CONFIG}.yml"
CONFIG_PATH=f"data/data_run3/{CONFIG_EXT}"

SIGMA02="0.007, 0.007, 0.013"
SIGMA23="0.007, 0.007, 0.013"
SIGMA34="0.007, 0.007, 0.012"
SIGMA45="0.008, 0.008, 0.016"
SIGMA56="0.010, 0.010, 0.016"
SIGMA67="0.008, 0.008, 0.017"
SIGMA78="0.012, 0.012, 0.018"
SIGMA810="0.015, 0.012, 0.018"
SIGMA1012="0.010, 0.010, 0.022"
SIGMA1216="0.016, 0.016, 0.029"
SIGMA1624="0.016, 0.016, 0.029"
FREE_SIGMAS=[SIGMA02, SIGMA23, SIGMA34, SIGMA45, SIGMA56, SIGMA67, SIGMA78,
             SIGMA810, SIGMA1012, SIGMA1216, SIGMA1624]

CENTRAL_TRIAL=""

BASE_TRIALS = (
    ["alpha-15%", "alpha+15%"],
    ["n-15%", "n+15%"],
    ["rebin-1", "rebin+1"],
    ["free-sigma"],
    ["poly3"]
)

def generate_trials(trial_classes):
    combinations = [""]
    for trial_class in trial_classes:
        class_comb = []
        for cur_comb in combinations:
            for trial in trial_class:
                class_comb.append(cur_comb + "_" + trial)
                print(f"{cur_comb}_{trial}")
        combinations.extend(class_comb)
    return combinations

def main():
    combinations = generate_trials(BASE_TRIALS)
    
    for trial in combinations:
        print(trial)

        resdir = f"results-24022025-newtrain-multitrial-{PERM_PATTERN}{trial}"
        respath = f"/data8/majak/MLHEP/{resdir}"
        os.makedirs(respath)

        cur_cfg = f"{CONFIG}{trial}.yml"
        shutil.copy2(CONFIG_PATH, cur_cfg)

        with open(cur_cfg, encoding="utf-8") as stream:
            cfg = yaml.safe_load(stream)
            print(f"Old cfg:\n{cfg}")

            ana_cfg = cfg["LcpKpi"]["analysis"]["Run3analysis"]
            fit_cfg = ana_cfg["mass_roofit"]
            mc_cfg = [fit_params for fit_params in fit_cfg \
                      if "level" in fit_params and fit_params["level"] == "mc"]
            data_cfg = [fit_params for fit_params in fit_cfg if not "level" in fit_params]

            if trial == "alpha-15%":
                for pt_cfg in mc_cfg:
                    pass
            elif trial == "alpha+15%":
                for pt_cfg in mc_cfg:
                    pass
            elif trial == "n-15%":
                for pt_cfg in mc_cfg:
                    pass
            elif trial == "n+15%":
                for pt_cfg in mc_cfg:
                    pass
            elif trial == "rebin-1":
                ana_cfg["n_rebin"] = [rebin - 1 for rebin in ana_cfg["n_rebin"]]
            elif trial == "rebin+1":
                ana_cfg["n_rebin"] = [rebin + 1 for rebin in ana_cfg["n_rebin"]]
            elif trial == "free-sigma":
                for pt_cfg, free_sigma in zip(mc_cfg, FREE_SIGMAS):
                    sig_fn = pt_cfg["components"]["sig"]["fn"]
                    # sed sigma_g1 to free_sigma
            elif trial == "poly3":
                for pt_cfg in data_cfg:
                    # add a3[-1e8, 1e8] to bkg fn
                    pass

            print(f"New cfg:\n{cfg}")
            yaml.dump(cfg, stream)


if __name__ == "__main__":
    main()
