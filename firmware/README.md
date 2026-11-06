# Firmware (Arduino Mega)

MultiWii 2.4 (version `release-2.4` du dépôt officiel multiwii/multiwii-firmware, licence GPLv3) configuré pour MediWing.
Les sources sont dans `MultiWii/`. Le premier commit les contient sans modification, le second ajoute les réglages MediWing : `git diff` entre les deux montre exactement ce qui a changé.

## Ce qui a été modifié

| Fichier | Modification |
|---|---|
| `config.h` | `QUADX`, `MPU6050` et `BMP085` (le BMP180 du GY-87 utilise le même pilote), `QMC5883L`, `SERIAL_SUM_PPM` (ordre RadioLink/Futaba : ROLL, PITCH, THROTTLE, YAW, AUX1…), `GPS_SERIAL 2` + `UBLOX` à 57600 bauds, `FAILSAFE`, `MINTHROTTLE 1070`, `MAG_DECLINATION 3.0f` (Nice). |
| `def.h` | `QMC5883L` ajouté à la liste des magnétomètres (sinon `MAG` reste à 0). |
| `Sensors.cpp` | Pilote de la boussole QMC5883L (adresse I2C 0x0D). Le « bypass » I2C du MPU-6050 est coupé : la boussole du GY-87 reste cachée sur son bus auxiliaire et ne peut pas gêner celle du BN-880. |
| `GPS.cpp` | Deux corrections pour que le mode UBLOX compile avec les IDE Arduino récents (tableau `uint8_t` au lieu de `char`, taille fixe pour le tableau de l'union). Sans elles : `error: flexible array member in union`. |

La carte Mega n'a pas besoin d'être déclarée : MultiWii la reconnaît tout seul (ATmega2560).

Compilation vérifiée pour l'ATmega2560 (avr-gcc 7.3, cœur Arduino AVR) : 31 250 octets de programme (12 %), 3 211 octets de RAM (39 %).

## Téléverser

1. Télécharger le dossier `MultiWii/` (bouton Code → Download ZIP, ou `git clone`). Le dossier doit garder le nom `MultiWii`, comme le fichier `MultiWii.ino`.
2. Ouvrir `MultiWii.ino` dans l'IDE Arduino. Tous les onglets (`config.h`, `Sensors.cpp`…) s'ouvrent avec.
3. Outils → Type de carte : « Arduino Mega or Mega 2560 », Processeur : « ATmega2560 (Mega 2560) ».
4. Outils → Port : le port USB de la Mega Pro (`/dev/cu.usbserial-…` sur Mac ; si rien n'apparaît, installer le pilote CH340).
5. Vérifier (✓), puis Téléverser (→).
6. Ouvrir MultiWiiConf à 115200 bauds sur le même port : les capteurs ACC, BARO, MAG, GPS doivent être allumés.

## Câblage prévu

| Élément | Broche Mega |
|---|---|
| GY-87 (MPU-6050 + BMP180) | SDA 20, SCL 21, 5 V, GND |
| Boussole QMC5883L du BN-880 | SDA 20, SCL 21 (même bus que le GY-87) |
| GPS du BN-880 | TX du GPS → RX2 (17), RX du GPS → TX2 (16), 5 V, GND |
| Récepteur R8EF en PPM | signal → broche 19 (RX1) |
| ESC (QUADX) | D3 arrière droit, D5 avant droit, D6 arrière gauche, D2 avant gauche |

Sens de rotation attendu par MultiWii en QUADX : avant gauche et arrière droit en horaire, avant droit et arrière gauche en anti-horaire. À confirmer sur le schéma de MultiWiiConf en S2, sans hélices.

## À vérifier en S2

- **Orientation de la boussole** : la puce du BN-880 n'est pas alignée comme le GY-87. Dans MultiWiiConf, tourner le drone à plat : le cap doit augmenter en tournant vers la droite et l'horizon doit rester juste quand on l'incline. Sinon, décommenter `FORCE_MAG_ORIENTATION` dans `config.h` et changer les signes ou l'ordre de X, Y, Z.
- **Bus I2C** : si MAG reste éteint, vérifier que le BN-880 est bien alimenté et que ses fils SDA/SCL ne sont pas inversés (la QMC5883L répond en 0x0D).
- **PPM** : le R8EF doit être passé en mode SBUS/PPM (voir sa notice) et son signal PPM relié à la broche 19. Les 4 voies doivent bouger dans le bon sens dans MultiWiiConf, sinon inverser la voie dans la T8FB.
- **MINTHROTTLE** : après la calibration des ESC, mettre la plus petite valeur où les 4 moteurs tournent tous de façon régulière.
- **Failsafe** : il se déclenche quand le signal PPM disparaît ou que les gaz passent sous 985 µs. Régler le failsafe du récepteur en conséquence, puis tester en S4 sans hélices. `FAILSAFE_THROTTLE` (1270 µs) est à ajuster pour une descente d'environ 1 m/s.
- **Déclinaison** : 3,0° Est est une estimation pour Nice en 2026, à confirmer sur magnetic-declination.com.
