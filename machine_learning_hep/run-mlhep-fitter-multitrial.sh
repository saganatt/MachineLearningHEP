#!/bin/bash

DB_PATTERN="database_ml_parameters_LcToPKPi_multiclass_fdd"
DB_DIR="data/data_run3"
OUT_DB_DIR="multitrial-db"
ext=".yml"

DIR_PATH="/data8/majak/MLHEP"
DIR_PATTERN="results-24022025-newtrain-multitrial-prompt"
MULTITRIAL_DIR="/data8/majak/MLHEP/multitrial-prompt"

BASE_DIR="/data8/majak/MLHEP/results-24022025-newtrain-ptshape-prompt"
DATA_HIST="LHC23pp/Results/resultsdatatot/masshisto.root"
MC_HIST="LHC24pp_mc/Results/resultsmctot/masshisto.root"

#python run-mlhep-fitter-multitrial.py "${DB_PATTERN}" "${DB_DIR}" "${OUT_DB_DIR}" "${DIR_PATTERN}" || exit 1

for db in ${OUT_DB_DIR}/*fdd.yml ; do
  db_basename=`basename ${db}`
  db_basename_no_ext=${db_basename%%${ext}}
  echo ${db_basename_no_ext}
  suffix=${db_basename_no_ext##${DB_PATTERN}}
  echo "suffix: ${suffix}"
  RESPATH="${DIR_PATH}/${DIR_PATTERN}${suffix}"
  echo "respath: ${RESPATH}"

  ./run-lc.sh ${db} submission/analyzer.yml logfile_${db_basename}.log

  #cp "${BASE_DIR}/${DATA_HIST}" "${RESPATH}/${DATA_HIST}"
  #cp "${BASE_DIR}/${MC_HIST}" "${RESPATH}/${MC_HIST}"

  #rm -rf ${RESPATH}/fig/
  #mv fig/ ${RESPATH}/fig/

  #rm -rf "${MULTITRIAL_DIR}/fig${suffix}"
  #cp -r "${RESPATH}/fig/LcpKpi/Run3analysis/roofit/" "${MULTITRIAL_DIR}/fig${suffix}"
done

