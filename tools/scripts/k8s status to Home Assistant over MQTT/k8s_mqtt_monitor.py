import time
import json
import paho.mqtt.client as mqtt
from kubernetes import client, config

MQTT_BROKER = "localhost" ## Your MQTT Broker ##
MQTT_PORT = 31883         ## Your MQTT Port   ##
MQTT_PREFIX = "homeassistant/sensor/k8s"

# Load kube config
config.load_kube_config()
v1 = client.CoreV1Api()

mqttc = mqtt.Client()
mqttc.connect(MQTT_BROKER, MQTT_PORT, 60)

def publish_sensor_discovery(pod_name, namespace):
    uid = f"k8s_{namespace}_{pod_name}"
    topic = f"{MQTT_PREFIX}/{uid}/config"
    payload = {
        "name": f"K8s {pod_name} Status",
        "state_topic": f"{MQTT_PREFIX}/{uid}/state",
        "unique_id": uid,
        "device_class": "connectivity"
    }
    mqttc.publish(topic, json.dumps(payload), retain=True)

def publish_pod_status(pod):
    pod_name = pod.metadata.name
    namespace = pod.metadata.namespace
    phase = pod.status.phase
    uid = f"k8s_{namespace}_{pod_name}"
    state_topic = f"{MQTT_PREFIX}/{uid}/state"
    mqttc.publish(state_topic, phase, retain=True)

while True:
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for pod in ret.items:
        publish_sensor_discovery(pod.metadata.name, pod.metadata.namespace)
        publish_pod_status(pod)
    mqttc.loop()
    time.sleep(30)