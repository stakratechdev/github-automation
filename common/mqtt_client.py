"""
MQTT Client for Event Publishing/Subscription.
Lightweight event system for agent communication.
"""

import logging
import json
import threading
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass

import paho.mqtt.client as mqtt

from .config_loader import MQTTConfig, get_config
from .event_types import AgentEvent, EventPublisher

logger = logging.getLogger(__name__)


@dataclass
class MQTTClient(EventPublisher):
    """
    MQTT client for publishing and subscribing to agent events.
    
    Attributes:
        config: MQTT configuration
        client: Paho MQTT client instance
        connected: Connection status
        subscriptions: Registered callbacks
    """
    config: MQTTConfig = None
    client: mqtt.Client = None
    connected: bool = False
    subscriptions: Dict[str, Callable] = None
    _lock: threading.Lock = None
    
    def __init__(self, config: Optional[MQTTConfig] = None):
        """Initialize MQTT client."""
        self.config = config or get_config().mqtt
        self.subscriptions = {}
        self._lock = threading.Lock()
        
        # Create client with unique ID
        client_id = f"{self.config.client_id_prefix}-{id(self)}"
        self.client = mqtt.Client(client_id=client_id)
        
        # Set up authentication if provided
        if self.config.username and self.config.password:
            self.client.username_pw_set(
                self.config.username,
                self.config.password
            )
        
        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
    
    def connect(self, broker: Optional[str] = None) -> bool:
        """
        Connect to MQTT broker.
        
        Args:
            broker: Broker URL (overrides config)
            
        Returns:
            True if connected successfully
        """
        try:
            broker_url = broker or self.config.broker
            
            # Parse broker URL
            protocol = "tcp"
            if broker_url.startswith("mqtts://"):
                protocol = "ssl"
                broker_url = broker_url[8:]
            elif broker_url.startswith("mqtt://"):
                broker_url = broker_url[7:]
            
            host, port_str = broker_url.split(":")
            port = int(port_str)
            
            logger.info(f"Connecting to MQTT broker {host}:{port}")
            self.client.connect(host, port, 60)
            self.client.loop_start()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            logger.info("Disconnected from MQTT broker")
        except Exception as e:
            logger.error(f"Error disconnecting from MQTT broker: {e}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for connection established."""
        if rc == 0:
            self.connected = True
            logger.info("Connected to MQTT broker")
            
            # Re-subscribe to all topics
            for topic in self.subscriptions:
                self.client.subscribe(topic)
        else:
            logger.error(f"Failed to connect to MQTT broker, code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for disconnection."""
        self.connected = False
        logger.warning(f"Disconnected from MQTT broker, code: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Callback for incoming messages."""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            if topic in self.subscriptions:
                try:
                    event = AgentEvent.from_json(payload)
                    self.subscriptions[topic](event)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling incoming message: {e}")
    
    def publish(self, event: AgentEvent) -> bool:
        """
        Publish an event to the events topic.
        
        Args:
            event: AgentEvent to publish
            
        Returns:
            True if published successfully
        """
        try:
            if not self.connected:
                logger.warning("Not connected to MQTT broker")
                return False
            
            topic = self.config.topics.get("events", "github/automation/events")
            payload = event.to_json()
            
            result = self.client.publish(topic, payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published event to {topic}: {event.event_type.value}")
                return True
            else:
                logger.error(f"Failed to publish event: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return False
    
    def publish_to_topic(self, topic: str, event: AgentEvent) -> bool:
        """
        Publish an event to a specific topic.
        
        Args:
            topic: Target topic
            event: AgentEvent to publish
            
        Returns:
            True if published successfully
        """
        try:
            if not self.connected:
                logger.warning("Not connected to MQTT broker")
                return False
            
            payload = event.to_json()
            result = self.client.publish(topic, payload, qos=1)
            
            return result.rc == mqtt.MQTT_ERR_SUCCESS
            
        except Exception as e:
            logger.error(f"Error publishing to topic: {e}")
            return False
    
    def subscribe(self, callback: Callable[[AgentEvent], None]) -> None:
        """
        Subscribe to all events.
        
        Args:
            callback: Function to call when event is received
        """
        topic = self.config.topics.get("events", "github/automation/events")
        self._subscribe_to_topic(topic, callback)
    
    def subscribe_to_topic(
        self,
        topic: str,
        callback: Callable[[AgentEvent], None]
    ) -> None:
        """
        Subscribe to a specific topic.
        
        Args:
            topic: Topic to subscribe to
            callback: Function to call when event is received
        """
        self._subscribe_to_topic(topic, callback)
    
    def _subscribe_to_topic(
        self,
        topic: str,
        callback: Callable[[AgentEvent], None]
    ) -> None:
        """Internal subscribe method with thread safety."""
        with self._lock:
            self.subscriptions[topic] = callback
            
            if self.connected:
                self.client.subscribe(topic)
                logger.info(f"Subscribed to topic: {topic}")
    
    def unsubscribe(self, topic: str) -> None:
        """
        Unsubscribe from a topic.
        
        Args:
            topic: Topic to unsubscribe from
        """
        with self._lock:
            if topic in self.subscriptions:
                del self.subscriptions[topic]
                
            if self.connected:
                self.client.unsubscribe(topic)
                logger.info(f"Unsubscribed from topic: {topic}")


def get_mqtt_client() -> MQTTClient:
    """Factory function to get a configured MQTT client."""
    return MQTTClient()
