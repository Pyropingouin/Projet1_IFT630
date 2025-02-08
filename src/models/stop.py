"""
Module: stop.py
--------------
Implémentation des arrêts de bus du réseau STS.

Gère les points d'arrêt individuels, leurs passagers
et leurs connexions avec d'autres arrêts.

Classes:
    Stop: Arrêt de bus

Dépendances:
    - models.origin
    - models.passenger
    - models.bus

Relations:
    - Hérite de Origin
    - Accueille des Passenger
    - Dessert des Bus
    - Appartient à des Station ou Intersection

Attributs:
    stop_id: Identifiant unique de l'arrêt
    name: Nom de l'arrêt
    passenger_list: Liste des passagers présents
    capacity: Capacité maximale
    waiting_passengers: Liste des passagers en attente
    is_occupied: État d'occupation par un bus

Auteur: Hubert Ngankam
Email: hubert.ngankam@usherbrooke.ca
Session: H2025
Cours: IFT630
Version: 1.0
"""

from collections import deque
from src.models.origin import Origin

# Stop class representing a stop in the system
class Stop(Origin):
    def __init__(self, origin_id, stop_id, name, passenger_list=None, neighboring_stops=None):
        """
        :param origin_id: Identifiant de l'origine
        :param stop_id: Identifiant unique de l'arrêt
        :param name: Nom de l'arrêt
        :param passenger_list: Liste des passagers présents
        :param neighboring_stops: Liste des arrêts voisins
        """
        super().__init__(origin_id, name, location_type="stop")
        self.stop_id = stop_id
        self.passenger_list = passenger_list if passenger_list is not None else []
        self.capacity = 50
        self.waiting_passengers = []
        self.is_occupied = False
        self.bus_queue = deque()  # File d'attente des bus (utilisation de deque pour une meilleure performance)
        self.current_buses = set()  # Ensemble des bus actuellement à l'arrêt
        self.neighboring_stops = set(neighboring_stops if neighboring_stops is not None else [])

    def __str__(self):
        """Représentation en chaîne de caractères de l'arrêt"""
        neighbors = [stop.name for stop in self.neighboring_stops]
        return (f"Stop ID: {self.stop_id}, "
                f"Name: {self.name}, "
                f"Passagers: {len(self.passenger_list)}/{self.capacity}, "
                f"Voisins: {neighbors}")

    def add_neighboring_stop(self, stop):
        """
        Ajoute un arrêt voisin
        Crée une connexion bidirectionnelle entre les arrêts
        """
        if stop not in self.neighboring_stops and stop != self:
            self.neighboring_stops.add(stop)
            # Assurer la connexion bidirectionnelle
            if not hasattr(stop, 'neighboring_stops'):
                stop.neighboring_stops = set()
            stop.neighboring_stops.add(self)
            return True
        return False

    def remove_neighboring_stop(self, stop):
        """
        Retire un arrêt voisin
        Retire la connexion bidirectionnelle
        """
        if stop in self.neighboring_stops:
            self.neighboring_stops.remove(stop)
            # Retirer la connexion dans l'autre sens aussi
            if hasattr(stop, 'neighboring_stops'):
                stop.neighboring_stops.discard(self)
            return True
        return False

    def get_neighboring_stops(self):
        """Retourne la liste des arrêts voisins"""
        return list(self.neighboring_stops)


    def can_accept_passengers(self, count=1):
        """Vérifie si l'arrêt peut accepter un certain nombre de passagers"""
        return len(self.passenger_list) + count <= self.capacity

    def add_passenger(self, passenger):
        """Ajoute un passager à l'arrêt"""
        if self.can_accept_passengers():
            self.passenger_list.append(passenger)
            self.waiting_passengers.append(passenger)
            passenger.current_stop = self
            print(f"Passager {passenger.name} ajouté à l'arrêt {self.name}")
            return True
        print(f"Arrêt {self.name} plein - impossible d'ajouter le passager {passenger.name}")
        return False

    def remove_passenger(self, passenger):
        """Retire un passager de l'arrêt"""
        if passenger in self.passenger_list:
            self.passenger_list.remove(passenger)
            if passenger in self.waiting_passengers:
                self.waiting_passengers.remove(passenger)
            print(f"Passager {passenger.name} retiré de l'arrêt {self.name}")
            return True
        return False

    def get_current_buses(self):
        """Retourne la liste des bus actuellement à l'arrêt"""
        return list(self.current_buses)

    def bus_arrival(self, bus):
        """Gère l'arrivée d'un bus à l'arrêt"""
        if self.is_occupied:
            self.bus_queue.append(bus)
            print(f"Bus {bus.id} mis en file d'attente à l'arrêt {self.name}")
            return False
        
        self.is_occupied = True
        self.current_buses.add(bus)
        print(f"Bus {bus.id} arrive à l'arrêt {self.name}")
        return True

    def bus_departure(self, bus):
        """Gère le départ d'un bus de l'arrêt"""
        if bus not in self.current_buses:
            return False
            
        self.current_buses.remove(bus)
        
        if not self.current_buses:
            self.is_occupied = False
            
            # Traiter le prochain bus dans la file d'attente s'il y en a
            if self.bus_queue:
                next_bus = self.bus_queue.popleft()
                self.current_buses.add(next_bus)
                self.is_occupied = True
                print(f"Bus {next_bus.id} peut maintenant accéder à l'arrêt {self.name}")
            
        print(f"Bus {bus.id} quitte l'arrêt {self.name}")
        return True

    def process_passenger_boarding(self, bus):
        """Gère l'embarquement des passagers"""
        boarded_passengers = []
        remaining_capacity = bus.capacity - len(bus.passenger_list)
        
        # Trouver les passagers qui attendent pour une destination desservie par ce bus
        potential_passengers = []
        for passenger in self.waiting_passengers:
            if bus.current_route and any(stop in bus.current_route.get_all_stops() 
                                       for stop in passenger.destination.get_all_stops()):
                potential_passengers.append(passenger)
        
        # Embarquer les passagers
        for passenger in potential_passengers[:remaining_capacity]:
            self.passenger_list.remove(passenger)
            self.waiting_passengers.remove(passenger)
            bus.add_passenger(passenger)
            boarded_passengers.append(passenger)
            
        return boarded_passengers
    
    def process_passenger_alighting(self, bus):
        """Gère le débarquement des passagers du bus"""
        alighting_passengers = []
        
        # Vérifier chaque passager dans le bus
        for passenger in bus.passenger_list[:]:  # Utiliser une copie de la liste pour éviter les problèmes de modification
            # Si c'est la destination du passager ou un arrêt de sa station de destination
            if passenger.destination == self or (
                hasattr(passenger.destination, 'stop_list') and 
                self in passenger.destination.stop_list
            ):
                bus.passenger_list.remove(passenger)
                passenger.current_bus = None
                self.add_passenger(passenger)
                alighting_passengers.append(passenger)
                print(f"Passager {passenger.name} débarque du bus {bus.id}")
        
        return alighting_passengers

    def get_next_stop_for_destination(self, destination):
        """Détermine le prochain arrêt optimal pour atteindre une destination"""
        # Si la destination est un voisin direct, le retourner
        if destination in self.neighboring_stops:
            return destination
            
        # Sinon, chercher parmi les voisins
        for neighbor in self.neighboring_stops:
            if hasattr(destination, 'stop_list') and neighbor in destination.stop_list:
                return neighbor
                
        # Si aucun voisin direct n'est trouvé, retourner le premier voisin
        return self.neighboring_stops[0] if self.neighboring_stops else None