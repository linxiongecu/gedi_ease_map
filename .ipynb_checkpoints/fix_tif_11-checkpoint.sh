#!/bin/bash
python Step2_gedi_merge.py --name X3_Y9
python Step3getEASEtif.py --ease --geotif --name X3_Y9
python Step2_gedi_merge.py --name X3_Y8
python Step3getEASEtif.py --ease --geotif --name X3_Y8
python Step2_gedi_merge.py --name X3_Y7
python Step3getEASEtif.py --ease --geotif --name X3_Y7
python Step2_gedi_merge.py --name X3_Y6
python Step3getEASEtif.py --ease --geotif --name X3_Y6
python Step2_gedi_merge.py --name X7_Y4
python Step3getEASEtif.py --ease --geotif --name X7_Y4
python Step2_gedi_merge.py --name X8_Y5
python Step3getEASEtif.py --ease --geotif --name X8_Y5
python Step2_gedi_merge.py --name X8_Y6
python Step3getEASEtif.py --ease --geotif --name X8_Y6
