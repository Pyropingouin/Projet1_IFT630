"""
Module: message_components.py
---------------------------
Adaptation des composants du réseau STS pour utiliser le système de messagerie.

Fournit des wrappers et adaptateurs permettant aux composants existants
d'utiliser le broker de messages pour la communication.

Classes:
    MessageBusAdapter: Adaptateur pour les objets Bus
    MessageStopAdapter: Adaptateur pour les objets Stop

Auteur: [Cédrik Lampron]
"""

import logging
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
           
            #raise Exception("Une erreur est survenue")
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
        #Todo: DONE

        # extraction des informations pertinentes du message        
        bus_id = message.data.get('bus_id')
        new_route = message.data.get('route_id')
        
        # s'assurer que les informations sont valides et/ou pertinentes
        if bus_id != self.bus.id or new_route is None:
            # gestion d'une route inexistante, on ne fait pas la mise à jour de la route pour le bus
            logging.warning(f"Bus {self.bus.id}: Route non spécifiée ou incorrecte dans le message: {message.data}")
            return
        
    
        # mise à jour de la route actuelle du bus
        if hasattr(self.bus, 'current_route'):
            self.bus.current_route = new_route


    
    def _handle_schedule_update(self, message: Message) -> None:
        """
        Traite une mise à jour d'horaire.
        
        Cette fonction doit:
        - Extraire les informations d'horaire du message
        - Mettre à jour les horaires de départ/arrivée du bus
        - Ajuster le planning du bus en conséquence
        """


        # extraction des informations pertinentes du message        
        bus_id = message.data.get('bus_id')
        departure_time = message.data.get('departure_time')
        arrival_time = message.data.get('arrival_time')
        
        # s'assurer que les informations sont valides et/ou pertinentes
        if bus_id != self.bus.id or departure_time is None or arrival_time is None:
            return
        

        # ajout des attributes nécéssaires si le bus ne les possèdes pas déja
        if not hasattr(self.bus, 'departure_time'):
           self.bus.departure_time = {}

        if not hasattr(self.bus, "arrival_time"):
           self.bus.arrival_time = {}   
        
           
        # mise à jour des temps d'arrivée et de départ du bus 
        if hasattr(self.bus, 'departure_time'):
            self.bus.departure_time = departure_time
               
        if hasattr(self.bus, 'arrival_time'):
            self.bus.arrival_time = arrival_time    



        logging.info(f"Bus {self.bus.id}: Horaire mis à jour - Départ: {departure_time}, Arrivée: {arrival_time}")

        #Todo: DONE

    
    def _handle_stop_status_update(self, message: Message) -> None:
        """
        Traite une mise à jour du statut d'un arrêt.
        
        Cette fonction doit:
        - Vérifier si l'arrêt concerné est pertinent pour ce bus
        - Mettre à jour les informations locales sur l'arrêt
        - Adapter le comportement du bus en fonction de l'état de l'arrêt
        (ex: file d'attente, occupation, passagers en attente)
        """
        #Todo:
        stop_id = message.data.get('stop_id')
        waiting_passengers = message.data.get('waiting_passengers', 0)
        is_occupied = message.data.get('is_occupied', False)
        
        if not stop_id or not hasattr(self.bus, 'current_stop'):
            return
        

        #ici changé pour stop et pas bus
        if self.bus.current_stop.stop_id == stop_id:
            self.bus.current_stop.update_status(waiting_passengers, is_occupied)
        
        
    
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

        #Todo:
        passenger_id = message.data.get('passenger_id')
        stop_id = message.data.get('stop_id')
        
       
        if self.bus.current_stop.stop_id != stop_id:
            logging.warning(f"Arrêt {self.bus.current_stop.stop_id}: N'est pas concerné par ce message: {message.data}")
            return
        
        # Vérifier si le passager est dans la liste des passagers en attente de l'arrêt
        passenger = next((p for p in self.bus.current_stop.waiting_passengers if p.id == passenger_id), None)
        if passenger is None:
            logging.warning(f"Passager {passenger_id} non trouvé dans la liste d'attente de l'arrêt {stop_id}.")
            return
        
        logging.info(f"Passager {passenger.name} ({passenger_id}) descendu à l'arrêt {stop_id}")
        
        # Ajouter le passager à la liste des passagers de l'arrêt
        self.bus.current_stop.passenger_list.append(passenger)
        self.bus.current_stop.waiting_passengers.remove(passenger)
        passenger.current_stop = self.bus.current_stop
        
        logging.info(f"Passager {passenger.name} ajouté à l'arrêt {self.bus.current_stop.name}")

    


      
    
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
        #Todo:

        bus_id = message.data.get("bus_id")
        stop_id = message.data.get("stop_id")
        available_seats = message.data.get("capacity")
        
        if bus_id != self.bus.id or available_seats is None or self.stop.stop_id != stop_id:
            return
        
        self.bus.capacity = available_seats
        logging.info(f"Bus {self.bus.id}: Capacité mise à jour {available_seats}")
        
        # Vérifier si l'arrêt actuel a des passagers en attente
        if hasattr(self.bus, 'current_stop') and hasattr(self.bus.current_stop, 'waiting_passengers'):
            stop = self.bus.current_stop
            waiting_passengers = stop.waiting_passengers
            
            if waiting_passengers:
                logging.info(f"Bus {self.bus.id}: {len(waiting_passengers)} passagers en attente à l'arrêt {stop.stop_id}")
                
                # Trier les passagers en attente selon un critère (ex: priorité, temps d'attente, etc.)
                sorted_passengers = sorted(waiting_passengers, key=lambda p: p.trip_start_time or 0)
                
                for passenger in sorted_passengers[:available_seats]:
                    if self.bus.add_passenger(passenger):
                        stop.waiting_passengers.remove(passenger)
                        logging.info(f"Passager {passenger.name} embarqué dans le bus {self.bus.id}")
        
        logging.info(f"Bus {self.bus.id}: Mise à jour de capacité traitée")
            
        
        
    
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