#!/bin/bash

source "${HOME}/Run3Analysisvalidation/exec/utilities.sh"

WORKDIR="${HOME}/MachineLearningHEP/machine_learning_hep/"
DATABASE="${WORKDIR}/data/data_run3/database_ml_parameters_LcToPKPi_multiclass_fdd"
DATABASE_EXT="${DATABASE}.yml"

for bkg in $(seq 0.35 0.05 0.5) ; do
  echo "bkg ${bkg}"

  RESDIR_PATTERN="results-bkg_0624_"
  RESDIR="${RESDIR_PATTERN}${bkg}\/"
  RESPATH="/data8/majak/MLHEP/${RESDIR}"
  
  rm -rf "${RESPATH}"
  
  CUR_DB="${DATABASE}_edit_bkg${bkg}.yml"
  cp "${DATABASE_EXT}" "${CUR_DB}" || ErrExit "Could not copy database"

  sed -i "s/${RESDIR_PATTERN}.*/${RESDIR}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%bkg%/${bkg}/g" "${CUR_DB}" || ErrExit "Could not edit database"

  mlhep --log-file "logfile_bkg${bkg}.log" \
      --run-config submission/default_complete.yml \
      --database-analysis ${CUR_DB} \
      --delete 
done
