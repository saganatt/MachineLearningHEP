#!/bin/bash

source "/home/mkabus/Run3Analysisvalidation/exec/utilities.sh"
YIELDS="Yields_LcpKpi_Run3analysis.root"
YIELDS_2="yields_LcpKpi_Run3analysis.root"

for fd in `seq 0 10 90` ; do
  echo "fd ${fd}"
  
  RESDIR="/data2/mkabus/MLHEP/results-multiclass-fd_${fd}-bkg_rv/LHC22pp/Results/resultsdatatot"
  RES_YIELDS="${RESDIR}/Yields"
  RES_YIELDS_2="${RESDIR}/yields"
  mkdir ${RES_YIELDS} || ErrExit "Couldn't create ${RES_YIELDS}"
  mkdir ${RES_YIELDS_2} || ErrExit "Couldn't create ${RES_YIELDS_2}"
  ~/CERN-useful-scripts/root_to_png.py "${RESDIR}/${YIELDS}" "${RES_YIELDS}" || ErrExit "root_to_png failed for ${YIELDS}"
  ~/CERN-useful-scripts/root_to_png.py "${RESDIR}/${YIELDS_2}" "${RES_YIELDS_2}" || ErrExit "root_to_png failed for ${YIELDS_2}"
done
