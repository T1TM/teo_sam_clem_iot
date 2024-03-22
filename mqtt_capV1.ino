#include <WiFi101.h>
#include <PubSubClient.h>
#include <DHT.h>

#define DHTPIN 6    // Définir la broche à laquelle est connecté le capteur DHT11
#define DHTTYPE DHT11  // Spécifier le type de capteur DHT (DHT11)

DHT dht(DHTPIN, DHTTYPE);

const char* ssid = "wifi-test";
const char* password = "wifi-test-2001";
const char* mqtt_server = "test.mosquitto.org";
const char* mqtt_topic_temp = "ecar/robot/value/temp";
const char* mqtt_topic_hum = "ecar/robot/value/hum";
const char* mqtt_topic = "ecar/robot/value/mouv";

const int pirPin = 2;   // Broche du capteur PIR
String value ;
float last_temp ; 
float last_hum ;

WiFiClient wifiClient;
PubSubClient client(wifiClient);

void setup() {
  pinMode(pirPin, INPUT);
  Serial.begin(9600);
  
  connectWiFi();
  client.setServer(mqtt_server, 1883);
  dht.begin();
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  dht_code();
  mouv();
  delay(1000);
}

void connectWiFi() {
  Serial.println("Connecting to WiFi");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
}

void reconnect() {
  while (!client.connected()) {
    Serial.println("Attempting MQTT connection...");

    if (client.connect("MKR1000Client")) {
      Serial.println("Connected to MQTT broker");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Retry in 5 seconds");
      delay(5000);
    }
  }
}
void dht_code(){
// Lecture de la température et de l'humidité depuis le capteur
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  if (temperature != last_temp || humidity != last_hum){
    // Vérification de la réussite de la lecture
    if (!isnan(temperature) && !isnan(humidity)) {
      // Convertir les valeurs en chaînes de caractères
      String temperatureString = String(temperature);
      String humidityString = String(humidity);
    
      // Afficher les valeurs dans la console série
      Serial.print("Temperature: ");
      Serial.println(temperatureString);
      Serial.print("Humidity: ");
      Serial.println(humidityString);
      client.publish(mqtt_topic_temp, temperatureString.c_str());
      client.publish(mqtt_topic_hum, humidityString.c_str());

      last_temp = temperature;
      last_hum = humidity;

      // Vous pouvez maintenant utiliser temperatureString et humidityString comme vous le souhaitez
    } else {
    Serial.println("Erreur de lecture du capteur DHT");
    }




  }
  
}

void mouv() {
  static int previousMotionState = LOW; // Variable statique pour suivre l'état précédent du mouvement
  int motionSensorValue = digitalRead(pirPin);

  if (motionSensorValue == HIGH && previousMotionState == LOW) {
    // Mouvement détecté
    Serial.println("Mouvement détecté !");
    value = "Detectée";
    client.publish(mqtt_topic, value.c_str());
    previousMotionState = HIGH; // Mettre à jour l'état précédent du mouvement
  } else if (motionSensorValue == LOW && previousMotionState == HIGH) {
    // Pas de mouvement
    Serial.println("Rien !");
    value = "Rien";
    previousMotionState = LOW; // Mettre à jour l'état précédent du mouvement
  }
}
