#!/bin/bash

python run-mlhep-fitter-multitrial.py || exit 1

DIR_PATH="/data8/majak/MLHEP"
DB_PATTERN="database_ml_parameters_LcToPKPi_multiclass_fdd"
DIR_PATTERN="results-24022025-newtrain-multitrial-prompt"
MULTITRIAL_DIR="/data8/majak/MLHEP/multitrial-prompt"
ext=".yml"

for db in multitrial-db/* ; do
  db_basename=`basename ${db}`
  db_basename_no_ext=${db_basename%%${ext}}
  echo ${db_basename_no_ext}
  suffix=${db_basename_no_ext##${DB_PATTERN}}
  echo "suffix: ${suffix}"
  ./run-lc.sh ${db} submission/analyzer.yml logfile_${db_basename}.log

  RESPATH="${DIR_PATH}/${DIR_PATTERN}${suffix}"
  echo "respath: ${RESPATH}"
  rm -rf ${RESPATH}/fig/
  mv fig/ ${RESPATH}/

  cp -r "${RESPATH}/fig/LcpKpi/Run3analysis/roofit/" "${MULTITRIAL_DIR}/fig${suffix}"
done 

