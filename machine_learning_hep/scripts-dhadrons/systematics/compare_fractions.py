# pylint: disable=missing-function-docstring
"""
file:  compare_fractions.py
brief: Compare non-prompt corrected fractions for the systematic uncertainties analysis.
usage: python3 compare_fractions.py config_compare_fractions.json
author: Maja Karwowska <mkarwowska@cern.ch>, Warsaw University of Technology
"""

import argparse
import json
import math
import os
from array import array

from ROOT import (  # pylint: disable=import-error,no-name-in-module
    TCanvas,
    TFile,
    TGraphAsymmErrors,
    TH1F,
    TLegend,
    TPaveText,
    TLine,
    TPad,
    gROOT,
    gStyle,
    kAzure,
    kBlack,
    kBlue,
    kCyan,
    kDashed,
    kGray,
    kGreen,
    kMagenta,
    kOrange,
    kRed,
    kTeal,
    kYellow,
    kFullCircle,
    kFullSquare,
    kFullTriangleUp,
    kOpenCircle,
    kOpenSquare,
    kOpenTriangleUp,
)


COLORS=[kBlack, kRed-3, kAzure-7, kGreen+2, kOrange-3, kBlue, kMagenta+2, kTeal+3, kGreen, kAzure+8,
        kYellow+3, kOrange-5, kMagenta+2, kBlue-6, kCyan+1, kGreen-6]
MODELS_COLORS=[kGray+1, kOrange-3, kCyan-2, kRed-9, kAzure-9]
MODELS_STYLES=[3245, 3250, 3244, 3254, 3209]
HIST_STYLES=[kFullCircle, kFullSquare, kFullTriangleUp, kOpenCircle, kOpenSquare, kOpenTriangleUp]


def get_alice_text(alice_text_config):
    alice_text = TPaveText(0.24, 0.68, 0.60, 0.90, "brNDC")
    alice_text.SetTextFont(42)
    alice_text.SetTextSize(0.045)
    alice_text.SetBorderSize(0)
    alice_text.SetFillStyle(0)
    alice_text.SetTextAlign(11)

    alice_text.AddText("#scale[1.40]{This Thesis}")
    alice_text.AddText(f"#scale[1.30]{{{alice_text_config}}}")
    alice_text.AddText("#scale[1.30]{pp, |#kern[0.06]{#it{y}| < 0.5}}")

    return alice_text


def get_legend(x_1, y_1, x_2, y_2, num_hists, header = None):
    leg = TLegend(x_1, y_1, x_2, y_2)
    if num_hists > 4:
        leg.SetNColumns(2)
    if header:
        leg.SetHeader(header)
    leg.SetTextAlign(12) #13)
    leg.SetTextSize(0.05)
    leg.SetMargin(0.1)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    return leg

def prepare_canvas(cname, logy):
    canv = TCanvas(cname, "", 443, 100, 700, 700)
    canv.Range(0, 0, 1, 1)
    #canv.SetLeftMargin(0.15)
    #canv.SetBottomMargin(0.15)

    canv_top = TPad(f"{cname}_top", "", 0.01, 0.3, 0.99, 0.99)
    if logy:
        canv_top.SetLogy()
    canv_top.SetTickx(1)
    canv_top.SetTicky(1)
    canv_top.SetLeftMargin(0.20)
    canv_top.SetRightMargin(0.02)
    canv_top.SetBottomMargin(0.0)
    canv_top.SetTopMargin(0.05)

    canv.Modified()
    canv.cd()
    canvr = TPad(f"{cname}_ratio", "", 0.01, 0.01, 0.99, 0.3)
    canvr.SetBottomMargin(0.35)
    canvr.SetLeftMargin(0.20)
    canvr.SetRightMargin(0.02)
    canvr.SetTopMargin(0.0)

    for canvas in (canv, canv_top, canvr):
        canvas.SetFillColor(0)
        canvas.SetBorderMode(0)
        canvas.SetBorderSize(2)
        canvas.SetFrameBorderMode(0)
        canvas.SetTickx(1)
        canvas.SetTicky(1)
    canvr.Draw()
    canv_top.cd()
    canv_top.Draw()

    return canv, canv_top, canvr


def save_canvas(canv, cfg, filename):
    for ext in ("png", "pdf"):
        canv.SaveAs(os.path.join(cfg["output"]["outdir"], f"{filename}.{ext}"))


def combine_syst_errors(syst_errors, value):
    err = 0.0
    err_perc = 0.0
    for syst in syst_errors:
        err += syst * syst
        err_perc += (100 * syst) * (100 * syst)
    err_perc = math.sqrt(err_perc)
    print(f"Combined percentage error: {err_perc:0.0f}")
    return math.sqrt(err) * value


def get_hist_limits(hist, graph_syst = None, miny = 0.0, maxy = 0.0):
    for binn in range(0, hist.GetNbinsX()):
        print(f"bin {binn + 1} [{hist.GetXaxis().GetBinLowEdge(binn + 1)}, "\
              f"{hist.GetXaxis().GetBinLowEdge(binn + 2)}) val {hist.GetBinContent(binn + 1)} "\
              f"err {hist.GetBinError(binn + 1)}")
        maxval = hist.GetBinContent(binn + 1) + hist.GetBinError(binn + 1)
        minval = hist.GetBinContent(binn + 1) - hist.GetBinError(binn + 1)
        if graph_syst:
            maxval = max(maxval, hist.GetBinContent(binn + 1) + graph_syst.GetErrorY(binn))
            minval = min(minval, hist.GetBinContent(binn + 1) - graph_syst.GetErrorY(binn))
        maxy = max(maxval, maxy)
        miny = min(minval, miny)
    return miny, maxy


def merge_fractions(inputdir, histname, filenames):
    with TFile.Open(os.path.join(inputdir, filenames[0])) as fin:
        reshist = fin.Get(histname).Clone()
        reshist.SetDirectory(0)

    for ind, file in enumerate(filenames[1:]):
        ind += 1
        with TFile.Open(os.path.join(inputdir, file)) as fin:
            hist = fin.Get(histname)
            reshist.SetBinContent(ind + 1, hist.GetBinContent(ind + 1))
            reshist.SetBinError(ind + 1, hist.GetBinError(ind + 1))

    return reshist


def set_hist_style(hist, color, y_axis, style=None):
    hist.GetYaxis().SetLabelFont(42)
    hist.GetXaxis().SetLabelFont(42)
    hist.GetYaxis().SetTitleFont(42)
    hist.GetXaxis().SetTitleFont(42)
    hist.GetYaxis().SetTitleSize(0.06)
    hist.GetYaxis().SetTitleOffset(1.4)
    hist.GetYaxis().SetLabelSize(0.06)
    hist.GetYaxis().SetLabelOffset(0.02)
    hist.GetXaxis().SetTitleSize(0.05)
    hist.GetXaxis().SetTitleOffset(1.0)
    hist.GetXaxis().SetLabelSize(0.07)
    hist.GetXaxis().SetLabelOffset(0.02)
    #hist.GetXaxis().SetNdivisions(808)
    hist.SetLineColor(color)
    hist.SetLineWidth(2)
    hist.GetXaxis().SetTitle("#it{p}_{T}(GeV/#it{c})")
    hist.GetYaxis().SetTitle(y_axis)
    
    if style:
        hist.SetFillColor(color)
        hist.SetFillStyle(style)
    else:
        hist.SetMarkerColor(color)
        hist.SetMarkerSize(1)
        hist.SetMarkerStyle(21)


def get_hist_for_label(label, color, cfg, style):
    if len(cfg["hists"][label]["file"]) == 1:
        with TFile.Open(os.path.join(cfg["inputdir"], cfg["hists"][label]["file"][0])) as fin:
            hist = fin.Get(cfg["histoname"])
            hist.SetDirectory(0)
    else:
        print(f"Merging histograms for {label}")
        hist = merge_fractions(cfg["inputdir"], cfg["histoname"], cfg["hists"][label]["file"])

    set_hist_style(hist, color, cfg["y_axis"])
    return hist


def get_graph_systematics(hist, label, color, cfg, style):
    if isinstance(cfg["hists"][label]["systematics"][0], str):
        with TFile.Open(os.path.join(cfg["inputdir"], \
                cfg["hists"][label]["systematics"][0])) as fin:
            graph_syst = fin.Get(cfg["hists"][label]["systematics"][1])
    else:
        graph_syst = TGraphAsymmErrors()
        graph_syst.SetName(f"graph_{label}_syst")
        for binn in range(hist.GetNbinsX()):
            syst_err = combine_syst_errors(cfg["hists"][label]["systematics"][binn],
                                               hist.GetBinContent(binn + 1))
            print(f"Syst error {label} bin {binn + 1} {syst_err}")
            x_point = hist.GetBinCenter(binn + 1)
            y_point = hist.GetBinContent(binn + 1)
            x_width = hist.GetBinWidth(binn + 1) / 4.0
            if y_point != 0:
                graph_syst.SetPoint(binn, x_point, y_point)
                graph_syst.SetPointError(binn, x_width, x_width, syst_err, syst_err)
    set_hist_style(graph_syst, color, cfg["y_axis"])
    graph_syst.SetFillStyle(0)
    return graph_syst


def get_hist_model(label, color, style, cfg):
    with TFile.Open(os.path.join(cfg["inputdir"], cfg["models"][label]["file"])) as fin:
        hist = fin.Get(cfg["models"][label]["histoname"])
        hist.SetDirectory(0)

    #hist.SetFillColor(color)
    #hist.SetFillStyle(style)
    #hist.SetTitle("")
    set_hist_style(hist, color, cfg["y_axis"], style)

    return hist


def plot_compare(cfg, canv_main, canv):
    maxy = 0.
    miny = 1000000.

    hists_models = []
    if cfg.get("models", None):
        leg_models = get_legend(*cfg["legend_models"], len(cfg["models"]))
        leg_models.SetMargin(0.2)
        leg_models.SetTextSize(0.05)
        leg = get_legend(*cfg["legend"], len(cfg["hists"]))
        for ind, (label, color, style) in \
                enumerate(zip(cfg["models"], MODELS_COLORS, MODELS_STYLES)):
            hist = get_hist_model(label, color, style, cfg)
            miny, maxy = get_hist_limits(hist, None, miny, maxy)

            canv.cd()
            draw_opt = "sameE3" if ind != 0 else "E3"
            hist.Draw(draw_opt)
            leg_models.AddEntry(hist, label, "f")

            hists_models.append(hist)
    else:
        #leg = get_legend(0.17, 0.58, 0.65, 0.70, len(cfg["hists"]))
        leg = get_legend(*cfg["legend"], len(cfg["hists"]))
        #                 "Prompt #kern[-0.5]{#Lambda_{c}^{#plus}}")
        leg_models = None

    hists = {}
    graphs_syst = []
    central_graph = None
    for ind, (label, color, style) in enumerate(zip(cfg["hists"], COLORS, HIST_STYLES)):
        print(f"histogram {label} style {style}")
        hist = get_hist_for_label(label, color, cfg, style)
        print(label)
        miny, maxy = get_hist_limits(hist, None, miny, maxy)

        canv.cd()
        draw_opt = "sameE" if ind != 0 or len(hists_models) > 0 else "E"
        hist.Draw(draw_opt)
        leg.AddEntry(hist, label, "p")

        hists[label] = hist

        if cfg["hists"][label].get("systematics", None):
            print("Plotting systematic")
            graph_syst = get_graph_systematics(hist, label, color, cfg, style)
            miny, maxy = get_hist_limits(hist, graph_syst, miny, maxy)
            graph_syst.Draw("sameE2")
            graphs_syst.append(graph_syst)
            if label == cfg["default"]:
                central_graph = graph_syst

    margin = 1.0
    #k = 1.0 - 2 * margin
    #rangey = maxy - miny
    #miny = miny - margin / k * rangey
    #maxy = maxy + margin / k * rangey
    print(f"Hist maxy: {maxy} miny: {miny}")
    #miny = min(miny - margin * miny, 0)
    miny = miny - margin * miny
    if miny <= 0:
        miny = 0.006
    maxy = 0.4
    print(f"Recalculated hist maxy: {maxy + margin * maxy} miny: {miny}")
    for hist_models in hists_models:
        hist_models.GetYaxis().SetRangeUser(miny, maxy) # + margin * maxy)
    for _, hist in hists.items():
        hist.GetYaxis().SetRangeUser(miny, maxy) # + margin * maxy)
    for graph_syst in graphs_syst:
        graph_syst.GetYaxis().SetRangeUser(miny, maxy) # + margin * maxy)

    leg.Draw()
    if len(hists_models) > 0:
        leg_models.Draw()

    if "alice_text" in cfg:
        alice_text = get_alice_text(cfg["alice_text"])
        alice_text.Draw("same")
    else:
        alice_text = None

    canv_main.cd()
    canv.Draw()
    canv_main.Draw()

    return canv_main, canv, hists, graphs_syst, hists_models, leg, leg_models, alice_text, central_graph


def get_average(hist, graph_syst):
    width_combined = hist.GetBinWidth(hist.GetNbinsX() -1) + hist.GetBinWidth(hist.GetNbinsX())
    val = ((hist.GetBinContent(hist.GetNbinsX() - 1) * hist.GetBinWidth(hist.GetNbinsX() - 1) +\
            hist.GetBinContent(hist.GetNbinsX()) * hist.GetBinWidth(hist.GetNbinsX())) /\
            width_combined)
    err = math.sqrt((hist.GetBinError(hist.GetNbinsX() - 1) *\
                     hist.GetBinWidth(hist.GetNbinsX() - 1) /\
                     width_combined) **2  +\
                    (hist.GetBinError(hist.GetNbinsX()) *\
                     hist.GetBinWidth(hist.GetNbinsX()) /\
                     width_combined) ** 2)
    syst_err = math.sqrt((graph_syst.GetErrorYlow(hist.GetNbinsX() - 2) *\
                          hist.GetBinWidth(hist.GetNbinsX() - 1) /\
                          width_combined) **2  +\
                         (graph_syst.GetErrorYlow(hist.GetNbinsX() - 1) *\
                          hist.GetBinWidth(hist.GetNbinsX()) /\
                          width_combined) ** 2)
    return val, err, syst_err


def hist_for_ratio(hist, graph, central_hist):
    print(f"central hist: {central_hist}")
    hist2 = TH1F(hist.GetName(), "", central_hist.GetNbinsX(),
                 array('d', central_hist.GetXaxis().GetXbins()))
    graph2 = TGraphAsymmErrors()
    for binn in range(central_hist.GetNbinsX() - 1):
        hist2.SetBinContent(binn + 1, hist.GetBinContent(binn + 1))
        hist2.SetBinError(binn + 1, hist.GetBinError(binn + 1))
        graph2.SetPoint(binn, graph.GetPointX(binn), graph.GetPointY(binn))
        graph2.SetPointError(binn, graph.GetErrorXlow(binn), graph.GetErrorXhigh(binn),
                             graph.GetErrorYlow(binn), graph.GetErrorYhigh(binn))
    val, err, syst_err = get_average(hist, graph)
    hist2.SetBinContent(hist2.GetNbinsX(), val)
    hist2.SetBinError(hist2.GetNbinsX(), err)
    graph2.SetPoint(hist2.GetNbinsX() - 1, hist2.GetBinCenter(hist2.GetNbinsX()), val)
    x_err = hist2.GetBinWidth(hist2.GetNbinsX()) / 4.0
    graph2.SetPointError(hist2.GetNbinsX() - 1, x_err, x_err, syst_err, syst_err)
    return hist2, graph2


def divide_syst_error(val, val1, val2, err1, err2, hist, binn):
    return val * math.sqrt((err1 / val1) **2 + (err2 / val2) **2)


def plot_ratio(cfg, hists, graphs_syst, central_graph, canv, canvr):
    legr = get_legend(*cfg["legend_ratio"], len(cfg["hists"]))

    histsr = []
    graphsr = []
    miny = 0.01
    maxy = 3.0
    maxx = 0.0
    central_hist = hists[cfg["default"]]
    for ind, (label, graph, color, style) in enumerate(zip(hists, graphs_syst, COLORS, HIST_STYLES)):
        print(f"central hist bins: {central_hist.GetNbinsX()} "\
              f"{label} bins: {hists[label].GetNbinsX()}")
        if label != cfg["default"]: #and hists[label].GetNbinsX() == central_hist.GetNbinsX():
            print("Doing ratio")
            hist_ratio, graph_ratio = hist_for_ratio(hists[label], graph, central_hist)
            histr = hist_ratio.Clone()
            histr.Divide(hist_ratio, central_hist, 1., 1., "B")
            histr.SetName(f"h_ratio_{label}")
            histr.SetMarkerColor(color)
            histr.SetLineColor(color)
            histr.SetLineWidth(2)
            for binn in range(1, central_hist.GetNbinsX() + 1):
                print(f"Ratio {binn}: {histr.GetBinContent(binn)}")

            graphr = None
            if central_graph:
                graphr = central_graph.Clone()
                graphr.SetName(f"g_ratio_{label}")
                for binn in range(2, central_hist.GetNbinsX() + 1):
                    x_err = histr.GetBinWidth(binn) / 4.0
                    y_low = divide_syst_error(histr.GetBinContent(binn),
                                              central_hist.GetBinContent(binn),
                                              hist_ratio.GetBinContent(binn),
                                              central_graph.GetErrorYlow(binn - 1),
                                              graph_ratio.GetErrorYlow(binn - 1), histr, binn)
                    y_high = divide_syst_error(histr.GetBinContent(binn),
                                               central_hist.GetBinContent(binn),
                                               hist_ratio.GetBinContent(binn),
                                               central_graph.GetErrorYhigh(binn - 1),
                                               graph_ratio.GetErrorYhigh(binn - 1), histr, binn)
                    graphr.SetPoint(binn - 1, histr.GetBinCenter(binn), histr.GetBinContent(binn))
                    graphr.SetPointError(binn - 1, x_err, x_err, y_low, y_high)
                    print(f"Central graph bin {binn-1} low {central_graph.GetErrorYlow(binn-1)} "\
                          f"{label} low: {graph_ratio.GetErrorYlow(binn-1)} "\
                          f"up {central_graph.GetErrorYhigh(binn-1)} {label} up: {graph_ratio.GetErrorYhigh(binn-1)}")
            figs = [fig for fig in (histr, graphr) if fig]
            for fig in figs:
                fig.SetMarkerColor(color)
                fig.SetLineColor(color)
                fig.SetMarkerStyle(style)
                fig.SetMarkerSize(1)
            canvr.cd()
            draw_opt = "sameE" if ind != 0 else "E"
            histr.SetMaximum(maxy)
            histr.SetMinimum(miny)
            for axis in (histr.GetXaxis(), histr.GetYaxis()):
                axis.SetLabelFont(42)
                axis.SetTitleFont(42)
            histr.GetXaxis().SetTitleOffset(0.95)
            histr.GetXaxis().SetTitleSize(0.15)
            histr.GetXaxis().SetLabelSize(0.15)
            histr.GetYaxis().SetLabelSize(0.15)
            histr.GetYaxis().SetTitleSize(0.15)
            histr.GetYaxis().SetTitleOffset(0.53)
            histr.GetYaxis().SetLabelOffset(0.02)
            #histr.GetYaxis().SetNdivisions(6)
            histr.GetYaxis().SetTitle("#frac{13.6 TeV}{13 TeV}")
            histr.GetYaxis().CenterTitle(True)
            histr.GetXaxis().SetTitle("#it{p}_{T}(GeV/#it{c})")
            histr.GetXaxis().SetNdivisions(808)
            histr.Draw(draw_opt)
            if graphr:
                graphr.Draw("sameE2")
            legr.AddEntry(histr, label, "p")
            histsr.append(histr)
            if graphr:
                graphsr.append(graphr)
            maxx = max(maxx, histr.GetBinLowEdge(histr.GetNbinsX() + 1))

    line = TLine(0.0, 1.0, maxx, 1.0)
    line.SetLineColor(COLORS[len(hists)])
    line.SetLineWidth(3)
    line.SetLineStyle(kDashed)
    line.Draw()

    #legr.Draw()
    canv.cd()
    canvr.Draw()
    canv.Draw()

    return canv, canvr, histsr, graphsr, legr, line


def calc_systematics(cfg, hists):
    syst_errors = []
    central_hist = hists[cfg["default"]]

    for binn in range(central_hist.GetNbinsX()):
        syst_err_bin = 0.00
        count = 0
        for label in hists:
            if label != cfg["default"] and hists[label].GetNbinsX() == central_hist.GetNbinsX():
                syst_err = float("inf") if central_hist.GetBinContent(binn + 1) == 0 else \
                           (hists[label].GetBinContent(binn + 1) - \
                             central_hist.GetBinContent(binn + 1)) / \
                             central_hist.GetBinContent(binn + 1)
                syst_err_bin += syst_err * syst_err
                count += 1
        if count == 0:
            return
        syst_err_bin = 100 * (math.sqrt(syst_err_bin / count))
        syst_errors.append(syst_err_bin)

    str_err = "Systematic errors:"
    for err in syst_errors:
        str_err = f"{str_err} {err:0.2f}"
    print(str_err)


def main():
    """
    Main function.
    """
    gROOT.SetBatch(True)

    gStyle.SetOptStat(0)
    gStyle.SetOptTitle(0)
    gStyle.SetFrameLineWidth(2)

    parser = argparse.ArgumentParser(description="Arguments to pass")
    parser.add_argument("config", help="JSON config file")
    args = parser.parse_args()

    with open(args.config, encoding="utf8") as fil:
        cfg = json.load(fil)

    with TFile(os.path.join(cfg["output"]["outdir"],
               f'{cfg["output"]["file"]}.root'), "recreate") as output:

        canv, canv_top, canvr = prepare_canvas(f'c_{cfg["histoname"]}', cfg.get("log_scale", False))
        canv, canv_top, hists, graphs_syst, hists_models, leg, leg_models, alice_text, central_graph = plot_compare(cfg, canv, canv_top) # pylint: disable=unused-variable
        output.cd()
        canv_top.Write()
        save_canvas(canv_top, cfg, f'{cfg["output"]["file"]}_top')
        for _, hist in hists.items():
            hist.Write()
        for graph in graphs_syst:
            graph.Write()
        for hist in hists_models:
            hist.Write()

        canv, canvr, histr, graphr, legr, line = plot_ratio(cfg, hists, graphs_syst, central_graph, canv, canvr)
        output.cd()
        canv.Write()
        save_canvas(canv, cfg, f'{cfg["output"]["file"]}')
        canvr.Write()
        save_canvas(canvr, cfg, f'{cfg["output"]["file"]}_ratio')
        for hist in histr:
            hist.Write()
        for graph in graphr:
            graph.Write()

        calc_systematics(cfg, hists)

        canv_top.Delete()
        canvr.Delete()


if __name__ == "__main__":
    main()
