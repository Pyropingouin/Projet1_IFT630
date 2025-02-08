"""
Point d'entrée principal pour la simulation avec gestion des synchronisations.
"""
import logging
from enum import Enum
from pathlib import Path
from datetime import datetime
from typing import Optional

from src.projects.project_1.core import (
    mutex_sync, rlock_sync, semaphore_sync, condition_sync,
    barrier_sync, rwlock_sync, future_sync, monitor_sync
)
from src.projects.project_1.monitoring import sync_monitor, performance_monitor
from src.ui.formatter import ColoredFormatter, FileFormatter
from src.seed.stsseed import STSSeed

class SyncType(Enum):
    """Types de synchronisation disponibles"""
    MUTEX = "mutex"
    RLOCK = "rlock"
    SEMAPHORE = "semaphore"
    CONDITION = "condition"
    BARRIER = "barrier"
    RWLOCK = "rwlock"
    FUTURE = "future"
    MONITOR = "monitor"

class Simulation1:
    def __init__(self, seed: STSSeed, sync_type: SyncType):
        """
        Initialise la simulation avec le type de synchronisation spécifié
        
        Args:
            seed: Instance de STSSeed initialisée
            sync_type: Type de synchronisation à utiliser
        """
        self.seed = seed
        self.sync_type = sync_type
        self.sync_manager = None
        self.monitor = sync_monitor.SyncMonitor()
        self.perf_monitor = performance_monitor.PerformanceMonitor()
        self.setup_logging()

    def setup_logging(self):
        """Configure le système de logging"""
        # Configuration du logger root pour que tous les loggers héritent de la même configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.handlers.clear()
        
        # Création du dossier logs
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = log_dir / f"simulation1_sync_{timestamp}.log"
        
        # Handler console avec couleurs
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter()
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # Handler fichier
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # DEBUG pour plus de détails dans le fichier
        file_formatter = FileFormatter()
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # Configuration du logger spécifique à simulation1
        self.logger = logging.getLogger('simulation1')
        self.logger.info("🔧 Initialisation du système de synchronisation")

    @staticmethod
    def run(duration: int, sync_type: str = "mutex"):
        """Lance la simulation avec le type de synchronisation spécifié"""
        try:
            sync_type = SyncType(sync_type.lower())
            
            # Initialisation du système
            seed = STSSeed()
            if not seed.initialize_system():
                logging.error("Échec de l'initialisation du système")
                return False
                
            # Création et exécution de la simulation
            sim = Simulation1(seed, sync_type)
            return sim._run_simulation(duration)
            
        except ValueError as e:
            logging.error(f"Type de synchronisation invalide: {e}")
            return False
        except Exception as e:
            logging.error(f"Erreur lors du lancement de la simulation: {e}")
            return False

    def _run_simulation(self, duration: int):
        """Exécute la simulation avec la synchronisation choisie"""
        try:
            self.logger.info(f"🚀 Démarrage de la simulation avec {self.sync_type.value}")
            
            # Création du gestionnaire de synchronisation approprié
            self.sync_manager = self._create_sync_manager()
            
            # Démarrage des moniteurs
            self.monitor.start_monitoring()
            self.perf_monitor.start_monitoring()
            
            # Initialisation de la synchronisation
            if not self.sync_manager.initialize():
                raise RuntimeError("Échec de l'initialisation du gestionnaire de synchronisation")
            
            # Exécution des scénarios
            self.sync_manager.run_scenarios(duration)
            
            self.logger.info("✅ Simulation terminée avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur pendant la simulation: {e}")
            return False
            
        finally:
            if self.sync_manager:
                self.sync_manager.cleanup()
            self.monitor.stop_monitoring()
            self.perf_monitor.stop_monitoring()
            self.logger.info(f"📝 Logs disponibles dans: {self.log_file}")

    def _create_sync_manager(self):
        """Crée le gestionnaire de synchronisation approprié"""
        sync_managers = {
            SyncType.MUTEX: mutex_sync.MutexSyncManager,
            SyncType.RLOCK: rlock_sync.RLockSyncManager,
            SyncType.SEMAPHORE: semaphore_sync.SemaphoreSyncManager,
            SyncType.CONDITION: condition_sync.ConditionSyncManager,
            SyncType.BARRIER: barrier_sync.BarrierSyncManager,
            SyncType.RWLOCK: rwlock_sync.RWLockSyncManager,
            SyncType.FUTURE: future_sync.FutureSyncManager,
            SyncType.MONITOR: monitor_sync.MonitorSyncManager
        }
        
        manager_class = sync_managers.get(self.sync_type)
        if not manager_class:
            raise ValueError(f"Type de synchronisation non supporté: {self.sync_type}")
            
        return manager_class(self.seed, self.monitor, self.perf_monitor)
    
    @staticmethod
    def run_simulation_1(duration):
        """Lance la simulation 1 en testant chaque type de synchronisation."""
        # Test de chaque type de synchronisation dans l'enum
        for sync_type in SyncType:
            print(f"\nSimulation de synchronisation avec {sync_type.value}")
            Simulation1.run(duration, sync_type=sync_type.value)