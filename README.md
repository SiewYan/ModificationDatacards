ModificationDatacards
=====================

Several scripts to modify datacards

Example working folder:

    cmsneu/lxplus
    /afs/cern.ch/user/a/amassiro/Limit/ModificationDatacards

    /home/amassiro/Cern/Code/VBF/RepositoryDataCardNewLumi/summer2013/ModificationDatacards

Kate:

    lxplus-Combine
    

# Setup combine

See: https://cms-hcomb.gitbooks.io/combine/content/part1/#for-end-users-that-dont-need-to-commit-or-do-any-development


    cd ~/Framework/Combine/CMSSW_8_1_0/src/    
    eval `scramv1 runtime -sh`
    cd -

# Remove samples with expected yield below a given threshold

Check the yield of given samples in some or all categories, and remove the sample if the yield is below some threshold (default threshold = 9999999...)

    python RemoveSample.py datacard.txt -o outdatacard.txt -i inputRemoveName.py --threshold 0.01

In order to check all samples in the datacard use the 'ALL' tag in the input file, i.e.:

    python RemoveSample.py datacard.txt -o outdatacard.txt -i inputRemoveAllSamplesBelowThreshold.py --threshold 0.01

    
    
# Prune nuisances

Check if a nuisance, selected by a string match with wild cards, has an effect smaller than A %.
If yes, remove the nuisance.
Create a copy of the datacard, do not touch the root file.

    python PruneDatacard.py  -d hwwof_shape.txt  -o hwwof_shape_pruned.txt  -i nuisances_to_prune.py
    
    python PruneDatacard.py  \
        -d /afs/cern.ch/user/a/amassiro/Framework/CMSSW_7_6_3/src/PlotsConfigurations/Configurations/ggHTest/datacards/hww2l2v_13TeV_em_0j/mllVSmth/datacard.txt  \
        -o datacard.test.txt  \
        -i examples/input_nuisances_to_prune.py    
    
    python PruneDatacard.py  \
        -d /afs/cern.ch/user/a/amassiro/Framework/CMSSW_7_6_3/src/PlotsConfigurations/Configurations/ggHTest/datacards/hww2l2v_13TeV_me_1j/mllVSmth/datacard.txt  \
        -o datacard.test.txt  \
        -i examples/input_nuisances_to_prune.py    
    
    python PruneDatacard.py  \
         -d /afs/cern.ch/user/a/amassiro/Framework/CMSSW_8_0_5/src/PlotsConfigurations/Configurations/VBF/datacards/hww2l2v_13TeV_top_of2j_vbf/events/datacard.txt \
         -o /afs/cern.ch/user/a/amassiro/Framework/CMSSW_8_0_5/src/PlotsConfigurations/Configurations/VBF/datacards/hww2l2v_13TeV_top_of2j_vbf/events/datacard.txt.pruned.txt \
         --suppressNegative=True  --suppressFluctuationError=True -i examples/input_nuisances_to_prune_aggressive.py

    
    
# Scale one sample by a factor

    python ScaleOneSample.py  -d hwwof_2j_shape_7TeV.txt    -i inputScale7TeV.py

and for multi-modifications:

    bash examples/doScale125to126GeV.sh


# Change the name of one sample

    python ChangeName.py        -d   hww-19.36fb.mH125.txt    -i   inputName.py


# Scale one nuisance

    python ScaleOneNuisance.py  -d   hww-19.36fb.mH125.txt    -i   inputScaleNuisance.py

# Transform gmN into lnN

  transform gmN into lnN.
  To easy perform signal injection without any bias (bug in combine?) and to remove gmN in case of "many" events in control region

    python TransformGmN.py  -d   hww-19.36fb.mH125.txt


# Transform shape datacard into cut based one

  transform a shape based datacard into a cut based one.
  To be performed for:
    * check of the gain of shape analysis, w.r.t just merging
    * easy read a simple cut based analysis, created through the shape package

    python TransformShapeToCutBased.py  -d   hww-19.36fb.mH125_toBeUsed.txt


# Clone one sample:
  clone one sample into a sample with a new name. Used to split VH into ZH and WH.
  Only for cut based datacard!
  Nuisances are "cloned" to the new sample.
  No new nuisances are added

    python CloneSample.py    hww-19.36fb.mH125.sf_0j_shape.txt     -i   inputClonedName.py


# Remove one sample:
  remove one sample from the datacard. Used to remove useless (0) ttH sample

    python RemoveSample.py   hww-19.36fb.mH125.sf_0j_shape.txt    -i   inputRemoveName.py

 example:

    bash examples/doRemoveTTH.sh

    bash examples/doTransformSVNDatacardsSearchesCouplings.sh



# Change name of nuisances

  change the name of the nuisances in the datacard,
  for example "met" into "met_res" or adding "_7TeV" on some nuisances.

    python ChangeNameNuisance.py  -d   hww-19.36fb.mH125_toBeUsed.txt      -i   inputNameNuisance.py



# Specific examples



e.g.

    python ../ScaleOneNuisance.py  -d   hwwof_0j_shape_8TeV.txt  -i   ../inputScaleNuisance.py
    cd /afs/cern.ch/user/a/amassiro/scratch0/VBF/Limit/CMSSW_6_1_0/src
    export SCRAM_ARCH=slc5_amd64_gcc462
    cmsenv
    cd -
    combine hwwof_0j_shape_8TeV.txt  -M MaxLikelihoodFit  --rMin=-1 --expectSignal=1 -t -1

    combineCards.py -S sf0j=hwwsf_0j_cut_8TeV.txt sf1j=hwwsf_1j_cut_8TeV.txt of0j=hwwof_0j_shape_8TeV.txt of1j=hwwof_1j_shape_8TeV.txt > total.txt


e.g. for ww


    cd /afs/cern.ch/user/a/amassiro/Limit/ModificationDatacards
    mkdir ww
    scp amassiro@cmsneu:/home/amassiro/Latinos/Shape/playground/WW?Fcut?jet.tgz ww/
    cd ww
    tar -xf WWDFcut0jet.tgz
    mv datacards  WWDFcut0jet
    tar -xf WWDFcut1jet.tgz
    mv datacards  WWDFcut1jet
    tar -xf WWSFcut0jet.tgz
    mv datacards  WWSFcut0jet
    tar -xf WWSFcut1jet.tgz
    mv datacards  WWSFcut1jet

    cd WWDFcut0jet
    python ../../TransformShapeToCutBased.py  -d   hww-19.36fb.mH125.of_0j_shape.txt
    cd ..
    cd WWDFcut1jet
    python ../../TransformShapeToCutBased.py  -d   hww-19.36fb.mH125.of_1j_shape.txt
    cd ..
    cd WWSFcut0jet
    python ../../TransformShapeToCutBased.py  -d   hww-19.36fb.mH125.sf_0j_shape.txt
    cd ..
    cd WWSFcut1jet
    python ../../TransformShapeToCutBased.py  -d   hww-19.36fb.mH125.sf_1j_shape.txt
    cd ..

    rm -r WW?Fcut?jet/shapes/



e.g. for hwidth hww


    cd /afs/cern.ch/user/a/amassiro/Limit/ModificationDatacards
    mkdir hwidth
    scp amassiro@cmsneu:/home/amassiro/Latinos/Shape/playground/Hwidth/?jetDF8TeV.tgz  hwidth/
    cd hwidth
    tar -xf 0jetDF8TeV.tgz
    mv datacards  0jetDF8TeV
    tar -xf 1jetDF8TeV.tgz
    mv datacards  1jetDF8TeV
    tar -xf 2jetDF8TeV.tgz
    mv datacards  2jetDF8TeV

    cd 0jetDF8TeV
    python ../../TransformShapeToCutBased.py  -d   hww-19.36fb.mH125.of_0j_shape.txt
    cd ..
    cd 1jetDF8TeV
    python ../../TransformShapeToCutBased.py  -d   hww-19.36fb.mH125.of_1j_shape.txt
    cd ..
    cd 2jetDF8TeV
    python ../../TransformShapeToCutBased.py  -d   hww-19.36fb.mH125.of_2j_shape.txt
    cd ..

    rm -r ?jetDF8TeV/shapes/




e.g. for svn datacards https://svnweb.cern.ch/cern/wsvn/cmshcg/trunk/summer2013/

    mkdir couplings
    cd couplings
    svn co  svn+ssh://amassiro@svn.cern.ch/reps/cmshcg/trunk/summer2013/couplings/vhww

change VH into ZH and WH: 1.2427/0.4300 = WH/ZH:
  WH = 74%
  ZH = 26%



   svn co  svn+ssh://amassiro@svn.cern.ch/reps/cmshcg/trunk/summer2013/searches/hww2l2v
   svn co  svn+ssh://amassiro@svn.cern.ch/reps/cmshcg/trunk/summer2013/searches/vhww









