import ROOT as r
import copy
from array import array
from copy import deepcopy
import glob
import os
import sys

def applyGeneralHPSConfig():
    #General configuration
    bottomFraction = 0.4
    bottomScale = 1./bottomFraction
    topScale = 1./(1. - bottomFraction)
    r.TProfile.Approximate(True)

def SetStyle():

    colors = getColorsHPS()
    r.gROOT.SetBatch(1)

    hpsStyle = r.TStyle("HPS", "HPS style")

    # use plain black on white colors
    icol = 0
    hpsStyle.SetFrameBorderMode(icol)
    hpsStyle.SetCanvasBorderMode(icol)
    hpsStyle.SetPadBorderMode(icol)
    hpsStyle.SetPadColor(icol)
    hpsStyle.SetCanvasColor(icol)
    hpsStyle.SetStatColor(icol)
#hpsStyle.SetFillColor(icol)

# set the paper & margin sizes
    hpsStyle.SetPaperSize(20, 26)
    hpsStyle.SetPadTopMargin(0.05)
    hpsStyle.SetPadRightMargin(0.05)
    hpsStyle.SetPadBottomMargin(0.18)
    hpsStyle.SetPadLeftMargin(0.14)

    # use large fonts
#font=72
    font = 42
    tsize = 0.08
    tzsize = 0.045
    hpsStyle.SetTextFont(font)

    hpsStyle.SetTextSize(tsize) 
    hpsStyle.SetLabelFont(font, "x")
    hpsStyle.SetTitleFont(font, "x")
    hpsStyle.SetLabelFont(font, "y")
    hpsStyle.SetTitleFont(font, "y")
    hpsStyle.SetLabelFont(font, "z")
    hpsStyle.SetTitleFont(font, "z")

    hpsStyle.SetLabelSize(tsize, "x")
    hpsStyle.SetTitleSize(tsize, "x")
    hpsStyle.SetLabelSize(tsize, "y")
    hpsStyle.SetTitleSize(tsize, "y")
    hpsStyle.SetLabelSize(tzsize, "z")
    hpsStyle.SetTitleSize(tzsize, "z")

    #hpsStyle.SetTitleOffset(0.7, "y")
    #hpsStyle.SetTitleOffset(1.15, "x")

    #hpsStyle.SetTitleOffset(0.7, "y")
    #hpsStyle.SetTitleOffset(1.15, "x")
#use bold lines and markers
    #hpsStyle.SetMarkerStyle(20)
    hpsStyle.SetMarkerSize(1.0)
    hpsStyle.SetHistLineWidth(3)
    hpsStyle.SetLineStyleString(2, "[12 12]")  # postscript dashes

#get rid of X error bars and y error bar caps
#hpsStyle.SetErrorX(0.001)

#do not display any of the standard histogram decorations
    hpsStyle.SetOptTitle(1)
#hpsStyle.SetOptStat(1111)
    hpsStyle.SetOptStat(0)
#hpsStyle.SetOptFit(1111)
    hpsStyle.SetOptFit(0)

# put tick marks on top and RHS of plots
    hpsStyle.SetPadTickX(1)
    hpsStyle.SetPadTickY(1)

    #r.gROOT.SetStyle("Plain")

#gStyle.SetPadTickX(1)
#gStyle.SetPadTickY(1)
    r.gROOT.SetStyle("HPS")
    r.gROOT.ForceStyle()
    r.gStyle.SetOptTitle(1)
    r.gStyle.SetOptStat(0)
    r.gStyle.SetOptFit(0)


# overwrite hps styles
    hpsStyle.SetPadLeftMargin(0.14)
    hpsStyle.SetPadRightMargin(0.06)
    hpsStyle.SetPadBottomMargin(0.11)
    hpsStyle.SetPadTopMargin(0.05)
    hpsStyle.SetFrameFillColor(0)

    NRGBs = 5
    NCont = 255

    stops = array("d", [0.00, 0.34, 0.61, 0.84, 1.00])
    red = array("d", [0.00, 0.00, 0.87, 1.00, 0.51])
    green = array("d", [0.00, 0.81, 1.00, 0.20, 0.00])
    blue = array("d", [0.51, 1.00, 0.12, 0.00, 0.00])
    r.TColor.CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont)
    r.gStyle.SetNumberContours(NCont)


def InsertText(insertText=[], text_x=0.3, text_y=0.9, line_spacing=0.03, text_size=0.025, Hps=True):

    drawText = insertText

    latex = r.TLatex()
    latex.SetTextFont(42)
    latex.SetTextSize(text_size)
    latex.SetTextAlign(12)
    latex.SetTextColor(r.kBlack)

    if (Hps):
        latex.DrawLatexNDC(text_x, text_y,'#bf{#it{HPS}} Internal')
        text_y = text_y - line_spacing

    for line in drawText:
        latex.DrawLatexNDC(text_x, text_y,line)
        text_y = text_y - line_spacing

    #text = r.TLatex()
    #text.SetNDC()
    #text.SetTextFont(42)
    #text.SetTextSize(0.05)
    #text.SetTextColor(r.kBlack)

def read_2d_plots_from_root_file_dirs(file_path, root_dir_key="",keyword=""):
    # List to store the matching 1D plots
    dir_plots = {}

    # Open the ROOT file
    root_file = r.TFile.Open(file_path)

    #Loop over all directories matching key
    for dir_key in root_file.GetListOfKeys():
        dir_obj = dir_key.ReadObj()

        # Check if the object is TDir
        if isinstance(dir_obj, r.TDirectory):
            if root_dir_key not in dir_obj.GetName():
                continue

            print("Navigating to directory ", dir_obj.GetName())
            # Get the directory within the ROOT file
            root_dir = root_file.GetDirectory(dir_obj.GetName())

            plots = []

            # Loop over all objects in the directory
            for key in root_dir.GetListOfKeys():
                obj = key.ReadObj()

                # Check if the object is a 1D histogram
                if isinstance(obj, r.TH2) and obj.GetDimension() == 2:
                    # Check if the object name contains the keyword (if provided)
                    if keyword and keyword not in obj.GetName():
                        continue
                    print("Copying plot", obj.GetName())
                    # Create a deepcopy of the plot and append to the list
                    plots.append(copy.deepcopy(obj))

            dir_plots[dir_obj.GetName()] = plots

    # Close the ROOT file
    root_file.Close()

    return dir_plots

def plot_2d_plots_side_by_side(hist1, hist2, canvas_name, save_directory,insertText=[],text_x=0.4, text_y=0.3, line_spacing=0.03, text_size=0.02):
    # Set transparent fill style for the statistics box
    r.gStyle.SetOptStat(1)  # Show statistics box
    r.gStyle.SetStatStyle(0)  # Set fill style to transparent
    canvas = r.TCanvas("%s"%(canvas_name), "%s"%(canvas_name), 1800, 900 )
    pad1 = r.TPad("pad1","Pad 1", 0.01, 0.01, 0.49, 0.99)
    pad2 = r.TPad("pad2","Pad 2", 0.51, 0.01, 0.99, 0.99)
    # Set margins and draw pads
    #pad1.SetBottomMargin(0)  # No margin at the bottom for pad1
    #pad2.SetTopMargin(0)     # No margin at the top for pad2
    pad1.SetRightMargin(0.15)
    pad1.SetLeftMargin(0.05)
    pad2.SetRightMargin(0.15)
    pad2.SetLeftMargin(0.05)

    pad1.Draw()
    pad2.Draw()

    pad1.cd()
    hist1.Draw("colz")

    pad2.cd()
    hist2.Draw("colz")

    canvas.Update()

    latex = r.TLatex()
    latex.SetTextSize(text_size)
    latex.SetTextAlign(12)
    for line in insertText:
        latex.DrawLatexNDC(text_x, text_y,line)
        text_y = text_y - line_spacing
    canvas.Update()

    file_name = save_directory + "/" + canvas_name + ".png"
    canvas.SaveAs(file_name)

    # Clean up
    canvas.Close()

def read_1d_plots_from_root_file_dirs(file_path, root_dir_key="", keyword=""):
    # List to store the matching 1D plots
    dir_plots = {}

    # Open the ROOT file
    root_file = r.TFile.Open(file_path)

    #Loop over all directories matching key
    for dir_key in root_file.GetListOfKeys():
        dir_obj = dir_key.ReadObj()

        # Check if the object is TDir
        if isinstance(dir_obj, r.TDirectory):
            if root_dir_key not in dir_obj.GetName():
                continue

            print("Navigating to directory ", dir_obj.GetName())
            # Get the directory within the ROOT file
            root_dir = root_file.GetDirectory(dir_obj.GetName())

            plots = []

            # Loop over all objects in the directory
            for key in root_dir.GetListOfKeys():
                obj = key.ReadObj()

                # Check if the object is a 1D histogram
                if isinstance(obj, r.TH1) and obj.GetDimension() == 1:
                    # Check if the object name contains the keyword (if provided)
                    if keyword and keyword not in obj.GetName():
                        continue
                    print("Copying plot", obj.GetName())
                    # Create a deepcopy of the plot and append to the list
                    plots.append(copy.deepcopy(obj))

            dir_plots[dir_obj.GetName()] = plots

    # Close the ROOT file
    root_file.Close()

    return dir_plots

def read_plot_from_root_file(file_path, name, root_dir=""):
    # Open the ROOT file
    root_file = r.TFile(file_path)

    # Get the directory within the ROOT file
    root_dir = root_file.GetDirectory(root_dir)

    # Check if the directory exists
    if not root_dir:
        print(f"Failed to find directory: {root_dir}")
        root_file.Close()
        return None

    plot = copy.deepcopy(root_dir.Get("%s"%(name)))

    root_file.Close()

    return plot

def read_1d_plots_from_root_file(file_path, root_dir="", keyword=""):
    # Open the ROOT file
    root_file = r.TFile.Open(file_path)

    # Check if the file is open
    if not root_file.IsOpen():
        print(f"Failed to open ROOT file: {file_path}")
        return []

    # Get the directory within the ROOT file
    root_dir = root_file.GetDirectory(root_dir)

    # Check if the directory exists
    if not root_dir:
        print(f"Failed to find directory: {root_dir}")
        root_file.Close()
        return []

    # List to store the matching 1D plots
    plots = []

    # Loop over all objects in the directory
    for key in root_dir.GetListOfKeys():
        obj = key.ReadObj()

        # Check if the object is a 1D histogram
        if isinstance(obj, r.TH1) and obj.GetDimension() == 1:
            # Check if the object name contains the keyword (if provided)
            if keyword and keyword not in obj.GetName():
                continue

            # Create a deepcopy of the plot and append to the list
            plots.append(copy.deepcopy(obj))

    # Close the ROOT file
    root_file.Close()

    return plots

def format_TH1(histogram, name=None, title=None, x_label=None, y_label=None,
        line_width=None, line_color=None, marker_style=None,
        marker_size=None, line_style=None):
    if name is not None:
        histogram.SetName(name)
    if title is not None:
        histogram.SetTitle(title)
    if x_label is not None:
        histogram.GetXaxis().SetTitle(x_label)
    if y_label is not None:
        histogram.GetYaxis().SetTitle(y_label)
    if line_width is not None:
        histogram.SetLineWidth(line_width)
    if line_color is not None:
        histogram.SetLineColor(line_color)
    if marker_style is not None:
        histogram.SetMarkerStyle(marker_style)
    if marker_size is not None:
        histogram.SetMarkerSize(marker_size)
    if line_style is not None:
        histogram.SetLineStyle(line_style)

    #histogram.GetXaxis().SetTitle(xtitle)
    #histogram.GetXaxis().SetTitleSize(
    #    histogram.GetXaxis().GetTitleSize()*0.7)
    #histogram.GetXaxis().SetLabelSize(
    #    histogram.GetXaxis().GetLabelSize()*0.75)
    #histogram.GetXaxis().SetTitleOffset(
    #    histogram.GetXaxis().GetTitleOffset()*0.8)

    #histogram.GetYaxis().SetTitleSize(
    #    histogram.GetYaxis().GetTitleSize()*0.7)
    #histogram.GetYaxis().SetLabelSize(
    #    histogram.GetYaxis().GetLabelSize()*0.75)
    #histogram.GetYaxis().SetTitleOffset(
    #    histogram.GetYaxis().GetTitleOffset()*1.7)
    #histogram.GetYaxis().SetTitle(ytitle)


def getMarkersHPS():
    markers = [r.kFullCircle, r.kFullTriangleUp, r.kFullSquare, r.kOpenSquare, r.kOpenTriangleUp, r.kOpenCircle, r.kFullCircle, r.kOpenSquare, r.kFullSquare, r.kOpenTriangleUp, r.kOpenCircle, r.kFullCircle, r.kOpenSquare, r.kFullSquare, r.kOpenTriangleUp, r.kOpenCircle, r.kFullCircle, r.kOpenSquare, r.kFullSquare, r.kOpenTriangleUp, r.kOpenCircle, r.kFullCircle, r.kOpenSquare, r.kFullSquare, r.kOpenTriangleUp, r.kOpenCircle, r.kFullCircle, r.kOpenSquare, r.kFullSquare, r.kOpenTriangleUp]
    return markers

def getColorsHPS():
    colors = [r.kBlue+2, r.kCyan+2, r.kRed+2, r.kOrange+10, r.kYellow+2, r.kGreen-1, r.kAzure-2, r.kGreen-8, r.kOrange+3, r.kYellow+2, r.kRed+2, r.kBlue+2, r.kGreen-8, r.kOrange+3, r.kYellow+2, r.kRed+2, r.kBlue+2, r.kGreen-8, r.kOrange+3, r.kYellow+2, r.kRed+2, r.kBlue+2, r.kGreen-8, r.kOrange+3, r.kYellow+2, r.kRed+2, r.kBlue+2, r.kGreen-8, r.kOrange+3]
    return colors

def getColors():
    # Array to store the colors
    colors = []

    # List of colors to choose from
    available_colors = [
            r.kBlack,
            r.kBlue,
            r.kRed,
            r.kGreen,
            r.kMagenta,
            r.kOrange,
            r.kTeal,
            r.kSpring,
            r.kGray,
            ]

    for color in available_colors:
        colors.append(color)

    print("Colors: ", colors)
    return colors

def format_multiStats(n):
    # Define the position and size of each statistics box
    box_x = 0.7  # X-coordinate of the top-right corner of the first box
    box_y = 0.7  # Y-coordinate of the top-right corner of the first box
    box_width = 0.2  # Width of each box
    box_height = 0.15  # Height of each box
    box_margin = 0.05  # Margin between each box

    # Calculate the positions for each statistics box
    box_positions = []
    for i in range(n):
        x = box_x
        y = box_y - (box_height + box_margin) * i
        box_positions.append((x, y))

    return box_positions 

def plot_TH1s_with_legend(histograms, canvas_name, save_directory,setStats=False,freezeXaxis=True,legx1=0.7,legy1=0.7,legx2=0.9,legy2=0.9, clear_legend=True, LogX=False, LogY=False, insertText=[],text_x=0.6, text_y=0.6, text_size = 0.03, line_spacing=0.03):
    # Create a canvas
    canvas = r.TCanvas(canvas_name, canvas_name, 2560, 1440)

    # Find the maximum x and y values among all histograms
    max_x, max_y = max(h.GetBinLowEdge(h.FindLastBinAbove(0)) for h in histograms), max(h.GetMaximum() for h in histograms)
    # Find the minimumg x and y values among all histograms
    min_x, min_y = min(h.GetBinLowEdge(h.FindFirstBinAbove(0)) for h in histograms), min(h.GetMinimum() for h in histograms)
    # Create a legend corresponding to each histogram
    legend = r.TLegend(0.7, 0.7, 0.9, 0.9)
    # Set the legend to transparent (clear) if the option is specified
    if clear_legend:
        legend.SetFillStyle(0)
        legend.SetFillColor(0)
        legend.SetLineColor(0)
        legend.SetBorderSize(0)

    for histogram in histograms:

        if(freezeXaxis == False):
            # Adjust the axis ranges for all histograms
            histogram.SetAxisRange(0.9*min_x, 1.1*max_x, "X")
            # Set the same maximum and minimum for both axes
            histogram.GetXaxis().SetRangeUser(0.9*min_x,1.1*max_x)
        histogram.SetAxisRange(min_y, 1.1 * max_y, "Y")
        histogram.GetYaxis().SetRangeUser(min_y, 1.1 * max_y)
        if LogY and max_y > 0 and min_y <= 0:
            histogram.SetAxisRange(0.5, 1.1 * max_y, "Y")
            histogram.GetYaxis().SetRangeUser(0.5, 1.1 * max_y)


        # Plot the histogram on the canvas
        histogram.Draw("SAME")

        if setStats == False:
            histogram.SetStats(0)
        else:
            stat_box = histogram.GetListOfFunctions().FindObject("stats")
            x, y = format_multiStats(len(histograms))
            stat_box.SetX1NDC(x)
            stat_box.SetY1NDC(y)
            stat_box.SetX2NDC(x + box_width)
            stat_box.SetY2NDC(y - box_height)
            stat_box.SetTextSize(0.02)  # Adjust the text size of the statistics box

        legend.AddEntry(histogram, histogram.GetTitle(), "l")


    # Draw the legend on the canvas
    legend.Draw()


    if LogX:
        canvas.SetLogx(1)
    if LogY:
        canvas.SetLogy(1)

    # Save the canvas as a PNG file
    histograms[0].SetTitle(canvas_name)

    #Add Latex
    if len(insertText) > 0:
        latex = r.TLatex()
        latex.SetTextSize(text_size)
        latex.SetTextAlign(12)
        for line in insertText:
            latex.DrawLatexNDC(text_x, text_y,line)
            text_y = text_y - line_spacing
        canvas.Update()

    file_name = save_directory + "/" + canvas_name + ".png"
    canvas.SaveAs(file_name)

    # Clean up
    #canvas.Close()
    return canvas

def plot_TH1_ratios_with_legend(histograms, numerators, denominators, ratioNames, ratioColors, canvas_name, save_directory,ratioMin=0.01, ratioMax=2.0, setStats=False,legx1=0.7,legy1=0.7,legx2=0.9,legy2=0.9, clear_legend=True, LogX=False, LogY=False):
    # Create a canvas
    canvas = r.TCanvas(canvas_name, canvas_name, 2560, 1440)
    canvas.SetMargin(0,0,0,0)
    top = r.TPad("top","top",0,0.42,1,1)
    bot = r.TPad("bot","bot",0,0,1,0.38)

    if LogX:
        top.SetLogx(1)
        bot.SetLogx(1)
    if LogY:
        top.SetLogy(1)
        bot.SetLogy(1)

    top.Draw()
    top.SetBottomMargin(0.0)
    bot.Draw()
    bot.SetTopMargin(0)
    bot.SetBottomMargin(0.1)
    top.cd()

    # Find the maximum x and y values among all histograms
    max_x, max_y = max(h.GetBinLowEdge(h.FindLastBinAbove(0)) for h in histograms), max(h.GetMaximum() for h in histograms)
    # Find the minimumg x and y values among all histograms
    min_x, min_y = min(h.GetBinLowEdge(h.FindFirstBinAbove(0)) for h in histograms), min(h.GetMinimum() for h in histograms)
    # Create a legend corresponding to each histogram
    legend = r.TLegend(legx1, legy1, legx2, legy2)
    # Set the legend to transparent (clear) if the option is specified
    if clear_legend:
        legend.SetFillStyle(0)
        legend.SetFillColor(0)
        legend.SetLineColor(0)
        legend.SetBorderSize(0)

    for histogram in histograms:

        # Adjust the axis ranges for all histograms
        histogram.SetAxisRange(0.9*min_x, 1.1*max_x, "X")
        histogram.SetAxisRange(min_y, 1.1 * max_y, "Y")
        # Set the same maximum and minimum for both axes
        histogram.GetXaxis().SetRangeUser(0.9*min_x,1.1*max_x)
        histogram.GetYaxis().SetRangeUser(min_y, 1.1 * max_y)

        # Plot the histogram on the canvas
        histogram.Draw("hist SAME")

        if setStats == False:
            histogram.SetStats(0)
        else:
            stat_box = histogram.GetListOfFunctions().FindObject("stats")
            x, y = format_multiStats(len(histograms))
            stat_box.SetX1NDC(x)
            stat_box.SetY1NDC(y)
            stat_box.SetX2NDC(x + box_width)
            stat_box.SetY2NDC(y - box_height)
            stat_box.SetTextSize(0.02)  # Adjust the text size of the statistics box

        legend.AddEntry(histogram, histogram.GetTitle(), "l")


    # Draw the legend on the canvas
    legend.Draw()

    histograms[0].SetTitle(canvas_name)

    #-------------Ratio---------------#

    ratio_plots = []
    bot.cd()
    for i, plot in enumerate(numerators):
        numerator = plot.Clone("numerator_%s"%plot.GetName())
        denominator = denominators[i].Clone("denominator_%s"%denominators[i].GetName())
        numerator.SetStats(0)
        numerator.GetYaxis().SetRangeUser(ratioMin,ratioMax)
        numerator.SetNdivisions(508)
        numerator.GetYaxis().SetDecimals(True)
        numerator.Draw("axis")
        numerator.SetTitle(ratioNames[i])

        denominator.SetStats(0)
        numerator.Divide(denominator)
        numerator.SetLineColor(ratioColors[i])
        ratio_plots.append(numerator)

    for i, plot in enumerate(ratio_plots):
        if i < 1:
            plot.Draw("ep")
        else:
            plot.Draw("ep same")

    bot_legend = bot.BuildLegend(legx1, legy1, legx2, legy2)
    bot_legend.Draw()
    if clear_legend:
        bot_legend.SetFillStyle(0)
        bot_legend.SetFillColor(0)
        bot_legend.SetLineColor(0)
        bot_legend.SetBorderSize(0)

    # Save the canvas as a PNG file
    file_name = save_directory + "/" + canvas_name + ".png"
    canvas.SaveAs(file_name)

    # Clean up
    canvas.Close()

def Make2DPlot(canvas_name, histo, xtitle="", ytitle="", ztitle="", insertText=[], zmin="", zmax="", outdir='.', save=False):
    oFext = ".png"
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    can = r.TCanvas()
    can.SetName('%s'%(canvas_name))
    #can.SetTitle('%s'%(canvas_name))
    can.SetRightMargin(0.2)

    #histolist[ih].GetZaxis().SetRangeUser(zmin,zmax)
    if xtitle:
        histo.GetXaxis().SetTitle(xtitle)
    histo.GetXaxis().SetTitleSize(
            histo.GetXaxis().GetTitleSize()*0.7)
    histo.GetXaxis().SetLabelSize(
            histo.GetXaxis().GetLabelSize()*0.75)
    histo.GetXaxis().SetTitleOffset(
            histo.GetXaxis().GetTitleOffset()*0.8)

    histo.GetYaxis().SetTitleSize(
            histo.GetYaxis().GetTitleSize()*0.7)
    histo.GetYaxis().SetLabelSize(
            histo.GetYaxis().GetLabelSize()*0.75)
    histo.GetYaxis().SetTitleOffset(
            histo.GetYaxis().GetTitleOffset()*1.7)
    if ytitle:
        histo.GetYaxis().SetTitle(ytitle)

    histo.Draw("colz")

    InsertText(insertText)

    if save:
        can.SaveAs(outdir+"/"+name+oFext)
    return deepcopy(can)

def Make1DPlot(canvas_name, histo, title="",xtitle="", ytitle="", ztitle="", drawOptions = "", insertText=[], outdir='.', LogY=False,save=True):
    oFext = ".png"
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    if title:
        histo.SetTitle(title)

    can = r.TCanvas('%s'%(canvas_name),'%s'%(canvas_name),2500,1440)
    #can.SetName('%s'%(canvas_name))
    #can.SetTitle('%s'%(canvas_name))
    can.SetRightMargin(0.2)

    #xmax = histo.GetBinLowEdge(histo.FindLastBinAbove(0))
    #ymax = histo.GetMaximum()
    #xmin = histo.GetBinLowEdge(histo.FindFirstBinAbove(0))
    #ymin = histo.GetMinimum()
    #if setymin:
    #    ymin = set_ymin

    if xtitle:
        histo.GetXaxis().SetTitle(xtitle)
    histo.GetXaxis().SetTitleSize(
            histo.GetXaxis().GetTitleSize()*0.7)
    histo.GetXaxis().SetLabelSize(
            histo.GetXaxis().GetLabelSize()*0.75)
    histo.GetXaxis().SetTitleOffset(
            histo.GetXaxis().GetTitleOffset()*0.8)

    if ytitle:
        histo.GetYaxis().SetTitle(ytitle)
    histo.GetYaxis().SetTitleSize(
            histo.GetYaxis().GetTitleSize()*0.7)
    histo.GetYaxis().SetLabelSize(
            histo.GetYaxis().GetLabelSize()*0.75)
    histo.GetYaxis().SetTitleOffset(
            histo.GetYaxis().GetTitleOffset()*1.7)




    histo.Draw("%s"%(drawOptions))

    if LogY:
        canvas.SetLogy(1)

    InsertText(insertText)

    if save:
        can.SaveAs(outdir+"/"+canvas_name+oFext)
    return deepcopy(can)

def saveCanvasesToPDF(canvases=[], pdf_name='my_canvases.pdf'):
    outfile = r.TFile('%s'%(pdf_name),"RECREATE")
    for canvas in canvases:
        canvas.Print('%s'%(pdf_name))
    outfile.Close()


