#!/bin/bash
python3 /home/app/opta/soccer_pipeline.py --folder_name All --competitie_name "Eredivisie 22-23" --competitie_id d1k1pqdg2yvw8e8my74yvrdw4 --outletAuthKey outletAuthKey_ereD
python3 /home/app/opta/soccer_pipeline.py --folder_name All --competitie_name "Eredivisie 21-22" --competitie_id dp0vwa5cfgx2e733gg98gfhg4 --outletAuthKey outletAuthKey_ereD
rm -rf /home/app/pages/data/*