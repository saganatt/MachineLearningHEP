#!/bin/bash

MLHEP_DIR="/data8/majak/MLHEP"
OUTPUT_DIR="${MLHEP_DIR}/pass6-input-fdd-rebin"

for fd in $(seq 0 5 90; seq 92 2 98) ; do
  RESDIR="results-fd_${fd}-bkg_0524-rebin"

  cp "${MLHEP_DIR}/${RESDIR}/LHC22pp_mc/Results/prod_LHC24d3/resultsmctot/efficienciesLcpKpiRun3analysis.root" \
     "${OUTPUT_DIR}/efficienciesLcpKpiRun3analysis-fd_${fd}.root"
  cp "${MLHEP_DIR}/${RESDIR}/LHC22pp/Results/resultsdatatot/Yields_LcpKpi_Run3analysis.root" \
     "${OUTPUT_DIR}/yieldsLcpKpiRun3analysis-fd_${fd}.root"
done
