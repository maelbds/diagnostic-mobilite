from api_diago.resources.common.db_request import db_request


date_cycle_parkings = db_request(
        """ SELECT saved_on
            FROM transportdatagouv_cycle_parkings 
            LIMIT 1
        """, {}).scalar().strftime("%m/%Y")

date_cycle_paths = db_request(
        """ SELECT saved_on
            FROM transportdatagouv_cycle_paths 
            LIMIT 1
        """, {}).scalar().strftime("%m/%Y")

date_bnlc = db_request(
        """ SELECT saved_on
            FROM transportdatagouv_bnlc 
            LIMIT 1
        """, {}).scalar().strftime("%m/%Y")

date_irve = db_request(
        """ SELECT saved_on
            FROM transportdatagouv_irve
            LIMIT 1
        """, {}).scalar().strftime("%m/%Y")


source_transportdatagouv_label = f"transport.data.gouv.fr - Point d’Accès National aux données de transport ({date_cycle_paths})"
source_transportdatagouv_link = "https://transport.data.gouv.fr/"

SOURCE_CYCLE_PATHS = "OSM"
source_transportdatagouv_cycle_paths_label = f"Base Nationale des Aménagements Cyclables - Export national OpenStreetMap ({date_cycle_paths})"
source_transportdatagouv_cycle_paths_link = "https://transport.data.gouv.fr/datasets/amenagements-cyclables-france-metropolitaine"

SOURCE_CYCLE_PARKINGS = "OSM"
source_transportdatagouv_cycle_parkings_label = f"Base Nationale du Stationnement Cyclable - Export OpenStreetMap ({date_cycle_parkings}) - © les contributeurs d’OpenStreetMap sous licence ODbL"
source_transportdatagouv_cycle_parkings_link = "https://transport.data.gouv.fr/datasets/stationnements-cyclables-issus-dopenstreetmap"

SOURCE_IRVE = "IRVE"
source_transportdatagouv_irve_label = f"Infrastructures de Recharge pour Véhicules Électriques - IRVE ({date_irve})"
source_transportdatagouv_irve_link = "https://transport.data.gouv.fr/datasets/fichier-consolide-des-bornes-de-recharge-pour-vehicules-electriques"

SOURCE_BNLC = "BNLC"
source_transportdatagouv_bnlc_label = f"Base nationale consolidée des lieux de covoiturage ({date_bnlc})"
source_transportdatagouv_bnlc_link = "https://transport.data.gouv.fr/datasets/base-nationale-des-lieux-de-covoiturage"

SOURCE_ZFE= "ZFE_20221103"
source_transportdatagouv_zfe_label = "Base Nationale des Zones à Faibles Émissions (Nov 2022)"
source_transportdatagouv_zfe_link = "https://transport.data.gouv.fr/datasets/base-nationale-consolidee-des-zones-a-faibles-emissions"

SOURCE_COVOITURAGE= "2022_12"
source_covoiturage_label = "Registre de Preuve de Covoiturage (2022)"
source_covoiturage_link = "https://www.data.gouv.fr/fr/datasets/trajets-realises-en-covoiturage-registre-de-preuve-de-covoiturage/#/resource"

