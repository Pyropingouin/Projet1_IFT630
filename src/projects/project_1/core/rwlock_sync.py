"""
Implémentation de la synchronisation par Read-Write Locks.

Gère:
- Consultation des horaires (lecture multiple simultanée)
- Accès aux informations des trajets (lecture/écriture)

Utilise des RW Locks pour:
- Permettre plusieurs lectures simultanées
- Garantir l'exclusivité des écritures
- Optimiser l'accès concurrent aux données
"""
