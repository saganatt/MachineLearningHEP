#!/bin/bash

#python run-mlhep-fitter-multitrial.py || exit 1

DIR_PATH="/data8/majak/MLHEP"
DB_PATTERN="LcMult"
DIR_PATTERN="results-24022025-luigi-multitrial-mult-prompt"
MULTITRIAL_DIR="/data8/majak/MLHEP/multitrial-mult-prompt"
ext=".yml"

BASE_DIR="/data8/majak/MLHEP/results-24022025-luigi-mult"
DATA_HIST="LHC23pp/Results/resultsdatatot/masshisto.root",
MC_HIST="LHC23pp_mc_tuner_mult/Results/resultsmctot/masshisto.root",
#"LHC24pp_mc/Results/resultsmctot/effhisto.root",
#"LHC24pp_mc/Results/resultsmctot/efficienciesLcpKpiRun3analysis.root"

for db in multitrial-mult-db/* ; do
  db_basename=`basename ${db}`
  db_basename_no_ext=${db_basename%%${ext}}
  echo ${db_basename_no_ext}
  suffix=${db_basename_no_ext##${DB_PATTERN}}
  echo "suffix: ${suffix}"
  RESPATH="${DIR_PATH}/${DIR_PATTERN}${suffix}"
  echo "respath: ${RESPATH}"

  ./run-lc.sh ${db} submission/analyzer.yml logfile_${db_basename}.log

  cp "${BASE_DIR}/${DATA_HIST}" "${RESPATH}/${DATA_HIST}"
  cp "${BASE_DIR}/${MC_HIST}" "${RESPATH}/${MC_HIST}"

  #rm -rf ${RESPATH}/fig/
  #mv fig/ ${RESPATH}/fig/

  #cp -r "${RESPATH}/fig/LcpKpi/Run3analysis/roofit/" "${MULTITRIAL_DIR}/fig${suffix}"
done

