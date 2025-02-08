"""
Module de surveillance des performances pour Project 1.

Suit les métriques de performance des différents mécanismes
de synchronisation et composants du système.

Classes:
    PerformanceMonitor: Moniteur principal des performances
    MetricCollector: Collecteur de métriques spécifiques
    PerformanceMetrics: Structure de données pour les métriques

Auteur: Hubert Ngankam
"""

import time
import logging
from threading import Event, Lock
from dataclasses import dataclass
from typing import Dict, List, Optional
from collections import defaultdict

@dataclass
class PerformanceMetrics:
    """Structure pour stocker les métriques de performance"""
    start_time: float
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    total_wait_time: float = 0.0
    total_processing_time: float = 0.0
    max_wait_time: float = 0.0
    min_wait_time: float = float('inf')

class MetricCollector:
    """Collecteur de métriques spécifiques"""
    
    def __init__(self, component_type: str):
        self.component_type = component_type
        self.metrics = PerformanceMetrics(start_time=time.time())
        self.lock = Lock()
        
    def record_operation(self, success: bool, wait_time: float, processing_time: float):
        """Enregistre une opération avec ses métriques"""
        with self.lock:
            self.metrics.total_operations += 1
            if success:
                self.metrics.successful_operations += 1
            else:
                self.metrics.failed_operations += 1
                
            self.metrics.total_wait_time += wait_time
            self.metrics.total_processing_time += processing_time
            self.metrics.max_wait_time = max(self.metrics.max_wait_time, wait_time)
            self.metrics.min_wait_time = min(self.metrics.min_wait_time, wait_time)
    
    def get_summary(self) -> Dict:
        """Retourne un résumé des métriques"""
        with self.lock:
            total_time = time.time() - self.metrics.start_time
            ops_per_second = self.metrics.total_operations / total_time if total_time > 0 else 0
            success_rate = (self.metrics.successful_operations / self.metrics.total_operations * 100 
                          if self.metrics.total_operations > 0 else 0)
            
            return {
                'component_type': self.component_type,
                'total_operations': self.metrics.total_operations,
                'operations_per_second': round(ops_per_second, 2),
                'success_rate': round(success_rate, 2),
                'avg_wait_time': (self.metrics.total_wait_time / self.metrics.total_operations 
                                if self.metrics.total_operations > 0 else 0),
                'max_wait_time': self.metrics.max_wait_time,
                'min_wait_time': self.metrics.min_wait_time if self.metrics.min_wait_time != float('inf') else 0
            }

class PerformanceMonitor:
    """Moniteur principal des performances du système"""
    
    def __init__(self):
        self.collectors: Dict[str, MetricCollector] = {}
        self.stop_event = Event()
        self.logger = logging.getLogger('performance_monitor')
        self.lock = Lock()
        
    def start_monitoring(self):
        """Démarre la surveillance des performances"""
        self.stop_event.clear()
        self.logger.info("Démarrage du moniteur de performance")
        
        # Initialisation des collecteurs pour chaque type de composant
        component_types = [
            'passenger', 'bus', 'stop', 'station', 'intersection',
            'mutex', 'rlock', 'semaphore', 'condition', 'barrier',
            'rwlock', 'future', 'monitor'
        ]
        
        with self.lock:
            for comp_type in component_types:
                self.collectors[comp_type] = MetricCollector(comp_type)
    
    def stop_monitoring(self):
        """Arrête la surveillance et génère un rapport final"""
        self.stop_event.set()
        self.logger.info("Arrêt du moniteur de performance")
        self._generate_report()
    
    def record_event(self, component_type: str, success: bool, 
                    wait_time: float = 0.0, processing_time: float = 0.0):
        """Enregistre un événement de performance"""
        if component_type in self.collectors:
            self.collectors[component_type].record_operation(
                success, wait_time, processing_time
            )
        else:
            self.logger.warning(f"Type de composant inconnu: {component_type}")
    
    def _generate_report(self):
        """Génère un rapport complet des performances"""
        self.logger.info("=== Rapport de Performance ===")
        
        with self.lock:
            for component_type, collector in self.collectors.items():
                metrics = collector.get_summary()
                self.logger.info(f"\nPerformance - {component_type}:")
                for key, value in metrics.items():
                    if isinstance(value, float):
                        self.logger.info(f"  {key}: {value:.2f}")
                    else:
                        self.logger.info(f"  {key}: {value}")
    
    def get_metrics(self, component_type: Optional[str] = None) -> Dict:
        """Récupère les métriques pour un type de composant ou tous"""
        with self.lock:
            if component_type:
                if component_type in self.collectors:
                    return {component_type: self.collectors[component_type].get_summary()}
                return {}
            
            return {comp_type: collector.get_summary() 
                   for comp_type, collector in self.collectors.items()}