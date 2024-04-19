import numpy as np
import pandas as pd
import ROOT

RHIST = {1: ROOT.TH1F, 2: ROOT.TH2F, 3: ROOT.TH3F, 4: ROOT.THnF}

def bin_spec(nbins, low, high):
    return np.linspace(low, high, nbins + 1, 'd')


# FIXME: clean up
def create_hist(name, title, *bin_specs):
    """Create ROOT histogram from standard bin specifications or arrays"""
    var_bins = [hasattr(spec, '__len__') for spec in bin_specs]
    assert all(var_bins) or not any(var_bins), f'either all bins must be variable or fixed width: {bin_specs=}'
    dim = len(bin_specs) if all(var_bins) else len(bin_specs) / 3
    assert dim in range(1, 10), 'only dimensions from 1 to 10 are supported'
    if all(var_bins):
        nbins = list(map(lambda a: len(a) - 1, bin_specs))
        if dim <= 3:
            bin_defs = zip(nbins, bin_specs)
            bin_specs = [arg for axis in bin_defs for arg in axis]
    if dim <= 3:
        return RHIST[min(dim, 4)](name, title, *bin_specs)
    else:
        nbins = np.asarray(nbins, 'i')
        return RHIST[min(dim, 4)](name, title, dim, nbins, bin_specs)


# TODO: generalize which columns can contain arrays
def fill_hist(hist, dfi: pd.DataFrame, weights = None, arraycols = False, write = False):
    """
    Fill histogram from dataframe

    :param hist: ROOT.TH1,2,3
    :param dfi: pandas series/dataframe (1 to 3 columns)
    :param weights: weights per row
    :param array: dataframe contains arrays
    :param write: call Write() after filling
    """
    dim_hist = hist.GetDimension() if isinstance(hist, ROOT.TH1) else hist.GetNdimensions()
    dim_df = dfi.shape[1] if dfi.ndim > 1 else dfi.ndim
    assert dim_df in range(1, 10), f'{dim_df} not supported'
    assert dim_df == dim_hist, 'dimensions of df and histogram do not match'
    if len(dfi) == 0:
        return
    if dim_hist == 1:
        if not arraycols:
            hist.FillN(len(dfi), np.float64(dfi), weights or ROOT.nullptr)
        else:
            dfi.apply(lambda row: [hist.Fill(v) for v in row])
    elif dim_hist == 2:
        if not arraycols:
            hist.FillN(len(dfi), np.float64(dfi.iloc[:, 0]), np.float64(dfi.iloc[:, 1]), weights or ROOT.nullptr)
        else:
            assert weights is None, 'weights not supported'
            dfi.apply(lambda row: [hist.Fill(row.iloc[0], v) for v in row.iloc[1]], axis=1)
    elif dim_hist == 3:
        # TODO: why does TH3 not support FillN?
        # hist.FillN(len(dfi), np.float64(dfi.iloc[:, 0]), np.float64(dfi.iloc[:, 1]), np.float64(dfi.iloc[:, 2]),
        #            weights or np.float64(len(dfi)*[1.]))
        assert weights is None, 'weights not supported'
        if not arraycols:
            dfi.apply(lambda row: hist.Fill(row.iloc[0], row.iloc[1], row.iloc[2]), axis=1)
        else:
            dfi.apply(lambda row: [hist.Fill(row.iloc[0], v[0], v[1]) for v in zip(row.iloc[1], row.iloc[2])], axis=1)
    elif dim_hist > 3:
        assert weights is None, 'weights not supported'
        assert not arraycols
        if not arraycols:
            dfi.apply(lambda row: hist.Fill(*row), axis=1)
    if write:
        hist.Write()


def scale_bin(hist, factor, *bin_indices):
    """Scale histogram bin-wise by given factor"""
    hist.SetBinContent(*bin_indices, hist.GetBinContent(*bin_indices) * factor)
    hist.SetBinError(*bin_indices, hist.GetBinError(*bin_indices) * factor)


def sum_hists(histos, name = None):
    """
    Return histogram with sum of all histograms from iterable
    """
    hist = None
    for h in histos:
        if h is None:
            continue
        if hist is None:
            hist = h.Clone(name or (h.GetName() + '_cloned'))
        else:
            hist.Add(h)
    return hist
