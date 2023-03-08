-- --------------------------------------------------------
-- Hôte:                         127.0.0.1
-- Version du serveur:           10.6.0-MariaDB - mariadb.org binary distribution
-- SE du serveur:                Win64
-- HeidiSQL Version:             11.2.0.6213
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;



-- Listage de la structure de la table mobility_raw_data. datagouv_pt_agency
CREATE TABLE IF NOT EXISTS `datagouv_pt_agency` (
  `datagouv_id` varchar(50) NOT NULL,
  `agency_id` varchar(100) NOT NULL,
  `agency_name` varchar(100) DEFAULT NULL,
  `saved_on` datetime DEFAULT NULL,
  PRIMARY KEY (`datagouv_id`,`agency_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. datagouv_pt_calendar
CREATE TABLE IF NOT EXISTS `datagouv_pt_calendar` (
  `datagouv_id` varchar(50) NOT NULL,
  `service_id` varchar(150) NOT NULL,
  `monday` tinyint(4) DEFAULT NULL,
  `tuesday` tinyint(4) DEFAULT NULL,
  `wednesday` tinyint(4) DEFAULT NULL,
  `thursday` tinyint(4) DEFAULT NULL,
  `friday` tinyint(4) DEFAULT NULL,
  `saturday` tinyint(4) DEFAULT NULL,
  `sunday` tinyint(4) DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `saved_on` datetime DEFAULT NULL,
  PRIMARY KEY (`datagouv_id`,`service_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. datagouv_pt_datasets
CREATE TABLE IF NOT EXISTS `datagouv_pt_datasets` (
  `datagouv_id` varchar(50) NOT NULL,
  `name` varchar(250) DEFAULT NULL,
  `file_name` varchar(250) DEFAULT NULL,
  `url` varchar(250) DEFAULT NULL,
  `end_calendar_validity` date DEFAULT NULL,
  `saved_on` datetime DEFAULT NULL,
  PRIMARY KEY (`datagouv_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. datagouv_pt_geocodes
CREATE TABLE IF NOT EXISTS `datagouv_pt_geocodes` (
  `geo_code` varchar(50) NOT NULL,
  `datagouv_id` varchar(50) NOT NULL,
  `route_id` varchar(150) NOT NULL,
  `main_trip_id` varchar(150) NOT NULL,
  PRIMARY KEY (`datagouv_id`,`route_id`,`geo_code`,`main_trip_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. datagouv_pt_routes
CREATE TABLE IF NOT EXISTS `datagouv_pt_routes` (
  `datagouv_id` varchar(50) NOT NULL,
  `route_id` varchar(150) NOT NULL,
  `agency_id` varchar(100) DEFAULT NULL,
  `route_short_name` varchar(250) DEFAULT NULL,
  `route_long_name` varchar(300) DEFAULT NULL,
  `route_type` int(11) DEFAULT NULL,
  `saved_on` datetime DEFAULT NULL,
  PRIMARY KEY (`datagouv_id`,`route_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. datagouv_pt_stops
CREATE TABLE IF NOT EXISTS `datagouv_pt_stops` (
  `datagouv_id` varchar(50) NOT NULL,
  `stop_id` varchar(100) NOT NULL,
  `stop_name` varchar(200) DEFAULT NULL,
  `stop_lat` float DEFAULT NULL,
  `stop_lon` float DEFAULT NULL,
  `saved_on` datetime DEFAULT NULL,
  PRIMARY KEY (`datagouv_id`,`stop_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. datagouv_pt_stop_times
CREATE TABLE IF NOT EXISTS `datagouv_pt_stop_times` (
  `datagouv_id` varchar(50) NOT NULL,
  `trip_id` varchar(150) NOT NULL,
  `stop_id` varchar(100) NOT NULL,
  `arrival_time` time DEFAULT NULL,
  `departure_time` time DEFAULT NULL,
  `stop_sequence` int(11) NOT NULL,
  `saved_on` datetime DEFAULT NULL,
  PRIMARY KEY (`datagouv_id`,`trip_id`,`stop_id`,`stop_sequence`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. datagouv_pt_trips
CREATE TABLE IF NOT EXISTS `datagouv_pt_trips` (
  `datagouv_id` varchar(50) NOT NULL,
  `trip_id` varchar(150) NOT NULL,
  `route_id` varchar(150) DEFAULT NULL,
  `service_id` varchar(150) DEFAULT NULL,
  `saved_on` datetime DEFAULT NULL,
  PRIMARY KEY (`datagouv_id`,`trip_id`),
  KEY `route_id` (`route_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. educationdatagouv_schools
CREATE TABLE IF NOT EXISTS `educationdatagouv_schools` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `geo_code` varchar(12) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `id_type` varchar(50) DEFAULT NULL,
  `lat` float DEFAULT NULL,
  `lon` float DEFAULT NULL,
  `quality` varchar(50) DEFAULT NULL,
  `source` varchar(50) DEFAULT 'BPE_2020',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `geo_code` (`geo_code`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2877760 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. emd_datasets
CREATE TABLE IF NOT EXISTS `emd_datasets` (
  `emd_id` varchar(50) NOT NULL,
  `emd_name` varchar(255) DEFAULT NULL,
  `emd_year` year(4) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`emd_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. emd_geo
CREATE TABLE IF NOT EXISTS `emd_geo` (
  `emd_id` varchar(50) NOT NULL,
  `id` varchar(50) NOT NULL DEFAULT '',
  `name` varchar(255) DEFAULT NULL,
  `geo_code` varchar(50) DEFAULT NULL,
  `geometry` geometrycollection DEFAULT NULL,
  PRIMARY KEY (`emd_id`,`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. emd_modes_dict
CREATE TABLE IF NOT EXISTS `emd_modes_dict` (
  `emd_id` varchar(50) NOT NULL,
  `value` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `mode_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`emd_id`,`value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. emd_persons
CREATE TABLE IF NOT EXISTS `emd_persons` (
  `emd_id` varchar(50) NOT NULL,
  `id_ind` varchar(50) NOT NULL,
  `id_hh` varchar(50) NOT NULL,
  `w_ind` float DEFAULT NULL,
  `ra_id` varchar(50) DEFAULT NULL,
  `ech` int(11) DEFAULT NULL,
  `per` int(11) DEFAULT NULL,
  `sexe` int(11) DEFAULT NULL,
  `age` int(11) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `csp` int(11) DEFAULT NULL,
  `nb_car` int(11) DEFAULT NULL,
  `day` int(11) DEFAULT NULL,
  PRIMARY KEY (`emd_id`,`id_ind`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. emd_reasons_dict
CREATE TABLE IF NOT EXISTS `emd_reasons_dict` (
  `emd_id` varchar(50) NOT NULL,
  `value` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `reason_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`emd_id`,`value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. emd_travels
CREATE TABLE IF NOT EXISTS `emd_travels` (
  `emd_id` varchar(50) NOT NULL,
  `id_trav` varchar(50) NOT NULL,
  `id_ind` varchar(50) NOT NULL,
  `ra_id` varchar(50) DEFAULT NULL,
  `ech` int(11) DEFAULT NULL,
  `per` int(11) DEFAULT NULL,
  `trav_nb` int(11) DEFAULT NULL,
  `reason_ori` varchar(50) DEFAULT NULL,
  `zone_ori` varchar(50) DEFAULT NULL,
  `hour_ori` varchar(50) DEFAULT NULL,
  `reason_des` varchar(50) DEFAULT NULL,
  `zone_des` varchar(50) DEFAULT NULL,
  `hour_des` varchar(50) DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `modp` varchar(50) DEFAULT NULL,
  `moip` varchar(50) DEFAULT NULL,
  `distance` int(11) DEFAULT NULL,
  PRIMARY KEY (`emd_id`,`id_trav`),
  KEY `id_ind` (`id_ind`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. entd_modes_2018
CREATE TABLE IF NOT EXISTS `entd_modes_2018` (
  `id_entd` varchar(50) NOT NULL DEFAULT '0',
  `id_mode` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_entd`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. entd_persons_2018
CREATE TABLE IF NOT EXISTS `entd_persons_2018` (
  `ident_ind` varchar(50) NOT NULL DEFAULT '0',
  `ident_men` varchar(50) DEFAULT NULL,
  `pond_indC` varchar(50) DEFAULT NULL,
  `MDATE_jour` varchar(50) DEFAULT NULL,
  `TYPEJOUR` int(11) DEFAULT NULL,
  `SEXE` int(11) DEFAULT NULL,
  `AGE` int(11) DEFAULT NULL,
  `DEP_RES` varchar(50) DEFAULT NULL,
  `CS24` int(11) DEFAULT NULL,
  `SITUA` int(11) DEFAULT NULL,
  `TYPFAM` int(11) DEFAULT NULL,
  `TRAVAILLE` int(11) DEFAULT NULL,
  `ETUDIE` int(11) DEFAULT NULL,
  `BTRAVTEL` int(11) DEFAULT NULL,
  `BTRAVNBJ` int(11) DEFAULT NULL,
  `BTRAVFIX` int(11) DEFAULT NULL,
  `TEMPTRAV` int(11) DEFAULT NULL,
  `dist_ign_trav` varchar(50) DEFAULT NULL,
  `dist_vo_trav` varchar(50) DEFAULT NULL,
  `dist_ign_etude` varchar(50) DEFAULT NULL,
  `dist_vo_etude` varchar(50) DEFAULT NULL,
  `pond_menC` varchar(50) DEFAULT NULL,
  `NPERS` int(11) DEFAULT NULL,
  `NENFANTS` int(11) DEFAULT NULL,
  `TYPMEN15` int(11) DEFAULT NULL,
  `quartile_rev` int(11) DEFAULT NULL,
  `decile_rev` int(11) DEFAULT NULL,
  `COEFFUC` varchar(50) DEFAULT NULL,
  `quartile_rev_uc` int(11) DEFAULT NULL,
  `decile_rev_uc` int(11) DEFAULT NULL,
  `TUU2017_RES` int(11) DEFAULT NULL,
  `STATUTCOM_UU_RES` varchar(50) DEFAULT NULL,
  `TAA2017_RES` int(11) DEFAULT NULL,
  `CATCOM_AA_RES` int(11) DEFAULT NULL,
  `DENSITECOM_RES` int(11) DEFAULT NULL,
  `dist_res_metro` int(11) DEFAULT NULL,
  `dist_res_tram` int(11) DEFAULT NULL,
  `dist_res_train` int(11) DEFAULT NULL,
  `dist_res_tgv` int(11) DEFAULT NULL,
  `JNBVEH` int(11) DEFAULT NULL,
  `JNBVELOAD` int(11) DEFAULT NULL,
  `JNBVELOENF` int(11) DEFAULT NULL,
  `BLOGDIST` int(11) DEFAULT NULL,
  `__csp` int(11) DEFAULT NULL,
  `__status` varchar(50) DEFAULT NULL,
  `__dist_pt` int(11) DEFAULT NULL,
  `__main_activity` varchar(50) DEFAULT NULL,
  `__main_distance` varchar(50) DEFAULT NULL,
  `__main_transport` varchar(50) DEFAULT NULL,
  `__work_transport` varchar(50) DEFAULT NULL,
  `__work_dist` varchar(50) DEFAULT NULL,
  `__immo_lun` int(11) DEFAULT NULL,
  `__immo_mar` int(11) DEFAULT NULL,
  `__immo_mer` int(11) DEFAULT NULL,
  `__immo_jeu` int(11) DEFAULT NULL,
  `__immo_ven` int(11) DEFAULT NULL,
  `__immo_sam` int(11) DEFAULT NULL,
  `__immo_dim` int(11) DEFAULT NULL,
  PRIMARY KEY (`ident_ind`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. entd_reasons_2018
CREATE TABLE IF NOT EXISTS `entd_reasons_2018` (
  `id_entd` varchar(50) NOT NULL DEFAULT '',
  `id_reason` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_entd`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. entd_travels_2018
CREATE TABLE IF NOT EXISTS `entd_travels_2018` (
  `IDENT_DEP` varchar(50) NOT NULL,
  `IDENT_MEN` varchar(50) DEFAULT NULL,
  `IDENT_IND` varchar(50) DEFAULT NULL,
  `num_dep` int(11) DEFAULT NULL,
  `nb_dep` int(11) DEFAULT NULL,
  `POND_JOUR` varchar(50) DEFAULT NULL,
  `MDATE_jour` varchar(50) DEFAULT NULL,
  `TYPEJOUR` int(11) DEFAULT NULL,
  `MORIHDEP` varchar(50) DEFAULT NULL,
  `MDESHARR` varchar(50) DEFAULT NULL,
  `MOTPREC` varchar(50) DEFAULT NULL,
  `MMOTIFDES` varchar(50) DEFAULT NULL,
  `DUREE` int(11) DEFAULT NULL,
  `mtp` varchar(50) DEFAULT NULL,
  `MDISTTOT_fin` varchar(50) DEFAULT NULL,
  `MACCOMPM` int(11) DEFAULT NULL,
  `MACCOMPHM` int(11) DEFAULT NULL,
  `dist_ign` varchar(50) DEFAULT NULL,
  `mobloc` int(11) DEFAULT NULL,
  `VAC_SCOL` int(11) DEFAULT NULL,
  PRIMARY KEY (`IDENT_DEP`) USING BTREE,
  KEY `IDENT_IND` (`IDENT_IND`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. esrdatagouv_universities
CREATE TABLE IF NOT EXISTS `esrdatagouv_universities` (
  `id` varchar(50) NOT NULL DEFAULT 'AUTO_INCREMENT',
  `geo_code` varchar(12) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `student_nb` int(11) DEFAULT NULL,
  `nature` varchar(100) DEFAULT NULL,
  `code_nature` varchar(50) DEFAULT NULL,
  `type` varchar(50) DEFAULT NULL,
  `code_type` varchar(50) DEFAULT NULL,
  `unit_id` varchar(50) DEFAULT NULL,
  `unit_name` varchar(50) DEFAULT NULL,
  `etab_type` varchar(100) DEFAULT NULL,
  `etab_name` varchar(255) DEFAULT NULL,
  `etab_id` varchar(50) DEFAULT NULL,
  `lat` float DEFAULT NULL,
  `lon` float DEFAULT NULL,
  `source` varchar(50) DEFAULT '',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `geo_code` (`geo_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. geodip_precariousness
CREATE TABLE IF NOT EXISTS `geodip_precariousness` (
  `geo_code` varchar(12) NOT NULL,
  `fuel_prop` float DEFAULT NULL,
  `fuel_housing_prop` float DEFAULT NULL,
  `fuel_nb` int(11) DEFAULT NULL,
  `fuel_housing_nb` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `source` varchar(12) NOT NULL,
  PRIMARY KEY (`geo_code`,`source`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. ign_commune_center
CREATE TABLE IF NOT EXISTS `ign_commune_center` (
  `geo_code` varchar(50) NOT NULL,
  `centroid_lat` float DEFAULT NULL,
  `centroid_lon` float DEFAULT NULL,
  `chflieu_lat` float DEFAULT NULL,
  `chflieu_lon` float DEFAULT NULL,
  `source` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`geo_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. ign_commune_outline
CREATE TABLE IF NOT EXISTS `ign_commune_outline` (
  `geo_code` varchar(50) NOT NULL,
  `outline` text DEFAULT NULL,
  `source` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`geo_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. ign_epci_outline
CREATE TABLE IF NOT EXISTS `ign_epci_outline` (
  `epci_siren` varchar(50) NOT NULL,
  `outline` geometrycollection DEFAULT NULL,
  `outline_light` geometrycollection DEFAULT NULL,
  `source` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`epci_siren`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_bpe
CREATE TABLE IF NOT EXISTS `insee_bpe` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `geo_code` varchar(12) DEFAULT NULL,
  `id_type` varchar(50) DEFAULT NULL,
  `lat` float DEFAULT NULL,
  `lon` float DEFAULT NULL,
  `quality` varchar(50) DEFAULT NULL,
  `source` varchar(50) DEFAULT 'BPE_2020',
  PRIMARY KEY (`id`),
  KEY `geo_code` (`geo_code`)
) ENGINE=InnoDB AUTO_INCREMENT=2762149 DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_census_2018
CREATE TABLE IF NOT EXISTS `insee_census_2018` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `CANTVILLE` varchar(50) DEFAULT NULL,
  `NUMMI` varchar(50) DEFAULT NULL,
  `AGED` varchar(50) DEFAULT NULL,
  `COUPLE` varchar(50) DEFAULT NULL,
  `DEPT` varchar(50) DEFAULT NULL,
  `ETUD` varchar(50) DEFAULT NULL,
  `CS1` varchar(50) DEFAULT NULL,
  `ILETUD` varchar(50) DEFAULT NULL,
  `ILT` varchar(50) DEFAULT NULL,
  `INPER` varchar(50) DEFAULT NULL,
  `IPONDI` varchar(50) DEFAULT NULL,
  `IRIS` varchar(50) DEFAULT NULL,
  `LIENF` varchar(50) DEFAULT NULL,
  `MOCO` varchar(50) DEFAULT NULL,
  `NENFR` varchar(50) DEFAULT NULL,
  `SEXE` varchar(50) DEFAULT NULL,
  `TACT` varchar(50) DEFAULT NULL,
  `TP` varchar(50) DEFAULT NULL,
  `TRANS` varchar(50) DEFAULT NULL,
  `TYPMR` varchar(50) DEFAULT NULL,
  `VOIT` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `DEPT` (`DEPT`) USING BTREE,
  KEY `CANTVILLE` (`CANTVILLE`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=58620426 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_cog_communes
CREATE TABLE IF NOT EXISTS `insee_cog_communes` (
  `COM` varchar(12) NOT NULL,
  `NCCENR` varchar(255) DEFAULT NULL,
  `LIBELLE` varchar(255) DEFAULT NULL,
  `CAN` varchar(12) DEFAULT NULL,
  `ARR` varchar(12) DEFAULT NULL,
  `DEP` varchar(12) DEFAULT NULL,
  `REG` varchar(12) DEFAULT NULL,
  `COMPARENT` varchar(12) DEFAULT NULL,
  `year` varchar(12) DEFAULT NULL,
  PRIMARY KEY (`COM`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_cog_evenements
CREATE TABLE IF NOT EXISTS `insee_cog_evenements` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `MODA` varchar(12) NOT NULL,
  `DATE_EFF` date NOT NULL,
  `TYPECOM_AV` varchar(12) NOT NULL,
  `COM_AV` varchar(12) NOT NULL,
  `TYPECOM_AP` varchar(12) NOT NULL,
  `COM_AP` varchar(12) NOT NULL,
  `COG` varchar(12) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=13740 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_communes
CREATE TABLE IF NOT EXISTS `insee_communes` (
  `geo_code` varchar(12) NOT NULL,
  `postal_code` varchar(12) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `canton_code` varchar(12) DEFAULT NULL,
  `lat` float DEFAULT NULL,
  `lon` float DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`geo_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_communes_aav
CREATE TABLE IF NOT EXISTS `insee_communes_aav` (
  `geo_code` varchar(12) NOT NULL,
  `code_aav` varchar(12) DEFAULT NULL,
  `cat_commune_aav` varchar(12) DEFAULT NULL,
  `source` varchar(12) DEFAULT 'AAV_2020',
  PRIMARY KEY (`geo_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_communes_density
CREATE TABLE IF NOT EXISTS `insee_communes_density` (
  `geo_code` varchar(12) NOT NULL,
  `density_code` varchar(2) DEFAULT NULL,
  `source` varchar(12) DEFAULT NULL,
  PRIMARY KEY (`geo_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_communes_epci
CREATE TABLE IF NOT EXISTS `insee_communes_epci` (
  `geo_code` varchar(50) NOT NULL,
  `epci_siren` varchar(50) DEFAULT NULL,
  `source` varchar(50) NOT NULL,
  PRIMARY KEY (`geo_code`,`source`) USING BTREE,
  KEY `epci_siren` (`epci_siren`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_communes_status
CREATE TABLE IF NOT EXISTS `insee_communes_status` (
  `geo_code` varchar(12) NOT NULL,
  `status_code` varchar(2) DEFAULT NULL,
  `source` varchar(12) DEFAULT 'UU_2020',
  PRIMARY KEY (`geo_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_epci
CREATE TABLE IF NOT EXISTS `insee_epci` (
  `epci_siren` varchar(50) NOT NULL,
  `epci_name` varchar(255) DEFAULT NULL,
  `epci_type` varchar(50) DEFAULT NULL,
  `epci_commune_nb` int(11) DEFAULT NULL,
  `dep_code` varchar(50) DEFAULT NULL,
  `region_code` varchar(50) DEFAULT NULL,
  `source` varchar(50) NOT NULL,
  PRIMARY KEY (`epci_siren`,`source`) USING BTREE,
  KEY `epci_name` (`epci_name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_filosofi
CREATE TABLE IF NOT EXISTS `insee_filosofi` (
  `geo_code` varchar(12) NOT NULL DEFAULT '0',
  `Q119` varchar(50) DEFAULT NULL,
  `Q219` varchar(50) DEFAULT NULL,
  `Q319` varchar(50) DEFAULT NULL,
  `RD` varchar(50) DEFAULT NULL,
  `S80S2019` varchar(50) DEFAULT NULL,
  `GI19` varchar(50) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `source` varchar(50) NOT NULL DEFAULT 'GEO2020RP2017',
  PRIMARY KEY (`geo_code`,`source`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_filosofi_gridded_pop
CREATE TABLE IF NOT EXISTS `insee_filosofi_gridded_pop` (
  `idGrid200` varchar(50) NOT NULL,
  `Ind` float DEFAULT NULL,
  `Men` float DEFAULT NULL,
  `Men_pauv` float DEFAULT NULL,
  `Men_prop` float DEFAULT NULL,
  `Ind_snv` float DEFAULT NULL,
  `Men_surf` float DEFAULT NULL,
  `geo_code` varchar(50) DEFAULT NULL,
  `source` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`idGrid200`),
  KEY `geo_code` (`geo_code`),
  KEY `source` (`source`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_flows_home_work
CREATE TABLE IF NOT EXISTS `insee_flows_home_work` (
  `geo_code_home` varchar(12) NOT NULL DEFAULT '',
  `geo_code_work` varchar(12) NOT NULL DEFAULT '',
  `TRANS` int(11) NOT NULL DEFAULT 0,
  `flow` float DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `source` varchar(50) NOT NULL DEFAULT 'ANCT_MOBPRO_2014',
  PRIMARY KEY (`geo_code_home`,`geo_code_work`,`source`,`TRANS`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_households_cars_nb
CREATE TABLE IF NOT EXISTS `insee_households_cars_nb` (
  `geo_code` varchar(12) NOT NULL DEFAULT '',
  `0c` int(11) DEFAULT NULL,
  `1c` int(11) DEFAULT NULL,
  `2c` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `source` varchar(50) NOT NULL DEFAULT 'GEO2020RP2017',
  PRIMARY KEY (`geo_code`,`source`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_jobs_nb
CREATE TABLE IF NOT EXISTS `insee_jobs_nb` (
  `geo_code` varchar(12) NOT NULL DEFAULT '0',
  `jobs_nb` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `source` varchar(50) NOT NULL DEFAULT 'GEO2020RP2017',
  PRIMARY KEY (`geo_code`,`source`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_nbenffr
CREATE TABLE IF NOT EXISTS `insee_nbenffr` (
  `geo_code` varchar(50) NOT NULL,
  `C18_NE24F0` int(11) DEFAULT NULL,
  `C18_NE24F1` int(11) DEFAULT NULL,
  `C18_NE24F2` int(11) DEFAULT NULL,
  `C18_NE24F3` int(11) DEFAULT NULL,
  `C18_NE24F4P` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `source` varchar(50) NOT NULL DEFAULT 'GEO2020RP2017',
  PRIMARY KEY (`geo_code`,`source`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_population
CREATE TABLE IF NOT EXISTS `insee_population` (
  `geo_code` varchar(12) NOT NULL DEFAULT '0',
  `P18_POP` int(11) DEFAULT NULL,
  `P18_POPH` int(11) DEFAULT NULL,
  `P18_POPF` int(11) DEFAULT NULL,
  `P18_POP0014` int(11) DEFAULT NULL,
  `P18_POP1529` int(11) DEFAULT NULL,
  `P18_POP3044` int(11) DEFAULT NULL,
  `P18_POP4559` int(11) DEFAULT NULL,
  `P18_POP6074` int(11) DEFAULT NULL,
  `P18_POP7589` int(11) DEFAULT NULL,
  `P18_POP90P` int(11) DEFAULT NULL,
  `C18_POP15P` int(11) DEFAULT NULL,
  `C18_POP15P_CS1` int(11) DEFAULT NULL,
  `C18_POP15P_CS2` int(11) DEFAULT NULL,
  `C18_POP15P_CS3` int(11) DEFAULT NULL,
  `C18_POP15P_CS4` int(11) DEFAULT NULL,
  `C18_POP15P_CS5` int(11) DEFAULT NULL,
  `C18_POP15P_CS6` int(11) DEFAULT NULL,
  `C18_POP15P_CS7` int(11) DEFAULT NULL,
  `C18_POP15P_CS8` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `source` varchar(50) NOT NULL DEFAULT 'GEO2020RP2017',
  PRIMARY KEY (`geo_code`,`source`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_pop_age
CREATE TABLE IF NOT EXISTS `insee_pop_age` (
  `geo_code` varchar(12) NOT NULL DEFAULT '0',
  `P18_POP` int(11) DEFAULT NULL,
  `P18_POP0002` int(11) DEFAULT NULL,
  `P18_POP0305` int(11) DEFAULT NULL,
  `P18_POP0610` int(11) DEFAULT NULL,
  `P18_POP1117` int(11) DEFAULT NULL,
  `P18_POP1824` int(11) DEFAULT NULL,
  `P18_POP2539` int(11) DEFAULT NULL,
  `P18_POP4054` int(11) DEFAULT NULL,
  `P18_POP5564` int(11) DEFAULT NULL,
  `P18_POP6579` int(11) DEFAULT NULL,
  `P18_POP80P` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `source` varchar(50) NOT NULL DEFAULT 'GEO2020RP2017',
  PRIMARY KEY (`geo_code`,`source`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_pop_status_nb
CREATE TABLE IF NOT EXISTS `insee_pop_status_nb` (
  `geo_code` varchar(12) NOT NULL DEFAULT '',
  `retired` int(11) DEFAULT NULL,
  `employed` int(11) DEFAULT NULL,
  `unemployed` int(11) DEFAULT NULL,
  `other` int(11) DEFAULT NULL,
  `scholars_2_5` int(11) DEFAULT NULL,
  `scholars_6_10` int(11) DEFAULT NULL,
  `scholars_11_14` int(11) DEFAULT NULL,
  `scholars_15_17` int(11) DEFAULT NULL,
  `scholars_18` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `source` varchar(50) NOT NULL DEFAULT 'GEO2020RP2017',
  PRIMARY KEY (`geo_code`,`source`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_topography
CREATE TABLE IF NOT EXISTS `insee_topography` (
  `geo_code` varchar(12) NOT NULL DEFAULT '',
  `surface` varchar(50) DEFAULT NULL,
  `density` varchar(50) DEFAULT NULL,
  `artificialization_rate` varchar(50) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `source` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`geo_code`,`source`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_typmr
CREATE TABLE IF NOT EXISTS `insee_typmr` (
  `geo_code` varchar(50) NOT NULL,
  `C18_PMEN` int(11) DEFAULT NULL,
  `C18_PMEN_MENPSEUL` int(11) DEFAULT NULL,
  `C18_PMEN_MENSFAM` int(11) DEFAULT NULL,
  `C18_PMEN_MENFAM` int(11) DEFAULT NULL,
  `C18_PMEN_MENCOUPSENF` int(11) DEFAULT NULL,
  `C18_PMEN_MENCOUPAENF` int(11) DEFAULT NULL,
  `C18_PMEN_MENFAMMONO` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `source` varchar(50) NOT NULL DEFAULT 'GEO2020RP2017',
  PRIMARY KEY (`geo_code`,`source`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_workers_within_commune
CREATE TABLE IF NOT EXISTS `insee_workers_within_commune` (
  `geo_code` varchar(12) NOT NULL DEFAULT '0',
  `P18_ACTOCC15P` int(11) DEFAULT NULL,
  `P18_ACTOCC15P_ILT1` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `source` varchar(50) NOT NULL DEFAULT 'GEO2020RP2017',
  PRIMARY KEY (`geo_code`,`source`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. insee_work_travel_mode
CREATE TABLE IF NOT EXISTS `insee_work_travel_mode` (
  `geo_code` varchar(12) NOT NULL DEFAULT '',
  `P18_ACTOCC15P` int(11) DEFAULT NULL,
  `P18_ACTOCC15P_PASTRANS` int(11) DEFAULT NULL,
  `P18_ACTOCC15P_MARCHE` int(11) DEFAULT NULL,
  `P18_ACTOCC15P_VELO` int(11) DEFAULT NULL,
  `P18_ACTOCC15P_2ROUESMOT` int(11) DEFAULT NULL,
  `P18_ACTOCC15P_VOITURE` int(11) DEFAULT NULL,
  `P18_ACTOCC15P_COMMUN` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `source` varchar(50) NOT NULL DEFAULT 'GEO2020RP2017',
  PRIMARY KEY (`geo_code`,`source`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. osm_adjacent
CREATE TABLE IF NOT EXISTS `osm_adjacent` (
  `geo_code` varchar(12) NOT NULL,
  `geo_code_neighbor` varchar(12) NOT NULL,
  `source` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`geo_code`,`geo_code_neighbor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. osm_railways
CREATE TABLE IF NOT EXISTS `osm_railways` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `geo_code` varchar(12) DEFAULT NULL,
  `coordinates` text DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12742 DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. rsvero_critair
CREATE TABLE IF NOT EXISTS `rsvero_critair` (
  `geo_code` varchar(50) NOT NULL,
  `critair1` int(11) DEFAULT NULL,
  `critair2` int(11) DEFAULT NULL,
  `critair3` int(11) DEFAULT NULL,
  `critair4` int(11) DEFAULT NULL,
  `critair5` int(11) DEFAULT NULL,
  `electrique` int(11) DEFAULT NULL,
  `non_classe` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `source` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`geo_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. transportdatagouv_bnlc
CREATE TABLE IF NOT EXISTS `transportdatagouv_bnlc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_lieu` varchar(50) NOT NULL,
  `nom_lieu` varchar(200) DEFAULT NULL,
  `type` varchar(50) DEFAULT NULL,
  `insee` varchar(10) DEFAULT NULL,
  `Ylat` float DEFAULT NULL,
  `Xlong` float DEFAULT NULL,
  `nbre_pl` int(11) DEFAULT NULL,
  `nbre_pmr` int(11) DEFAULT NULL,
  `proprio` varchar(100) DEFAULT NULL,
  `date_maj` date DEFAULT NULL,
  `source` varchar(50) DEFAULT 'OSM_20230201',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `code_com_d` (`insee`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=8978 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. transportdatagouv_cycle_parkings
CREATE TABLE IF NOT EXISTS `transportdatagouv_cycle_parkings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_local` varchar(50) NOT NULL,
  `id_osm` varchar(50) NOT NULL,
  `code_com` varchar(10) DEFAULT NULL,
  `lat` float DEFAULT NULL,
  `lon` float DEFAULT NULL,
  `capacite` int(11) DEFAULT NULL,
  `acces` varchar(50) DEFAULT NULL,
  `gestionnaire` varchar(200) DEFAULT NULL,
  `date_maj` date DEFAULT NULL,
  `source` varchar(50) DEFAULT 'OSM_20230201',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `code_com_d` (`code_com`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=84838 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. transportdatagouv_cycle_paths
CREATE TABLE IF NOT EXISTS `transportdatagouv_cycle_paths` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_local` varchar(50) NOT NULL,
  `id_osm` varchar(50) NOT NULL,
  `code_com_d` varchar(10) DEFAULT NULL,
  `code_com_g` varchar(10) DEFAULT NULL,
  `ame_d` varchar(50) DEFAULT NULL,
  `ame_g` varchar(50) DEFAULT NULL,
  `sens_d` varchar(50) DEFAULT NULL,
  `sens_g` varchar(50) DEFAULT NULL,
  `trafic_vit` int(11) DEFAULT NULL,
  `date_maj` date DEFAULT NULL,
  `geometry` geometrycollection DEFAULT NULL,
  `source` varchar(50) DEFAULT 'OSM_20230201',
  PRIMARY KEY (`id`),
  KEY `code_com_d` (`code_com_d`),
  KEY `code_com_g` (`code_com_g`)
) ENGINE=InnoDB AUTO_INCREMENT=276639 DEFAULT CHARSET=utf8;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. transportdatagouv_irve
CREATE TABLE IF NOT EXISTS `transportdatagouv_irve` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_station_itinerance` varchar(50) NOT NULL,
  `id_pdc_itinerance` varchar(50) NOT NULL,
  `nom_station` varchar(200) NOT NULL,
  `implantation_station` varchar(50) NOT NULL,
  `nom_operateur` varchar(200) DEFAULT NULL,
  `nom_amenageur` varchar(200) DEFAULT NULL,
  `code_insee_commune` varchar(10) DEFAULT NULL,
  `lat` float DEFAULT NULL,
  `lon` float DEFAULT NULL,
  `nbre_pdc` int(11) DEFAULT NULL,
  `puissance_nominale` int(11) DEFAULT NULL,
  `prise_type_ef` varchar(5) DEFAULT NULL,
  `prise_type_2` varchar(5) DEFAULT NULL,
  `prise_type_combo_ccs` varchar(5) DEFAULT NULL,
  `prise_type_chademo` varchar(5) DEFAULT NULL,
  `prise_type_autre` varchar(5) DEFAULT NULL,
  `condition_acces` varchar(50) DEFAULT NULL,
  `date_maj` date DEFAULT NULL,
  `source` varchar(50) DEFAULT 'OSM_20230201',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `code_com_d` (`code_insee_commune`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=50808 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

-- Listage de la structure de la table mobility_raw_data. transportdatagouv_zfe
CREATE TABLE IF NOT EXISTS `transportdatagouv_zfe` (
  `id` varchar(50) NOT NULL,
  `date_debut` date NOT NULL,
  `date_fin` date DEFAULT NULL,
  `main_geo_code` varchar(10) DEFAULT NULL,
  `siren` varchar(50) DEFAULT NULL,
  `vp_critair` varchar(50) DEFAULT NULL,
  `vp_horaires` varchar(50) DEFAULT NULL,
  `vul_critair` varchar(50) DEFAULT NULL,
  `vul_horaires` varchar(50) DEFAULT NULL,
  `pl_critair` varchar(50) DEFAULT NULL,
  `pl_horaires` varchar(50) DEFAULT NULL,
  `autobus_autocars_critair` varchar(50) DEFAULT NULL,
  `autobus_autocars_horaires` varchar(50) DEFAULT NULL,
  `deux_rm_critair` varchar(50) DEFAULT NULL,
  `deux_rm_horaires` varchar(50) DEFAULT NULL,
  `geometry` geometrycollection DEFAULT NULL,
  `source` varchar(50) DEFAULT 'OSM_20230201',
  PRIMARY KEY (`id`,`date_debut`) USING BTREE,
  KEY `code_com_d` (`main_geo_code`) USING BTREE,
  KEY `date_fin` (`date_fin`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Les données exportées n'étaient pas sélectionnées.

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
