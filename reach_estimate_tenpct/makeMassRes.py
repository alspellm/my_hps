#/bin/env python
import glob
import numpy as np
import ROOT as r
import utilities as utils
import copy
from optparse import OptionParser

utils.SetStyle()

parser = OptionParser()

parser.add_option("-i", "--inputFile", type="string", dest="inputFile",
    help="Name of file to run on.", metavar="inputFile", default="toys/toys.root")
parser.add_option("-o", "--outputFile", type="string", dest="outputFile",
    help="Specify the output filename.", metavar="outputFile", default="massResolution.root")

(options, args) = parser.parse_args()

invMasses = [40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 170, 175, 180, 185, 190, 195, 200]

outFile = r.TFile(options.outputFile,"RECREATE")

zeros = [0.0 for mass in invMasses]
masses = [float(mass) for mass in invMasses]
massRezs = []
massRezErrs = []
massRezsScaled = []
massRezErrsScaled = []

for mass in invMasses:
    print(mass)
    selection = "vtxana_kf_radMatchTight_2016_simp_reach_SR"
    signalFilename = "/sdf/group/hps/users/alspellm/projects/THESIS/mc/2016/simps/signal_beam/20230713_slic/20230713_readout/20230713_recon/20230721_tuples/20230724_ana/ana_files/hadd_simp_%i_MeV_egsv6_HPS-PhysicsRun2016-Pass2_recon_targetTracks_NObeamPosCorr_ana.root"%(mass)
    signalFile = r.TFile(signalFilename)
    sigRecoMass_h = copy.deepcopy( signalFile.Get("%s/%s_vtx_InvM_h"%(selection, selection)) )
    sigRecoMass_h.SetName("%s_vtx_InvM%i_h"%(selection,mass))
    print("Mass %i MeV: %i"%(mass,sigRecoMass_h.GetEntries()))
    signalFile.Close()
    frl = sigRecoMass_h.GetXaxis().GetBinLowEdge(sigRecoMass_h.FindFirstBinAbove(0))
    frh = sigRecoMass_h.GetXaxis().GetBinLowEdge(sigRecoMass_h.FindLastBinAbove(0))
    fitRes = sigRecoMass_h.Fit("gaus","ES+","", frl,frh)
    outFile.cd()
    sigRecoMass_h.Write()
    massRez = 1000.0*fitRes.GetParams()[2]
    massRezErr = 1000.0*fitRes.GetErrors()[2]
    massRezs.append(massRez)
    massRezErrs.append(massRezErr)
    massRezsScaled.append(1.43*massRez)
    massRezErrsScaled.append(1.43*massRezErr)
    print("Mass res: %f +- %f"%(massRez, massRezErr))
    pass

massRes_ge = r.TGraphErrors(len(masses),np.array(masses), np.array(massRezs), np.array(zeros), np.array(massRezErrs))
massRes_ge.SetName("massRes_ge")
massRes_ge.SetTitle(";m_{vtx} [MeV];#sigma_{m} [MeV]")
massRes_ge.SetLineColor(utils.colors[4])
massRes_ge.SetLineWidth(4)
massResScaled_ge = r.TGraphErrors(len(masses),np.array(masses), np.array(massRezsScaled), np.array(zeros), np.array(massRezErrsScaled))
massResScaled_ge.SetName("massResScaled_ge")
massResScaled_ge.SetTitle(";m_{vtx} [MeV];#sigma_{m} [MeV]")
massResScaled_ge.SetLineColor(utils.colors[5])
massResScaled_ge.SetLineWidth(4)

nPoints = len(masses)
chi2s = []
fstats = []
for polyO in range(5):
    fitResult = massResScaled_ge.Fit('pol%i'%polyO,"ES")
    chi2s.append(fitResult.Chi2())
    if polyO > 0:
        fstats.append((chi2s[polyO-1]-chi2s[polyO])*(nPoints-polyO-1)/(chi2s[polyO]))
    else:
        fitCon = fitResult.GetParams()[0]

print("nPoints: %i"%nPoints)
for polyO in range(1,5):
    print("Order: %i    NDF: %f    chi2: %f    f-stat: %f"%(polyO, nPoints-polyO-1,chi2s[polyO], fstats[polyO-1]))
fitResult = massResScaled_ge.Fit('pol2',"ES")
fitFunc = massResScaled_ge.GetListOfFunctions().FindObject("pol2")
fitFunc.SetLineColor(utils.colors[3])

canv = r.TCanvas("canv", "canv", 1400, 1000)
canv.cd()
massResScaled_ge.SetMinimum(0.0)
massResScaled_ge.SetMaximum(20.0)
massResScaled_ge.Draw("ape")
massRes_ge.Draw("pesame")
fitFunc.Draw("same")
utils.InsertText()
canv.SaveAs("massRes.png")

massRes_ge.Write()
massResScaled_ge.Write()

outFile.Close()

#2016 Simps KF 11/15/22
'''
EXT PARAMETER                                   STEP         FIRST   
  NO.   NAME      VALUE            ERROR          SIZE      DERIVATIVE 
   1  p0           1.06314e+00   5.08804e-02   1.96911e-06   8.32806e-09
   2  p1           3.45955e-02   1.20154e-03  -2.30725e-08  -5.34448e-07
   3  p2          -6.62113e-05   6.48625e-06   6.48625e-06  -1.73755e-05
'''

#2016 Simps KF 08/22/23
'''
Order: 1    NDF: 31.000000    chi2: 282.620749    f-stat: 1689.684982
Order: 2    NDF: 30.000000    chi2: 148.355535    f-stat: 27.150699
Order: 3    NDF: 29.000000    chi2: 123.858315    f-stat: 5.735742
Order: 4    NDF: 28.000000    chi2: 113.229004    f-stat: 2.628485
 FCN=148.356 FROM MINOS     STATUS=SUCCESSFUL     20 CALLS         113 TOTAL
                     EDM=2.53867e-09    STRATEGY= 1      ERROR MATRIX ACCURATE 
  EXT PARAMETER                                   STEP         FIRST   
  NO.   NAME      VALUE            ERROR          SIZE      DERIVATIVE 
   1  p0           1.15880e+00   3.46026e-02  -2.57213e-07   1.54936e-09
   2  p1           3.22263e-02   8.21640e-04   3.15675e-09  -1.17020e-07
   3  p2          -5.16703e-05   4.45936e-06   4.45936e-06   2.26676e-05
'''
