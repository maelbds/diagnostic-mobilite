from flask_restful import Resource

from api.resources.mobility.flows import dataset_flows
from api.resources.offer.bnlc import dataset_bnlc
from api.resources.offer.critair import dataset_critair
from api.resources.offer.cycle_parkings import dataset_cycle_parkings
from api.resources.offer.cycle_paths import dataset_cycle_paths
from api.resources.offer.households_motorisation import dataset_households_motorisation
from api.resources.offer.irve import dataset_irve
from api.resources.offer.public_transport import dataset_public_transport
from api.resources.offer.railways import dataset_railways
from api.resources.offer.train_stations import dataset_train_stations
from api.resources.offer.zfe import dataset_zfe
from api.resources.territory.education import dataset_education

from api.resources.territory.gridded_pop import dataset_gridded_pop
from api.resources.territory.grocery import dataset_grocery
from api.resources.territory.health import dataset_health
from api.resources.territory.incomes import dataset_incomes
from api.resources.territory.jobs import dataset_jobs
from api.resources.territory.pop_csp import dataset_pop_csp
from api.resources.territory.pop_status import dataset_pop_status
from api.resources.territory.population import dataset_population
from api.resources.territory.precariousness import dataset_precariousness
from api.resources.territory.services_clusters import dataset_services_cluster
from api.resources.territory.work_flows import dataset_work_flows
from api.resources.territory.work_flows_outside import dataset_work_flows_outside


class Datasets(Resource):
    def get(self):
        return {
            "territory/population": dataset_population,
            "territory/pop_csp": dataset_pop_csp,
            "territory/pop_status": dataset_pop_status,
            "territory/gridded_pop": dataset_gridded_pop,
            "territory/incomes": dataset_incomes,
            "territory/precariousness": dataset_precariousness,
            "territory/jobs": dataset_jobs,
            "territory/work_flows": dataset_work_flows,
            "territory/work_flows_outside": dataset_work_flows_outside,
            "territory/education": dataset_education,
            "territory/health": dataset_health,
            "territory/grocery": dataset_grocery,
            "territory/services_cluster": dataset_services_cluster,

            "offer/households_motorisation": dataset_households_motorisation,
            "offer/critair": dataset_critair,
            "offer/zfe": dataset_zfe,
            "offer/cycle_paths": dataset_cycle_paths,
            "offer/cycle_parkings": dataset_cycle_parkings,
            "offer/irve": dataset_irve,
            "offer/bnlc": dataset_bnlc,
            "offer/public_transport": dataset_public_transport,
            "offer/railways": dataset_railways,
            "offer/train_stations": dataset_train_stations,

            "mobility/flows": dataset_flows,
        }
