#!/bin/bash

source "/home/mkabus/Run3Analysisvalidation/exec/utilities.sh"

WORKDIR="/home/mkabus/MachineLearningHEP/machine_learning_hep/"
DATABASE="${WORKDIR}/data/data_run3/database_ml_parameters_LcToPKPi_multiclass"
DATABASE_EXT="${DATABASE}.yml"

for fd in `seq 0 10 90` ; do
  echo "fd ${fd}"
  
  RESDIR="results-multiclass-fd_${fd}-bkg_rv-new"
  RESPATH="/data2/mkabus/MLHEP/${RESDIR}/"
  rm -rf "${RESPATH}"
  
  CUR_DB="${DATABASE}_edit_fd${fd}.yml"
  cp "${DATABASE_EXT}" "${CUR_DB}" || ErrExit "Could not copy database"

  sed -i "s/results-multiclass-fd_.*-bkg_rv/${RESDIR}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%fd%/0.${fd}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  
  python do_entire_analysis.py -r submission/default_complete.yml -d "${CUR_DB}" > "debug_fd${fd}.txt" 2>&1 || ErrExit "Analysis failed"
  #cat ${CUR_DB}
done
