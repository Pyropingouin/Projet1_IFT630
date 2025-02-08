"""
Module: passenger.py
-------------------
Gestion des passagers dans le réseau STS.

Implémente le comportement des passagers, leur déplacement
et leurs interactions avec les bus et arrêts.

Classes:
    Passenger: Représentation d'un passager

Dépendances:
    - models.station
    - models.stop
    - models.bus

Relations:
    - Utilise des Bus
    - Se déplace entre des Stop
    - A pour destination des Station ou Stop

Attributs:
    id: Identifiant unique du passager
    name: Nom du passager
    destination: Destination finale (Station ou Stop)
    current_stop: Arrêt actuel
    current_bus: Bus actuel (si applicable)
    status: État actuel (waiting, in_bus, etc.)

Constantes:
    STATUS_WAITING: En attente à un arrêt
    STATUS_BOARDING: En train de monter
    STATUS_IN_BUS: Dans un bus
    STATUS_ALIGHTING: En train de descendre
    STATUS_ARRIVED: Arrivé à destination

Auteur: Hubert Ngankam
Email: hubert.ngankam@usherbrooke.ca
Session: H2025
Cours: IFT630
Version: 1.0
"""

from models.station import Station
from models.stop import Stop


class Passenger:
    # États possibles d'un passager
    STATUS_WAITING = "waiting"       # En attente à un arrêt
    STATUS_BOARDING = "boarding"     # En train de monter dans un bus
    STATUS_IN_BUS = "in_bus"        # Dans un bus
    STATUS_ALIGHTING = "alighting"   # En train de descendre du bus
    STATUS_ARRIVED = "arrived"       # Arrivé à destination
    
    def __init__(self, passenger_id, name, destination, current_stop, origin_stop, category, current_bus=None):
        """
        :param passenger_id: Identifiant unique du passager
        :param name: Nom du passager
        :param destination: Destination finale (Station ou Stop)
        :param current_stop: Arrêt actuel
        :param origin_stop: Arrêt de départ
        :param category: Catégorie du passager (Regular, Senior, Student)
        :param current_bus: Bus actuel (si dans un bus)
        """
        self.id = passenger_id
        self.name = name
        self.destination = destination
        self.current_stop = current_stop
        self.origin_stop = origin_stop
        self.category = category
        self.current_bus = current_bus
        self.status = self.STATUS_WAITING
        
        # Informations de voyage
        self.trip_start_time = None
        self.trip_end_time = None
        self.stops_visited = []
        self.buses_taken = []
        self.current_route = None
        self.planned_route = []  # Liste des arrêts prévus pour atteindre la destination

    def __str__(self):
        return (f"Passager {self.id}: {self.name}, "
                f"Catégorie: {self.category}, "
                f"Status: {self.status}, "
                f"Origine: {self.origin_stop.name if self.origin_stop else 'N/A'}, "
                f"Destination: {self.destination.name if self.destination else 'N/A'}, "
                f"Position actuelle: {self.get_current_location()}")

    def get_current_location(self):
        """Retourne la position actuelle du passager"""
        if self.current_bus:
            return f"Dans le bus {self.current_bus.id} à l'arrêt {self.current_bus.current_stop.name}"
        elif self.current_stop:
            return f"À l'arrêt {self.current_stop.name}"
        return "Position inconnue"

    def board_bus(self, bus):
        """Tente de monter dans un bus"""
        if self.status != self.STATUS_WAITING:
            return False
            
        if not bus.can_accept_passengers():
            return False
            
        self.status = self.STATUS_BOARDING
        self.current_bus = bus
        if self.current_stop:
            self.stops_visited.append(self.current_stop)
        self.buses_taken.append(bus)
        self.status = self.STATUS_IN_BUS
        self.current_route = bus.current_route
        
        print(f"Passager {self.name} monte dans le bus {bus.id}")
        return True

    def alight_bus(self, stop):
        """Descend du bus à un arrêt"""
        if self.status != self.STATUS_IN_BUS:
            return False
            
        self.status = self.STATUS_ALIGHTING
        previous_bus = self.current_bus
        self.current_bus = None
        self.current_stop = stop
        self.stops_visited.append(stop)
        self.status = self.STATUS_WAITING
        
        # Vérifier si c'est la destination finale
        if self.is_at_destination():
            self.status = self.STATUS_ARRIVED
            print(f"Passager {self.name} est arrivé à destination")
        else:
            print(f"Passager {self.name} descend du bus {previous_bus.id} à l'arrêt {stop.name}")
            
        return True

    def is_at_destination(self):
        """Vérifie si le passager est arrivé à destination"""
        if not self.current_stop or not self.destination:
            return False
            
        # Si la destination est un arrêt spécifique
        if isinstance(self.destination, Stop):
            return self.current_stop == self.destination
            
        # Si la destination est une station
        if isinstance(self.destination, Station):
            return self.current_stop in self.destination.stop_list
            
        return False

    def should_board_bus(self, bus):
        """Détermine si le passager doit monter dans ce bus"""
        if not bus.current_route:
            return False
            
        # Vérifier si le bus va vers la destination
        if isinstance(self.destination, Stop):
            return self.destination in bus.current_route.stop_list
            
        elif isinstance(self.destination, Station):
            # Vérifier si le bus passe par un des arrêts de la station de destination
            return any(stop in self.destination.stop_list for stop in bus.current_route.stop_list)
            
        return False

    def should_alight_bus(self, stop):
        """Détermine si le passager doit descendre à cet arrêt"""
        if not self.current_bus:
            return False
            
        # Descendre si c'est la destination
        if self.is_at_destination():
            return True
            
        # Descendre si le bus termine sa route
        if stop == self.current_bus.current_route.stop_list[-1]:
            return True
            
        # Descendre si une correspondance est nécessaire
        if self.needs_transfer(stop):
            return True
            
        return False

    def needs_transfer(self, stop):
        """Détermine si le passager doit faire une correspondance à cet arrêt"""
        if not self.current_bus or not self.current_bus.current_route:
            return False
            
        current_route = self.current_bus.current_route
        
        # Si l'arrêt est une intersection
        if hasattr(stop, 'intersection') and stop.intersection:
            # Vérifier si une autre route depuis cette intersection mène à la destination
            for route in stop.intersection.routes_starting:
                if route != current_route:
                    if isinstance(self.destination, Stop):
                        if self.destination in route.stop_list:
                            return True
                    elif isinstance(self.destination, Station):
                        if any(s in self.destination.stop_list for s in route.stop_list):
                            return True
                            
        return False

    def update_planned_route(self, new_route):
        """Met à jour l'itinéraire prévu"""
        self.planned_route = new_route
        print(f"Nouvel itinéraire pour {self.name}: " + 
              " -> ".join(stop.name for stop in new_route))

    def get_trip_summary(self):
        """Retourne un résumé du voyage"""
        return {
            'passenger_id': self.id,
            'name': self.name,
            'category': self.category,
            'origin': self.origin_stop.name if self.origin_stop else 'N/A',
            'destination': self.destination.name if self.destination else 'N/A',
            'status': self.status,
            'stops_visited': [stop.name for stop in self.stops_visited],
            'buses_taken': [bus.id for bus in self.buses_taken],
            'total_stops': len(self.stops_visited),
            'total_buses': len(self.buses_taken),
            'is_completed': self.status == self.STATUS_ARRIVED
        }