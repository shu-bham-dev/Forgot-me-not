from machine import Pin, Timer
import network
import time
from umqtt.robust import MQTTClient
import sys
import usocket as socket        #importing socket
import esp                 #importing ESP
import gc

esp.osdebug(None)
gc.collect()

ssid = 'ShubhamPagal'                  #Set access point name 
password = '12345678'      #Set your access point password

led=Pin(2,Pin.OUT)                          # Onboard LED on Pin 2 of ESP32

temp = 0

WIFI_SSID     = 'sonal'
WIFI_PASSWORD = 'shubham1'

mqtt_client_id      = bytes('client_'+'12321', 'utf-8') # Just a random client ID

ADAFRUIT_IO_URL     = 'io.adafruit.com' 
ADAFRUIT_USERNAME   = 'onalsingh'
ADAFRUIT_IO_KEY     = 'aio_mxlV49DeYDRqMME7TI6rfLogApOh'

TOGGLE_FEED_ID      = 'led'
RANGE_FEED_ID_1      = 'wifi-range'
RANGE_FEED_ID_2      = 'wifi-range-1'


def access_point():
  
                ap = network.WLAN(network.AP_IF)
                ap.active(True)            # activating
                ap.config(essid=ssid, password=password)


                while ap.active() == False:
                  pass
                print('Connection is successful')
                print(ap.ifconfig())
                def web_page():
                  if led.value() == 1:
                    gpio_state="ON"
                  else:
                    gpio_state="OFF"
                  
                  html = """<html> <head> <title>ESP Web Server</title> <meta name="viewport" content="width=device-width, initial-scale=1"> <link rel="icon" href="data:,"> <style> body { background: #efefef; } button { padding: 1.5em 5em; background: #efefef; border: none; border-radius: .5rem; color: #444; font-size: 1rem; font-weight: 700; letter-spacing: .2rem; text-align: center; outline: none; cursor: pointer; transition: .2s ease-in-out; box-shadow: -6px -6px 14px rgba(255, 255, 255, .7), -6px -6px 10px rgba(255, 255, 255, .5), 6px 6px 8px rgba(255, 255, 255, .075), 6px 6px 10px rgba(0, 0, 0, .15); } button:hover { box-shadow: -2px -2px 6px rgba(255, 255, 255, .6), -2px -2px 4px rgba(255, 255, 255, .4), 2px 2px 2px rgba(255, 255, 255, .05), 2px 2px 4px rgba(0, 0, 0, .1); } button:active { box-shadow: inset -2px -2px 6px rgba(255, 255, 255, .7), inset -2px -2px 4px rgba(255, 255, 255, .5), inset 2px 2px 2px rgba(255, 255, 255, .075), inset 2px 2px 4px rgba(0, 0, 0, .15); } html { font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center; } h1 { color: #0F3376; padding: 2vh; } p { font-size: 1.5rem; } .mystyle{ background-color: darkgreen; } .origin{ background: #efefef; } .head1{ border: 1px solid black; } #alert{ color: red; } header{ font-size: 25px; } </style> </head> <body id="myBody"> <header>Forgot Me Not ! </header> <h1 class="head1" id="headtop">ESP Web Server</h1> <p>GPIO state: <div id="alert">""" + gpio_state + """</div></p> <p> <a href="/?led=on"> <button id="btnClass" onclick="change(1)" class="button">ON</button> </a> </p> <p> <a href="/?led=off"> <button id="btnClass" onclick="change(0)" class="button">OFF</button> </a> </p> </body> <script> var bg = document.getElementById("myBody"); var btn = document.getElementById("btnClass"); var headimp = document.getElementById("headtop"); function change(x) { if(x){ bg.style.backgroundColor = "Green"; headimp.style.color = "black"; }else{ bg.style.backgroundColor = "#efefef"; headimp.style.color = "#0F3376";

 } } </script> </html>"""
                  return html
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #creating socket object
                s.bind(('', 80))
                s.listen(5)
                while True:
                      conn, addr = s.accept()
                      print('Got a connection from %s' % str(addr))
                      request = conn.recv(1024)
                      request = str(request)
                      print('Content = %s' % request)
                      led_on = request.find('/?led=on')
                      led_off = request.find('/?led=off')
                      if led_on == 6:
                        print('LED ON')
                        led.value(1)
                      if led_off == 6:
                        print('LED OFF')
                        led.value(0)
                      response = web_page()
                      conn.send('HTTP/1.1 200 OK\n')
                      conn.send('Content-Type: text/html\n')
                      conn.send('Connection: close\n\n')
                      conn.sendall(response)
                      conn.close()
                          
       
def connect_wifi():

        global wifi
        wifi = network.WLAN(network.STA_IF)
        wifi.active(True)
        wifi.disconnect()
        wifi.connect(WIFI_SSID,WIFI_PASSWORD)
        if not wifi.isconnected():
            print('connecting..')
            timeout = 0
            while (not wifi.isconnected() and timeout < 10):
                print(10 - timeout)
                timeout = timeout + 1
                time.sleep(1) 
        if(wifi.isconnected()):
            print('connected')
        else:
            access_point()


        
      

connect_wifi() # Connecting to WiFi Router



client = MQTTClient(client_id=mqtt_client_id, 
                        server=ADAFRUIT_IO_URL, 
                        user=ADAFRUIT_USERNAME, 
                        password=ADAFRUIT_IO_KEY,
                        ssl=False)
try:            
    client.connect()
except Exception as e:
        print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
        sys.exit()



range_feed_1 = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME,RANGE_FEED_ID_1), 'utf-8') # format - onalsingh/feeds/range   
toggle_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, TOGGLE_FEED_ID), 'utf-8') # format - onalsingh/feeds/led
range_feed_2 = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME,RANGE_FEED_ID_2), 'utf-8') # format - onalsingh/feeds/range-1


def cb(topic, msg):                             # Callback function
        print('Received Data:  Topic = {}, Msg = {}'.format(topic, msg))
        recieved_data = str(msg,'utf-8')            #   Recieving Data
        if recieved_data=="0":
            led.value(0)
        if recieved_data=="1":
            led.value(1)
            
            
client.set_callback(cb)      # Callback function               
client.subscribe(toggle_feed) # Subscribing to particular topic   

            

def sens_data(data):
         
         if (wifi.isconnected()):
             
             networks = wifi.scan() # Scan the available wifi networks
             print(networks)
             print(len(networks))
                 
             for i in range(len(networks)):
                 
                 if networks[i][0] == b'sonal': # if sonal is not present then in access point
                     
                     wifi_range_1 = 100 + int(networks[i][3])
 
             
                     client.publish(range_feed_1,    
                                   bytes(str(wifi_range_1), 'utf-8'),   # Publishing the range of room1 to adafruit.io
                                   qos=0)
                     print("range1 - " , str(wifi_range_1))
                     
                     
                 if networks[i][0] == b'Rashi':
                     
                     wifi_range_2 = 100 + int(networks[i][3])
 
             
                     client.publish(range_feed_2,    
                                   bytes(str(wifi_range_2), 'utf-8'),   # Publishing the range of room2 to adafruit.io
                                   qos=0)
                     print("range2 - " , str(wifi_range_2))
        
         else:
             access_point()
 
 
 
 
timer = Timer(0)
timer.init(period=5000, mode=Timer.PERIODIC, callback = sens_data)
        

while True:
    try:
        client.check_msg()                  # non blocking function
    except :
        client.disconnect()
        sys.exit()
