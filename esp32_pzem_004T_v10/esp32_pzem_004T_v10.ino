#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <PZEM004Tv30.h>
#include <math.h>
#include <stdlib.h>

// ============================================================
//                    WIFI
// ============================================================

const char* WIFI_SSID = "moto g stylus 5G - 2023";
const char* WIFI_PASSWORD = "12345678@53";


// ============================================================
//                    DJANGO
// ============================================================

const char* DEVICE_ID = "COMPTEUR_01";

const char* API_BASE_URL =
  "https://tsito.pythonanywhere.com";

static const char API_ROOT_CA[] PROGMEM = R"EOF(
-----BEGIN CERTIFICATE-----
MIIFazCCA1OgAwIBAgIRAIIQz7DSQONZRGPgu2OCiwAwDQYJKoZIhvcNAQELBQAw
TzELMAkGA1UEBhMCVVMxKTAnBgNVBAoTIEludGVybmV0IFNlY3VyaXR5IFJlc2Vh
cmNoIEdyb3VwMRUwEwYDVQQDEwxJU1JHIFJvb3QgWDEwHhcNMTUwNjA0MTEwNDM4
WhcNMzUwNjA0MTEwNDM4WjBPMQswCQYDVQQGEwJVUzEpMCcGA1UEChMgSW50ZXJu
ZXQgU2VjdXJpdHkgUmVzZWFyY2ggR3JvdXAxFTATBgNVBAMTDElTUkcgUm9vdCBY
MTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAK3oJHP0FDfzm54rVygc
h77ct984kIxuPOZXoHj3dcKi/vVqbvYATyjb3miGbESTtrFj/RQSa78f0uoxmyF+
0TM8ukj13Xnfs7j/EvEhmkvBioZxaUpmZmyPfjxwv60pIgbz5MDmgK7iS4+3mX6U
A5/TR5d8mUgjU+g4rk8Kb4Mu0UlXjIB0ttov0DiNewNwIRt18jA8+o+u3dpjq+sW
T8KOEUt+zwvo/7V3LvSye0rgTBIlDHCNAymg4VMk7BPZ7hm/ELNKjD+Jo2FR3qyH
B5T0Y3HsLuJvW5iB4YlcNHlsdu87kGJ55tukmi8mxdAQ4Q7e2RCOFvu396j3x+UC
B5iPNgiV5+I3lg02dZ77DnKxHZu8A/lJBdiB3QW0KtZB6awBdpUKD9jf1b0SHzUv
KBds0pjBqAlkd25HN7rOrFleaJ1/ctaJxQZBKT5ZPt0m9STJEadao0xAH0ahmbWn
OlFuhjuefXKnEgV4We0+UXgVCwOPjdAvBbI+e0ocS3MFEvzG6uBQE3xDk3SzynTn
jh8BCNAw1FtxNrQHusEwMFxIt4I7mKZ9YIqioymCzLq9gwQbooMDQaHWBfEbwrbw
qHyGO0aoSCqI3Haadr8faqU9GY/rOPNk3sgrDQoo//fb4hVC1CLQJ13hef4Y53CI
rU7m2Ys6xt0nUW7/vGT1M0NPAgMBAAGjQjBAMA4GA1UdDwEB/wQEAwIBBjAPBgNV
HRMBAf8EBTADAQH/MB0GA1UdDgQWBBR5tFnme7bl5AFzgAiIyBpY9umbbjANBgkq
hkiG9w0BAQsFAAOCAgEAVR9YqbyyqFDQDLHYGmkgJykIrGF1XIpu+ILlaS/V9lZL
ubhzEFnTIZd+50xx+7LSYK05qAvqFyFWhfFQDlnrzuBZ6brJFe+GnY+EgPbk6ZGQ
3BebYhtF8GaV0nxvwuo77x/Py9auJ/GpsMiu/X1+mvoiBOv/2X/qkSsisRcOj/KK
NFtY2PwByVS5uCbMiogziUwthDyC3+6WVwW6LLv3xLfHTjuCvjHIInNzktHCgKQ5
ORAzI4JMPJ+GslWYHb4phowim57iaztXOoJwTdwJx4nLCgdNbOhdjsnvzqvHu7Ur
TkXWStAmzOVyyghqpZXjFaH3pO3JLF+l+/+sKAIuvtd7u+Nxe5AW0wdeRlN8NwdC
jNPElpzVmbUq4JUagEiuTDkHzsxHpFKVK7q4+63SM1N95R1NbdWhscdCb+ZAJzVc
oyi3B43njTOQ5yOf+1CceWxG1bQVs5ZufpsMljq4Ui0/1lvh+wjChP4kqKOJ2qxq
4RgqsahDYVvTH9w7jXbyLeiNdd8XM2w9U/t7y0Ff/9yi0GE44Za4rF2LN9d11TPA
mRGunUHBcnWEvgJBQl9nJEiU0Zsnvgc/ubhPgXRR4Xq37Z0j4r7g1SgEEzwxA57d
emyPxgcYxn/eR44/KJ4EBs+lVDR3veyJm+kXQ99b21/+jh5Xos1AnX5iItreGCc=
-----END CERTIFICATE-----
)EOF";

WiFiClientSecure apiTlsClient;

String apiUrl(const char* path)
{
  return String(API_BASE_URL) + path;
}


// ============================================================
//                    PZEM
// ============================================================

HardwareSerial pzemSerial(2);

PZEM004Tv30 pzem(
  pzemSerial,
  16,   // RX2 ESP32
  17    // TX2 ESP32
);


// ============================================================
//                    LCD
// ============================================================

LiquidCrystal_I2C lcd(
  0x27,
  20,
  4
);


// ============================================================
//                    GPIO
// ============================================================

#define RELAY_PIN 25

#define RELAY_ON  LOW
#define RELAY_OFF HIGH

#define BUZZER_PIN 26

#define LED_VERTE  27
#define LED_ORANGE 32
#define LED_ROUGE  33


// ============================================================
//                    ETAT SYSTEME
// ============================================================

bool autorisationActuelle = true;
bool contacteurDjango = false;

float soldeActuel = 0.0;

float tension = 0.0;
float courant = 0.0;
float puissance = 0.0;
float energie = 0.0;
bool mesurePZEMValide = false;
bool etatDjangoValide = false;


// ============================================================
//                    TIMERS
// ============================================================

unsigned long dernierEnvoiPZEM = 0;
unsigned long derniereLectureEtat = 0;
unsigned long dernierHeartbeat = 0;

const unsigned long INTERVAL_PZEM = 10000;
const unsigned long INTERVAL_ETAT = 1000;
const unsigned long INTERVAL_HEARTBEAT = 1000;
const unsigned long INTERVAL_RECONNEXION_WIFI = 10000;
unsigned long derniereTentativeWiFi = 0;


// ============================================================
//                    TIMEOUT HTTP
// ============================================================

const uint16_t HTTP_TIMEOUT = 10000;


// ============================================================
//                    FONCTION : CONNECTER WIFI
// ============================================================

void connecterWiFi()
{
  Serial.println();
  Serial.println("================================");
  Serial.println("        CONNEXION WIFI");
  Serial.println("================================");

  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(
    WIFI_SSID,
    WIFI_PASSWORD
  );

  derniereTentativeWiFi = millis();

  if (WiFi.status() == WL_CONNECTED)
  {
    Serial.println("WiFi CONNECTE");

    Serial.print("SSID : ");
    Serial.println(WiFi.SSID());

    Serial.print("IP ESP32 : ");
    Serial.println(WiFi.localIP());

    Serial.print("RSSI : ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  }
  else
  {
    Serial.println("WiFi connexion en cours");
  }
}


// ============================================================
//                    TROUVER VALEUR JSON
// ============================================================

bool trouverValeurJSON(
  const String& json,
  const char* cle,
  int& debut,
  int& fin
)
{
  String recherche = "\"";
  recherche += cle;
  recherche += "\"";

  int position = 0;

  while (position < json.length())
  {
    position = json.indexOf(recherche, position);

    if (position < 0)
    {
      return false;
    }

    int apresCle = position + recherche.length();

    while (
      apresCle < json.length() &&
      (
        json.charAt(apresCle) == ' ' ||
        json.charAt(apresCle) == '\t' ||
        json.charAt(apresCle) == '\r' ||
        json.charAt(apresCle) == '\n'
      )
    )
    {
      apresCle++;
    }

    if (
      apresCle < json.length() &&
      json.charAt(apresCle) == ':'
    )
    {
      debut = apresCle + 1;

      while (
        debut < json.length() &&
        (
          json.charAt(debut) == ' ' ||
          json.charAt(debut) == '\t' ||
          json.charAt(debut) == '\r' ||
          json.charAt(debut) == '\n'
        )
      )
      {
        debut++;
      }

      fin = debut;

      while (
        fin < json.length() &&
        json.charAt(fin) != ',' &&
        json.charAt(fin) != '}' &&
        json.charAt(fin) != ']' &&
        json.charAt(fin) != ' ' &&
        json.charAt(fin) != '\t' &&
        json.charAt(fin) != '\r' &&
        json.charAt(fin) != '\n'
      )
      {
        fin++;
      }

      int apresValeur = fin;

      while (
        apresValeur < json.length() &&
        (
          json.charAt(apresValeur) == ' ' ||
          json.charAt(apresValeur) == '\t' ||
          json.charAt(apresValeur) == '\r' ||
          json.charAt(apresValeur) == '\n'
        )
      )
      {
        apresValeur++;
      }

      if (
        apresValeur < json.length() &&
        json.charAt(apresValeur) != ',' &&
        json.charAt(apresValeur) != '}' &&
        json.charAt(apresValeur) != ']'
      )
      {
        return false;
      }

      return fin > debut;
    }

    position += recherche.length();
  }

  return false;
}


// ============================================================
//                    EXTRAIRE FLOAT JSON
// ============================================================

bool extraireFloatJSON(
  const String& json,
  const char* cle,
  float& valeur
)
{
  int debut;
  int fin;

  if (!trouverValeurJSON(json, cle, debut, fin))
  {
    return false;
  }

  String texte = json.substring(debut, fin);
  const char* nombre = texte.c_str();
  size_t longueur = texte.length();
  size_t index = 0;

  if (index < longueur && nombre[index] == '-')
  {
    index++;
  }

  if (index >= longueur)
  {
    return false;
  }

  if (nombre[index] == '0')
  {
    index++;
  }
  else if (nombre[index] >= '1' && nombre[index] <= '9')
  {
    do
    {
      index++;
    }
    while (
      index < longueur &&
      nombre[index] >= '0' &&
      nombre[index] <= '9'
    );
  }
  else
  {
    return false;
  }

  if (index < longueur && nombre[index] == '.')
  {
    index++;

    if (
      index >= longueur ||
      nombre[index] < '0' ||
      nombre[index] > '9'
    )
    {
      return false;
    }

    while (
      index < longueur &&
      nombre[index] >= '0' &&
      nombre[index] <= '9'
    )
    {
      index++;
    }
  }

  if (
    index < longueur &&
    (
      nombre[index] == 'e' ||
      nombre[index] == 'E'
    )
  )
  {
    index++;

    if (
      index < longueur &&
      (
        nombre[index] == '+' ||
        nombre[index] == '-'
      )
    )
    {
      index++;
    }

    if (
      index >= longueur ||
      nombre[index] < '0' ||
      nombre[index] > '9'
    )
    {
      return false;
    }

    while (
      index < longueur &&
      nombre[index] >= '0' &&
      nombre[index] <= '9'
    )
    {
      index++;
    }
  }

  if (index != longueur)
  {
    return false;
  }

  char* finConversion;
  float valeurConvertie = strtof(
    nombre,
    &finConversion
  );

  if (
    finConversion == nombre ||
    *finConversion != '\0' ||
    !isfinite(valeurConvertie)
  )
  {
    return false;
  }

  valeur = valeurConvertie;
  return true;
}


// ============================================================
//                    EXTRAIRE BOOL JSON
// ============================================================

bool extraireBoolJSON(
  const String& json,
  const char* cle,
  bool& valeur
)
{
  int debut;
  int fin;

  if (!trouverValeurJSON(json, cle, debut, fin))
  {
    return false;
  }

  String texte = json.substring(debut, fin);

  if (texte == "true")
  {
    valeur = true;
    return true;
  }

  if (texte == "false")
  {
    valeur = false;
    return true;
  }

  return false;
}


// ============================================================
//                    AFFICHER LCD
// ============================================================

void afficherLCD()
{
  lcd.clear();

  // Ligne 0
  lcd.setCursor(0, 0);

  lcd.print("ID:");

  lcd.print(DEVICE_ID);


  // Ligne 1
  lcd.setCursor(0, 1);

  lcd.print("U:");
  lcd.print(tension, 1);
  lcd.print("V ");

  lcd.print("I:");
  lcd.print(courant, 2);
  lcd.print("A");


  // Ligne 2
  lcd.setCursor(0, 2);

  lcd.print("P:");
  lcd.print(puissance, 1);
  lcd.print("W ");

  lcd.print("E:");
  lcd.print(energie, 3);


  // Ligne 3
  lcd.setCursor(0, 3);

  lcd.print("Solde:");
  lcd.print(soldeActuel, 3);

  lcd.print(" ");

  bool alimentationAutorisee =
    autorisationActuelle &&
    contacteurDjango &&
    soldeActuel > 0.0;

  if (alimentationAutorisee)
  {
    lcd.print("ON");
  }
  else
  {
    lcd.print("OFF");
  }

  if (!etatDjangoValide)
  {
    lcd.setCursor(0, 3);
    lcd.print("ERREUR DJANGO");
  }
}


// ============================================================
//                    GERER LEDS
// ============================================================

void gererLEDs()
{
  // Tout éteindre
  digitalWrite(
    LED_VERTE,
    LOW
  );

  digitalWrite(
    LED_ORANGE,
    LOW
  );

  digitalWrite(
    LED_ROUGE,
    LOW
  );


  // Etat distant inconnu ou solde nul
  if (!etatDjangoValide || soldeActuel <= 0.0)
  {
    digitalWrite(
      LED_ROUGE,
      HIGH
    );
  }

  // Solde faible
  else if (soldeActuel <= 5.0)
  {
    digitalWrite(
      LED_ORANGE,
      HIGH
    );
  }

  // Solde normal
  else
  {
    digitalWrite(
      LED_VERTE,
      HIGH
    );
  }
}


// ============================================================
//                    GERER BUZZER
// ============================================================

void gererBuzzer()
{
  if (soldeActuel <= 0.0)
  {
    digitalWrite(
      BUZZER_PIN,
      HIGH
    );
  }
  else
  {
    digitalWrite(
      BUZZER_PIN,
      LOW
    );
  }
}


// ============================================================
//                    APPLIQUER ETAT RELAIS
// ============================================================

void appliquerEtatRelais()
{
  bool relaisFinal =
    etatDjangoValide &&
    autorisationActuelle &&
    soldeActuel > 0.0 &&
    contacteurDjango;


  if (relaisFinal)
  {
    digitalWrite(
      RELAY_PIN,
      RELAY_ON
    );
  }
  else
  {
    digitalWrite(
      RELAY_PIN,
      RELAY_OFF
    );
  }


  // ========================================================
  // DEBUG
  // ========================================================

  Serial.println();
  Serial.println("================================");
  Serial.println("         ETAT RELAIS");
  Serial.println("================================");

  Serial.print("Solde        : ");
  Serial.print(soldeActuel, 3);
  Serial.println(" kWh");

  Serial.print("Autorisation : ");

  if (autorisationActuelle)
  {
    Serial.println("OUI");
  }
  else
  {
    Serial.println("NON");
  }

  Serial.print("Django       : ");

  if (contacteurDjango)
  {
    Serial.println("ON");
  }
  else
  {
    Serial.println("OFF");
  }

  Serial.print("Relais final : ");

  if (relaisFinal)
  {
    Serial.println("ON");
  }
  else
  {
    Serial.println("OFF");
  }

  Serial.println("================================");
}


void mettreEnSecuriteDjango(const char* raison)
{
  etatDjangoValide = false;
  autorisationActuelle = false;
  contacteurDjango = false;

  digitalWrite(
    RELAY_PIN,
    RELAY_OFF
  );

  Serial.print("Etat Django invalide : ");
  Serial.println(raison);

  gererLEDs();
  gererBuzzer();
  afficherLCD();
}


void afficherErreurHTTP(
  HTTPClient& http,
  int httpCode,
  const char* operation
)
{
  Serial.print(operation);
  Serial.print(" : HTTP ");
  Serial.println(httpCode);

  if (httpCode < 0)
  {
    Serial.println(http.errorToString(httpCode));
    return;
  }

  String response = http.getString();
  if (response.length() > 0)
  {
    Serial.println("Erreur retournee par Django :");
    Serial.println(response);
  }
  else
  {
    Serial.println("Le serveur n'a pas renvoye de details.");
  }
}


// ============================================================
//                    LIRE ETAT DJANGO
// ============================================================

void lireEtatDjango()
{
  if (
    WiFi.status() != WL_CONNECTED
  )
  {
    mettreEnSecuriteDjango("WiFi non connecte");
    return;
  }


  HTTPClient http;


  String url =
    apiUrl("/api/esp32/etat/") +
    String(DEVICE_ID) +
    "/";


  Serial.println();
  Serial.println("================================");
  Serial.println("        LECTURE DJANGO");
  Serial.println("================================");

  Serial.print("URL : ");
  Serial.println(url);


  if (!http.begin(apiTlsClient, url))
  {
    mettreEnSecuriteDjango("http.begin() a echoue");
    return;
  }


  http.setTimeout(
    HTTP_TIMEOUT
  );


  int httpCode =
    http.GET();


  Serial.print(
    "Code HTTP : "
  );

  Serial.println(httpCode);


  if (httpCode != 200)
  {
    afficherErreurHTTP(http, httpCode, "Lecture etat Django");
    http.end();
    mettreEnSecuriteDjango("requete HTTP sans reponse valide");
    return;
  }

  String response = http.getString();

  Serial.println("Reponse Django :");
  Serial.println(response);

  float nouveauSolde;
  bool nouvelleAutorisation;
  bool nouveauContacteur;

  bool soldeValide = extraireFloatJSON(
    response,
    "solde",
    nouveauSolde
  );
  bool autorisationValide = extraireBoolJSON(
    response,
    "autorisation",
    nouvelleAutorisation
  );
  bool contacteurValide = extraireBoolJSON(
    response,
    "contacteur",
    nouveauContacteur
  );

  const char* erreurJSON = NULL;

  if (!soldeValide)
  {
    erreurJSON = "champ solde absent ou invalide";
  }
  else if (!autorisationValide)
  {
    erreurJSON = "champ autorisation absent ou invalide";
  }
  else if (!contacteurValide)
  {
    erreurJSON = "champ contacteur absent ou invalide";
  }

  http.end();

  if (erreurJSON != NULL)
  {
    mettreEnSecuriteDjango(erreurJSON);
    return;
  }

  soldeActuel = nouveauSolde;
  autorisationActuelle = nouvelleAutorisation;
  contacteurDjango = nouveauContacteur;
  etatDjangoValide = true;

  appliquerEtatRelais();
  gererLEDs();
  gererBuzzer();
  afficherLCD();
}


// ============================================================
//                    LIRE PZEM
// ============================================================

bool lirePZEM()
{
  float nouvelleTension = pzem.voltage();
  float nouveauCourant = pzem.current();
  float nouvellePuissance = pzem.power();
  float nouvelleEnergie = pzem.energy();


  // ========================================================
  // SECURITE NaN
  // ========================================================

  mesurePZEMValide =
    isfinite(nouvelleTension) &&
    isfinite(nouveauCourant) &&
    isfinite(nouvellePuissance) &&
    isfinite(nouvelleEnergie);

  if (!mesurePZEMValide)
  {
    Serial.println(
      "Erreur PZEM : mesure absente ou non finie; valeurs conservees"
    );
    return false;
  }

  tension = nouvelleTension;
  courant = nouveauCourant;
  puissance = nouvellePuissance;
  energie = nouvelleEnergie;


  // ========================================================
  // SERIAL
  // ========================================================

  Serial.println();
  Serial.println("================================");
  Serial.println("             PZEM");
  Serial.println("================================");

  Serial.print("Tension   : ");
  Serial.print(tension, 1);
  Serial.println(" V");

  Serial.print("Courant   : ");
  Serial.print(courant, 3);
  Serial.println(" A");

  Serial.print("Puissance : ");
  Serial.print(puissance, 2);
  Serial.println(" W");

  Serial.print("Energie   : ");
  Serial.print(energie, 3);
  Serial.println(" kWh");

  Serial.println("================================");

  return true;
}


// ============================================================
//                    ENVOYER PZEM
// ============================================================

void envoyerPZEM()
{
  if (!mesurePZEMValide)
  {
    Serial.println(
      "PZEM : envoi ignore, aucune mesure valide"
    );
    return;
  }

  if (
    WiFi.status() != WL_CONNECTED
  )
  {
    Serial.println(
      "PZEM : WiFi non connecte"
    );

    return;
  }


  HTTPClient http;


  if (!http.begin(apiTlsClient, apiUrl("/api/pzem/mesure/")))
  {
    Serial.println(
      "PZEM : erreur http.begin()"
    );

    return;
  }


  http.setTimeout(
    HTTP_TIMEOUT
  );


  http.addHeader(
    "Content-Type",
    "application/json"
  );


  // ========================================================
  // CREATION JSON
  // ========================================================

  String json = "{";

  json +=
    "\"device_id\":\"" +
    String(DEVICE_ID) +
    "\",";

  json +=
    "\"tension\":" +
    String(tension, 2) +
    ",";

  json +=
    "\"courant\":" +
    String(courant, 3) +
    ",";

  json +=
    "\"puissance\":" +
    String(puissance, 2) +
    ",";

  json +=
    "\"energie\":" +
    String(energie, 3);

  json += "}";


  Serial.println();
  Serial.println("================================");
  Serial.println("          ENVOI PZEM");
  Serial.println("================================");

  Serial.println(json);


  int httpCode =
    http.POST(json);


  Serial.print(
    "Code HTTP PZEM : "
  );

  Serial.println(httpCode);


  if (httpCode >= 200 && httpCode < 300)
  {
    String response =
      http.getString();

    Serial.println(
      "Reponse Django :"
    );

    Serial.println(response);
  }
  else
  {
    afficherErreurHTTP(http, httpCode, "Envoi PZEM");
  }


  http.end();
}


// ============================================================
//                    ENVOYER HEARTBEAT
// ============================================================

void envoyerHeartbeat()
{
  if (
    WiFi.status() != WL_CONNECTED
  )
  {
    Serial.println(
      "Heartbeat : WiFi non connecte"
    );

    return;
  }


  HTTPClient http;


  if (!http.begin(apiTlsClient, apiUrl("/api/esp32/heartbeat/")))
  {
    Serial.println(
      "Heartbeat : erreur http.begin()"
    );

    return;
  }


  http.setTimeout(
    HTTP_TIMEOUT
  );


  http.addHeader(
    "Content-Type",
    "application/json"
  );


  // ========================================================
  // LIRE LE RELAIS PHYSIQUE
  // ========================================================

  bool relaisON =
    (
      digitalRead(RELAY_PIN)
      == RELAY_ON
    );


  // ========================================================
  // JSON
  // ========================================================

  String json = "{";

  json +=
    "\"device_id\":\"" +
    String(DEVICE_ID) +
    "\",";

  json +=
    "\"relais_on\":";

  if (relaisON)
  {
    json += "true";
  }
  else
  {
    json += "false";
  }

  json += "}";


  Serial.println();
  Serial.println("================================");
  Serial.println("          HEARTBEAT");
  Serial.println("================================");

  Serial.print(
    "Relais reel : "
  );

  if (relaisON)
  {
    Serial.println("ON");
  }
  else
  {
    Serial.println("OFF");
  }

  Serial.print(
    "JSON : "
  );

  Serial.println(json);


  int httpCode =
    http.POST(json);


  Serial.print(
    "Code HTTP heartbeat : "
  );

  Serial.println(httpCode);


  if (httpCode >= 200 && httpCode < 300)
  {
    String response =
      http.getString();

    Serial.println(
      "Reponse Django :"
    );

    Serial.println(response);
  }
  else
  {
    afficherErreurHTTP(http, httpCode, "Heartbeat ESP32");
  }


  http.end();
}


// ============================================================
//                    SETUP
// ============================================================

void setup()
{
  Serial.begin(
    115200
  );

  apiTlsClient.setCACert(API_ROOT_CA);

  // ========================================================
  // GPIO
  // ========================================================

  pinMode(
    RELAY_PIN,
    OUTPUT
  );

  pinMode(
    BUZZER_PIN,
    OUTPUT
  );

  pinMode(
    LED_VERTE,
    OUTPUT
  );

  pinMode(
    LED_ORANGE,
    OUTPUT
  );

  pinMode(
    LED_ROUGE,
    OUTPUT
  );


  // ========================================================
  // ETAT INITIAL SECURISE
  // ========================================================

  digitalWrite(
    RELAY_PIN,
    RELAY_OFF
  );

  digitalWrite(
    BUZZER_PIN,
    LOW
  );

  digitalWrite(
    LED_VERTE,
    LOW
  );

  digitalWrite(
    LED_ORANGE,
    LOW
  );

  digitalWrite(
    LED_ROUGE,
    LOW
  );


  // ========================================================
  // I2C LCD
  // SDA = GPIO21
  // SCL = GPIO22
  // ========================================================

  Wire.begin(
    21,
    22
  );


  lcd.init();

  lcd.backlight();

  lcd.clear();


  lcd.setCursor(
    0,
    0
  );

  lcd.print(
    "Compteur ELEC"
  );


  lcd.setCursor(
    0,
    1
  );

  lcd.print(
    DEVICE_ID
  );


  lcd.setCursor(
    0,
    2
  );

  lcd.print(
    "Initialisation..."
  );


  delay(1500);


  // ========================================================
  // PZEM
  // UART2
  // RX = GPIO16
  // TX = GPIO17
  // ========================================================

  pzemSerial.begin(
    9600,
    SERIAL_8N1,
    16,
    17
  );


  Serial.println();
  Serial.println("================================");
  Serial.println("        COMPTEUR ELECTRIQUE");
  Serial.println("================================");

  Serial.print("Device ID : ");
  Serial.println(DEVICE_ID);

  Serial.println("PZEM RX : GPIO16");
  Serial.println("PZEM TX : GPIO17");

  Serial.println("LCD SDA : GPIO21");
  Serial.println("LCD SCL : GPIO22");

  Serial.println("Relais   : GPIO25");
  Serial.println("Buzzer   : GPIO26");

  Serial.println("LED V    : GPIO27");
  Serial.println("LED O    : GPIO32");
  Serial.println("LED R    : GPIO33");


  // ========================================================
  // WIFI
  // ========================================================

  connecterWiFi();


  lcd.clear();


  if (
    WiFi.status() == WL_CONNECTED
  )
  {
    lcd.setCursor(
      0,
      0
    );

    lcd.print(
      "WiFi CONNECTE"
    );


    lcd.setCursor(
      0,
      1
    );

    lcd.print(
      WiFi.localIP()
    );
  }
  else
  {
    lcd.setCursor(
      0,
      0
    );

    lcd.print(
      "WiFi NON CONNECTE"
    );
  }


  delay(1500);


  // ========================================================
  // PREMIERE LECTURE DJANGO
  // ========================================================

  lireEtatDjango();


  // ========================================================
  // PREMIERE LECTURE PZEM
  // ========================================================

  lirePZEM();


  // ========================================================
  // AFFICHAGE FINAL
  // ========================================================

  afficherLCD();


  // ========================================================
  // INITIALISATION TIMERS
  // ========================================================

  dernierEnvoiPZEM =
    millis();

  derniereLectureEtat =
    millis();

  dernierHeartbeat =
    millis();
}


// ============================================================
//                    LOOP
// ============================================================

void loop()
{
  // ========================================================
  // RECONNEXION WIFI
  // ========================================================

  if (
    WiFi.status() != WL_CONNECTED
  )
  {
    if (etatDjangoValide)
    {
      mettreEnSecuriteDjango("WiFi perdu");
    }

    if (
      millis() - derniereTentativeWiFi >=
      INTERVAL_RECONNEXION_WIFI
    )
    {
      Serial.println("WiFi : nouvelle tentative de connexion");
      WiFi.reconnect();
      derniereTentativeWiFi = millis();
    }
  }


  // ========================================================
  // LECTURE ETAT DJANGO
  // Toutes les 2 secondes
  // ========================================================

  if (
    millis() -
    derniereLectureEtat >=
    INTERVAL_ETAT
  )
  {
    derniereLectureEtat =
      millis();

    lireEtatDjango();
  }


  // ========================================================
  // LECTURE + ENVOI PZEM
  // Toutes les 10 secondes
  // ========================================================

  if (
    millis() -
    dernierEnvoiPZEM >=
    INTERVAL_PZEM
  )
  {
    dernierEnvoiPZEM =
      millis();


    lirePZEM();


    envoyerPZEM();


    afficherLCD();
  }


  // ========================================================
  // HEARTBEAT
  // Toutes les 2 secondes
  // ========================================================

  if (
    millis() -
    dernierHeartbeat >=
    INTERVAL_HEARTBEAT
  )
  {
    dernierHeartbeat =
      millis();


    envoyerHeartbeat();
  }


  delay(10);
}
