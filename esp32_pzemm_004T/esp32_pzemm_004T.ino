#include <WiFi.h>
#include <HTTPClient.h>

#include <PZEM004Tv30.h>

#include <Wire.h>
#include <LiquidCrystal_I2C.h>


// =====================================================
// WIFI
// =====================================================

const char* WIFI_SSID = "moto g stylus 5G - 2023";
const char* WIFI_PASSWORD = "12345678@53";


// =====================================================
// SERVEUR DJANGO
// =====================================================

const char* API_URL =
  "http://10.65.107.74:8000/api/pzem/mesure/";


// =====================================================
// IDENTIFICATION DU COMPTEUR
// =====================================================

const char* DEVICE_ID = "COMPTEUR_01";


// =====================================================
// PZEM-004T
// =====================================================

#define PZEM_RX_PIN 16
#define PZEM_TX_PIN 17

HardwareSerial pzemSerial(2);

PZEM004Tv30 pzem(
  pzemSerial,
  PZEM_RX_PIN,
  PZEM_TX_PIN
);


// =====================================================
// LCD 20x4 I2C
// =====================================================

#define LCD_SDA 21
#define LCD_SCL 22

LiquidCrystal_I2C lcd(0x27, 20, 4);


// =====================================================
// INTERVALLE D'ENVOI
// =====================================================

const unsigned long INTERVALLE_ENVOI = 10000;

unsigned long dernierEnvoi = 0;


// =====================================================
// CONNEXION WIFI
// =====================================================

void connecterWiFi()
{
  Serial.println();
  Serial.println("================================");
  Serial.println("Connexion Wi-Fi...");
  Serial.println("================================");

  WiFi.begin(
    WIFI_SSID,
    WIFI_PASSWORD
  );

  lcd.clear();

  lcd.setCursor(0, 0);
  lcd.print("Connexion WiFi...");

  int compteur = 0;

  while (
    WiFi.status() != WL_CONNECTED &&
    compteur < 30
  )
  {
    delay(500);

    Serial.print(".");

    lcd.setCursor(0, 1);
    lcd.print("Attente...        ");

    compteur++;
  }


  if (WiFi.status() == WL_CONNECTED)
  {
    Serial.println();
    Serial.println("WiFi connecte !");

    Serial.print("IP ESP32 : ");
    Serial.println(WiFi.localIP());

    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("WiFi CONNECTE");

    lcd.setCursor(0, 1);
    lcd.print(WiFi.localIP());

    delay(2000);
  }
  else
  {
    Serial.println();
    Serial.println("Erreur WiFi !");

    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("WiFi ERREUR");

    delay(2000);
  }
}


// =====================================================
// AFFICHAGE LCD
// =====================================================

void afficherLCD(
  float tension,
  float courant,
  float puissance,
  float energie
)
{
  lcd.clear();


  // Ligne 1
  lcd.setCursor(0, 0);
  lcd.print("V: ");

  if (!isnan(tension))
  {
    lcd.print(tension, 1);
  }
  else
  {
    lcd.print("---");
  }

  lcd.print(" V");


  // Ligne 2
  lcd.setCursor(0, 1);
  lcd.print("I: ");

  if (!isnan(courant))
  {
    lcd.print(courant, 2);
  }
  else
  {
    lcd.print("---");
  }

  lcd.print(" A");


  // Ligne 3
  lcd.setCursor(0, 2);
  lcd.print("P: ");

  if (!isnan(puissance))
  {
    lcd.print(puissance, 1);
  }
  else
  {
    lcd.print("---");
  }

  lcd.print(" W");


  // Ligne 4
  lcd.setCursor(0, 3);
  lcd.print("E: ");

  if (!isnan(energie))
  {
    lcd.print(energie, 3);
  }
  else
  {
    lcd.print("---");
  }

  lcd.print(" kWh");
}


// =====================================================
// ENVOI VERS DJANGO
// =====================================================

void envoyerDjango(
  float tension,
  float courant,
  float puissance,
  float energie
)
{
  if (WiFi.status() != WL_CONNECTED)
  {
    Serial.println(
      "WiFi non connecte. Envoi impossible."
    );

    return;
  }


  HTTPClient http;


  Serial.println();
  Serial.println(
    "Envoi des donnees vers Django..."
  );


  http.begin(API_URL);

  http.addHeader(
    "Content-Type",
    "application/json"
  );


  // ---------------------------------------------------
  // Création du JSON
  // ---------------------------------------------------

  String json = "{";

  json += "\"device_id\":\"";
  json += DEVICE_ID;
  json += "\",";

  json += "\"tension\":";
  json += String(tension, 2);
  json += ",";

  json += "\"courant\":";
  json += String(courant, 3);
  json += ",";

  json += "\"puissance\":";
  json += String(puissance, 2);
  json += ",";

  json += "\"energie\":";
  json += String(energie, 3);

  json += "}";


  Serial.println("JSON :");
  Serial.println(json);


  // ---------------------------------------------------
  // POST
  // ---------------------------------------------------

  int codeHTTP =
    http.POST(json);


  Serial.print(
    "Code HTTP : "
  );

  Serial.println(codeHTTP);


  if (codeHTTP > 0)
  {
    String reponse =
      http.getString();

    Serial.println(
      "Reponse Django :"
    );

    Serial.println(reponse);
  }
  else
  {
    Serial.println(
      "Erreur communication avec Django."
    );
  }


  http.end();
}


// =====================================================
// SETUP
// =====================================================

void setup()
{
  Serial.begin(115200);

  delay(1000);


  Serial.println();
  Serial.println(
    "========================================"
  );

  Serial.println(
    "COMPTEUR ELECTRIQUE ESP32"
  );

  Serial.println(
    "PZEM + LCD + Django"
  );

  Serial.println(
    "========================================"
  );


  // ---------------------------------------------------
  // LCD
  // ---------------------------------------------------

  Wire.begin(
    LCD_SDA,
    LCD_SCL
  );

  lcd.init();

  lcd.backlight();


  lcd.clear();

  lcd.setCursor(0, 0);
  lcd.print("COMPTEUR ELECTRIQUE");

  lcd.setCursor(0, 1);
  lcd.print("ESP32 + PZEM");

  lcd.setCursor(0, 2);
  lcd.print(DEVICE_ID);

  delay(2000);


  // ---------------------------------------------------
  // WiFi
  // ---------------------------------------------------

  connecterWiFi();


  // ---------------------------------------------------
  // PZEM
  // ---------------------------------------------------

  Serial.println(
    "PZEM initialise."
  );

  lcd.clear();

  lcd.setCursor(0, 0);
  lcd.print("PZEM initialise");

  delay(1000);
}


// =====================================================
// LOOP
// =====================================================

void loop()
{
  // ---------------------------------------------------
  // Vérification WiFi
  // ---------------------------------------------------

  if (WiFi.status() != WL_CONNECTED)
  {
    Serial.println(
      "WiFi perdu..."
    );

    connecterWiFi();
  }


  // ---------------------------------------------------
  // Lecture PZEM
  // ---------------------------------------------------

  float tension =
    pzem.voltage();


  float courant =
    pzem.current();


  float puissance =
    pzem.power();


  float energie =
    pzem.energy();


  // ---------------------------------------------------
  // Affichage série
  // ---------------------------------------------------

  Serial.println();
  Serial.println(
    "========== PZEM =========="
  );


  Serial.print(
    "Tension : "
  );

  Serial.print(
    tension
  );

  Serial.println(
    " V"
  );


  Serial.print(
    "Courant : "
  );

  Serial.print(
    courant
  );

  Serial.println(
    " A"
  );


  Serial.print(
    "Puissance : "
  );

  Serial.print(
    puissance
  );

  Serial.println(
    " W"
  );


  Serial.print(
    "Energie : "
  );

  Serial.print(
    energie
  );

  Serial.println(
    " kWh"
  );


  // ---------------------------------------------------
  // Vérification lecture
  // ---------------------------------------------------

  if (
    isnan(tension) ||
    isnan(courant) ||
    isnan(puissance) ||
    isnan(energie)
  )
  {
    Serial.println(
      "ERREUR : lecture PZEM impossible."
    );


    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("ERREUR PZEM");

    lcd.setCursor(0, 1);
    lcd.print("Verifier cablage");

    delay(2000);

    return;
  }


  // ---------------------------------------------------
  // LCD
  // ---------------------------------------------------

  afficherLCD(
    tension,
    courant,
    puissance,
    energie
  );


  // ---------------------------------------------------
  // Envoi Django toutes les 10 secondes
  // ---------------------------------------------------

  if (
    millis() - dernierEnvoi >=
    INTERVALLE_ENVOI
  )
  {
    dernierEnvoi = millis();


    envoyerDjango(
      tension,
      courant,
      puissance,
      energie
    );
  }


  delay(1000);
}
