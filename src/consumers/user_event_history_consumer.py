"""
Kafka Historical User Event Consumer (Event Sourcing)
SPDX-License-Identifier: LGPL-3.0-or-later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

import json
import os
from pathlib import Path
import config
from logger import Logger
from typing import Optional
from kafka import KafkaConsumer
from handlers.handler_registry import HandlerRegistry

class UserEventHistoryConsumer:
    """A consumer that starts reading Kafka events from the earliest point from a given topic"""
    
    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        group_id: str,
        registry: HandlerRegistry
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.registry = registry
        self.auto_offset_reset = "earliest"
        self.consumer: Optional[KafkaConsumer] = None
        self.logger = Logger.get_instance("UserEventHistoryConsumer")
        self.events = []
    
    def start(self) -> None:
        """Start consuming messages from Kafka"""
        self.logger.info(f"Démarrer un consommateur : {self.group_id}")
        
        try:
            # TODO: implémentation basée sur UserEventConsumer
            # TODO: enregistrez les événements dans un fichier JSON
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset=self.auto_offset_reset,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),  
                enable_auto_commit=True
            )
            for message in self.consumer:
                self._process_message(message.value)         
        except Exception as e:
            self.logger.error(f"Erreur: {e}", exc_info=True)
        finally:
            self.stop()

    def _process_message(self, event_data: dict) -> None:
        """Process a single message"""
        event_type = event_data.get('event')
        if not event_type:
            self.logger.warning(f"Message missing 'event' field: {event_data}")
            return

        self.logger.info(f"Processing event: {event_type} -> {event_data}")
        
        self.events.append(event_data)

        try:
            filename = os.path.join(config.OUTPUT_DIR, "user_event_history.json")
            with open(filename, "a", encoding="utf-8") as f:
                json.dump(event_data, f)
                f.write("\n")
            self.logger.info("Event appended to user_event_history.json")
        except Exception as e:
            self.logger.error(f"Failed to append event to JSON file: {e}", exc_info=True)

    def stop(self) -> None:
        """Stop the consumer gracefully"""
        if self.consumer:
            self.consumer.close()
            self.logger.info("Arrêter le consommateur!")

        try:
            filename = os.path.join(config.OUTPUT_DIR, "user_event_history.json")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.events, f)
            self.logger.info("Events successfully written to user_event_history.json")
        except Exception as e:
            self.logger.error(f"Failed to write JSON file: {e}", exc_info=True)

        self.logger.info("Consumer stopped.")
