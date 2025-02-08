"""
Module de journalisation des événements pour Project 1.

Fournit un système de journalisation avancé pour suivre tous les
événements liés aux mécanismes de synchronisation et aux composants
du système.

Classes:
    EventLogger: Logger principal des événements système
    EventType: Types d'événements du système
    SyncEvent: Structure pour les événements de synchronisation

Auteur: Hubert Ngankam
"""

import logging
import time
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from threading import Lock
from pathlib import Path
from typing import Dict, List, Optional
from colorama import Fore, Style, init

# Initialisation de colorama pour le support des couleurs dans la console
init()

class EventType(Enum):
    """Types d'événements du système"""
    # Événements de synchronisation
    MUTEX_ACQUIRE = "MUTEX_ACQUIRE"
    MUTEX_RELEASE = "MUTEX_RELEASE"
    RLOCK_ACQUIRE = "RLOCK_ACQUIRE"
    RLOCK_RELEASE = "RLOCK_RELEASE"
    SEMAPHORE_ACQUIRE = "SEMAPHORE_ACQUIRE"
    SEMAPHORE_RELEASE = "SEMAPHORE_RELEASE"
    CONDITION_WAIT = "CONDITION_WAIT"
    CONDITION_NOTIFY = "CONDITION_NOTIFY"
    BARRIER_WAIT = "BARRIER_WAIT"
    BARRIER_RELEASE = "BARRIER_RELEASE"
    RWLOCK_READ_ACQUIRE = "RWLOCK_READ_ACQUIRE"
    RWLOCK_WRITE_ACQUIRE = "RWLOCK_WRITE_ACQUIRE"
    RWLOCK_RELEASE = "RWLOCK_RELEASE"
    FUTURE_START = "FUTURE_START"
    FUTURE_COMPLETE = "FUTURE_COMPLETE"
    MONITOR_ENTER = "MONITOR_ENTER"
    MONITOR_EXIT = "MONITOR_EXIT"
    
    # Événements système
    SYSTEM_START = "SYSTEM_START"
    SYSTEM_STOP = "SYSTEM_STOP"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    
    # Événements composants
    PASSENGER_BOARD = "PASSENGER_BOARD"
    PASSENGER_ALIGHT = "PASSENGER_ALIGHT"
    BUS_ARRIVE = "BUS_ARRIVE"
    BUS_DEPART = "BUS_DEPART"
    STOP_FULL = "STOP_FULL"
    STOP_AVAILABLE = "STOP_AVAILABLE"
    RESERVATION_MADE = "RESERVATION_MADE"
    RESERVATION_CANCELLED = "RESERVATION_CANCELLED"
    TRANSFER_START = "TRANSFER_START"
    TRANSFER_COMPLETE = "TRANSFER_COMPLETE"

@dataclass
class SyncEvent:
    """Structure pour stocker les informations d'un événement"""
    event_type: EventType
    component_id: str
    timestamp: float
    thread_id: str
    details: Dict
    duration: Optional[float] = None
    status: str = "SUCCESS"
    
    def to_dict(self) -> Dict:
        """Convertit l'événement en dictionnaire"""
        return {
            'event_type': self.event_type.value,
            'component_id': self.component_id,
            'timestamp': self.timestamp,
            'thread_id': self.thread_id,
            'details': self.details,
            'duration': self.duration,
            'status': self.status
        }

class EventLogger:
    """Logger principal des événements système"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.events: List[SyncEvent] = []
        self.lock = Lock()
        self._setup_logging()
        
        # Couleurs pour différents types d'événements
        self.colors = {
            'MUTEX': Fore.GREEN,
            'RLOCK': Fore.BLUE,
            'SEMAPHORE': Fore.YELLOW,
            'CONDITION': Fore.MAGENTA,
            'BARRIER': Fore.CYAN,
            'RWLOCK': Fore.RED,
            'FUTURE': Fore.WHITE,
            'MONITOR': Fore.LIGHTBLUE_EX,
            'SYSTEM': Fore.LIGHTWHITE_EX,
            'PASSENGER': Fore.LIGHTGREEN_EX,
            'BUS': Fore.LIGHTYELLOW_EX,
            'STOP': Fore.LIGHTRED_EX,
            'RESERVATION': Fore.LIGHTMAGENTA_EX,
            'TRANSFER': Fore.LIGHTCYAN_EX
        }
    
    def _setup_logging(self):
        """Configure les loggers"""
        # Timestamp pour le nom du fichier
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Logger pour les événements
        self.event_logger = logging.getLogger('event_logger')
        self.event_logger.setLevel(logging.INFO)
        
        # Handler pour la console avec couleurs
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self._get_colored_formatter())
        self.event_logger.addHandler(console_handler)
        
        # Handler pour le fichier
        file_handler = logging.FileHandler(
            self.log_dir / f"events_{timestamp}.log",
            encoding='utf-8'
        )
        file_handler.setFormatter(self._get_file_formatter())
        self.event_logger.addHandler(file_handler)
    
    def _get_colored_formatter(self):
        """Retourne un formateur pour la sortie console colorée"""
        return logging.Formatter(
            '%(asctime)s - %(color)s%(levelname)s - %(message)s%(reset)s',
            datefmt='%H:%M:%S'
        )
    
    def _get_file_formatter(self):
        """Retourne un formateur pour la sortie fichier"""
        return logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def log_event(self, event_type: EventType, component_id: str,
                  thread_id: str, details: Dict = None,
                  duration: float = None, status: str = "SUCCESS"):
        """Enregistre un nouvel événement"""
        with self.lock:
            event = SyncEvent(
                event_type=event_type,
                component_id=component_id,
                timestamp=time.time(),
                thread_id=thread_id,
                details=details or {},
                duration=duration,
                status=status
            )
            self.events.append(event)
            
            # Détermine la couleur basée sur le type d'événement
            event_category = event_type.value.split('_')[0]
            color = self.colors.get(event_category, Fore.WHITE)
            
            # Formatage du message
            message = self._format_event_message(event)
            
            # Log avec le niveau approprié
            if status == "ERROR":
                self.event_logger.error(message, extra={'color': color, 'reset': Style.RESET_ALL})
            elif status == "WARNING":
                self.event_logger.warning(message, extra={'color': color, 'reset': Style.RESET_ALL})
            else:
                self.event_logger.info(message, extra={'color': color, 'reset': Style.RESET_ALL})
    
    def _format_event_message(self, event: SyncEvent) -> str:
        """Formate le message de l'événement pour le log"""
        message = f"[{event.event_type.value}] {event.component_id} - {event.thread_id}"
        
        if event.duration is not None:
            message += f" (durée: {event.duration:.3f}s)"
        
        if event.details:
            details_str = ", ".join(f"{k}: {v}" for k, v in event.details.items())
            message += f" - {details_str}"
        
        if event.status != "SUCCESS":
            message += f" - Status: {event.status}"
        
        return message
    
    def get_events(self, event_type: Optional[EventType] = None,
                  component_id: Optional[str] = None,
                  start_time: Optional[float] = None,
                  end_time: Optional[float] = None) -> List[SyncEvent]:
        """Récupère les événements filtrés"""
        with self.lock:
            filtered_events = self.events
            
            if event_type:
                filtered_events = [e for e in filtered_events if e.event_type == event_type]
            
            if component_id:
                filtered_events = [e for e in filtered_events if e.component_id == component_id]
            
            if start_time:
                filtered_events = [e for e in filtered_events if e.timestamp >= start_time]
            
            if end_time:
                filtered_events = [e for e in filtered_events if e.timestamp <= end_time]
            
            return filtered_events
    
    def generate_report(self, output_file: Optional[str] = None):
        """Génère un rapport détaillé des événements"""
        with self.lock:
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.log_dir / f"event_report_{timestamp}.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=== Rapport des Événements de Synchronisation ===\n\n")
                
                # Statistiques globales
                f.write("Statistiques Globales:\n")
                f.write(f"Total des événements: {len(self.events)}\n")
                
                # Événements par type
                events_by_type = {}
                for event in self.events:
                    events_by_type.setdefault(event.event_type.value, []).append(event)
                
                f.write("\nRépartition par type d'événement:\n")
                for event_type, events in events_by_type.items():
                    f.write(f"{event_type}: {len(events)}\n")
                
                # Événements par composant
                events_by_component = {}
                for event in self.events:
                    events_by_component.setdefault(event.component_id, []).append(event)
                
                f.write("\nRépartition par composant:\n")
                for component, events in events_by_component.items():
                    f.write(f"{component}: {len(events)}\n")
                
                # Détails des événements
                f.write("\nDétail des événements:\n")
                for event in self.events:
                    f.write(f"\n{self._format_event_message(event)}")
            
            self.event_logger.info(f"Rapport généré: {output_file}")

# Exemples d'utilisation
# if __name__ == "__main__":
#     logger = EventLogger()
    
#     # Log d'événements exemple
#     logger.log_event(
#         EventType.MUTEX_ACQUIRE,
#         "Bus-1",
#         "Thread-1",
#         {"action": "boarding", "passengers": 3}
#     )
    
#     time.sleep(0.5)
    
#     logger.log_event(
#         EventType.MUTEX_RELEASE,
#         "Bus-1",
#         "Thread-1",
#         {"action": "boarding_complete"},
#         duration=0.5
#     )
    
#     # Génération du rapport
#     logger.generate_report()