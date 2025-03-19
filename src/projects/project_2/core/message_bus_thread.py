"""
Module: message_bus_thread.py
--------------------------
Version adaptée du thread de bus utilisant le système de messagerie.

Étend la fonctionnalité du BusThread standard pour utiliser
le broker de messages pour la communication.

Classes:
    MessageBusThread: Thread de simulation pour un bus avec messagerie

Auteur: [Votre Nom]
"""
from src.core.bus_thread import BusThread
from src.projects.project_2.core.message_broker import MessageBroker, Message, MessageType
from src.projects.project_2.core.message_components import MessageBusAdapter

class MessageBusThread(BusThread):
    """Thread de simulation pour un bus avec communication par messages"""
    
    def __init__(self, bus, stop_event):
        """
        Initialise le thread de bus avec messagerie
        
        Args:
            bus: L'objet Bus à gérer
            stop_event: Événement de signal d'arrêt
        """
        super().__init__(bus, stop_event)
        
        # Adaptateur de messagerie pour ce bus
        self.message_adapter = MessageBusAdapter(bus)
        self.broker = MessageBroker()
        
    def run(self):
        """Boucle principale du thread avec messagerie"""
        if not self._verify_and_fix_bus_initialization():
            self.logger.error(f"Bus {self.component.id}: Impossible de démarrer - initialisation incorrecte")
            return

        # Notification de démarrage via messagerie
        self._publish_status_update("started")

        while not self.stop_event.is_set():
            try:
                if not self.component.current_route:
                    self.logger.error(f"Bus {self.component.id}: Pas de route assignée")
                    break

                if not self.component.current_stop:
                    self.logger.error(f"Bus {self.component.id}: Pas d'arrêt actuel")
                    break

                # Log de l'état actuel
                self.logger.info(
                    f"🚌 Bus {self.component.id} à {self.component.current_stop.name} - "
                    f"Passagers: {len(self.component.passenger_list)}/{self.component.capacity} - "
                    f"Route: {self.component.current_route.id}"
                )

                # Notification de l'arrivée à l'arrêt via messagerie
                self.message_adapter.publish_arrival(self.component.current_stop.stop_id)
                
                # Publier une mise à jour de capacité
                self.message_adapter.publish_capacity_update()

                # Gérer les passagers à l'arrêt actuel
                self._handle_passenger_exchange()
                self.sleep_random(2, 4)

                # Notification du départ via messagerie
                current_stop_id = self.component.current_stop.stop_id
                
                # Tenter de se déplacer vers le prochain arrêt
                if not self._move_to_next_stop():
                    self.logger.warning(
                        f"Bus {self.component.id}: Impossible de se déplacer depuis "
                        f"{self.component.current_stop.name}"
                    )
                else:
                    self.message_adapter.publish_departure(current_stop_id)
                    self.logger.info(
                        f"➡️ Bus {self.component.id} en route vers {self.component.current_stop.name}"
                    )
                self.sleep_random(3, 5)

            except Exception as e:
                self.logger.error(f"Bus {self.component.id}: Erreur - {str(e)}")
                self._publish_status_update("error", {"error": str(e)})
                self.sleep_random(2, 4)
                
        # Notification d'arrêt via messagerie
        self._publish_status_update("stopped")
                
    def _publish_status_update(self, status, details=None):
        """
        Publie une mise à jour de statut du bus
        
        Args:
            status: État du bus (started, running, error, stopped)
            details: Détails additionnels
        """
        message = Message(
            MessageType.SYSTEM_ALERT,
            f"BusThread-{self.component.id}",
            {
                'component_type': 'bus',
                'bus_id': self.component.id,
                'status': status,
                'details': details or {}
            }
        )
        self.broker.publish(message)