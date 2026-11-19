# Détection d'un marqueur ArUco (DICT_4X4_50) à la webcam, touche q pour quitter
import cv2

dictionnaire = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
detecteur = cv2.aruco.ArucoDetector(dictionnaire, cv2.aruco.DetectorParameters())

camera = cv2.VideoCapture(0)
while True:
    ok, image = camera.read()
    if not ok:
        break
    hauteur, largeur = image.shape[:2]
    cx_image, cy_image = largeur // 2, hauteur // 2

    gris = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    coins, ids, _ = detecteur.detectMarkers(gris)

    if ids is not None:
        cv2.aruco.drawDetectedMarkers(image, coins, ids)
        for c, i in zip(coins, ids.flatten()):
            cx, cy = c[0].mean(axis=0).astype(int)
            dx, dy = cx - cx_image, cy - cy_image
            cv2.line(image, (cx_image, cy_image), (cx, cy), (0, 0, 255), 2)
            cv2.putText(image, f"id {i}  dx={dx}  dy={dy}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.drawMarker(image, (cx_image, cy_image), (0, 255, 0), cv2.MARKER_CROSS, 20, 2)
    cv2.imshow("MediWing - ArUco", image)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
