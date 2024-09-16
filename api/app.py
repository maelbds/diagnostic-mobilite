from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from api.resources.general.datasets import Datasets
from api.resources.general.geography import Geography
from api.resources.mobility.flows import Flows
from api.resources.mobility.focus_home_not_work import FocusHomeNotWork
from api.resources.mobility.focus_home_work import FocusHomeWork
from api.resources.mobility.key_figures import KeyFiguresMobility
from api.resources.mobility.modes import Modes
from api.resources.mobility.origin import Origin
from api.resources.mobility.reasons import Reasons

from api.resources.offer.bnlc import BNLC
from api.resources.offer.critair import Critair
from api.resources.offer.cycle_parkings import CycleParkings
from api.resources.offer.cycle_paths import CyclePaths
from api.resources.offer.households_motorisation import HouseholdsMotorisation
from api.resources.offer.irve import IRVE

from api.resources.offer.railways import Railways
from api.resources.offer.train_stations import TrainStations
from api.resources.offer.public_transport import PublicTransport
from api.resources.offer.zfe import ZFE
from api.resources.stats.stats import Stats, get_stats
from api.resources.stats.stats_com import get_stats_com
from api.resources.territory.education import Education
from api.resources.territory.grocery import Grocery
from api.resources.territory.health import Health
from api.resources.territory.incomes import Incomes
from api.resources.territory.jobs import Jobs
from api.resources.territory.key_figures import KeyFigures
from api.resources.territory.pop_status import Pop_Status
from api.resources.territory.services_clusters import ServicesCluster
from api.resources.territory.work_flows import WorkFlows

from api.resources.territory.population import Population
from api.resources.territory.pop_csp import Pop_CSP
from api.resources.territory.gridded_pop import GriddedPop
from api.resources.territory.precariousness import Precariousness
from api.resources.territory.work_flows_outside import WorkFlowsOutside

app = Flask(__name__)
app.secret_key = "b86156ab11a155274a7c2471c6ac5f90162ae0709cb081de186e21bd2c81821b"

CORS(app, supports_credentials=True)
api = Api(app)


# initialization
api.add_resource(Geography, '/api/main/general/geography')
# api.add_resource(Sources, '/api/main/general/sources')
api.add_resource(Datasets, '/api/main/general/datasets')

api.add_resource(KeyFigures, '/api/main/territory/key_figures')

api.add_resource(Population, '/api/main/territory/population')
api.add_resource(Pop_CSP, '/api/main/territory/pop_csp')
api.add_resource(Pop_Status, '/api/main/territory/pop_status')
api.add_resource(GriddedPop, '/api/main/territory/gridded_pop')

api.add_resource(Incomes, '/api/main/territory/incomes')
api.add_resource(Precariousness, '/api/main/territory/precariousness')

api.add_resource(Jobs, '/api/main/territory/jobs')
api.add_resource(WorkFlows, '/api/main/territory/work_flows')
api.add_resource(WorkFlowsOutside, '/api/main/territory/work_flows_outside')

api.add_resource(Education, '/api/main/territory/education')
api.add_resource(Health, '/api/main/territory/health')
api.add_resource(Grocery, '/api/main/territory/grocery')
api.add_resource(ServicesCluster, '/api/main/territory/services_cluster')

api.add_resource(HouseholdsMotorisation, '/api/main/offer/households_motorisation')
api.add_resource(Critair, '/api/main/offer/critair')
api.add_resource(ZFE, '/api/main/offer/zfe')

api.add_resource(CyclePaths, '/api/main/offer/cycle_paths')
api.add_resource(CycleParkings, '/api/main/offer/cycle_parkings')

api.add_resource(IRVE, '/api/main/offer/irve')
api.add_resource(BNLC, '/api/main/offer/bnlc')

api.add_resource(PublicTransport, '/api/main/offer/public_transport')
api.add_resource(Railways, '/api/main/offer/railways')
api.add_resource(TrainStations, '/api/main/offer/train_stations')

api.add_resource(Origin, '/api/main/mobility/origin')
api.add_resource(Modes, '/api/main/mobility/modes')
api.add_resource(Reasons, '/api/main/mobility/reasons')
api.add_resource(Flows, '/api/main/mobility/flows')
api.add_resource(FocusHomeWork, '/api/main/mobility/focus_home_work')
api.add_resource(FocusHomeNotWork, '/api/main/mobility/focus_home_not_work')
api.add_resource(KeyFiguresMobility, '/api/main/mobility/key_figures')


@app.route("/api/main/stats")
def stats():
    return get_stats()


@app.route("/api/main/stats_com")
def stats_com():
    return get_stats_com()


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'max-age=604800'
    #response.headers['Cache-Control'] = 'no-cache'
    return response


if __name__ == '__main__':
    app.run(debug=False)

