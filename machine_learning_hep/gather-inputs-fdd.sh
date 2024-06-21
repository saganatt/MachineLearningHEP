#!/bin/bash

MLHEP_DIR="/data8/majak/MLHEP"
OUTPUT_DIR="${MLHEP_DIR}/input-fd_batch_0624"

RESDIR_PATTERN="${MLHEP_DIR}/results-bkg_0624_fd_"

for dir in ${RESDIR_PATTERN}* ; do
  suffix=${dir##${RESDIR_PATTERN}}
  echo $suffix

  cp "${dir}/LHC22pp_mc/Results/prod_LHC24d3b/resultsmctot/efficienciesLcpKpiRun3analysis.root" \
     "${OUTPUT_DIR}/efficienciesLcpKpiRun3analysis-fd_${suffix}.root"
  cp "${dir}/LHC22pp/Results/resultsdatatot/Yields_LcpKpi_Run3analysis.root" \
     "${OUTPUT_DIR}/yieldsLcpKpiRun3analysis-fd_${suffix}.root"
done
