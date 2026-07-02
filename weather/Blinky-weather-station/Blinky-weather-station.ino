// board is 0.9 model 
// https://www.amazon.com/dp/B09SPWYS4B?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_13&th=1

// web data - http://192.168.0.98/weather

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <DHT.h>

#define DHTPIN D5
#define DHTTYPE DHT22
#define STATUS_LED LED_BUILTIN  // GPIO2 / D4

const char* ssid     = "########";
const char* password = "########";

DHT dht(DHTPIN, DHTTYPE);
ESP8266WebServer server(80);

float currentTemp = 0;
float currentHum  = 0;
bool hasReading   = false;

void ledOn()  { digitalWrite(STATUS_LED, LOW); }
void ledOff() { digitalWrite(STATUS_LED, HIGH); }

void blinkLed(int times, int delayMs) {
  for (int i = 0; i < times; i++) {
    ledOn();
    delay(delayMs);
    ledOff();
    delay(delayMs);
  }
}

void handleWeather() {
  blinkLed(1, 60); // flash to show a request came in
  if (!hasReading) {
    server.send(503, "application/json", "{\"error\":\"no reading\"}");
    return;
  }
  String json = "{\"temp\":" + String(currentTemp, 1) + ",\"hum\":" + String(currentHum, 1) + "}";
  server.send(200, "application/json", json);
}

void setup() {
  Serial.begin(115200);
  pinMode(STATUS_LED, OUTPUT);
  ledOff();

  dht.begin();
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(250);
    digitalWrite(STATUS_LED, !digitalRead(STATUS_LED)); // fast blink while connecting
    Serial.print(".");
  }
  ledOn(); // solid LED = connected

  Serial.println("\nWiFi connected: " + WiFi.localIP().toString());
  server.on("/weather", handleWeather);
  server.begin();
  Serial.println("Server started");
}

void loop() {
  server.handleClient();

  // If WiFi drops, let the LED show it
  if (WiFi.status() != WL_CONNECTED) {
    digitalWrite(STATUS_LED, (millis() / 200) % 2); // fast blink = disconnected
  } else {
    ledOn(); // solid = connected/idle
  }

  static unsigned long lastRead = 0;
  if (millis() - lastRead > 3000) {
    float t = dht.readTemperature(true);
    float h = dht.readHumidity();
    if (!isnan(t) && !isnan(h)) {
      currentTemp = t;
      currentHum  = h;
      hasReading  = true;
      blinkLed(1, 40); // small flash on successful read
      Serial.printf("Temp: %.1f F  Hum: %.1f%%\n", t, h);
    }
    lastRead = millis();
  }
}