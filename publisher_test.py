import json
import time
import paho.mqtt.client as mqtt

for a in range(5):
    my_dict = {"beats": a, 'two': 2, 'three': 3, 'four': 4}
    dict_str = json.dumps(my_dict)

    client_name = 'client-pub'
    broker = 'mqtt.eclipseprojects.io'

    client = mqtt.Client(client_name)
    print('connecting to broker: ', broker)
    client.connect(broker)

    print('publishing')
    client.publish('studentdata', dict_str)
    time.sleep(4)
    print('Just published'+str(dict_str)+' to topic studentdata')
    client.disconnect()


