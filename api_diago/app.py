from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from api_diago.resources.general.sources import Sources
from api_diago.resources.general.summary import Summary
from api_diago.resources.general.topography import Topography
from api_diago.resources.general.perimeters import Petr, Pnr, Arr, Perimeters
from api_diago.resources.inclusive_mobility.beneficiaries_insee import BeneficiariesInsee
from api_diago.resources.inclusive_mobility.services import ServicesGeocodes, Services
from api_diago.resources.inclusive_mobility.structures import Structures
from api_diago.resources.mobility.car_households import CarHouseholds
from api_diago.resources.mobility.carsharing import BNLC, RPC
from api_diago.resources.mobility.childhood import Childhood
from api_diago.resources.mobility.critair import Critair
from api_diago.resources.mobility.cycle import CyclePaths, CycleParkings
from api_diago.resources.mobility.health import Health
from api_diago.resources.mobility.irve import IRVE
from api_diago.resources.mobility.public_transport import PublicTransport
from api_diago.resources.mobility.railways import Railways
from api_diago.resources.mobility.roads import Roads
from api_diago.resources.mobility.security import Security
from api_diago.resources.mobility.services_dist import ServicesDist
from api_diago.resources.mobility.train_stations import TrainStations
from api_diago.resources.mobility.work_flows import WorkFlows
from api_diago.resources.population.eco_dependance_ind import EcoDependanceInd
from api_diago.resources.population.evol_rate import EvolRate
from api_diago.resources.population.households import Households
from api_diago.resources.population.p75_alone import P75Alone
from api_diago.resources.population.population import Population
from api_diago.resources.population.population_evolution import PopulationEvolution
from api_diago.resources.socio.allocation import Allocation
from api_diago.resources.socio.beneficiaries import Beneficiaries
from api_diago.resources.socio.foreigners import Foreigners
from api_diago.resources.socio.newcomers import Newcomers
from api_diago.resources.socio.part_time import PartTime
from api_diago.resources.socio.poverty import Poverty
from api_diago.resources.socio.precarious_jobs import PrecariousJobs
from api_diago.resources.socio.qpv import QPV
from api_diago.resources.territory.budget import BudgetCom, BudgetEpci
from api_diago.resources.territory.pole_emploi import PoleEmploiCommunes, PoleEmploiAgencies, \
    PoleEmploiPerimeters
from api_diago.resources.work.csp import CSP
from api_diago.resources.work.csp_migration import CSPMigration
from api_diago.resources.work.emp_rate import EmpRate
from api_diago.resources.work.jobs_applicants import JobsApplicants
from api_diago.resources.work.jobs_organisation import JobsOrganisation

app = Flask(__name__)
CORS(app)
api = Api(app)

# initialization
api.add_resource(Topography, '/api/general/topography')
api.add_resource(Sources, '/api/general/sources')

# general
api.add_resource(Petr, '/api/general/petr')
api.add_resource(Pnr, '/api/general/pnr')
api.add_resource(Arr, '/api/general/arr')
api.add_resource(Perimeters, '/api/general/perimeters')
api.add_resource(Summary, '/api/general/summary')

api.add_resource(BudgetCom, '/api/territory/budget_com')
api.add_resource(BudgetEpci, '/api/territory/budget_epci')

api.add_resource(PoleEmploiCommunes, '/api/territory/pole_emploi')
api.add_resource(PoleEmploiAgencies, '/api/territory/pole_emploi_agencies')
api.add_resource(PoleEmploiPerimeters, '/api/territory/pole_emploi_perimeters')

api.add_resource(Beneficiaries, '/api/socio/beneficiaries')
api.add_resource(PrecariousJobs, '/api/socio/precarious_jobs')
api.add_resource(PartTime, '/api/socio/part_time')
api.add_resource(QPV, '/api/socio/qpv')
api.add_resource(Foreigners, '/api/socio/foreigners')
api.add_resource(Newcomers, '/api/socio/newcomers')
api.add_resource(Poverty, '/api/socio/poverty')
api.add_resource(Allocation, '/api/socio/allocation')

api.add_resource(EmpRate, '/api/work/emp_rate')
api.add_resource(JobsOrganisation, '/api/work/jobs_organisation')
api.add_resource(JobsApplicants, '/api/work/jobs_applicants')
api.add_resource(CSP, '/api/work/csp')
api.add_resource(CSPMigration, '/api/work/csp_migration')

api.add_resource(Population, '/api/population/population')
api.add_resource(Households, '/api/population/households')
api.add_resource(PopulationEvolution, '/api/population/population_evolution')
api.add_resource(EcoDependanceInd, '/api/population/eco_dependance_ind')
api.add_resource(P75Alone, '/api/population/p75_alone')
api.add_resource(EvolRate, '/api/population/evol_rate')

api.add_resource(PublicTransport, '/api/mobility/public_transport')
api.add_resource(Railways, '/api/mobility/railways')
api.add_resource(TrainStations, '/api/mobility/train_stations')
api.add_resource(IRVE, '/api/mobility/irve')
api.add_resource(CyclePaths, '/api/mobility/cycle_paths')
api.add_resource(CycleParkings, '/api/mobility/cycle_parkings')
api.add_resource(BNLC, '/api/mobility/bnlc')
api.add_resource(RPC, '/api/mobility/rpc')
api.add_resource(Roads, '/api/mobility/roads')
api.add_resource(CarHouseholds, '/api/mobility/car_households')
api.add_resource(Critair, '/api/mobility/critair')
api.add_resource(Security, '/api/mobility/security')

api.add_resource(ServicesDist, '/api/mobility/services_dist')
api.add_resource(Health, '/api/mobility/health')
api.add_resource(Childhood, '/api/mobility/childhood')

api.add_resource(WorkFlows, '/api/mobility/work_flows')

api.add_resource(Structures, '/api/inclusive_mobility/structures')
api.add_resource(Services, '/api/inclusive_mobility/services')
api.add_resource(ServicesGeocodes, '/api/inclusive_mobility/services_geocodes')

api.add_resource(BeneficiariesInsee, '/api/inclusive_mobility/beneficiaries_insee')

if __name__ == '__main__':
    app.run(debug=False)

