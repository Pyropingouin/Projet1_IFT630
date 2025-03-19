"""
Module: message_components.py
---------------------------
Adaptation des composants du réseau STS pour utiliser le système de messagerie.

Fournit des wrappers et adaptateurs permettant aux composants existants
d'utiliser le broker de messages pour la communication.

Classes:
    MessageBusAdapter: Adaptateur pour les objets Bus
    MessageStopAdapter: Adaptateur pour les objets Stop

Auteur: [Votre Nom]
"""

from src.models.bus import Bus
from src.models.stop import Stop
from src.models.passenger import Passenger
from src.projects.project_2.core.message_broker import MessageBroker, Subscriber, Message, MessageType
from typing import List, Dict, Any


class MessageBusAdapter(Subscriber):
    """Adaptateur pour connecter les bus au système de messagerie"""
    
    def __init__(self, bus: Bus):
        """
        Initialise l'adaptateur pour un bus
        
        Args:
            bus: L'objet Bus à adapter
        """
        self.bus = bus
        self.broker = MessageBroker()
        self.id = f"Bus-{bus.id}"
        
        # Abonnement aux types de messages pertinents pour un bus
        self.broker.subscribe(
            self, 
            [
                MessageType.PASSENGER_BOARDING,
                MessageType.PASSENGER_ALIGHTING,
                MessageType.ROUTE_UPDATE,
                MessageType.SCHEDULE_UPDATE,
                MessageType.STOP_STATUS
            ]
        )
    
    def on_message(self, message: Message) -> None:
        """
        Traite les messages reçus du broker
        
        Args:
            message: Le message reçu
        """
        try:
            # Ignorer les messages envoyés par soi-même pour éviter les boucles
            if message.sender_id == self.id:
                return
            
            # Vérification de sécurité des données
            if not message.data or not isinstance(message.data, dict):
                return
                
            if message.type == MessageType.PASSENGER_BOARDING:
                # Un passager demande à monter
                self._handle_passenger_boarding_request(message)
                    
            elif message.type == MessageType.PASSENGER_ALIGHTING:
                # Un passager demande à descendre
                self._handle_passenger_alighting_request(message)
                        
            elif message.type == MessageType.ROUTE_UPDATE:
                # Mise à jour de route
                self._handle_route_update(message)
                
            elif message.type == MessageType.SCHEDULE_UPDATE:
                # Mise à jour d'horaire
                self._handle_schedule_update(message)
                
            elif message.type == MessageType.STOP_STATUS:
                # Mise à jour du statut d'un arrêt
                self._handle_stop_status_update(message)
                
        except Exception as e:
            # Log de l'erreur pour debuggage
            import logging
            logging.getLogger("bus_adapter").error(f"Erreur dans on_message: {e}")
    
    def _handle_passenger_boarding_request(self, message: Message) -> None:
        """Traite une demande d'embarquement de passager"""
        passenger_id = message.data.get('passenger_id')
        stop_id = message.data.get('stop_id')
        
        if not passenger_id or not stop_id:
            return
            
        # Vérifier si le bus peut accepter ce passager
        if (self.bus.current_stop and 
            hasattr(self.bus.current_stop, 'stop_id') and
            self.bus.current_stop.stop_id == stop_id and 
            self.bus.can_accept_passengers()):
            
            # Trouver le passager à l'arrêt
            if hasattr(self.bus.current_stop, 'waiting_passengers'):
                for passenger in self.bus.current_stop.waiting_passengers:
                    if hasattr(passenger, 'id') and passenger.id == passenger_id:
                        # Accepter le passager
                        if self.bus.add_passenger(passenger):
                            # Confirmer l'embarquement
                            self.publish_passenger_boarded(passenger, stop_id)
                        break
    
    def _handle_passenger_alighting_request(self, message: Message) -> None:
        """Traite une demande de débarquement de passager"""
        passenger_id = message.data.get('passenger_id')
        stop_id = message.data.get('stop_id')
        
        if not passenger_id or not stop_id:
            return
            
        # Vérifier les conditions pour le débarquement
        if (self.bus.current_stop and 
            hasattr(self.bus.current_stop, 'stop_id') and
            self.bus.current_stop.stop_id == stop_id):
            
            # Chercher le passager dans le bus
            for passenger in self.bus.passenger_list:
                if hasattr(passenger, 'id') and passenger.id == passenger_id:
                    # Faire descendre le passager
                    if self.bus.remove_passenger(passenger):
                        # Confirmer le débarquement
                        self.publish_passenger_alighted(passenger, stop_id)
                    break
    
    def _handle_route_update(self, message: Message) -> None:
        """
        Traite une mise à jour de route pour un bus.
        
        Cette fonction doit:
        - Vérifier que la mise à jour concerne bien ce bus
        - Trouver la nouvelle route dans le système
        - Mettre à jour la route actuelle du bus
        - Gérer les cas où la route n'existe pas
        """
        # TODO : À implémenter
        pass
    
    def _handle_schedule_update(self, message: Message) -> None:
        """
        Traite une mise à jour d'horaire.
        
        Cette fonction doit:
        - Extraire les informations d'horaire du message
        - Mettre à jour les horaires de départ/arrivée du bus
        - Ajuster le planning du bus en conséquence
        """
        # TODO : À implémenter
        pass
    
    def _handle_stop_status_update(self, message: Message) -> None:
        """
        Traite une mise à jour du statut d'un arrêt.
        
        Cette fonction doit:
        - Vérifier si l'arrêt concerné est pertinent pour ce bus
        - Mettre à jour les informations locales sur l'arrêt
        - Adapter le comportement du bus en fonction de l'état de l'arrêt
        (ex: file d'attente, occupation, passagers en attente)
        """
        # TODO : À implémenter
        pass
        
        
    
    def publish_arrival(self, stop_id: int) -> None:
        """
        Publie un message d'arrivée du bus à un arrêt
        
        Args:
            stop_id: ID de l'arrêt où le bus arrive
        """
        message = Message(
            MessageType.BUS_ARRIVAL,
            self.id,
            {
                'bus_id': self.bus.id,
                'stop_id': stop_id,
                'passenger_count': len(self.bus.passenger_list),
                'available_seats': self.bus.capacity - len(self.bus.passenger_list),
                'route_id': self.bus.current_route.id if self.bus.current_route else None
            }
        )
        self.broker.publish(message)
    
    def publish_departure(self, stop_id: int) -> None:
        """
        Publie un message de départ du bus d'un arrêt
        
        Args:
            stop_id: ID de l'arrêt que le bus quitte
        """
        message = Message(
            MessageType.BUS_DEPARTURE,
            self.id,
            {
                'bus_id': self.bus.id,
                'stop_id': stop_id,
                'passenger_count': len(self.bus.passenger_list),
                'next_stop_id': self.bus.next_stop.stop_id if self.bus.next_stop else None,
                'route_id': self.bus.current_route.id if self.bus.current_route else None
            }
        )
        self.broker.publish(message)
    
    def publish_passenger_boarded(self, passenger: Passenger, stop_id: int) -> None:
        """
        Publie un message confirmant l'embarquement d'un passager
        
        Args:
            passenger: Le passager qui est monté
            stop_id: ID de l'arrêt où l'embarquement a eu lieu
        """
        message = Message(
            MessageType.PASSENGER_BOARDING,
            self.id,
            {
                'bus_id': self.bus.id,
                'passenger_id': passenger.id,
                'stop_id': stop_id,
                'status': 'confirmed',
                'available_seats': self.bus.capacity - len(self.bus.passenger_list)
            }
        )
        self.broker.publish(message)
    
    def publish_passenger_alighted(self, passenger: Passenger, stop_id: int) -> None:
        """
        Publie un message confirmant le débarquement d'un passager
        
        Args:
            passenger: Le passager qui est descendu
            stop_id: ID de l'arrêt où le débarquement a eu lieu
        """
        message = Message(
            MessageType.PASSENGER_ALIGHTING,
            self.id,
            {
                'bus_id': self.bus.id,
                'passenger_id': passenger.id,
                'stop_id': stop_id,
                'status': 'confirmed',
                'available_seats': self.bus.capacity - len(self.bus.passenger_list)
            }
        )
        self.broker.publish(message)
    
    def publish_capacity_update(self) -> None:
        """Publie une mise à jour de la capacité du bus"""
        message = Message(
            MessageType.CAPACITY_UPDATE,
            self.id,
            {
                'bus_id': self.bus.id,
                'total_capacity': self.bus.capacity,
                'available_seats': self.bus.capacity - len(self.bus.passenger_list),
                'passenger_count': len(self.bus.passenger_list)
            }
        )
        self.broker.publish(message)


class MessageStopAdapter(Subscriber):
    """Adaptateur pour connecter les arrêts au système de messagerie"""
    
    def __init__(self, stop: Stop):
        """
        Initialise l'adaptateur pour un arrêt
        
        Args:
            stop: L'objet Stop à adapter
        """
        self.stop = stop
        self.broker = MessageBroker()
        self.id = f"Stop-{stop.stop_id}"
        
        # Abonnement aux types de messages pertinents pour un arrêt
        self.broker.subscribe(
            self, 
            [
                MessageType.BUS_ARRIVAL,
                MessageType.BUS_DEPARTURE,
                MessageType.PASSENGER_BOARDING,
                MessageType.PASSENGER_ALIGHTING,
                MessageType.CAPACITY_UPDATE
            ]
        )
    
    def on_message(self, message: Message) -> None:
        """
        Traite les messages reçus du broker
        
        Args:
            message: Le message reçu
        """
        try:
            # Ignorer les messages envoyés par soi-même pour éviter les boucles
            if message.sender_id == self.id:
                return
                
            # Vérification de sécurité des données
            if not message.data or not isinstance(message.data, dict):
                return
                
            if message.type == MessageType.BUS_ARRIVAL:
                # Un bus arrive à cet arrêt
                self._handle_bus_arrival(message)
                    
            elif message.type == MessageType.BUS_DEPARTURE:
                # Un bus quitte cet arrêt
                self._handle_bus_departure(message)
                    
            elif message.type == MessageType.PASSENGER_BOARDING:
                # Confirmation d'embarquement d'un passager
                self._handle_passenger_boarding_confirmation(message)
                    
            elif message.type == MessageType.PASSENGER_ALIGHTING:
                # Un passager est descendu à cet arrêt
                self._handle_passenger_alighting_confirmation(message)
                    
            elif message.type == MessageType.CAPACITY_UPDATE:
                # Mise à jour de la capacité d'un bus
                self._handle_capacity_update(message)
                
        except Exception as e:
            # Log de l'erreur pour debuggage
            import logging
            logging.getLogger("stop_adapter").error(f"Erreur dans on_message: {e}")
    
    def _handle_bus_arrival(self, message: Message) -> None:
        """Traite l'arrivée d'un bus à cet arrêt"""
        stop_id = message.data.get('stop_id')
        
        # Vérifier que le message concerne bien cet arrêt
        if not hasattr(self.stop, 'stop_id') or stop_id != self.stop.stop_id:
            return
            
        bus_id = message.data.get('bus_id')
        if bus_id is not None:
            # Notifier les passagers en attente
            self.publish_stop_status(bus_arrivals=[bus_id])
    
    def _handle_bus_departure(self, message: Message) -> None:
        """Traite le départ d'un bus de cet arrêt"""
        stop_id = message.data.get('stop_id')
        
        # Vérifier que le message concerne bien cet arrêt
        if not hasattr(self.stop, 'stop_id') or stop_id != self.stop.stop_id:
            return
            
        bus_id = message.data.get('bus_id')
        if bus_id is not None:
            # Mettre à jour l'état de l'arrêt
            self.publish_stop_status(bus_departures=[bus_id])
    
    def _handle_passenger_boarding_confirmation(self, message: Message) -> None:
        """Traite la confirmation d'embarquement d'un passager"""
        stop_id = message.data.get('stop_id')
        
        # Vérifier que le message concerne bien cet arrêt et qu'il s'agit d'une confirmation
        if (not hasattr(self.stop, 'stop_id') or 
            stop_id != self.stop.stop_id or 
            message.data.get('status') != 'confirmed'):
            return
            
        passenger_id = message.data.get('passenger_id')
        if passenger_id is not None and hasattr(self.stop, 'waiting_passengers'):
            # Retirer le passager de la liste d'attente
            for passenger in list(self.stop.waiting_passengers):  # Copie pour éviter les problèmes de modification
                if hasattr(passenger, 'id') and passenger.id == passenger_id:
                    self.stop.remove_passenger(passenger)
                    break
    
    def _handle_passenger_alighting_confirmation(self, message: Message) -> None:
        """
        Traite la confirmation de débarquement d'un passager.
        
        Cette fonction gère l'arrivée d'un passager à l'arrêt après qu'il
        soit descendu d'un bus, en l'ajoutant à la liste des passagers présents.
        
        Cette fonction doit:
        - Vérifier que le message concerne bien cet arrêt
        - Identifier le passager concerné
        - Ajouter le passager à la liste des passagers de l'arrêt
        - Mettre à jour les statistiques de l'arrêt
        """
        stop_id = message.data.get('stop_id')
        
        # TODO : À implémenter
        pass
    
    def _handle_capacity_update(self, message: Message) -> None:
        """
        Traite une mise à jour de capacité d'un bus.
        
        Cette fonction permet à l'arrêt de connaître la disponibilité des bus
        et d'optimiser l'embarquement des passagers en attente.
        
        Cette fonction doit:
        - Extraire les informations de capacité du message
        - Informer les passagers en attente des places disponibles
        - Optimiser l'ordre d'embarquement des passagers en fonction des places disponibles
        - Mettre à jour l'affichage virtuel de l'arrêt
    
        """
        # TODO : À implémenter
        pass
    
    def publish_stop_status(self, bus_arrivals=None, bus_departures=None) -> None:
        """
        Publie l'état actuel de l'arrêt
        
        Args:
            bus_arrivals: Liste des ID des bus qui viennent d'arriver
            bus_departures: Liste des ID des bus qui viennent de partir
        """
        current_buses = [bus.id for bus in self.stop.get_current_buses()]
        queued_buses = [bus.id for bus in self.stop.bus_queue]
        
        message = Message(
            MessageType.STOP_STATUS,
            self.id,
            {
                'stop_id': self.stop.stop_id,
                'stop_name': self.stop.name,
                'is_occupied': self.stop.is_occupied,
                'waiting_passengers': len(self.stop.waiting_passengers),
                'current_buses': current_buses,
                'queued_buses': queued_buses,
                'bus_arrivals': bus_arrivals or [],
                'bus_departures': bus_departures or []
            }
        )
        self.broker.publish(message)
    
    def request_boarding(self, passenger: Passenger, target_bus_id: int) -> None:
        """
        Demande l'embarquement d'un passager dans un bus spécifique
        
        Args:
            passenger: Le passager qui souhaite embarquer
            target_bus_id: L'ID du bus ciblé
        """
        
        # Vérification que l'arrêt et le passager ont les attributs nécessaires
        if not hasattr(self.stop, 'stop_id') or not hasattr(passenger, 'id'):
            import logging
            logging.getLogger("stop_adapter").error(
                f"Impossible de demander l'embarquement: attributs manquants"
            )
            return
            
        message = Message(
            MessageType.PASSENGER_BOARDING,
            self.id,
            {
                'passenger_id': passenger.id,
                'stop_id': self.stop.stop_id,
                'bus_id': target_bus_id,
                'category': getattr(passenger, 'category', 'Regular'),
                'destination_id': getattr(passenger.destination, 'id', None) if hasattr(passenger, 'destination') else None,
                'status': 'requested'
            }
        )
        self.broker.publish(message)