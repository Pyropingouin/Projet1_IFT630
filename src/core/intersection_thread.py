"""
Module: component_threads.py
--------------------------
Implémentation des threads pour chaque composant du réseau STS.

Définit le comportement spécifique des threads pour les bus,
stations, arrêts, passagers et intersections.

Classes:
    BusThread: Thread de simulation pour un bus
    StationThread: Thread de simulation pour une station
    StopThread: Thread de simulation pour un arrêt
    PassengerThread: Thread de simulation pour un passager
    IntersectionThread: Thread de simulation pour une intersection

Auteur: Hubert Ngankam
Email: hubert.ngankam@usherbrooke.ca
Session: H2025
Cours: IFT630
Version: 1.0
"""

from threading import Thread
from src.core.base_component_thread import BaseComponentThread

class IntersectionThread(BaseComponentThread):
    """Thread gérant le cycle de vie d'une intersection"""
    
    def __init__(self, intersection, stop_event):
        super().__init__(
            intersection, 
            stop_event, 
            f"Intersection-{intersection.name}"
        )
        
    def run(self):
        """Cycle de vie principal de l'intersection"""
        while not self.stop_event.is_set():
            # Surveillance du trafic à l'intersection
            self._monitor_traffic()
            self.sleep_random(1, 2)

    def _monitor_traffic(self):
        """Surveille le trafic à l'intersection"""
        buses_present = sum(
            1 for stop in self.component.stop_list 
            if getattr(stop, 'is_occupied', False)
        )
        if buses_present > 0:
            self.logger.info(
                f"🚦 Intersection {self.component.name}: {buses_present} bus présents"
            )
            
        bus_count = sum(1 for stop in self.component.stop_list if hasattr(stop, 'current_buses') and stop.current_buses)
        if bus_count > 0:
            self.logger.info(f"🚦 {self.component.name}: {bus_count} bus présents")
        self.sleep_random(2, 4)
            
     