import threading
import logging

class ConditionSyncManager:
    def __init__(self, seed, monitor, perf_monitor):
        """
        Initialise le gestionnaire de synchronisation basé sur les variables de condition.

        Args:
            seed: Instance de STSSeed contenant les ressources.
            monitor: Moniteur de synchronisation (non utilisé dans cette version).
            perf_monitor: Moniteur de performance (non utilisé dans cette version).
        """
        self.seed = seed
        self.monitor = monitor
        self.perf_monitor = perf_monitor

        # 1.1 Variables de condition
        self.stop_conditions = {}  # 1.1.1 Conditions pour les arrêts
        self.bus_conditions = {}  # 1.1.2 Conditions pour les bus
        self.transfer_condition = threading.Condition()  # 1.1.3 Condition globale pour les transferts

        # 1.2 États partagés à protéger
        self.bus_at_stop = {}  # 1.2.1 Stocke les bus présents à chaque arrêt
        self.boarding_complete = {}  # 1.2.2 État d'embarquement de chaque bus
        self.alighting_complete = {}  # 1.2.3 État de débarquement de chaque bus
        self.transfers_in_progress = {}  # 1.2.4 Suivi des transferts en cours

        # Initialisation des verrous et variables de condition
        self._initialize_conditions()

    def _initialize_conditions(self):
        """
        Initialise les variables de condition et les verrous pour chaque arrêt et bus.
        """
        logging.info("🔧 Initialisation des variables de condition.")

        try:
            # Création des variables de condition pour les arrêts
            for stop_id in self.seed.stops.keys():
                self.stop_conditions[stop_id] = threading.Condition()

            # Création des variables de condition pour les bus
            for bus_id in self.seed.buses.keys():
                self.bus_conditions[bus_id] = threading.Condition()
                self.boarding_complete[bus_id] = False
                self.alighting_complete[bus_id] = False

            logging.info(" Variables de condition initialisées.")
        except Exception as e:
            logging.error(f" Erreur lors de l'initialisation des conditions : {e}")
            raise RuntimeError("Échec de l'initialisation de ConditionSyncManager") from e
        

    def initialize(self) -> bool:
        """
        Initialise les variables de condition et les états partagés.

        Returns:
            bool: True si l'initialisation a réussi, False sinon.
        """
        logging.info("Initialisation des variables de condition et des états partagés.")
        try:
            # Initialisation des conditions pour les arrêts
            self.stop_conditions = {}
            for stop_id in self.seed.stops.keys():
                self.stop_conditions[stop_id] = threading.Condition()
                logging.info(f"Condition créée pour l'arrêt {stop_id}.")

            # Initialisation des conditions pour les bus
            self.bus_conditions = {}
            self.boarding_complete = {}
            self.alighting_complete = {}
            for bus_id in self.seed.buses.keys():
                self.bus_conditions[bus_id] = threading.Condition()
                self.boarding_complete[bus_id] = False
                self.alighting_complete[bus_id] = False
                logging.info(f"Condition et états d'embarquement/débarquement initialisés pour le bus {bus_id}.")

            # Initialisation de la condition globale pour les correspondances
            self.transfer_condition = threading.Condition()
            self.transfers_in_progress = {}
            logging.info("Condition globale pour les correspondances initialisée.")

            logging.info("Initialisation des variables de condition terminée avec succès.")
            return True

        except Exception as e:
            logging.error(f"Erreur lors de l'initialisation des conditions: {e}")
            return False


    def wait_for_bus(self, passenger_id, stop_id, target_bus_id=None, timeout=30.0) -> int:
        """
        Un passager attend qu'un bus spécifique (ou n'importe quel bus) arrive à un arrêt.

        Args:
            passenger_id (int): Identifiant du passager.
            stop_id (int): Identifiant de l'arrêt.
            target_bus_id (int, optional): Identifiant du bus spécifique attendu (None pour n'importe quel bus).
            timeout (float): Délai d'attente maximum en secondes.

        Returns:
            int: L'identifiant du bus arrivé, ou -1 si timeout.
        """
        if stop_id not in self.stop_conditions:
            logging.warning(f"Arrêt {stop_id} introuvable.")
            return -1

        condition = self.stop_conditions[stop_id]

        with condition:
            start_time = time.time()
            while time.time() - start_time < timeout:
                # Vérifier si un bus attendu est à l'arrêt
                available_buses = self.bus_at_stop.get(stop_id, [])
                
                if target_bus_id is None:  # N'importe quel bus
                    if available_buses:
                        return available_buses[0]  # Retourne le premier bus disponible
                elif target_bus_id in available_buses:
                    return target_bus_id  # Retourne le bus spécifique si présent
                
                # Attente sur la condition de l'arrêt
                condition.wait(timeout=timeout - (time.time() - start_time))

            logging.warning(f"Passager {passenger_id} a attendu trop longtemps à l'arrêt {stop_id}.")
            return -1  # Timeout

    def notify_bus_arrival(self, bus_id, stop_id) -> bool:
        """
        Notifie tous les passagers en attente qu'un bus est arrivé à un arrêt.

        Args:
            bus_id (int): Identifiant du bus.
            stop_id (int): Identifiant de l'arrêt.

        Returns:
            bool: True si la notification a réussi, False sinon.
        """
        if stop_id not in self.stop_conditions:
            logging.warning(f"Arrêt {stop_id} introuvable.")
            return False

        with self.stop_conditions[stop_id]:
            # Ajouter le bus à la liste des bus présents à l'arrêt
            if stop_id not in self.bus_at_stop:
                self.bus_at_stop[stop_id] = []
            self.bus_at_stop[stop_id].append(bus_id)

            logging.info(f"Bus {bus_id} a été notifié à l'arrêt {stop_id}.")
            self.stop_conditions[stop_id].notify_all()  # Réveille tous les passagers en attente
            return True

    def notify_bus_departure(self, bus_id, stop_id) -> bool:
        """
        Notifie que le bus quitte l'arrêt et met à jour l'état.

        Args:
            bus_id (int): Identifiant du bus.
            stop_id (int): Identifiant de l'arrêt.

        Returns:
            bool: True si la notification a réussi, False sinon.
        """
        if stop_id not in self.stop_conditions:
            logging.warning(f"Arrêt {stop_id} introuvable.")
            return False

        with self.stop_conditions[stop_id]:
            if stop_id in self.bus_at_stop and bus_id in self.bus_at_stop[stop_id]:
                self.bus_at_stop[stop_id].remove(bus_id)
                logging.info(f"Bus {bus_id} a quitté l'arrêt {stop_id}.")

            self.stop_conditions[stop_id].notify_all()  # Réveille tous les passagers en attente
            return True
        


    def start_boarding(self, bus_id, stop_id) -> bool:
        """
        Commence l'opération d'embarquement des passagers dans un bus.

        Args:
            bus_id (int): Identifiant du bus.
            stop_id (int): Identifiant de l'arrêt.

        Returns:
            bool: True si l'opération a commencé avec succès, False sinon.
        """
        if bus_id not in self.bus_conditions or stop_id not in self.stop_conditions:
            logging.warning(f"Bus {bus_id} ou arrêt {stop_id} introuvable.")
            return False

        with self.bus_conditions[bus_id]:
            self.boarding_complete[bus_id] = False
            logging.info(f"Bus {bus_id} commence l'embarquement à l'arrêt {stop_id}.")
            self.bus_conditions[bus_id].notify_all()  # Réveille les passagers pour qu'ils montent
        return True


    def complete_boarding(self, bus_id) -> bool:
        """
        Marque l'opération d'embarquement comme terminée et notifie le bus.

        Args:
            bus_id (int): Identifiant du bus.

        Returns:
            bool: True si la notification a réussi, False sinon.
        """
        if bus_id not in self.bus_conditions:
            logging.warning(f"Bus {bus_id} introuvable.")
            return False

        with self.bus_conditions[bus_id]:
            self.boarding_complete[bus_id] = True
            logging.info(f"Bus {bus_id} a terminé l'embarquement.")
            self.bus_conditions[bus_id].notify_all()  # Réveille le bus qui attend la fin de l'embarquement
        return True
    

    def wait_for_boarding_completion(self, bus_id, timeout=10.0) -> bool:
        """
        Le bus attend que l'embarquement des passagers soit terminé.

        Args:
            bus_id (int): Identifiant du bus.
            timeout (float): Délai d'attente maximum en secondes.

        Returns:
            bool: True si l'embarquement est terminé, False si timeout.
        """
        if bus_id not in self.bus_conditions:
            logging.warning(f"Bus {bus_id} introuvable.")
            return False

        with self.bus_conditions[bus_id]:
            start_time = time.time()
            while not self.boarding_complete[bus_id]:
                remaining_time = timeout - (time.time() - start_time)
                if remaining_time <= 0:
                    logging.warning(f"Timeout : Bus {bus_id} n'a pas pu terminer l'embarquement.")
                    return False
                self.bus_conditions[bus_id].wait(timeout=remaining_time)

        logging.info(f"Bus {bus_id} a confirmé la fin de l'embarquement.")
        return True


    def start_alighting(self, bus_id, stop_id) -> bool:
        """
        Commence l'opération de débarquement des passagers d'un bus.

        Args:
            bus_id (int): Identifiant du bus.
            stop_id (int): Identifiant de l'arrêt.

        Returns:
            bool: True si l'opération a commencé avec succès, False sinon.
        """
        if bus_id not in self.bus_conditions or stop_id not in self.stop_conditions:
            logging.warning(f"Bus {bus_id} ou arrêt {stop_id} introuvable.")
            return False

        with self.bus_conditions[bus_id]:
            self.alighting_complete[bus_id] = False
            logging.info(f"Bus {bus_id} commence le débarquement à l'arrêt {stop_id}.")
            self.bus_conditions[bus_id].notify_all()  # Réveille les passagers pour qu'ils descendent
        return True


    def complete_alighting(self, bus_id) -> bool:
        """
        Marque l'opération de débarquement comme terminée et notifie le bus.

        Args:
            bus_id (int): Identifiant du bus.

        Returns:
            bool: True si la notification a réussi, False sinon.
        """
        if bus_id not in self.bus_conditions:
            logging.warning(f"Bus {bus_id} introuvable.")
            return False

        with self.bus_conditions[bus_id]:
            self.alighting_complete[bus_id] = True
            logging.info(f"Bus {bus_id} a terminé le débarquement.")
            self.bus_conditions[bus_id].notify_all()  # Réveille le bus qui attend la fin du débarquement
        return True


    def wait_for_alighting_completion(self, bus_id, timeout=10.0) -> bool:
        """
        Le bus attend que le débarquement des passagers soit terminé.

        Args:
            bus_id (int): Identifiant du bus.
            timeout (float): Délai d'attente maximum en secondes.

        Returns:
            bool: True si le débarquement est terminé, False si timeout.
        """
        if bus_id not in self.bus_conditions:
            logging.warning(f"Bus {bus_id} introuvable.")
            return False

        with self.bus_conditions[bus_id]:
            start_time = time.time()
            while not self.alighting_complete[bus_id]:
                remaining_time = timeout - (time.time() - start_time)
                if remaining_time <= 0:
                    logging.warning(f"Timeout : Bus {bus_id} n'a pas pu terminer le débarquement.")
                    return False
                self.bus_conditions[bus_id].wait(timeout=remaining_time)

        logging.info(f"Bus {bus_id} a confirmé la fin du débarquement.")
        return True
    

    
    def start_transfer(self, passenger_id, from_bus_id, to_bus_id) -> bool:
        """
        Commence un transfert de passager entre deux bus.

        Args:
            passenger_id (int): Identifiant du passager.
            from_bus_id (int): Bus de départ.
            to_bus_id (int): Bus d'arrivée.

        Returns:
            bool: True si le transfert a commencé avec succès, False sinon.
        """
        if from_bus_id not in self.bus_conditions or to_bus_id not in self.bus_conditions:
            logging.warning(f"Bus {from_bus_id} ou {to_bus_id} introuvable.")
            return False

        with self.transfer_condition:
            self.transfers_in_progress[(passenger_id, from_bus_id, to_bus_id)] = False
            logging.info(f"Passager {passenger_id} commence son transfert de {from_bus_id} à {to_bus_id}.")
            self.transfer_condition.notify_all()  # Notifie les bus concernés qu'un transfert a commencé
        return True


    def complete_transfer(self, passenger_id, from_bus_id, to_bus_id) -> bool:
        """
        Termine un transfert de passager et notifie les bus concernés.

        Args:
            passenger_id (int): Identifiant du passager.
            from_bus_id (int): Bus de départ.
            to_bus_id (int): Bus d'arrivée.

        Returns:
            bool: True si le transfert a été terminé avec succès, False sinon.
        """
        if (passenger_id, from_bus_id, to_bus_id) not in self.transfers_in_progress:
            logging.warning(f"Transfert inexistant pour passager {passenger_id} entre {from_bus_id} et {to_bus_id}.")
            return False

        with self.transfer_condition:
            self.transfers_in_progress[(passenger_id, from_bus_id, to_bus_id)] = True
            logging.info(f"Passager {passenger_id} a terminé son transfert de {from_bus_id} à {to_bus_id}.")
            self.transfer_condition.notify_all()  # Notifie les bus en attente de ce transfert
        return True
    
    def wait_for_transfer_completion(self, bus_id, timeout=15.0) -> bool:
        """
        Un bus attend que tous les transferts le concernant soient terminés.

        Args:
            bus_id (int): Identifiant du bus.
            timeout (float): Délai d'attente maximum en secondes.

        Returns:
            bool: True si tous les transferts sont terminés, False si timeout.
        """
        if bus_id not in self.bus_conditions:
            logging.warning(f"Bus {bus_id} introuvable.")
            return False

        with self.transfer_condition:
            start_time = time.time()
            while any(not completed for (passenger, from_bus, to_bus), completed in self.transfers_in_progress.items() 
                    if from_bus == bus_id or to_bus == bus_id):
                remaining_time = timeout - (time.time() - start_time)
                if remaining_time <= 0:
                    logging.warning(f"Timeout : Bus {bus_id} n'a pas pu terminer tous les transferts.")
                    return False
                self.transfer_condition.wait(timeout=remaining_time)

        logging.info(f"Bus {bus_id} a confirmé la fin de tous les transferts.")
        return True

    def run_scenarios(self, duration):
        """
        Exécute les scénarios de test.

        Args:
            duration (int): Durée d'exécution des scénarios en secondes.
        """
        logging.info("Démarrage des scénarios de test.")

        # Création de l'événement d'arrêt
        self.stop_event = threading.Event()

        # Liste des threads
        threads = []

        # 1. Création des threads pour les bus
        for bus_id in self.seed.buses.keys():
            thread = threading.Thread(target=self.simulate_bus, args=(bus_id,))
            threads.append(thread)

        # 2. Création des threads pour les passagers
        for passenger_id in self.seed.passengers.keys():
            thread = threading.Thread(target=self.simulate_passenger, args=(passenger_id,))
            threads.append(thread)

        # 3. Démarrage des threads
        for thread in threads:
            thread.start()

        # 4. Attente de la durée de la simulation
        start_time = time.time()
        while time.time() - start_time < duration:
            time.sleep(1)  # Pause pour éviter de monopoliser le CPU

        # 5. Arrêt des threads
        self.stop_event.set()

        # 6. Attente que tous les threads terminent leur exécution
        for thread in threads:
            thread.join()

        logging.info(" Simulation terminée.")


    def cleanup(self):
        """
        Nettoie les ressources utilisées par ConditionSyncManager.

        Returns:
            bool: True si le nettoyage réussit, False sinon.
        """
        try:
            logging.info("🧹 Nettoyage des ressources.")
            self.bus_conditions.clear()
            self.stop_conditions.clear()
            self.transfer_condition = None
            self.bus_at_stop.clear()
            self.boarding_complete.clear()
            self.alighting_complete.clear()
            self.transfers_in_progress.clear()
            logging.info(" Nettoyage terminé.")
            return True
        except Exception as e:
            logging.error(f" Erreur lors du nettoyage : {e}")
            return False
