import sys
import numpy as np
from ROOT import *
from KITDataFile import KITDataFile
from KITPlot import KITPlot

file1 = KITDataFile(sys.argv[1])
file2 = KITDataFile(sys.argv[2])

kPlot = KITPlot(file1.getX(), file1.getY())



g1 = TGraph(len(file1.getX()),file1.getX(True),file1.getY(True))
g2 = TGraph(len(file1.getX()),file1.getX(True),file1.getZ(True))
g3 = TGraph(len(file2.getX()),file2.getX(True),file2.getY(True))

y2 = [x + y for x, y in zip(file1.getY(), file1.getZ())]
g4 = TGraph(len(file1.getX()),file1.getX(1),np.asarray(y2))

g1.SetMarkerColor(1100)
g2.SetMarkerColor(1200)
g3.SetMarkerColor(1300)
g4.SetMarkerColor(1400)

c1 = TCanvas("c1","c1",1280,768)
c1.cd()

g2.SetTitle("IV-Curve")

g2.Draw("AP")
g1.Draw("PSAME")
g3.Draw("PSAME")
g4.Draw("PSAME")

c1.SaveAs("test.pdf")
    
raw_input()
