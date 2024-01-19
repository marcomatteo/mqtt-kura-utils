import argparse
import time
import paho.mqtt.client as mqtt
import logging
from logging.handlers import RotatingFileHandler
import configparser
import kurapayload_pb2

def init_log(path=None):
    """
    Creates a rotating log
    """
    logger = logging.getLogger("Log")
    logger.setLevel(logging.INFO)

    if path is None:
        handler = logging.StreamHandler()
    else:
        handler = RotatingFileHandler(path, maxBytes=10000000, backupCount=10)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S %Z")
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

def on_connect(client, userdata, flags, rc):
    logger.info("Connnected with result code " + str(rc))

def on_message(client, userdata, msg):
    logger.info('Message received')
    logger.info(str(msg))

def on_publish(client,userdata,result):
    logger.info("Message published")

def on_subscribe(client,userdata,mid,granted_qos):
    logger.info('Subscribed')

def parse_args(parser):
    parser.add_argument('--metric', default="value", help='kura metric')
    parser.add_argument('--msg', default="This is a message", help='kura message to pubish')
    parser.add_argument('--num', type=int, default=10, help='number of messages')

    args = parser.parse_args()
    return args

def build_msg(name, msg, with_body=False):
    message = kurapayload_pb2.KuraPayload()

    metric = kurapayload_pb2.KuraPayload().KuraMetric()
    metric.name = name
    metric.type = 5
    metric.string_value = msg

    message.metric.extend([metric])
    if with_body:
        message.body = bytes(msg, encoding='utf-8')

    timestamp = int(time.time()) * 1000
    message.timestamp = timestamp

    return message

logger = init_log()

# config properties
config = configparser.ConfigParser()
config.read('config.ini')
 
if __name__=='__main__':
    
    parser = argparse.ArgumentParser()
    args = parse_args(parser)

    # mqtt
    mqtt_url = config.get('MQTTSection', 'mqtt.url')
    mqtt_clientid = config.get('MQTTSection', 'mqtt.clientid')
    mqtt_user = config.get('MQTTSection', 'mqtt.user')
    mqtt_password = config.get('MQTTSection', 'mqtt.password')
    mqtt_topic = config.get('MQTTSection', 'mqtt.topic')
    mqtt_client = mqtt.Client(client_id=mqtt_clientid)

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_publish = on_publish
    mqtt_client.on_subscribe = on_subscribe

    logger.info(f"Setting up mqtt_user: {mqtt_user}, mqtt_password: {mqtt_password}")
    mqtt_client.username_pw_set(username=mqtt_user, password=mqtt_password)
    # mqtt_client.tls_set() # TLS - change mqtt port to 8883

    logger.info("Trying to connect to: " + mqtt_url)

    res = -1
    while res != 0:
        try:
            res = mqtt_client.connect(mqtt_url)
        except:
            logger.error("Failed to connect, check internet connection. Trying to automatically reconnect in 5 seconds.")
            time.sleep(5)
            pass
        
    logger.info('Connected to: ' + mqtt_url)

    msg = args.msg
    metric_name = args.metric
    n = args.num

    for i in range(n):
        message_payload = msg + '-' + str(i)
        message = build_msg(metric_name,message_payload).SerializeToString()
        
        logger.info(f"Trying to publish message to {mqtt_topic} topic:")
        logger.info(f"metric name: {metric_name}")
        logger.info(f"metric value: {message_payload}")
        
        try:
            info = mqtt_client.publish(mqtt_topic, message, qos=0, retain=False)
        except Exception as e:
            logger.exception(f"Failed to publish the message n°{i}!")
    
        time.sleep(1)

