# Raspberry Pi Zero 2 W

Code Python pour l'atterrissage guidé :
- détection du marqueur ArUco (`DICT_4X4_50`) avec OpenCV et la Camera Module 3 ;
- lecture de la hauteur (VL53L1X) ;
- envoi des consignes à MultiWii par le protocole MSP (UART).


`vision/aruco_webcam.py` : premier essai de détection ArUco à la webcam du PC (séance 2). Il affiche l'écart dx, dy entre le marqueur et le centre de l'image.
