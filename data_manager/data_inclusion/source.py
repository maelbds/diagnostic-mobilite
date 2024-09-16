from api_diago.resources.common.db_request import db_request

try:
        date_di = db_request(
                """ SELECT saved_on
                    FROM datainclusion_structures 
                    LIMIT 1
                """, {}).scalar().strftime("%d %b %Y")
except:
        date_di = "erreur mise à jour"


SOURCE_DATA_INCLUSION = "datainclusion"
source_data_inclusion_label = f"Data-Inclusion (au {date_di})"
source_data_inclusion_link = "https://www.data.inclusion.beta.gouv.fr/"

