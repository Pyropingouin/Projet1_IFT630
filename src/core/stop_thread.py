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


class StopThread(BaseComponentThread):
    """Thread gérant le cycle de vie d'un arrêt"""
    
    def __init__(self, stop, stop_event):
        super().__init__(
            stop, 
            stop_event, 
            f"Stop-{stop.name}"
        )
        
    def run(self):
        """Cycle de vie principal de l'arrêt"""
        while not self.stop_event.is_set():
            # Gestion de la file d'attente des bus
            self._manage_bus_queue()
            
            # Gestion des passagers en attente
            self._manage_waiting_passengers()
            
            passenger_count = len(self.component.waiting_passengers)
            if passenger_count > 0:
                self.logger.info(f"🚏 {passenger_count} passagers en attente à {self.component.name}")
            self.sleep_random(2, 4)
            

    def _manage_bus_queue(self):
        """Gère la file d'attente des bus"""
        if not self.component.is_occupied and len(self.component.bus_queue) > 0:
            next_bus = self.component.bus_queue.popleft()  # Utilisation de popleft() pour deque
            self.component.bus_arrival(next_bus)
            self.logger.info(f"🚌 Bus {next_bus.id} accède à l'arrêt {self.component.name}")

    def _manage_waiting_passengers(self):
        """Gère les passagers en attente"""
        waiting_count = len(self.component.waiting_passengers)
        if waiting_count > 0:
            self.logger.info(
                f"⌛ {waiting_count} passagers en attente à {self.component.name}"
            )