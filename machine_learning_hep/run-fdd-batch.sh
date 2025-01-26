#!/bin/bash

source "${HOME}/Run3Analysisvalidation/exec/utilities.sh"

WORKDIR="${HOME}/MachineLearningHEP/machine_learning_hep/"
DATABASE="${WORKDIR}/data/data_run3/database_ml_parameters_LcToPKPi_multiclass_fdd"
DATABASE_EXT="${DATABASE}.yml"
RESDIR_PATTERN="results-24012025-hyp-ml_"

fd=0.0

for bkg in $(seq 0.55 0.05 0.80) ; do
  echo "bkg ${bkg}"

  suffix="bkg_${bkg}"
  RESDIR="${RESDIR_PATTERN}${suffix}"
  RESPATH="/data8/majak/MLHEP/${RESDIR}/"

  #rm -rf "${RESPATH}"

  CUR_DB="${DATABASE}_edit_bkg${bkg}.yml"
  cp "${DATABASE_EXT}" "${CUR_DB}" || ErrExit "Could not copy database"

  sed -i "s/%resdir%/${RESDIR}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%bkg12%/${bkg}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%bkg23%/${bkg}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%bkg34%/${bkg}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%bkg45%/${bkg}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%bkg56%/${bkg}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%bkg67%/${bkg}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%bkg78%/${bkg}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%bkg810%/${bkg}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%bkg1012%/${bkg}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%bkg1216%/${bkg}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%bkg1624%/${bkg}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%fd12%/${fd}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%fd23%/${fd}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%fd34%/${fd}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%fd45%/${fd}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%fd56%/${fd}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%fd68%/${fd}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%fd812%/${fd}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%fd1216%/${fd}/g" "${CUR_DB}" || ErrExit "Could not edit database"
  sed -i "s/%fd1624%/${fd}/g" "${CUR_DB}" || ErrExit "Could not edit database"

  yes | mlhep --log-file "logfile_${suffix}.log" \
      -a Run3analysis \
      --run-config submission/analyzer.yml \
      --database-analysis "${CUR_DB}" \
      --delete \
     > "debug_${suffix}.txt" 2>&1 || ErrExit "Analysis failed"

  mv fig/ ${RESPATH}/
done
