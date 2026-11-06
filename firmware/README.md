# Firmware (Arduino Mega)

MultiWii 2.4 configuré pour MediWing.

- `config.h` : QUADX, MPU-6050 + BMP180 (GY-87), GPS u-blox BN-880, récepteur en PPM.
- Boussole : QMC5883L du BN-880 (pilote ajouté dans `Sensors.cpp`), le magnétomètre du GY-87 n'est pas utilisé.

Téléversement : ouvrir `MultiWii.ino` dans l'IDE Arduino, carte « Arduino Mega 2560 ».
