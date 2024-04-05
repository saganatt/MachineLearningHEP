#!/bin/bash

for fd in `seq 0 10 90` ; do
  cp /data2/mkabus/MLHEP/results-multiclass-fd_${fd}-bkg_rv/LHC22pp_mc/Results/prod_LHC22/resultsmctot/efficienciesLcpKpiRun3analysis.root \
     /data2/mkabus/MLHEP/input-fdd/efficienciesLcpKpiRun3analysis-fd_${fd}.root
  cp /data2/mkabus/MLHEP/results-multiclass-fd_${fd}-bkg_rv/LHC22pp/Results/resultsdatatot/Yields_LcpKpi_Run3analysis.root \
     /data2/mkabus/MLHEP/input-fdd/yieldsLcpKpiRun3analysis-fd_${fd}.root
done
