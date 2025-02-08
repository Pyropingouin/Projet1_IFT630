"""
Module: bus.py
-------------
Implémentation de la classe Bus pour la gestion des véhicules du réseau STS.

Cette classe gère le comportement des bus, incluant le transport des passagers,
le suivi des routes et la gestion des arrêts.

Classes:
    Bus: Représentation d'un bus dans le réseau

Dépendances:
    - models.stop
    - models.route
    - models.passenger

Relations:
    - Transporte des Passenger
    - Se déplace entre des Stop
    - Suit des Route
    - Appartient à des Line

Attributs:
    id: Identifiant unique du bus
    name: Nom du bus
    type: Type de bus (regular, express, etc.)
    capacity: Capacité maximale en passagers
    passenger_list: Liste des passagers actuels
    current_stop: Arrêt actuel
    current_route: Route actuelle
    next_stop: Prochain arrêt prévu

Auteur: Hubert Ngankam
Email: hubert.ngankam@usherbrooke.ca
Session: H2025
Cours: IFT630
Version: 1.0
"""

class Bus:
    def __init__(self, bus_id, bus_name, bus_type, capacity, current_stop):
        """
        :param bus_id: Unique ID for the bus
        :param bus_name: The bus name
        :param bus_type: Type of the bus (e.g., regular, express)
        :param capacity: Maximum number of passengers the bus can carry
        :param current_stop: The current stop where the bus is located
        """
        self.id = bus_id
        self.name = bus_name
        self.type = bus_type
        self.capacity = capacity
        self.passenger_list = []  # List of passengers currently on the bus
        self.current_stop = current_stop
        self.current_route = None # Ajout d'une référence à la route actuelle
        self.next_stop = None  # Prochain arrêt prévu
        self.current_station = None
    
    def __str__(self):
        return (f"Bus {self.id}: Name {self.name}, "
                f"Type: {self.type}, "
                f"Capacité: {self.capacity}, "
                f"Passagers: {len(self.passenger_list)}/{self.capacity}, "
                f"Stop courant: {self.current_stop.name if self.current_stop else 'None'}")

    
    def initialize_buses(self, central_station):
        if hasattr(central_station, 'stop_list'):
            self.current_stop = central_station.stop_list[0]
        else:
            self.current_stop = None
            
            
    def initialize_at_station(self, starting_station):
        """ Initialise le bus à sa station de départ"""
        if starting_station and starting_station.stop_list:
            self.current_stop = starting_station.stop_list[0]
            print(f"Bus {self.id} initialisé à l'arrêt {self.current_stop.name} de la station {starting_station.name}")
            return True
        return False
    
    def can_accept_passengers(self, count=1):
        """
        Vérifie si le bus peut accepter un certain nombre de passagers
        :param count: Nombre de passagers à ajouter (défaut: 1)
        :return: True si le bus peut accepter les passagers, False sinon
        """
        return len(self.passenger_list) + count <= self.capacity

    def add_passenger(self, passenger):
        """
        Ajoute un passager au bus
        :param passenger: Le passager à ajouter
        :return: True si l'ajout est réussi, False sinon
        """
        if self.can_accept_passengers():
            self.passenger_list.append(passenger)
            passenger.current_bus = self
            print(f"Passager {passenger.name} ajouté au bus {self.id}")
            return True
        print(f"Bus {self.id} plein - impossible d'ajouter le passager {passenger.name}")
        return False

    def remove_passenger(self, passenger):
        """
        Retire un passager du bus
        :param passenger: Le passager à retirer
        :return: True si le retrait est réussi, False sinon
        """
        if passenger in self.passenger_list:
            self.passenger_list.remove(passenger)
            passenger.current_bus = None
            print(f"Passager {passenger.name} retiré du bus {self.id}")
            return True
        return False

    def get_passenger_count(self):
        """Retourne le nombre actuel de passagers"""
        return len(self.passenger_list)

    def get_available_seats(self):
        """Retourne le nombre de places disponibles"""
        return self.capacity - len(self.passenger_list)

    def is_full(self):
        """Vérifie si le bus est plein"""
        return len(self.passenger_list) >= self.capacity

    def is_empty(self):
        """Vérifie si le bus est vide"""
        return len(self.passenger_list) == 0

    def get_passengers_for_stop(self, stop):
        """
        Retourne la liste des passagers qui doivent descendre à cet arrêt
        :param stop: L'arrêt à vérifier
        :return: Liste des passagers qui descendent
        """
        return [p for p in self.passenger_list if p.should_alight_bus(stop)]

    def get_route_destinations(self):
        """
        Retourne la liste des arrêts restants sur la route actuelle
        :return: Liste des arrêts à venir
        """
        if not self.current_route or not self.current_stop:
            return []
        
        try:
            current_index = self.current_route.stop_list.index(self.current_stop)
            return self.current_route.stop_list[current_index:]
        except ValueError:
            return []

    def handle_passenger_boarding(self, stop):
        """
        Gère l'embarquement des passagers à un arrêt
        :param stop: L'arrêt actuel
        :return: Nombre de passagers embarqués
        """
        if self.is_full():
            return 0

        boarded_count = 0
        available_seats = self.get_available_seats()
        waiting_passengers = [p for p in stop.waiting_passengers if p.should_board_bus(self)]

        for passenger in waiting_passengers[:available_seats]:
            if self.add_passenger(passenger):
                boarded_count += 1

        return boarded_count

    def handle_passenger_alighting(self, stop):
        """
        Gère le débarquement des passagers à un arrêt
        :param stop: L'arrêt actuel
        :return: Nombre de passagers débarqués
        """
        alighting_passengers = self.get_passengers_for_stop(stop)
        alighting_count = 0

        for passenger in alighting_passengers:
            if self.remove_passenger(passenger):
                passenger.alight_bus(stop)
                alighting_count += 1

        return alighting_count

    def process_stop(self, stop):
        """
        Traite toutes les opérations à un arrêt (débarquement puis embarquement)
        :param stop: L'arrêt à traiter
        :return: (nombre de passagers débarqués, nombre de passagers embarqués)
        """
        # D'abord faire descendre les passagers
        alighting_count = self.handle_passenger_alighting(stop)
        
        # Ensuite faire monter les nouveaux passagers
        boarding_count = self.handle_passenger_boarding(stop)
        
        return alighting_count, boarding_count
    
    
    def move_to_next_stop(self):
        """Déplace le bus vers son prochain arrêt en suivant la route"""
        if not self.current_route or not self.current_stop:
            return False

        current_index = self.current_route.stop_list.index(self.current_stop)
        if current_index < len(self.current_route.stop_list) - 1:
            self.next_stop = self.current_route.stop_list[current_index + 1]
            print(f"Bus {self.id} se déplace de {self.current_stop.name} vers {self.next_stop.name}")
            self.current_stop = self.next_stop
            return True
        return False
    
    
    def handle_intersection(self, intersection, next_route):
        """Gère le transfert à une intersection vers une nouvelle route"""
        # Vérifie si le stop actuel appartient à l'intersection
        current_intersection = self.current_stop.intersection
        if current_intersection and current_intersection == intersection:
            self.current_route = next_route
            # Prendre le premier stop de la nouvelle route qui appartient à l'intersection
            intersection_stops = intersection.stop_list
            next_stops = [stop for stop in next_route.stop_list if stop in intersection_stops]
            if next_stops:
                self.current_stop = next_stops[0]
                print(f"Bus {self.id} traverse l'intersection {intersection.name} "
                      f"de {next_route.origin_start.name} vers {next_route.origin_end.name} "
                      f"via l'arrêt {self.current_stop.name}")
                return True
        return False
