rem Batch file for ccx with PaSTiX/SPOOLES/ITerative solvers
rem @echo off

rem ==== Set path to CalculiX executable here ====
set CCX_PATH=C:\Tools\CalculiX

rem ==== CalculiX settings ========
set CCX_NPROC_RESULTS=%NUMBER_OF_PROCESSORS%   
set CCX_NPROC_STIFFNESS=%NUMBER_OF_PROCESSORS%
set OMP_NUM_THREADS=%NUMBER_OF_PROCESSORS%

rem ==== PasTiX settings ===========
set OPENBLAS_NUM_THREADS=1
rem Must be used for this version
set PASTIX_MIXED_PRECISION=1
rem 1 - yes(*), 0 - no
set PASTIX_ORDERING=0
rem   0 - Scotch(*), 1 - Metis 
set PASTIX_SCHEDULER=0
rem 0 - Static(*), 1 - StarPU, 3 - Sequential, 2 - parsec (not working yet)

rem === Final CCX run command (output in the Exodus II format) === 
%CCX_PATH%\ccx_pastix_exodus.exe -i %~n1 -o exo
