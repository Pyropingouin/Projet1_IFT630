from src.models.station import Station
from src.models.stop import Stop
from src.models.intersection import Intersection
from src.models.route import Route
from src.models.line import Line
from src.models.bus import Bus
from src.models.passenger import Passenger
import random

from ui.console_ui import ConsoleUI

class STSSeed:
    def __init__(self):
        self.stations = {}
        self.intersections = {}
        self.stops = {}
        self.routes = {}
        self.lines = {}
        self.buses = {}
        self.passengers = {}

    def initialize_system(self):
        """Initialise tout le système STS avec vérification dans le bon ordre"""
        try:
            ConsoleUI.print_status_update("Démarrage de l'initialisation du système...", "white")
            
            # 1. Création des composants de base
            self._create_stops()
            ConsoleUI.print_status_update("✓ Arrêts créés", "green")
            
            self._create_stations()
            ConsoleUI.print_status_update("✓ Stations créées", "green")
            
            self._create_intersections()
            ConsoleUI.print_status_update("✓ Intersections créées", "green")
            
            # 2. Établissement des connexions
            self._connect_station_stops()
            ConsoleUI.print_status_update("✓ Connexions stations-arrêts établies", "green")
            
            self._connect_intersections()
            ConsoleUI.print_status_update("✓ Intersections connectées", "green")
            
            # 3. Vérification des prérequis pour les routes
            ConsoleUI.print_status_update("Vérification des prérequis pour les routes...", "cyan")
            if self._verify_route_prerequisites():
                ConsoleUI.print_status_update("✓ Prérequis validés", "green")
            
            # 4. Création des routes
            self._create_routes()
            ConsoleUI.print_status_update("✓ Routes créées", "green")
            
            # 5. Création des bus
            self._create_buses()
            ConsoleUI.print_status_update("✓ Bus créés", "green")
            
            # 6. Création des lignes (maintenant que les bus existent)
            self._create_lines()
            ConsoleUI.print_status_update("✓ Lignes créées", "green")
            
            # 7. Initialisation des bus avec leurs lignes
            self._initialize_buses()
            ConsoleUI.print_status_update("✓ Bus initialisés", "green")
            
            # 8. Création des passagers en dernier
            self._create_passengers()
            ConsoleUI.print_status_update("✓ Passagers créés", "green")
            
            # Résumé final
            self._display_initialization_stats()
            
            ConsoleUI.print_success("Système initialisé avec succès !")
            return True
            
        except Exception as e:
            ConsoleUI.print_error(f"Erreur lors de l'initialisation du système: {str(e)}")
            return False
    

    def _initialize_buses(self):
        """Initialise correctement les bus avec leurs lignes et routes"""
        ConsoleUI.print_status_update("Initialisation des bus...", "cyan")
        
        for line_id, line in self.lines.items():
            if not line.routes:
                ConsoleUI.print_warning(f"Ligne {line_id} n'a pas de routes définies")
                continue
                
            for bus in line.buses:
                try:
                    # Assigner la ligne au bus
                    bus.current_line = line
                    
                    # Assigner une route au bus
                    bus.current_route = line.routes[0]
                    
                    # Vérifier que la route a des arrêts
                    if not bus.current_route.stop_list:
                        ConsoleUI.print_error(f"Route {bus.current_route.id} n'a pas d'arrêts")
                        continue
                    
                    # Placer le bus au premier arrêt de sa route
                    bus.current_stop = bus.current_route.stop_list[0]
                    
                    # Initialiser à la station de départ
                    if line.starting_station:
                        if bus.initialize_at_station(line.starting_station):
                            ConsoleUI.print_status_update(
                                f"Bus {bus.id} initialisé - "
                                f"Ligne: {line_id}, "
                                f"Route: {bus.current_route.id}, "
                                f"Arrêt initial: {bus.current_stop.name}",
                                "green"
                            )
                    
                except Exception as e:
                    ConsoleUI.print_error(f"Erreur lors de l'initialisation du bus {bus.id}: {str(e)}")



    def _create_stops(self):
        """Crée tous les 66 arrêts (S0-S64 + S99)"""
        try:
            ConsoleUI.print_status_update("Création des arrêts...", "cyan")
            
            # Création des arrêts standards
            for i in range(65):
                stop = Stop(
                    origin_id=f"SP{i}",
                    stop_id=i,
                    name=f"S{i}",
                    passenger_list=[],
                    neighboring_stops=set()  # Initialisation explicite
                )
                self.stops[f"S{i}"] = stop
                
            # Création de l'arrêt spécial S99
            stop_99 = Stop(
                origin_id="SP99",
                stop_id=99,
                name="S99",
                passenger_list=[],
                neighboring_stops=set()  # Initialisation explicite
            )
            self.stops["S99"] = stop_99
            
            ConsoleUI.print_success(f"{len(self.stops)} arrêts créés")
            
            # Établir les connexions initiales entre les arrêts
            self._create_initial_stop_connections()
            
        except Exception as e:
            ConsoleUI.print_error(f"Erreur lors de la création des arrêts: {str(e)}")
            raise

    def _create_initial_stop_connections(self):
        """Établit les connexions initiales entre les arrêts selon la topologie du réseau"""
        ConsoleUI.print_status_update("Établissement des connexions entre arrêts...", "cyan")
        
        # Définition complète des connexions selon la topologie du réseau
        basic_connections = {
            # STS Central (S0)
            "S0": ["S21", "S22"],  # Connexion vers la Zone Nord

            # Carrefour-Estrie (S1-S4)
            "S1": ["S2", "S31", "S32"],  # Connexions internes et vers Zone Est
            "S2": ["S1", "S3", "S32", "S33"],
            "S3": ["S2", "S4", "S33", "S34"],
            "S4": ["S3", "S34", "S35"],

            # CEGEP (S5-S9)
            "S5": ["S6", "S41", "S42"],  # Connexions internes et vers Zone Sud
            "S6": ["S5", "S7", "S42", "S43"],
            "S7": ["S6", "S8", "S43", "S44"],
            "S8": ["S7", "S9", "S44", "S45"],
            "S9": ["S8", "S45", "S46"],

            # Dépôt (S10-S12)
            "S10": ["S11", "S51", "S52"],  # Connexions internes et vers Zone Ouest
            "S11": ["S10", "S12", "S52", "S53"],
            "S12": ["S11", "S53", "S54"],

            # Bishop (S13-S15)
            "S13": ["S14", "S61", "S62"],  # Connexions internes et vers Zone Ouest
            "S14": ["S13", "S15", "S62", "S63"],
            "S15": ["S14", "S63", "S64"],

            # UdeS (S16-S20)
            "S16": ["S17", "S55", "S56"],  # Connexions internes et vers Zone Ouest
            "S17": ["S16", "S18", "S56", "S57"],
            "S18": ["S17", "S19", "S57", "S58"],
            "S19": ["S18", "S20", "S58", "S59"],
            "S20": ["S19", "S59", "S60"],

            # Zone Nord (S21-S30)
            "S21": ["S0", "S22", "S23", "S61"],  # Connexion avec STS Central et Bishop
            "S22": ["S0", "S21", "S23", "S41"],  # Connexion avec STS Central et CEGEP
            "S23": ["S21", "S22", "S24", "S25"],
            "S24": ["S23", "S25", "S26"],
            "S25": ["S23", "S24", "S26", "S27"],
            "S26": ["S24", "S25", "S27", "S28"],
            "S27": ["S25", "S26", "S28", "S29"],
            "S28": ["S26", "S27", "S29", "S30"],
            "S29": ["S27", "S28", "S30"],
            "S30": ["S28", "S29"],

            # Zone Est (S31-S40)
            "S31": ["S1", "S32", "S33"],  # Connexion avec Carrefour-Estrie
            "S32": ["S1", "S2", "S31", "S33", "S34"],
            "S33": ["S2", "S3", "S31", "S32", "S34", "S35"],
            "S34": ["S3", "S4", "S32", "S33", "S35", "S36"],
            "S35": ["S4", "S33", "S34", "S36", "S55"],  # Connexion vers UdeS
            "S36": ["S34", "S35", "S37", "S38"],
            "S37": ["S36", "S38", "S39"],
            "S38": ["S36", "S37", "S39", "S40"],
            "S39": ["S37", "S38", "S40"],
            "S40": ["S38", "S39"],

            # Zone Sud (S41-S50)
            "S41": ["S5", "S22", "S42", "S43"],  # Connexion avec CEGEP
            "S42": ["S5", "S6", "S41", "S43", "S44"],
            "S43": ["S6", "S7", "S41", "S42", "S44", "S45"],
            "S44": ["S7", "S8", "S42", "S43", "S45", "S46"],
            "S45": ["S8", "S9", "S43", "S44", "S46", "S47"],
            "S46": ["S9", "S44", "S45", "S47", "S55"],  # Connexion vers UdeS
            "S47": ["S45", "S46", "S48", "S49"],
            "S48": ["S47", "S49", "S50"],
            "S49": ["S47", "S48", "S50"],
            "S50": ["S48", "S49"],

            # Zone Ouest (S51-S64)
            "S51": ["S10", "S52", "S55"],  # Connexions Dépôt et UdeS
            "S52": ["S10", "S11", "S51", "S53"],
            "S53": ["S11", "S12", "S52", "S54"],
            "S54": ["S12", "S53", "S55"],
            "S55": ["S16", "S35", "S46", "S51", "S54", "S56"],  # Hub important
            "S56": ["S16", "S17", "S55", "S57"],
            "S57": ["S17", "S18", "S56", "S58"],
            "S58": ["S18", "S19", "S57", "S59"],
            "S59": ["S19", "S20", "S58", "S60"],
            "S60": ["S20", "S59"],
            "S61": ["S13", "S21", "S62"],  # Connexion Bishop
            "S62": ["S13", "S14", "S61", "S63"],
            "S63": ["S14", "S15", "S62", "S64"],
            "S64": ["S15", "S63"],

            # Arrêt spécial S99 (point de régulation près de I5)
            "S99": ["S35", "S46", "S55"]  # Connecté aux axes majeurs
        }
        
        # Création des connexions
        connections_count = 0
        for stop_name, neighbors in basic_connections.items():
            if stop_name in self.stops:
                current_stop = self.stops[stop_name]
                for neighbor_name in neighbors:
                    if neighbor_name in self.stops:
                        neighbor_stop = self.stops[neighbor_name]
                        if current_stop.add_neighboring_stop(neighbor_stop):
                            connections_count += 1
                            ConsoleUI.print_status_update(
                                f"Connexion établie: {stop_name} <-> {neighbor_name}",
                                "white"
                            )
                    else:
                        ConsoleUI.print_warning(f"Arrêt voisin non trouvé: {neighbor_name}")
            else:
                ConsoleUI.print_warning(f"Arrêt source non trouvé: {stop_name}")
        
        # Vérification finale des connexions
        total_connections = sum(len(stop.neighboring_stops) for stop in self.stops.values())
        ConsoleUI.print_success(
            f"Connexions établies: {connections_count} connexions unidirectionnelles "
            f"({total_connections//2} connexions bidirectionnelles)"
        )

        # Vérification de la connectivité
        self._verify_network_connectivity()

    def _verify_network_connectivity(self):
        """Vérifie que tous les arrêts sont connectés au réseau"""
        visited = set()
        to_visit = {next(iter(self.stops.values()))}  # Commence par le premier arrêt
        
        while to_visit:
            current_stop = to_visit.pop()
            visited.add(current_stop)
            to_visit.update(
                neighbor for neighbor in current_stop.neighboring_stops 
                if neighbor not in visited
            )
        
        # Vérification
        unconnected = set(self.stops.values()) - visited
        if unconnected:
            unconnected_names = [stop.name for stop in unconnected]
            ConsoleUI.print_warning(
                f"Arrêts non connectés au réseau principal: {unconnected_names}"
            )
        else:
            ConsoleUI.print_success("Tous les arrêts sont connectés au réseau principal")
        


    def _create_stations(self):
        """Crée les 6 stations avec leurs arrêts associés"""
        station_configs = {
            "STS Central": ["S0"],
            "Carrefour-Estrie": ["S1", "S2", "S3", "S4"],
            "CEGEP": ["S5", "S6", "S7", "S8", "S9"],
            "Dépôt": ["S10", "S11", "S12"],
            "Bishop": ["S13", "S14", "S15"],
            "UdeS": ["S16", "S17", "S18", "S19", "S20"]
        }

        for idx, (name, stop_list) in enumerate(station_configs.items()):
            station_stops = [self.stops[stop_name] for stop_name in stop_list]
            station = Station(
                origin_id=f"ST{idx}",
                station_id=idx,
                name=name,
                stop_list=station_stops
            )
            self.stations[name] = station

            # Connecter tous les arrêts entre eux dans la station
            for i, stop1 in enumerate(station_stops):
                for stop2 in station_stops[i+1:]:
                    stop1.add_neighboring_stop(stop2)

    def _create_intersections(self):
        """Crée les 9 intersections"""
        for i in range(9):
            intersection = Intersection(
                origin_id=f"IN{i}",
                name=f"I{i}",
                intersection_id=i,
                stop_list=[]
            )
            self.intersections[f"I{i}"] = intersection

    def _connect_station_stops(self):
        """Connecte les arrêts dans les stations et avec les arrêts voisins"""
        # Connexions des arrêts de station aux arrêts voisins
        stop_connections = {
            # Zone STS Central
            "S0": ["S21", "S22"],
            # Zone Carrefour-Estrie
            "S1": ["S31", "S32"], "S2": ["S32", "S33"],
            "S3": ["S33", "S34"], "S4": ["S34", "S35"],
            # Zone CEGEP
            "S5": ["S41", "S42"], "S6": ["S42", "S43"],
            "S7": ["S43", "S44"], "S8": ["S44", "S45"],
            "S9": ["S45", "S46"],
            # Zone Dépôt
            "S10": ["S51", "S52"], "S11": ["S52", "S53"],
            "S12": ["S53", "S54"],
            # Zone Bishop
            "S13": ["S61", "S62"], "S14": ["S62", "S63"],
            "S15": ["S63", "S64"],
            # Zone UdeS
            "S16": ["S55", "S56"], "S17": ["S56", "S57"],
            "S18": ["S57", "S58"], "S19": ["S58", "S59"],
            "S20": ["S59", "S60"]
        }

        for stop_name, neighbors in stop_connections.items():
            stop = self.stops[stop_name]
            for neighbor in neighbors:
                stop.add_neighboring_stop(self.stops[neighbor])

    def _connect_intersections(self):
        """Connecte les intersections entre elles et avec les stations"""
        # Connexions I5 avec 6 autres intersections
        i5_connections = ["I0", "I1", "I2", "I3", "I4", "I6"]
        for conn in i5_connections:
            self.intersections["I5"].add_neighbor(self.intersections[conn])

        # Autres connexions entre intersections
        intersection_connections = [
            ("I0", "I1"), ("I1", "I2"), ("I2", "I3"),
            ("I3", "I4"), ("I6", "I7"), ("I7", "I8")
        ]
        
        for int1, int2 in intersection_connections:
            self.intersections[int1].add_neighbor(self.intersections[int2])

        # Connexions stations-intersections
        station_intersection_map = {
            "STS Central": "I0",
            "Carrefour-Estrie": "I2",
            "CEGEP": "I4",
            "Dépôt": "I6",
            "Bishop": "I8",
            "UdeS": "I7"
        }

        for station_name, intersection_name in station_intersection_map.items():
            self.stations[station_name].add_intersection(self.intersections[intersection_name])

    def _create_buses(self):
        """Crée 40 bus de différentes capacités"""
        bus_configs = [
            # 15 bus standards (capacité 30)
            *(15 * [("regular", 30)]),
            # 15 bus moyens (capacité 40)
            *(15 * [("regular", 40)]),
            # 5 bus articulés (capacité 60)
            *(5 * [("articulated", 60)]),
            # 5 bus express (capacité 50)
            *(5 * [("express", 50)])
        ]

        for i, (bus_type, capacity) in enumerate(bus_configs):
            bus = Bus(
                bus_id=i,
                bus_name=f"Bus-{i}",
                bus_type=bus_type,
                capacity=capacity,
                current_stop=self.stops["S0"]  # Tous les bus commencent au dépôt
            )
            self.buses[i] = bus

    def _create_routes(self):
        """Crée les routes pour les 15 lignes bidirectionnelles"""
        try:
            ConsoleUI.print_status_update("Création des routes...", "cyan")
            
            # Vérification préalable de l'existence des stations
            required_stations = [
                "STS Central", "Carrefour-Estrie", "CEGEP", 
                "Dépôt", "Bishop", "UdeS"
            ]
            for station_name in required_stations:
                if station_name not in self.stations:
                    raise ValueError(f"Station requise non trouvée: {station_name}")
            
            # Définition des routes principales
            main_routes = [
                # Route 1: STS Central - Carrefour-Estrie
                ("R1", ["S0", "S21", "S22", "S31", "S1", "S2", "S3", "S4"],
                "STS Central", "Carrefour-Estrie"),
                
                # Route 2: STS Central - CEGEP
                ("R2", ["S0", "S22", "S41", "S5", "S6", "S7", "S8", "S9"],
                "STS Central", "CEGEP"),
                
                # Route 3: Carrefour-Estrie - UdeS
                ("R3", ["S4", "S34", "S35", "S55", "S16", "S17", "S18", "S19", "S20"],
                "Carrefour-Estrie", "UdeS"),
                
                # Route 4: CEGEP - Bishop
                ("R4", ["S9", "S45", "S46", "S61", "S13", "S14", "S15"],
                "CEGEP", "Bishop"),
                
                # Route 5: UdeS - Dépôt
                ("R5", ["S20", "S59", "S60", "S51", "S10", "S11", "S12"],
                "UdeS", "Dépôt"),
                
                # Route 6: STS Central - Bishop
                ("R6", ["S0", "S21", "S61", "S13", "S14", "S15"],
                "STS Central", "Bishop"),
                
                # Route 7: Carrefour-Estrie - Dépôt
                ("R7", ["S4", "S35", "S51", "S10", "S11", "S12"],
                "Carrefour-Estrie", "Dépôt"),
                
                # Route 8: CEGEP - UdeS
                ("R8", ["S9", "S46", "S55", "S16", "S17", "S18", "S19", "S20"],
                "CEGEP", "UdeS"),
                
                # Route 9: Bishop - Dépôt
                ("R9", ["S15", "S63", "S64", "S51", "S10", "S11", "S12"],
                "Bishop", "Dépôt"),
                
                # Route 10: STS Central - UdeS
                ("R10", ["S0", "S22", "S55", "S16", "S17", "S18", "S19", "S20"],
                "STS Central", "UdeS"),
                
                # Route 11: Carrefour-Estrie - Bishop
                ("R11", ["S4", "S34", "S61", "S13", "S14", "S15"],
                "Carrefour-Estrie", "Bishop"),
                
                # Route 12: CEGEP - Dépôt
                ("R12", ["S9", "S45", "S51", "S10", "S11", "S12"],
                "CEGEP", "Dépôt"),
                
                # Route 13: STS Central - Dépôt
                ("R13", ["S0", "S21", "S51", "S10", "S11", "S12"],
                "STS Central", "Dépôt"),
                
                # Route 14: Carrefour-Estrie - CEGEP
                ("R14", ["S4", "S34", "S41", "S5", "S6", "S7", "S8", "S9"],
                "Carrefour-Estrie", "CEGEP"),
                
                # Route 15: Bishop - UdeS
                ("R15", ["S15", "S63", "S55", "S16", "S17", "S18", "S19", "S20"],
                "Bishop", "UdeS")
            ]
            
            route_count = 0
            for route_id, stop_list, start_station_name, end_station_name in main_routes:
                try:
                    # Vérification des stations
                    if start_station_name not in self.stations:
                        raise ValueError(f"Station de départ non trouvée: {start_station_name}")
                    if end_station_name not in self.stations:
                        raise ValueError(f"Station d'arrivée non trouvée: {end_station_name}")
                    
                    # Vérification des arrêts
                    stops_forward = []
                    for stop_name in stop_list:
                        if stop_name not in self.stops:
                            raise ValueError(f"Arrêt non trouvé: {stop_name}")
                        stops_forward.append(self.stops[stop_name])
                    
                    # Vérification de la connexion entre les arrêts
                    for i in range(len(stops_forward) - 1):
                        current_stop = stops_forward[i]
                        next_stop = stops_forward[i + 1]
                        if next_stop not in current_stop.neighboring_stops:
                            ConsoleUI.print_warning(
                                f"Les arrêts {current_stop.name} et {next_stop.name} "
                                f"ne sont pas connectés - ajout de la connexion"
                            )
                            current_stop.add_neighboring_stop(next_stop)
                    
                    # Création de la route aller
                    route_forward = Route(
                        route_id=f"{route_id}-A",
                        stop_list=stops_forward,
                        origin_start=self.stations[start_station_name],
                        origin_end=self.stations[end_station_name]
                    )
                    
                    # Vérification de la validité de la route
                    if not route_forward.is_valid():
                        raise ValueError(
                            f"Route invalide: {route_id}-A "
                            f"(vérifiez les connexions entre arrêts)"
                        )
                    
                    self.routes[f"{route_id}-A"] = route_forward
                    route_count += 1
                    
                    # Création de la route retour
                    route_backward = Route(
                        route_id=f"{route_id}-B",
                        stop_list=list(reversed(stops_forward)),
                        origin_start=self.stations[end_station_name],
                        origin_end=self.stations[start_station_name]
                    )
                    
                    # Vérification de la validité de la route retour
                    if not route_backward.is_valid():
                        raise ValueError(
                            f"Route invalide: {route_id}-B "
                            f"(vérifiez les connexions entre arrêts)"
                        )
                    
                    self.routes[f"{route_id}-B"] = route_backward
                    route_count += 1
                    
                    ConsoleUI.print_status_update(
                        f"Routes {route_id}-A et {route_id}-B créées avec succès", 
                        "green"
                    )
                    
                except Exception as e:
                    ConsoleUI.print_error(f"Erreur lors de la création des routes {route_id}: {str(e)}")
                    raise
            
            ConsoleUI.print_success(f"Création des routes terminée - {route_count} routes créées")
            
        except Exception as e:
            ConsoleUI.print_error(f"Erreur lors de la création des routes: {str(e)}")
            raise ValueError(f"Échec de la création des routes: {str(e)}")

    def _verify_route_prerequisites(self):
        """Vérifie que toutes les conditions préalables sont remplies pour la création des routes"""
        try:
            # Vérification des stations
            if not self.stations:
                raise ValueError("Aucune station n'a été créée")
            
            # Vérification des arrêts
            if not self.stops:
                raise ValueError("Aucun arrêt n'a été créé")
            
            # Vérification des intersections
            if not self.intersections:
                raise ValueError("Aucune intersection n'a été créée")
            
            # Vérification des connexions stations-arrêts
            for station in self.stations.values():
                if not station.stop_list:
                    raise ValueError(f"Station {station.name} n'a pas d'arrêts")
            
            # Vérification des connexions entre arrêts
            connected_stops = set()
            for stop in self.stops.values():
                if not stop.neighboring_stops:
                    ConsoleUI.print_warning(f"Arrêt {stop.name} n'a pas de connexions")
                connected_stops.add(stop)
                connected_stops.update(stop.neighboring_stops)
            
            if len(connected_stops) < len(self.stops):
                raise ValueError("Certains arrêts ne sont pas connectés au réseau")
            
            return True
            
        except Exception as e:
            ConsoleUI.print_error(f"Vérification des prérequis échouée: {str(e)}")
            raise

    def _create_lines(self):
        """Crée les 15 lignes bidirectionnelles"""
        try:
            ConsoleUI.print_status_update("Création des lignes de bus...", "cyan")
            
            # Vérification des prérequis
            if not self.routes:
                raise ValueError("Aucune route n'a été créée")
            if not self.buses:
                raise ValueError("Aucun bus n'a été créé")

            # Configuration d'allocation des bus pour chaque ligne
            bus_allocation = {
                "L1": 4,  # STS Central - Carrefour-Estrie
                "L2": 3,  # STS Central - CEGEP
                "L3": 3,  # Carrefour-Estrie - UdeS
                "L4": 2,  # CEGEP - Bishop
                "L5": 3,  # UdeS - Dépôt
                "L6": 2,  # STS Central - Bishop
                "L7": 3,  # Carrefour-Estrie - Dépôt
                "L8": 2,  # CEGEP - UdeS
                "L9": 2,  # Bishop - Dépôt
                "L10": 3,  # STS Central - UdeS
                "L11": 2,  # Carrefour-Estrie - Bishop
                "L12": 3,  # CEGEP - Dépôt
                "L13": 2,  # STS Central - Dépôt
                "L14": 3,  # Carrefour-Estrie - CEGEP
                "L15": 3   # Bishop - UdeS
            }

            # Correspondance entre lignes et routes
            line_route_mapping = {
                "L1": ("R1-A", "R1-B"),
                "L2": ("R2-A", "R2-B"),
                "L3": ("R3-A", "R3-B"),
                "L4": ("R4-A", "R4-B"),
                "L5": ("R5-A", "R5-B"),
                "L6": ("R6-A", "R6-B"),
                "L7": ("R7-A", "R7-B"),
                "L8": ("R8-A", "R8-B"),
                "L9": ("R9-A", "R9-B"),
                "L10": ("R10-A", "R10-B"),
                "L11": ("R11-A", "R11-B"),
                "L12": ("R12-A", "R12-B"),
                "L13": ("R13-A", "R13-B"),
                "L14": ("R14-A", "R14-B"),
                "L15": ("R15-A", "R15-B")
            }

            current_bus = 0  # Index pour suivre l'allocation des bus
            created_lines = 0

            for line_id, (route_a_id, route_b_id) in line_route_mapping.items():
                try:
                    # Vérifier l'existence des routes
                    if route_a_id not in self.routes or route_b_id not in self.routes:
                        raise ValueError(f"Routes non trouvées pour la ligne {line_id}")

                    route_forward = self.routes[route_a_id]
                    route_backward = self.routes[route_b_id]

                    # Vérifier le nombre de bus nécessaire
                    num_buses_needed = bus_allocation[line_id]
                    if current_bus + num_buses_needed > len(self.buses):
                        raise ValueError(f"Pas assez de bus disponibles pour la ligne {line_id}")

                    # Sélectionner les bus pour cette ligne
                    line_buses = [self.buses[i] for i in range(current_bus, current_bus + num_buses_needed)]
                    current_bus += num_buses_needed

                    # Créer la ligne aller
                    line_forward = Line(
                        line_id=f"{line_id}-A",
                        name=f"Ligne {line_id[1:]} (Aller)",
                        starting_station=route_forward.origin_start,
                        ending_station=route_forward.origin_end,
                        buses=line_buses[:num_buses_needed//2]
                    )
                    line_forward.add_route(route_forward)
                    
                    # Vérifier la validité de la ligne
                    if not line_forward.validate_routes():
                        raise ValueError(f"Routes invalides pour la ligne {line_id}-A")
                    
                    self.lines[f"{line_id}-A"] = line_forward

                    # Créer la ligne retour
                    line_backward = Line(
                        line_id=f"{line_id}-B",
                        name=f"Ligne {line_id[1:]} (Retour)",
                        starting_station=route_backward.origin_start,
                        ending_station=route_backward.origin_end,
                        buses=line_buses[num_buses_needed//2:]
                    )
                    line_backward.add_route(route_backward)
                    
                    # Vérifier la validité de la ligne
                    if not line_backward.validate_routes():
                        raise ValueError(f"Routes invalides pour la ligne {line_id}-B")
                    
                    self.lines[f"{line_id}-B"] = line_backward

                    created_lines += 2
                    ConsoleUI.print_status_update(
                        f"Ligne {line_id} créée avec {num_buses_needed} bus", 
                        "green"
                    )

                except Exception as e:
                    ConsoleUI.print_error(f"Erreur lors de la création de la ligne {line_id}: {str(e)}")
                    raise

            ConsoleUI.print_success(
                f"Création des lignes terminée - {created_lines} lignes créées "
                f"({current_bus} bus assignés)"
            )

            # Vérification finale
            self._verify_line_initialization()

        except Exception as e:
            ConsoleUI.print_error(f"Erreur lors de la création des lignes: {str(e)}")
            raise ValueError(f"Échec de la création des lignes: {str(e)}")

    def _verify_line_initialization(self):
        """Vérifie l'initialisation correcte de toutes les lignes"""
        try:
            for line_id, line in self.lines.items():
                # Vérifier les routes
                if not line.routes:
                    raise ValueError(f"Ligne {line_id} n'a pas de routes")

                # Vérifier les bus
                if not line.buses:
                    raise ValueError(f"Ligne {line_id} n'a pas de bus")

                # Vérifier les stations
                if not line.starting_station or not line.ending_station:
                    raise ValueError(f"Ligne {line_id} n'a pas de stations définies")

                ConsoleUI.print_status_update(
                    f"Ligne {line_id} validée : "
                    f"{len(line.buses)} bus, "
                    f"{len(line.routes)} routes, "
                    f"de {line.starting_station.name} à {line.ending_station.name}",
                    "white"
                )

        except Exception as e:
            ConsoleUI.print_error(f"Erreur lors de la vérification des lignes: {str(e)}")
            raise

    def _create_passengers(self):
        """Crée 100 passagers initiaux"""
        passenger_categories = ["Regular", "Senior", "Student"]
        all_stations = list(self.stations.values())

        for i in range(100):
            # Choisir origine et destination aléatoires
            origin_station = random.choice(all_stations)
            destination_station = random.choice([s for s in all_stations if s != origin_station])
            
            # Choisir un arrêt de départ dans la station d'origine
            origin_stop = random.choice(origin_station.stop_list) if origin_station.stop_list else None
            
            if origin_stop:
                passenger = Passenger(
                    passenger_id=i,
                    name=f"Passenger-{i}",
                    destination=destination_station,
                    current_stop=origin_stop,
                    origin_stop=origin_stop,
                    category=random.choice(passenger_categories)
                )
                self.passengers[i] = passenger
                origin_stop.add_passenger(passenger)
            
    def _display_initialization_stats(self):
        """Affiche les statistiques d'initialisation"""
        stats = [
            ("Stations", len(self.stations)),
            ("Intersections", len(self.intersections)),
            ("Arrêts", len(self.stops)),
            ("Routes", len(self.routes)),
            ("Lignes", len(self.lines)),
            ("Bus", len(self.buses)),
            ("Passagers", len(self.passengers))
        ]
        
        ConsoleUI.print_status_update("\nStatistiques d'initialisation:", "cyan")
        for name, count in stats:
            ConsoleUI.print_status_update(f"{name}: {count}", "white")

