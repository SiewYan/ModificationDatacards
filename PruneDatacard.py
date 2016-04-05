#!/usr/bin/python

###   
###      _ \                                 __ \          |                                 |       
###     |   |   __|  |   |  __ \    _ \      |   |   _` |  __|   _` |   __|   _` |   __|  _` |   __| 
###     ___/   |     |   |  |   |   __/      |   |  (   |  |    (   |  (     (   |  |    (   | \__ \ 
###    _|     _|    \__,_| _|  _| \___|     ____/  \__,_| \__| \__,_| \___| \__,_| _|   \__,_| ____/ 
###                                                                                                  
###   

######################################
# workaround to disable pyroot parser!
import sys
tmpargv = sys.argv
sys.argv = [ '-b','-n' ]
import ROOT
from ROOT import TFile, TH1F, TCanvas, gStyle, TLine
sys.argv = tmpargv
from optparse import OptionParser
######################################

import re
import os
import subprocess
import operator
from commands import getstatusoutput
from operator import itemgetter

import fnmatch

import math

import string


######################################

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----

def PruneDatacard (datacardname, datacardnameOut, nameFileConfiguration, threshold) :

    # open the datacard file

    #currentFolder = getstatusoutput ('pwd')[1]
    #datacardname = currentFolder + '/' +  datacardname 
    print 'Opening original input datacard: ', datacardname
    lines = open (datacardname, 'r').read().split ('\n')
    nametag = datacardname.split ('/')[-1].replace ('.txt', '')
    thepath = datacardname.replace (nametag + '.txt', '')

    print "nametag = ",nametag
    print "thepath = ",thepath
    print "datacardnameOut = ", datacardnameOut

    # read datacard and separate bin, sample, rate, ...

    systime = 0
    header = []
    binName = []
    longListBin = [] # the bin list just before systematics
    sampleName = []
    reducedsampleName = [] # remove duplicate!
    sampleRate = []
    observation = []
    systematics = []
    systematicsName = []
    longListRateIndex = []
    rootFiles = {}
    firstTimeBin = True
    firstTimeProcess = True
    for line in lines:
      if '---' in line : continue
      if systime == 0 :
        tempLine = line.split (' ')
        tempLine = filter(lambda a: a != '', tempLine)
        #print " line.split (' ')[0] = ", line.split (' ')[0], "\n"
        if len(tempLine) == 0 : continue #skip if empty
        if tempLine[0] == 'bin' and firstTimeBin:
          binName = line.split (' ')
          binName = filter(lambda a: a != 'bin', binName)
          binName = filter(lambda a: a != '', binName)
          firstTimeBin = False
        elif tempLine[0] == 'bin':
          longListBin.append(line)
        elif tempLine[0] == 'observation' :
          observation.append(line)
        elif tempLine[0] == 'process' and firstTimeProcess:
          sampleName = line.split (' ')
          sampleName = filter(lambda a: a != 'process', sampleName)
          sampleName = filter(lambda a: a != '', sampleName)
          firstTimeProcess = False
        elif tempLine[0] == 'process':
          longListRateIndex.append(line)
        elif tempLine[0] == 'rate' :
          systime = 1
          sampleRate = line.split (' ')
          sampleRate = filter(lambda a: a != 'rate', sampleRate)
          sampleRate = filter(lambda a: a != '', sampleRate)
        else :
          header.append (line)
          # 0 1 2 3
          #shapes * hwwof_1j_shape_7TeV hwwof_1j.input_7TeV.root histo_$PROCESS histo_$PROCESS_$SYSTEMATIC
        if tempLine[0] == 'shapes' :
            tempRootList = line.split (' ')
            tempRootList = filter(lambda a: a != '', tempRootList)
            if tempRootList[1] == '*' :
              rootFiles[tempRootList[2]] = tempRootList[3]
      else:
        systematics.append (line)
        systematicsName.append (line.split (' ')[0])

    # clean empty systematics
    systematics = [elem for elem in systematics if len (elem.split ()) > 0]
    systematicsName = [elem for elem in systematicsName if len (elem.split ()) > 0]

    #print "header = ", header, "\n\n"
    #print "binName = ", binName, "\n\n"
    #print "sampleName = ", sampleName, "\n\n"
    #print "sampleRate = ", sampleRate, "\n\n"
    #print "systematics = ", systematics, "\n\n"
    #print "systematicsName = ", systematicsName, "\n\n"
    #print " --------------------------------------------------------------- "

    nuisancesToPrune = {}
    if os.path.exists(nameFileConfiguration):
      handle = open(nameFileConfiguration,'r')
      exec(handle)
      handle.close()

    print "nuisancesToPrune = ", nuisancesToPrune

    # remove duplicates in "sampleName"
    # used in scaling histograms in case of "matching"
    # and in case the same sample name is used in several "bin"
    # NB: the order is not preserved, but who cares!
    reducedsampleName = list(set(sampleName))

    # modify sample rate in root file!

    for rootFileBin in rootFiles:
      print "rootFile[", rootFileBin, "] = ",rootFiles[rootFileBin]
      # check if root file is present (the name must end with .root)
      matchfile = re.search(".root", rootFiles[rootFileBin])
      if not matchfile:
       continue
      rootFile = ROOT.TFile.Open(str(thepath)+"/"+str(rootFiles[rootFileBin]))

      # get the histograms
      histograms = {}
      for k in rootFile.GetListOfKeys():
        h = k.ReadObj()
        # only 1d histograms supported
        histoName = h.GetName()
        match = re.search("histo_", histoName)
        if not match:
          continue
        histograms[h.GetName()] = h
      #print " histograms = ", histograms

      nuisance_to_be_removed = []
      for nuisance in systematicsName :
        for  hr_list_nuisances_to_test, nuisance_to_test in nuisancesToPrune.iteritems() :
          #print " hr_list_nuisances_to_test = ", hr_list_nuisances_to_test, " -> ", nuisance_to_test
          matchNuisance = fnmatch.fnmatch(str(nuisance), nuisance_to_test)
          if matchNuisance :
            #print "matchNuisance[", nuisance_to_test, "] -> ", nuisance
            # relative variation
            nuisance_to_be_removed_samples = {}
            
            for sample in reducedsampleName:
              nameTempUp   = "histo_"+str(sample)+"_"+str(nuisance)+"Up"
              nameTempDown = "histo_"+str(sample)+"_"+str(nuisance)+"Down"
              nameTemp     = "histo_"+str(sample)
              
              if nameTempUp in histograms.keys() and  nameTempDown in histograms.keys() : 
                #print 'nameTemp = ', nameTemp
                #print 'nameTempUp   = ', nameTempUp
                #print 'nameTempDown = ', nameTempDown
                
                histo_nominal = histograms[nameTemp] 
                histo_up   = histograms[nameTempUp] 
                histo_down = histograms[nameTempDown] 
                
                max_var_up = 0
                max_var_down = 0
                
                for ibin in range( histo_nominal.GetNbinsX() ) :
                  nominal = histo_nominal.GetBinContent(ibin+1)
                  up      = histo_up.GetBinContent(ibin+1)
                  down    = histo_down.GetBinContent(ibin+1)
                  
                  # calculate maximum relative variation
                  #  - if for any reason I have negative entries, that nuisance is kept!
                  if nominal > 0 :
                    if max_var_up < abs((nominal - up)/math.sqrt(nominal)) : 
                      max_var_up = abs((nominal - up)/math.sqrt(nominal))
                    if max_var_down < abs((nominal - down)/math.sqrt(nominal)) : 
                      max_var_down = abs((nominal - down)/math.sqrt(nominal))
                
                # save the value
                nuisance_to_be_removed_samples[sample] = (max_var_down, max_var_up)
                 
            max_variation = 0     
            for sampleNameToCheck, values in nuisance_to_be_removed_samples.iteritems() :
              if max_variation < values[0] or  max_variation < values[1] :
                max_variation = max(values[0], values[1])
            
            # default value of threshold is 0.10
            if max_variation < threshold :
              nuisance_to_be_removed.append(nuisance)
              print " To be removed: ", nuisance, " --> ", max_variation
             
 

    # write new datacard
    filename = datacardnameOut
    f = open(filename, 'w')

    # header
    for line in header: f.write (line + '\n')

    f.write ("---------------------------------------------------------------------------------------------------- \n")
    # bin name
    f.write ("bin ")
    for it in range (len (binName)) :
      f.write (binName[it] + ' ')
    f.write ("\n")

    # observation
    for it in range (len (observation)) :
      f.write (observation[it] + '\n')

    f.write ("---------------------------------------------------------------------------------------------------- \n")
    # long list of bin
    for it in range (len (longListBin)) :
      f.write (longListBin[it] + '\n')

    # process names (a.k.a. samples)
    f.write ("process ")
    for it in range (len (sampleName)) :
      f.write (sampleName[it] + ' ')
    f.write ("\n")

    # long list of rate indexes
    for it in range (len (longListRateIndex)) :
      f.write (longListRateIndex[it] + '\n')


    # rate
    f.write ("rate ")
    for it in range (len (sampleRate)) :
      f.write (str(sampleRate[it]) + ' ')
    f.write ("\n")


    # systematics
    f.write ("---------------------------------------------------------------------------------------------------- \n")
    numSyst = 0
    for nuisance in systematicsName :
      if nuisance not in nuisance_to_be_removed :
        f.write (systematics[numSyst] + '\n')
      numSyst+=1


    f.close ()


######################################


if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-d", "--datacard",           dest="datacardInput",          help="datacard name", metavar="DATACARD")
    parser.add_option("-o", "--outdatacard",        dest="datacardOutput",         help="datacard name output", metavar="DATACARD")
    parser.add_option("-i", "--inputConfiguration", dest="nameFileConfiguration",  help="name configuration file with nuisances to remove", default='blabla.py')
    parser.add_option("-t", "--threshold",          dest="threshold",              help="threshold", default=0.10,  type='float')

    (options, args) = parser.parse_args()

    PruneDatacard (options.datacardInput, options.datacardOutput, options.nameFileConfiguration,  options.threshold)
    
    print "options.threshold = ", options.threshold
    


