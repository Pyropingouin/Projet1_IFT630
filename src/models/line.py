"""
Module: line.py
--------------
Implémentation des lignes de bus du réseau STS.

Gère les lignes de bus, leurs routes et les bus qui y sont affectés.

Classes:
    Line: Ligne de bus du réseau

Dépendances:
    - models.bus
    - models.route
    - models.station
    - models.intersection

Relations:
    - Contient des Bus
    - Suit des Route
    - Relie des Station

Attributs:
    id: Identifiant unique de la ligne
    name: Nom de la ligne
    starting_station: Station de départ
    ending_station: Station d'arrivée
    buses: Liste des bus affectés
    routes: Liste des routes composant la ligne

Auteur: Hubert Ngankam
Email: hubert.ngankam@usherbrooke.ca
Session: H2025
Cours: IFT630
Version: 1.0
"""

from models.intersection import Intersection


class Line:
    def __init__(self, line_id, name, starting_station, ending_station, buses):
        """
        :param line_id: Unique ID for the line
        :param name: Line name unique in each direction
        :param starting_station: The station where the line starts
        :param ending_station: The station where the line ends
        :param buses: List of buses assigned to this line
        """
        self.id = line_id
        self.name = name
        self.starting_station = starting_station
        self.ending_station = ending_station
        self.buses = buses
        self.routes = []  # Routes composant la ligne

    def __str__(self):
        buses_str = ', '.join([str(bus.id) if hasattr(bus, 'id') else "None" for bus in self.buses])
        return (f"Line ID: {self.id}, "
                f"Line name: {self.name}, "
                f"Starting Station: {self.starting_station.name}, "
                f"Ending Station: {self.ending_station.name}, "
                f"Buses: [{buses_str}]")

    def add_route(self, route):
        """Ajoute une route à la ligne"""
        self.routes.append(route)

    def initialize_line(self):
        """Initialise tous les bus de la ligne à la station de départ"""
        if not self.starting_station.stop_list:
            print(f"Erreur: La station de départ {self.starting_station.name} n'a pas d'arrêts")
            return False

        for bus in self.buses:
            bus.current_stop = self.starting_station.stop_list[0]
            if self.routes:
                bus.current_route = self.routes[0]
            print(f"Bus {bus.id} initialisé à l'arrêt {bus.current_stop.name}")
        return True

    def find_next_route(self, current_intersection):
        """Trouve la prochaine route à partir d'une intersection"""
        for route in self.routes:
            # Vérifie si la route part de cette intersection
            if (route.origin_start == current_intersection and 
                any(stop in current_intersection.stop_list for stop in route.stop_list)):
                return route
        return None

    def find_route_to_destination(self, current_stop, destination):
        """Trouve une route qui mène à la destination"""
        for route in self.routes:
            if current_stop in route.stop_list:
                # Vérifie si la route mène directement à la destination
                if destination in route.stop_list:
                    return route
                # Ou si elle mène à une intersection connectée à la destination
                elif route.origin_end and any(stop in destination.stop_list for stop in route.origin_end.stop_list):
                    return route
        return None

    def operate_line(self):
        """Fait fonctionner la ligne en déplaçant les bus le long des routes"""
        if not self.routes:
            print(f"Erreur: Aucune route définie pour la ligne {self.name}")
            return False

        for bus in self.buses:
            print(f"Démarrage du trajet pour le bus {bus.id}")
            
            while True:
                current_stop = bus.current_stop
                
                # Vérifier si on est arrivé à destination
                if current_stop in self.ending_station.stop_list:
                    print(f"Bus {bus.id} est arrivé à destination: {self.ending_station.name}")
                    break

                # Si le stop actuel fait partie d'une intersection
                if current_stop.intersection:
                    # Trouver la prochaine route à partir de cette intersection
                    next_route = self.find_next_route(current_stop.intersection)
                    if next_route:
                        if bus.handle_intersection(current_stop.intersection, next_route):
                            continue
                
                # Si on n'est pas à une intersection ou si le changement a échoué
                # chercher une route directe vers la destination
                route_to_destination = self.find_route_to_destination(current_stop, self.ending_station)
                if route_to_destination:
                    bus.current_route = route_to_destination
                
                # Déplacer le bus vers le prochain arrêt de sa route actuelle
                if not bus.move_to_next_stop():
                    print(f"Bus {bus.id} ne peut pas continuer depuis {current_stop.name}")
                    break

                # Gérer les passagers à chaque arrêt
                self.handle_passengers_at_stop(bus)

        return True

    def handle_passengers_at_stop(self, bus):
        """Gère l'embarquement et le débarquement des passagers à un arrêt"""
        current_stop = bus.current_stop
        
        # Débarquement
        if current_stop.process_passenger_alighting(bus):
            print(f"Débarquement de passagers à l'arrêt {current_stop.name}")
            
        # Embarquement
        if current_stop.process_passenger_boarding(bus):
            print(f"Embarquement de passagers à l'arrêt {current_stop.name}")

    def validate_routes(self):
        """Vérifie que les routes de la ligne forment un chemin valide"""
        if not self.routes:
            return False

        # Vérifier que la première route commence à la station de départ
        first_route = self.routes[0]
        if not any(stop in self.starting_station.stop_list for stop in first_route.stop_list):
            return False

        # Vérifier que la dernière route mène à la station d'arrivée
        last_route = self.routes[-1]
        if not any(stop in self.ending_station.stop_list for stop in last_route.stop_list):
            return False

        # Vérifier la continuité des routes
        for i in range(len(self.routes) - 1):
            current_route = self.routes[i]
            next_route = self.routes[i + 1]
            
            # Les routes doivent être connectées par une intersection
            if not (current_route.origin_end and 
                   current_route.origin_end == next_route.origin_start and
                   isinstance(current_route.origin_end, Intersection)):
                return False

        return True