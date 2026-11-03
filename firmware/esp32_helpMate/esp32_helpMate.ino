/*
 HelpMate² AgriBrain ESP32 HTTP example.
 Sensors: adapt readSensor*() functions to your actual modules.
 Actuators: adapt setPump() and setValve() to a relay driver.
 IMPORTANT: add physical interlocks, flyback protection, manual override,
 safe boot defaults and TLS before field deployment.
*/
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* WIFI_SSID = "YOUR_WIFI";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* API_BASE = "https://YOUR-BACKEND.onrender.com";
const char* DEVICE_ID = "esp32-01";
const char* DEVICE_KEY = "SET_THE_SAME_DEVICE_INGEST_KEY_AS_BACKEND";
const int PUMP_RELAY_PIN = 26; // verify relay active HIGH/LOW for your board
const int VALVE_RELAY_PIN = 27;

unsigned long lastSend=0, lastPoll=0;
const unsigned long SEND_EVERY_MS=30000, POLL_EVERY_MS=5000;

float readSoilMoisture(){ return NAN; } // replace with calibrated sensor reading, 0-100%
float readTemperature(){ return NAN; }  // replace with temperature sensor
float readPH(){ return NAN; }           // pH requires calibrated probe/interface
float readNitrogen(){ return NAN; }     // NPK sensor protocol-specific
float readPhosphorus(){ return NAN; }
float readPotassium(){ return NAN; }

void setPump(bool on){ digitalWrite(PUMP_RELAY_PIN, on ? HIGH : LOW); }
void setValve(bool open){ digitalWrite(VALVE_RELAY_PIN, open ? HIGH : LOW); }

void connectWiFi(){
  WiFi.mode(WIFI_STA); WiFi.begin(WIFI_SSID,WIFI_PASSWORD);
  while(WiFi.status()!=WL_CONNECTED){delay(500);}
}
bool postReading(){
  if(WiFi.status()!=WL_CONNECTED) return false;
  HTTPClient http; http.begin(String(API_BASE)+"/api/sensors/ingest");
  http.addHeader("Content-Type","application/json"); http.addHeader("X-Device-Key",DEVICE_KEY);
  StaticJsonDocument<512> doc;
  doc["device_id"]=DEVICE_ID;
  // Set farm_id to the integer ID returned by POST /api/farms; omit if unassigned.
  // doc["farm_id"]=1;
  float v=readSoilMoisture(); if(!isnan(v))doc["soil_moisture"]=v;
  v=readTemperature(); if(!isnan(v))doc["temperature"]=v;
  v=readPH(); if(!isnan(v))doc["ph"]=v;
  v=readNitrogen(); if(!isnan(v))doc["nitrogen"]=v;
  v=readPhosphorus(); if(!isnan(v))doc["phosphorus"]=v;
  v=readPotassium(); if(!isnan(v))doc["potassium"]=v;
  String body; serializeJson(doc,body); int code=http.POST(body); http.end();
  return code>=200 && code<300;
}
void executeCommand(const char* command, JsonObject payload){
  if(!strcmp(command,"PUMP_ON")) setPump(true);
  else if(!strcmp(command,"PUMP_OFF")) setPump(false);
  else if(!strcmp(command,"VALVE_OPEN")) setValve(true);
  else if(!strcmp(command,"VALVE_CLOSE")) setValve(false);
  // Add allow-listed command handlers here. Never execute arbitrary code from payload.
}
void pollCommands(){
  if(WiFi.status()!=WL_CONNECTED)return;
  HTTPClient http; String url=String(API_BASE)+"/api/sensors/devices/"+DEVICE_ID+"/commands";
  http.begin(url); http.addHeader("X-Device-Key",DEVICE_KEY);
  int code=http.GET();
  if(code==200){
    DynamicJsonDocument doc(4096); deserializeJson(doc,http.getString());
    for(JsonObject cmd:doc["commands"].as<JsonArray>()){
      int id=cmd["id"]|0; const char* name=cmd["command"]|"";
      JsonObject payload=cmd["payload"].as<JsonObject>(); executeCommand(name,payload);
      HTTPClient ack; ack.begin(String(API_BASE)+"/api/sensors/devices/"+DEVICE_ID+"/commands/"+String(id)+"/ack");
      ack.addHeader("X-Device-Key",DEVICE_KEY); ack.POST(""); ack.end();
    }
  }
  http.end();
}
void setup(){
  pinMode(PUMP_RELAY_PIN,OUTPUT);pinMode(VALVE_RELAY_PIN,OUTPUT);
  setPump(false);setValve(false); // fail-safe OFF at boot
  Serial.begin(115200);connectWiFi();
}
void loop(){
  if(WiFi.status()!=WL_CONNECTED)connectWiFi();
  unsigned long now=millis();
  if(now-lastSend>SEND_EVERY_MS){postReading();lastSend=now;}
  if(now-lastPoll>POLL_EVERY_MS){pollCommands();lastPoll=now;}
  delay(20);
}
