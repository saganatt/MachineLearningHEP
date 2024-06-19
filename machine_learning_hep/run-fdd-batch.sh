#!/bin/bash

source "${HOME}/Run3Analysisvalidation/exec/utilities.sh"

WORKDIR="${HOME}/MachineLearningHEP/machine_learning_hep/"
DATABASE="${WORKDIR}/data/data_run3/database_ml_parameters_LcToPKPi_multiclass_fdd"
DATABASE_EXT="${DATABASE}.yml"

for fd in $(seq 0.1 0.05 0.95) ; do
  echo "fd ${fd}"
  
  RESDIR_PATTERN="results-bkg_0624_fd_"
  RESDIR="${RESDIR_PATTERN}${fd}\/"
  RESPATH="/data8/majak/MLHEP/${RESDIR}/"
  
  rm -rf "${RESPATH}"
  
  CUR_DB="${DATABASE}_edit_fd${fd}.yml"
  cp "${DATABASE_EXT}" "${CUR_DB}" || ErrExit "Could not copy database"

  sed -i "s/${RESDIR_PATTERN}.*/${RESDIR}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%fd%/${fd}/g" "${CUR_DB}" || ErrExit "Could not edit database"

  cat ${CUR_DB}

  mlhep --log-file "logfile_fd${fd}.log" \
      --run-config submission/default_complete.yml \
      --database-analysis ${CUR_DB} \
      --delete
done
