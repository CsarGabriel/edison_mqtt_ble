
import subprocess
import signal 
import thread
import time
import mraa
import json
import urllib
import urllib2
import traceback

import paho.mqtt.client as paho

p1 = None
blink_start = False
 
def someFunc():
   
    time.sleep(5)
    print "end sleep"
    if p1:
        try:
            p1.send_signal(signal.SIGINT)
        except:
            print "err"

        #for line in p1.stdout:
            #the real code does filtering here
        #    print "test:", line.rstrip()
	
        #p1.send_signal(signal.SIGINT)

def readDevices():
    response = False
    url = "http://127.0.0.1:8000/api_devices"
    try:
        query = urllib.urlopen(url)
        response = query.read()
    except:
        print "URL no response from server"
        pass

    if response:
        try:
            dev_list = json.loads(response)
            return dev_list
        except:
            print "Error on parse response" + str(response[:130])
            pass
    return False

def appendToDeviceLog(data):
    #print str(data)
    status = False
    url = "http://127.0.0.1:8000/api_log_save/"
    response = False

    try:
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')
        exc_req = urllib2.urlopen(req, json.dumps(data))
        response = exc_req.read()

    except:
        print traceback.format_exc()

    
    if response:
        try:
            status = json.loads(response)
            print "START SAVE LOG TO SERVER -------------------------->"
            print status
            print "END SAVE LOG TO SERVER -------------------------->"
            return status
        except:
            print "Error on parse response" + str(response[:130])

    return False


#-- MQTT ------------------------------------------>
# Define event callbacks
def on_connect(mosq, obj, rc):
    print("MQTT Connected: " + str(rc))

def on_message(mosq, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def on_publish(mosq, obj, mid):
    print("MQTT Publish: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    print("MQTT Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    print("MQTT Log: " + string)
#------------------------------------------------>    

def blink():

    led = mraa.Gpio(13)
    led.dir(mraa.DIR_OUT)

    while True:
	if blink_start:
            led.write(1)
            time.sleep(0.2)
            led.write(0)
            time.sleep(0.2)
        else:
            led.write(0)
            time.sleep(1)


if __name__ == "__main__":
    MQTT_SERVER = "127.0.0.1"
    MQTT_PORT = "1883"

    thread.start_new_thread(blink, ())
    
    mqttc = paho.Client()
    # Assign MQTT event callbacks
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe

    mqttc.connect(MQTT_SERVER, MQTT_PORT)
    print "Configuring MQTT Client"
    time.sleep(4)


    while True:
        devices_list = readDevices()
        if devices_list:
            if "status" in devices_list:
                if devices_list["status"]:
                    if devices_list["num_devices"] >= 1:

                        out = subprocess.check_output(['/home/root/lescan.sh', '2', 'devs.lst'])
                        
                        print out

                        #out, err = p1.communicate()
                        #p1.send_signal(signal.SIGINT)
                        #p1.poll()
                        #p1.terminate()

                        print "OUT -->" + str(out)
                        #print err

                        with open('devs.lst') as f:
                            lines = f.readlines()

                        blink_start = False
                        for l in lines:
                            print l
                            for reg_dev in devices_list["devices"]:
                                print "--> verifing " + str(reg_dev["mac_address"]) + " -- " + str(reg_dev["ble_name"])
                                if reg_dev["mac_address"] in l and reg_dev["ble_name"] in l:
                                    blink_start = True                                    
                                    log_entry = {
                                        "mac_address":reg_dev["mac_address"],
                                        "ble_name":reg_dev["ble_name"],
                                        "event":"Device in range " + str(time.ctime()) 
                                    }
                                    thread.start_new_thread(appendToDeviceLog, (log_entry,))
                                    mqttc.publish("bleManager/events", json.dumps(log_entry))
                                
                                if blink_start:
                                    print "blink"
                                else:
                                    print "not blink"  
                            