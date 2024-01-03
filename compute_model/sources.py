
sources = {
    "gridded_pop": {
        "name": "Données carroyées (INSEE Filosofi 2017)",
        "link": "https://www.insee.fr/fr/statistiques/6214726?sommaire=6215217#dictionnaire",
        "year": "2017"
    },
    "census": {
        "name": "Recensement de la population (INSEE 2018)",
        "link": "https://www.insee.fr/fr/statistiques/5542859?sommaire=5395764",
        "year": "2018"
    },
    "dossier_complet": {
        "name": "Recensement de la population, Dossier complet (INSEE 2018)",
        "link": "https://www.insee.fr/fr/statistiques/5359146#consulter",
        "year": "2018"
    },
    "bpe": {
        "name": "Base permanente des équipements (INSEE 2021)",
        "link": "https://www.insee.fr/fr/statistiques/3568638?sommaire=3568656",
        "year": "2021"
    },
    "adjacent": {
        "name": "Liste des adjacences des communes françaises (OSM 2021)",
        "link": "https://www.data.gouv.fr/fr/datasets/liste-des-adjacences-des-communes-francaises/",
        "year": "2021"
    },
    "mobpro": {
        "name": "Mobilités professionnelles (INSEE 2018)",
        "link": "https://www.insee.fr/fr/statistiques/5395749?sommaire=5395764#consulter",
        "year": "2018"
    },
    "esrdatagouv": {
        "name": "Etablissements scolaires (Ministère de l'Enseignement supérieur, de la Recherche et de l'Innovation 2017)",
        "link": "https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-implantations_etablissements_d_enseignement_superieur_publics/export/?disjunctive.bcnag_n_nature_uai_libelle_editi&disjunctive.services&disjunctive.type_uai&disjunctive.nature_uai",
        "year": "2017"
    },
    "educationdatagouv": {
        "name": "Etablissements scolaires (Ministère de l'Éducation nationale, de la Jeunesse et des Sports 2023)",
        "link": "https://data.education.gouv.fr/explore/dataset/fr-en-adresse-et-geolocalisation-etablissements-premier-et-second-degre/export/?disjunctive.numero_uai&disjunctive.nature_uai&disjunctive.nature_uai_libe&disjunctive.code_departement&disjunctive.code_region&disjunctive.code_academie&disjunctive.code_commune&disjunctive.libelle_departement&disjunctive.libelle_region&disjunctive.libelle_academie&disjunctive.secteur_prive_code_type_contrat&disjunctive.secteur_prive_libelle_type_contrat&disjunctive.code_ministere&disjunctive.libelle_ministere",
        "year": "2023"
    },
    "emp": {
        "name": "Enquête Mobilité des Personnes (EMP) (SDES 2018)",
        "link": "https://www.statistiques.developpement-durable.gouv.fr/resultats-detailles-de-lenquete-mobilite-des-personnes-de-2019?rubrique=60&dossier=1345",
        "year": "2018"
    },
    "ign": {
        "name": "Découpage administratif Admin-Express (IGN - COG édition 2021 France entière)",
        "link": "https://geoservices.ign.fr/adminexpress",
        "year": "2021"
    },
    "insee_cog": {
        "name": "Code officiel géographique (INSEE 2021)",
        "link": "https://www.insee.fr/fr/information/5057840",
        "year": "2021"
    },
    "insee_density": {
        "name": "Densité communes (INSEE 2020)",
        "link": "https://www.insee.fr/fr/information/2114627",
        "year": "2020"
    },
    "insee_status": {
        "name": "Base des unités urbaines (INSEE 2020)",
        "link": "https://www.insee.fr/fr/information/4802589",
        "year": "2020"
    },
    "transportdatagouv": {
        "name": "Transport public collectif (transport.data.gouv 2023)",
        "link": "https://transport.data.gouv.fr/datasets?type=public-transit",
        "year": "2023"
    },
}


if __name__ == '__main__':
    for desc in sources.values():
        print(desc["name"])

