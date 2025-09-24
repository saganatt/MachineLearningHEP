#############################################################################
##  © Copyright CERN 2018. All rights not expressly granted are reserved.  ##
##                 Author: Gian.Michele.Innocenti@cern.ch                  ##
## This program is free software: you can redistribute it and/or modify it ##
##  under the terms of the GNU General Public License as published by the  ##
## Free Software Foundation, either version 3 of the License, or (at your  ##
## option) any later version. This program is distributed in the hope that ##
##  it will be useful, but WITHOUT ANY WARRANTY; without even the implied  ##
##     warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    ##
##           See the GNU General Public License for more details.          ##
##    You should have received a copy of the GNU General Public License    ##
##   along with this program. if not, see <https://www.gnu.org/licenses/>. ##
#############################################################################

"""
Methods to: utility methods to conpute efficiency and study expected significance
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator
from matplotlib.colors import LogNorm
from ROOT import TH1F, TFile  # pylint: disable=import-error,no-name-in-module

from machine_learning_hep.logger import get_logger


def select_by_threshold(df_label, label, thr, name):
    # Changed from >= to > since we use that atm for the nominal selection
    # See processer.py self.l_selml
    label = label.replace("-", "_")
    if label == "bkg":
        return df_label[df_label[f"y_test_prob{name}{label}"].values <= thr]
    if label == "":
        return df_label[df_label[f"y_test_prob{name}{label}"].values > thr]
    return df_label[df_label[f"y_test_prob{name}{label}"].values >= thr]


def get_x_axis(num_steps):
    ns_left = int(num_steps / 10) - 1
    ns_right = num_steps - ns_left
    x_axis_left = np.linspace(0., 0.49, ns_left)
    x_axis_right = np.linspace(0.5, 1.0, ns_right)
    x_axis = np.concatenate((x_axis_left, x_axis_right))
    return x_axis

def get_x_y_axis(thr_args, num_steps):
    x_axis = np.linspace(thr_args["x_min"], thr_args["x_max"], num_steps)
    y_axis = np.linspace(thr_args["y_min"], thr_args["y_max"], num_steps)
    return x_axis, y_axis

def get_axis_label_for_mltype(mltype, threshold_args, num_steps):
    if mltype == "MultiClassification":
        x_axis, y_axis = get_x_y_axis(threshold_args, num_steps)
        return x_axis, y_axis, "bkg"
    x_axis = get_x_axis(num_steps)
    return x_axis, None, ""

def calc_bkg(df_bkg, name, threshold_args, num_steps, fit_region, bkg_func, bin_width, sig_region, save_fit, #pylint: disable=too-many-arguments
             out_dir, pt_lims, invmassvar, mltype, label):
    """
    Estimate the number of background candidates under the signal peak. This is obtained
    from real data with a fit of the sidebands of the invariant mass distribution.
    """
    logger = get_logger()
    num_bins = (fit_region[1] - fit_region[0]) / bin_width
    num_bins = int(round(num_bins))
    bin_width = (fit_region[1] - fit_region[0]) / num_bins
    x_axis, y_axis, class_label = get_axis_label_for_mltype(mltype, threshold_args[label], num_steps)

    if save_fit:
        logger.debug("Saving bkg fits to file")
        pt_min = pt_lims[0]
        pt_max = pt_lims[1]
        out_file = TFile(f"{out_dir}/bkg_fits_{name}_pt{pt_min:.1f}_{pt_max:.1f}.root", "recreate")
        out_file.cd()

    def bkg_for_threshold(sel_mass_array, thr, thr2 = ""):
        hmass = TH1F(f'hmass_{thr:.5f}_{thr2:.5f}', '', num_bins, fit_region[0], fit_region[1])
        bkg = 0.
        bkg_err = 0.
        if len(sel_mass_array) > 5:
            for mass_value in np.nditer(sel_mass_array):
                hmass.Fill(mass_value)
            fit = hmass.Fit(bkg_func, "Q", "", fit_region[0], fit_region[1])
            if save_fit:
                hmass.Write()
            if int(fit) == 0:
                fit_func = hmass.GetFunction(bkg_func)
                bkg = fit_func.Integral(sig_region[0], sig_region[1]) / bin_width
                bkg_err = fit_func.IntegralError(sig_region[0], sig_region[1]) / bin_width
                del fit_func
        elif save_fit:
            hmass.Write()
        del hmass
        return bkg, bkg_err

    bkg_array = []
    bkg_err_array = []
    logger.debug("To fit the bkg a %s function is used", bkg_func)
    for thr in x_axis:
        df_bkg_sel = select_by_threshold(df_bkg, class_label, thr, name)
        if mltype == "MultiClassification":
            for thr2 in y_axis:
                df_bkg_sel2 = select_by_threshold(df_bkg_sel, label, thr2, name)
                sel_mass_array = df_bkg_sel2[invmassvar].values
                bkg, bkg_err = bkg_for_threshold(sel_mass_array, thr, thr2)
                bkg_array.append(bkg)
                bkg_err_array.append(bkg_err)
        else:
            sel_mass_array = df_bkg_sel[invmassvar].values
            bkg, bkg_err = bkg_for_threshold(sel_mass_array, thr)
            bkg_array.append(bkg)
            bkg_err_array.append(bkg_err)

    out_file.Close()
    return bkg_array, bkg_err_array, x_axis, y_axis

def calc_signif(sig_array, sig_err_array, bkg_array, bkg_err_array):
    """
    Calculate the expected signal significance as a function of the treshold on the
    ML model output.
    """
    signif_array = []
    signif_err_array = []

    for sig, bkg, sig_err, bkg_err in zip(sig_array, bkg_array, sig_err_array, bkg_err_array):
        signif = 0.0
        signif_err = 0.0

        if sig > 0 and (sig + bkg) > 0:
            signif = sig / np.sqrt(sig + bkg)
            signif_err = signif * np.sqrt((sig_err**2 + bkg_err**2) / (4 * (sig + bkg)**2) + \
                         (bkg / (sig + bkg)) * sig_err**2 / sig**2)
            print(f"significance > 0: {signif}")
        else:
            print("significance 0")

        signif_array.append(signif)
        signif_err_array.append(signif_err)

    return signif_array, signif_err_array

def calc_eff(num, den):
    eff = num / den
    eff_err = np.sqrt(eff * (1 - eff) / den)

    return eff, eff_err

def calc_sigeff_steps(threshold_args, num_steps, df_sig, name, mltype, label):
    logger = get_logger()
    x_axis, y_axis, class_label = get_axis_label_for_mltype(mltype, threshold_args[label], num_steps)
    if df_sig.empty:
        logger.error("In division denominator is empty")
        if mltype == "MultiClassification":
            eff_array = [0] * len(y_axis) * len(x_axis)
            eff_err_array = [0] * len(y_axis) * len(x_axis)
        else:
            eff_array = [0] * len(x_axis)
            eff_err_array = [0] * len(x_axis)
        return eff_array, eff_err_array, x_axis, y_axis
    num_tot_cand = len(df_sig)
    eff_array = []
    eff_err_array = []
    for thr in x_axis:
        df_sig_sel = select_by_threshold(df_sig, class_label, thr, name)
        num_sel_cand = len(df_sig_sel)
        if mltype == "MultiClassification":
            for thr2 in y_axis:
                num_sel_cand2 = len(select_by_threshold(df_sig_sel, label, thr2, name))
                eff, err_eff = calc_eff(num_sel_cand2, num_tot_cand)
                eff_array.append(eff)
                eff_err_array.append(err_eff)
        else:
            num_sel_cand = len(select_by_threshold(df_sig, class_label, thr, name))
            eff, err_eff = calc_eff(num_sel_cand, num_tot_cand)
            eff_array.append(eff)
            eff_err_array.append(err_eff)

    return eff_array, eff_err_array, x_axis, y_axis

def prepare_eff_signif_figure(var_label, mltype, class_label):
    fig = plt.figure(figsize=(20, 15))
    ax = plt.subplot(1, 1, 1)
    if mltype == "MultiClassification":
        ax.set_xlabel("Score for bkg hyp. <=", fontsize=30)
        ax.set_ylabel(f"Score for {class_label} hyp. >=", fontsize=30)
        ax.tick_params(labelsize=20)
    else:
        ax.set_xlabel("Score for prompt hyp. >", fontsize=30)
        ax.set_ylabel(var_label, fontsize=30)
        ax.xaxis.set_major_locator(MultipleLocator(0.1))
        ax.set_xlim(0.0, 1.0)
        plt.yticks([])
        ax.tick_params(labelsize=20)
    return fig

def plot_heatmap(data, y_label, threshold_args, log_scale=False):
    print(f"Plotting heatmap for data:\n{data}")
    ax = plt.gca()
    norm = LogNorm() if log_scale else None
    im = ax.imshow(data, cmap="cividis", interpolation="none", origin="lower",
                   extent=(threshold_args["x_min"], threshold_args["x_max"],
                           threshold_args["y_min"], threshold_args["y_max"]),
                   norm=norm)
    ax.set_aspect((threshold_args["x_max"] - threshold_args["x_min"]) /\
                  (threshold_args["y_max"] - threshold_args["y_min"]))
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel(y_label, rotation=90, va="top", fontsize=30, labelpad=15)
    cbar.ax.tick_params(labelsize=20)
