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

class StationThread(BaseComponentThread):
    """Thread gérant le cycle de vie d'une station"""
    
    def __init__(self, station, stop_event):
        super().__init__(
            station, 
            stop_event, 
            f"Station-{station.name}"
        )
        
    def run(self):
        """Cycle de vie principal de la station"""
        while not self.stop_event.is_set():
            # Surveillance des arrêts de la station
            self._monitor_stops()
            self.sleep_random(2, 4)

    def _monitor_stops(self):
        """Surveille l'état des arrêts de la station"""
        total_passengers = sum(len(stop.passenger_list) for stop in self.component.stop_list)
        if total_passengers > 0:
            self.logger.info(
                f"🏢 Station {self.component.name}: {total_passengers} passagers total"
            )
