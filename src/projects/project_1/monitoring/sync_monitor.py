import logging
from threading import Event

class SyncMonitor:
    def __init__(self):
        self.stop_event = Event()
        self.logger = logging.getLogger('sync_monitor')

    def start_monitoring(self):
        """Démarre la surveillance"""
        self.stop_event.clear()
        self.logger.info("Démarrage de la surveillance de synchronisation")

    def stop_monitoring(self):
        """Arrête la surveillance"""
        self.stop_event.set()
        self.logger.info("Arrêt de la surveillance de synchronisation")

    def log_sync_event(self, sync_type: str, component: str, event: str):
        """Enregistre un événement de synchronisation"""
        self.logger.info(f"[{sync_type}] {component}: {event}")