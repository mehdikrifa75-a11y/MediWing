// Test du récepteur R8EF en PPM sur la broche 19 (Moniteur série à 115200 bauds)

const byte PIN_PPM = 19;
const byte NB_VOIES = 8;
volatile unsigned int voies[NB_VOIES];
volatile byte indexVoie = 0;
volatile unsigned long dernierFront = 0;

void frontPPM() {
  unsigned long maintenant = micros();
  unsigned long duree = maintenant - dernierFront;
  dernierFront = maintenant;
  if (duree > 3000) {
    indexVoie = 0;
  } else if (indexVoie < NB_VOIES) {
    voies[indexVoie++] = duree;
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_PPM, INPUT);
  attachInterrupt(digitalPinToInterrupt(PIN_PPM), frontPPM, RISING);
  Serial.println("Test PPM : bouge les manches de la T8FB");
}

void loop() {
  unsigned int copie[NB_VOIES];
  noInterrupts();
  for (byte i = 0; i < NB_VOIES; i++) copie[i] = voies[i];
  interrupts();
  const char* noms[NB_VOIES] = {"AIL", "ELE", "GAZ", "DIR", "CH5", "CH6", "CH7", "CH8"};
  for (byte i = 0; i < NB_VOIES; i++) {
    Serial.print(noms[i]); Serial.print('='); Serial.print(copie[i]); Serial.print("  ");
  }
  Serial.println();
  delay(200);
}
