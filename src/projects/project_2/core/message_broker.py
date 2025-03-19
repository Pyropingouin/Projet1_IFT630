"""
Module: message_broker.py
-----------------------
Implémentation d'un système de messagerie simple pour la communication
entre les différents composants du réseau STS.

Fournit un mécanisme de publication/abonnement (pub/sub) pour découpler
les composants et faciliter la communication asynchrone.

Classes:
    Message: Structure d'un message
    MessageBroker: Broker central de messagerie
    Subscriber: Interface pour les abonnés

Auteur: [Votre Nom]
"""

import queue
import threading
import time
from enum import Enum
from typing import Dict, List, Any, Callable, Set


class MessageType(Enum):
    """Types de messages supportés par le système"""
    BUS_ARRIVAL = "bus_arrival"
    BUS_DEPARTURE = "bus_departure"
    PASSENGER_BOARDING = "passenger_boarding"
    PASSENGER_ALIGHTING = "passenger_alighting"
    ROUTE_UPDATE = "route_update"
    SCHEDULE_UPDATE = "schedule_update"
    SYSTEM_ALERT = "system_alert"
    STOP_STATUS = "stop_status"
    STATION_STATUS = "station_status"
    CAPACITY_UPDATE = "capacity_update"


class Message:
    """Structure de base d'un message dans le système"""
    
    def __init__(self, msg_type: MessageType, sender_id: str, data: Dict[str, Any] = None, 
                 timestamp: float = None):
        """
        Initialise un nouveau message
        
        Args:
            msg_type: Type du message (de l'enum MessageType)
            sender_id: Identifiant du composant émetteur
            data: Données associées au message (dictionnaire)
            timestamp: Horodatage du message (par défaut: temps actuel)
        """
        self.type = msg_type
        self.sender_id = sender_id
        self.data = data or {}
        self.timestamp = timestamp or time.time()
        self.id = f"{sender_id}-{self.timestamp}"
    
    def __str__(self):
        """Représentation textuelle du message"""
        return f"Message[{self.type.value}] from {self.sender_id}: {self.data}"


class Subscriber:
    """Interface pour les composants qui s'abonnent à des messages"""
    
    def on_message(self, message: Message) -> None:
        """
        Méthode appelée lors de la réception d'un message
        
        Args:
            message: Le message reçu
        """
        raise NotImplementedError("Les classes dérivées doivent implémenter cette méthode")


class MessageBroker:
    """
    Broker central pour la communication par messages entre composants.
    Implémente un pattern Singleton pour assurer une instance unique.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Implémentation du pattern Singleton"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MessageBroker, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        """Initialisation du broker (une seule fois)"""
        if self._initialized:
            return
            
        self._initialized = True
        self._subscribers: Dict[MessageType, Set[Subscriber]] = {msg_type: set() for msg_type in MessageType}
        self._message_queue = queue.Queue()
        self._stop_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._process_messages, daemon=True, 
                                              name="MessageBroker")
        self._worker_thread.start()
        self._logger = self._setup_logger()
    
    def _setup_logger(self):
        """Configure un logger pour le broker"""
        import logging
        logger = logging.getLogger("message_broker")
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def subscribe(self, subscriber: Subscriber, message_types: List[MessageType]) -> None:
        """
        Abonne un composant à des types de messages spécifiques
        
        Args:
            subscriber: Le composant à abonner
            message_types: Liste des types de messages d'intérêt
        """
        for msg_type in message_types:
            self._subscribers[msg_type].add(subscriber)
            self._logger.info(f"Nouvel abonnement: {subscriber.__class__.__name__} pour {msg_type.value}")
    
    def unsubscribe(self, subscriber: Subscriber, message_types: List[MessageType] = None) -> None:
        """
        Désabonne un composant de types de messages spécifiques ou de tous les types
        
        Args:
            subscriber: Le composant à désabonner
            message_types: Liste des types de messages à désabonner, ou None pour tous
        """
        if message_types is None:
            message_types = list(MessageType)
            
        for msg_type in message_types:
            if subscriber in self._subscribers[msg_type]:
                self._subscribers[msg_type].remove(subscriber)
                self._logger.info(f"Désabonnement: {subscriber.__class__.__name__} de {msg_type.value}")
    
    def publish(self, message: Message) -> None:
        """
        Publie un message à tous les abonnés concernés
        
        Args:
            message: Le message à publier
        """
        self._message_queue.put(message)
        self._logger.debug(f"Message mis en file: {message}")
    
    def _process_messages(self) -> None:
        """
        Traite les messages en file d'attente et les distribue aux abonnés.
        Cette méthode s'exécute dans un thread dédié.
        """
        while not self._stop_event.is_set():
            try:
                # Attendre un message avec timeout pour permettre l'arrêt propre
                try:
                    message = self._message_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                    
                # Distribuer le message aux abonnés du type correspondant
                subscribers = self._subscribers.get(message.type, set())
                
                for subscriber in subscribers:
                    try:
                        subscriber.on_message(message)
                    except Exception as e:
                        self._logger.error(f"Erreur lors de la livraison à {subscriber.__class__.__name__}: {e}")
                        
                # Marquer le message comme traité
                self._message_queue.task_done()
                
            except Exception as e:
                self._logger.error(f"Erreur dans le thread de traitement: {e}")
    
    def shutdown(self) -> None:
        """Arrête proprement le broker de messages"""
        self._logger.info("Arrêt du broker de messages...")
        self._stop_event.set()
        
        if self._worker_thread.is_alive():
            self._worker_thread.join(timeout=2.0)
            
        # Vider la file de messages
        while not self._message_queue.empty():
            try:
                self._message_queue.get_nowait()
                self._message_queue.task_done()
            except queue.Empty:
                break
                
        self._logger.info("Broker de messages arrêté")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur le broker"""
        stats = {
            "queue_size": self._message_queue.qsize(),
            "subscribers_count": {msg_type.value: len(subs) for msg_type, subs in self._subscribers.items()},
            "total_subscribers": sum(len(subs) for subs in self._subscribers.values())
        }
        return stats