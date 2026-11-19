# MediWing – Drone complet (assemblage de principe) pour Fusion 360

import adsk.core, adsk.fusion, traceback, math

# ---------- COTES PRINCIPALES (mm) ----------
MOT_X = 62.0      # moitié de 124 mm (entraxe moteurs en longueur)
MOT_Y = 52.0      # moitié de 104 mm (entraxe moteurs en largeur)
CH_L, CH_W = 85.0, 30.0    # longueur × largeur max des plaques centrales (À MESURER)
CH_BOUT = 18.0             # largeur aux deux extrémités (À MESURER)
CH_DROIT = 60.0            # longueur de la partie à pleine largeur (À MESURER)
EP_BAS = 2.5      # plaque inférieure
EP_BRAS = 3.5     # bras
EP_MED = 2.5      # plaque médiane
EP_HAUT = 2.0     # plaque du haut
CH_H = 35.0       # hauteur totale du châssis, dessous -> dessus (rapport ≈ 35 mm, À MESURER)
PATIN_D = 24.0    # diamètre du patin moteur au bout du bras (À MESURER)
FLASQUE_L = 18.0  # longueur des flasques alu avant (À MESURER)
STACK_X = 15.0    # centre du stack arrière (ESC)
HELICE_D = 89.0   # 3,5"
BAT = (75.0, 35.0, 35.0)    # LiPo 4S 1550 mAh (L × l × h)
BOITE = (80.0, 120.0, 25.0) # boîte du colis : 8 cm selon X, 12 cm selon Y, 2,5 cm de haut
JEU_LOQUET = 3.0  # espace sous la plaque pour le palonnier du servo
# -------------------------------------------

COUL = {                         # palette monochrome (niveaux de gris)
    'carbone':   (30, 30, 30),
    'flasque':   (70, 70, 70),
    'moteur':    (110, 110, 110),
    'helice':    (200, 200, 200),
    'lipo':      (55, 55, 55),
    'esc':       (90, 90, 90),
    'arduino':   (100, 100, 100),
    'gy87':      (130, 130, 130),
    'pi':        (120, 120, 120),
    'camera':    (45, 45, 45),
    'vl53':      (140, 140, 140),
    'gps':       (80, 80, 80),
    'recepteur': (60, 60, 60),
    'hc12':      (150, 150, 150),
    'servo':     (75, 75, 75),
    'palonnier': (235, 235, 235),
    'imprime':   (245, 245, 245),  # pièces imprimées en 3D : blanc
}

app = adsk.core.Application.get()
ui = app.userInterface
_apps = {}
_base = [None]

def cm(v):
    return v / 10.0

def P(x, y, z=0.0):
    return adsk.core.Point3D.create(cm(x), cm(y), cm(z))

def trouver_base():
    if _base[0]:
        return _base[0]
    libs = []
    try:
        l = app.materialLibraries.itemById('BA5EE55E-9982-449B-9D66-9F036540E140')
        if l: libs.append(l)
    except:
        pass
    for i in range(app.materialLibraries.count):
        libs.append(app.materialLibraries.item(i))
    for lib in libs:
        try:
            n = lib.appearances.count
        except:
            continue
        for i in range(min(n, 400)):
            try:
                ap = lib.appearances.item(i)
                for j in range(ap.appearanceProperties.count):
                    cp = adsk.core.ColorProperty.cast(ap.appearanceProperties.item(j))
                    if cp and not cp.hasConnectedTexture:
                        _base[0] = ap
                        return ap
            except:
                continue
    return None

def colorer(corps, nom):
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if nom not in _apps:
            base = trouver_base()
            if base is None:
                return
            a = design.appearances.addByCopy(base, 'MediWing ' + nom)
            r, g, b = COUL[nom]
            for j in range(a.appearanceProperties.count):
                cp = adsk.core.ColorProperty.cast(a.appearanceProperties.item(j))
                if cp:
                    cp.value = adsk.core.Color.create(r, g, b, 255)
                    break
            _apps[nom] = a
        corps.appearance = _apps[nom]
    except:
        pass  # la couleur est un bonus : on n'arrête pas le script pour ça

def y_vers_le_haut():
    try:
        return (app.preferences.generalPreferences.defaultModelingOrientation ==
                adsk.core.DefaultModelingOrientations.YUpModelingOrientation)
    except:
        return False

def matrice_pose():
    m = adsk.core.Matrix3D.create()
    if y_vers_le_haut():
        m.setToRotation(-math.pi / 2, adsk.core.Vector3D.create(1, 0, 0),
                        adsk.core.Point3D.create(0, 0, 0))
    return m

def contour_corps():
    l, w, b, d = CH_L / 2, CH_W / 2, CH_BOUT / 2, CH_DROIT / 2
    return [(-l, -b), (-d, -w), (d, -w), (l, -b), (l, b), (d, w), (-d, w), (-l, b)]

def plaque(c, nom, z1, z2, coul):
    sk = c.sketches.add(c.xYConstructionPlane)
    pts = [P(x, y) for (x, y) in contour_corps()]
    for i in range(len(pts)):
        sk.sketchCurves.sketchLines.addByTwoPoints(pts[i], pts[(i + 1) % len(pts)])
    b = extruder(c, sk.profiles.item(0), z1, z2 - z1, NEW).bodies.item(0)
    b.name = nom
    colorer(b, coul)
    return b

def composant(root, nom):
    occ = root.occurrences.addNewComponent(matrice_pose())
    occ.component.name = nom
    return occ.component

def extruder(c, prof, z1, h, op, corps=None):
    ext = c.features.extrudeFeatures
    inp = ext.createInput(prof, op)
    inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByReal(cm(h))),
        adsk.fusion.ExtentDirections.PositiveExtentDirection)
    if z1:
        inp.startExtent = adsk.fusion.OffsetStartDefinition.create(
            adsk.core.ValueInput.createByReal(cm(z1)))
    if corps is not None:
        inp.participantBodies = [corps]
    return ext.add(inp)

def tous(sk):
    col = adsk.core.ObjectCollection.create()
    for p in sk.profiles:
        col.add(p)
    return col

NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation

def bloc(c, nom, x1, y1, z1, x2, y2, z2, coul, op=NEW, corps=None):
    sk = c.sketches.add(c.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(P(x1, y1), P(x2, y2))
    b = extruder(c, sk.profiles.item(0), z1, z2 - z1, op, corps).bodies.item(0)
    if op == NEW:
        b.name = nom
        colorer(b, coul)
    return b

def cylindre(c, nom, x, y, d, z1, z2, coul, op=NEW, corps=None):
    sk = c.sketches.add(c.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(P(x, y), cm(d / 2))
    b = extruder(c, sk.profiles.item(0), z1, z2 - z1, op, corps).bodies.item(0)
    if op == NEW:
        b.name = nom
        colorer(b, coul)
    return b

def run(context):
    try:
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        root = design.rootComponent
        moteurs = [(sx * MOT_X, sy * MOT_Y) for sx in (-1, 1) for sy in (-1, 1)]
        z_haut = CH_H                       # dessus de la plaque du haut
        z_bras = EP_BAS + EP_BRAS           # dessus des bras (les moteurs sont posés dessus)
        z_int = z_bras + EP_MED             # dessus de la plaque médiane

        # ===== CHÂSSIS FlyFishRC VOLADOR VX3.5 =====
        c = composant(root, 'Chassis VX3.5')
        bas = plaque(c, 'Plaque inferieure 2,5', 0, EP_BAS, 'carbone')
        sk = c.sketches.add(c.xYConstructionPlane)
        lignes = sk.sketchCurves.sketchLines
        for (mx, my) in moteurs:
            n = math.hypot(mx, my); dx, dy = mx / n, my / n
            px, py = -dy, dx
            pts = [P(px * 9, py * 9), P(-px * 9, -py * 9),
                   P(mx - px * 6, my - py * 6), P(mx + px * 6, my + py * 6)]
            for i in range(4):
                lignes.addByTwoPoints(pts[i], pts[(i + 1) % 4])
            sk.sketchCurves.sketchCircles.addByCenterRadius(P(mx, my), cm(PATIN_D / 2))
        bras = extruder(c, tous(sk), EP_BAS, EP_BRAS, NEW).bodies.item(0)
        bras.name = 'Bras 3,5'; colorer(bras, 'carbone')
        skt = c.sketches.add(c.xYConstructionPlane)
        for (mx, my) in moteurs:
            skt.sketchCurves.sketchCircles.addByCenterRadius(P(mx, my), cm(2.5))
            for (ex, ey) in ((6, 6), (-6, 6), (6, -6), (-6, -6)):   # F2004 : 12 × 12, M2
                skt.sketchCurves.sketchCircles.addByCenterRadius(P(mx + ex, my + ey), cm(1.0))
        trous = adsk.core.ObjectCollection.create()
        for p in skt.profiles:
            if p.profileLoops.count == 1 and p.areaProperties().area < cm(6) ** 2:
                trous.add(p)
        extruder(c, trous, EP_BAS, EP_BRAS, CUT, bras)
        med = plaque(c, 'Plaque mediane 2,5', z_bras, z_int, 'carbone')
        for e in (10.0, 12.75):          # trous du stack 20 × 20 et 25,5 × 25,5 (M2)
            for sx in (-1, 1):
                for sy in (-1, 1):
                    cylindre(c, '', STACK_X + sx * e, sy * e, 2.2, z_bras, z_int, 'carbone', CUT, med)
        plaque(c, 'Plaque du haut 2', z_haut - EP_HAUT, z_haut, 'carbone')
        for sy in (-1, 1):               # flasques CNC alu avant (variante Yellow)
            x0 = -CH_DROIT / 2
            bloc(c, 'Flasque alu avant', x0, sy * CH_W / 2 - (5 if sy > 0 else 0),
                 z_int, x0 + FLASQUE_L, sy * CH_W / 2 + (5 if sy < 0 else 0),
                 z_haut - EP_HAUT, 'flasque')
            cylindre(c, 'Entretoise arriere', CH_L / 2 - 3.5, sy * 5, 5,
                     z_int, z_haut - EP_HAUT, 'carbone')

        c = composant(root, 'Propulsion')
        for i, (mx, my) in enumerate(moteurs):
            cylindre(c, 'Moteur F2004 %d' % (i + 1), mx, my, 25.5, z_bras, z_bras + 17, 'moteur')
            skh = c.sketches.add(c.xYConstructionPlane)
            R = HELICE_D / 2
            pale = [(3, -3), (12, -5.5), (22, -6), (34, -4.5), (R - 1, -2), (R, 0),
                    (R - 1, 2.5), (34, 6), (22, 7.5), (12, 6.5), (3, 3)]
            calage = math.radians(30 + 45 * i)
            for k in range(3):
                a = calage + k * 2 * math.pi / 3
                ca, sa = math.cos(a), math.sin(a)
                pts = [P(mx + u * ca - v * sa, my + u * sa + v * ca) for (u, v) in pale]
                for j in range(len(pts)):
                    skh.sketchCurves.sketchLines.addByTwoPoints(pts[j], pts[(j + 1) % len(pts)])
            skh.sketchCurves.sketchCircles.addByCenterRadius(P(mx, my), cm(5))
            hel = extruder(c, tous(skh), z_bras + 20, 1.5, NEW).bodies.item(0)
            hel.name = 'Helice 3525 %d' % (i + 1)
            colorer(hel, 'helice')
            cylindre(c, 'Moyeu %d' % (i + 1), mx, my, 8, z_bras + 17, z_bras + 23, 'moteur')

        # ===== ÉLECTRONIQUE ENTRE LES PLAQUES =====
        c = composant(root, 'Electronique')
        bloc(c, 'ESC HAKRC 4-en-1 35A', STACK_X - 13, -13, z_int + 1, STACK_X + 13, 13,
             z_int + 6, 'esc')
        bloc(c, 'HC-12 433 MHz', -13.4, -13.9, z_int + 1, 1, 13.9, z_int + 5, 'hc12')
        bloc(c, 'Arduino Mega 2560 Pro', -14, -19, z_int + 7, 40, 19, z_int + 15, 'arduino')
        bloc(c, 'GY-87 (MPU-6050 + BMP180)', -10, -8, z_int + 15, 11, 8, z_int + 18, 'gy87')
        bloc(c, 'Recepteur R8EF', 14, -8, z_int + 15, 34, 8, z_int + 23, 'recepteur')
        bloc(c, 'Servo MG90S (couche)', 16, -11.25, -12.2, 38.8, 11.25, 0, 'servo')
        bloc(c, 'Palonnier', 8, 15, -7.1, 24, 17, -5.1, 'palonnier')

        # ===== SUR LA PLAQUE DU HAUT =====
        c = composant(root, 'Dessus')
        bx0 = CH_L / 2 - 12 - BAT[0]        # batterie avancée pour laisser 12 mm au support GPS
        bloc(c, 'LiPo OVONIC 4S 1550 mAh', bx0, -BAT[1] / 2, z_haut,
             bx0 + BAT[0], BAT[1] / 2, z_haut + BAT[2], 'lipo')
        bloc(c, 'Raspberry Pi Zero 2 WH (sur la tranche)', -32.5, 18.5, z_haut,
             32.5, 28.5, z_haut + 30, 'pi')

        # support GPS imprimé (arrière) + BN-880
        g = composant(root, 'Support GPS (imprime)')
        x0, x1 = CH_L / 2 - 12, CH_L / 2          # base 12 mm à l'arrière de la plaque du haut
        s = bloc(g, 'Support GPS', x0, -15, z_haut, x1, 15, z_haut + 3, 'imprime')
        bloc(g, '', x1 - 3, -16, z_haut + 3, x1, 16, z_haut + 18, 'imprime', JOIN, s)
        bloc(g, '', x1 - 3, -16, z_haut + 18, x1 + 32, 16, z_haut + 20, 'imprime', JOIN, s)
        bloc(g, '', x1, -16, z_haut + 20, x1 + 32, 16, z_haut + 23, 'imprime', JOIN, s)
        bloc(g, '', x1 + 1.5, -14.5, z_haut + 20, x1 + 30.5, 14.5, z_haut + 23, 'imprime', CUT, s)
        bloc(g, 'GPS BN-880 + QMC5883L', x1 + 2, -14, z_haut + 20, x1 + 30, 14,
             z_haut + 30, 'gps')

        # ===== SOUS LA PLAQUE INFÉRIEURE =====
        c = composant(root, 'Vision')
        xe = -CH_DROIT / 2                   # avant des flasques = arrière de la plaque
        sc = composant(root, 'Equerre camera (imprimee)')
        eq = bloc(sc, 'Equerre camera + VL53L1X', xe, -10, z_int, xe + 12, 10, z_int + 11.5, 'imprime')
        bloc(sc, '', xe - 56, -14, z_int + 3.5, xe, 14, z_int + 6, 'imprime', JOIN, eq)
        bloc(c, 'Camera Module 3', xe - 38.5, -12.5, z_int + 3.5 - 11.5, xe - 13.5, 12.5,
             z_int + 3.5, 'camera')
        bloc(c, 'VL53L1X', xe - 54.5, -9, z_int + 1.5, xe - 41.5, 9, z_int + 3.5, 'vl53')

        pz = composant(root, 'Pieds (imprimes TPU)')
        z_sol = EP_BAS - 17.0                 # pieds de 17 mm (2 mm sous le servo couché)
        for i, (mx, my) in enumerate(moteurs):
            p = cylindre(pz, 'Pied %d' % (i + 1), mx, my, 24, EP_BAS - 2, EP_BAS, 'imprime')
            cylindre(pz, '', mx, my, 10, z_sol + 2, EP_BAS - 2, 'imprime', JOIN, p)
            cylindre(pz, '', mx, my, 16, z_sol, z_sol + 2, 'imprime', JOIN, p)

        # ===== BOÎTE DU COLIS (imprimée) =====
        b = composant(root, 'Boite du colis (imprimee)')
        bx, by, bh = BOITE
        z_dessus = -JEU_LOQUET
        z_bas = z_dessus - bh
        corps = bloc(b, 'Corps boite', -bx / 2, -by / 2, z_bas, bx / 2, by / 2,
                     z_dessus - 2, 'imprime')
        bloc(b, '', -bx / 2 + 2, -by / 2 + 2, z_bas + 2, bx / 2 - 2, by / 2 - 2,
             z_dessus - 2, 'imprime', CUT, corps)
        couv = bloc(b, 'Couvercle', -bx / 2, -by / 2, z_dessus - 2, bx / 2, by / 2,
                    z_dessus, 'imprime')
        zb = z_bas
        for corps_ in (corps,):
            bloc(b, '', 12, -13, zb + 14, bx / 2, 21, zb + 23, 'imprime', CUT, corps_)
            bloc(b, '', 10, -15, zb + 12, bx / 2, 23, zb + 14, 'imprime', JOIN, corps_)
            bloc(b, '', 10, -15, zb + 14, 12, 23, zb + 23, 'imprime', JOIN, corps_)
            bloc(b, '', 12, -15, zb + 14, bx / 2, -13, zb + 23, 'imprime', JOIN, corps_)
            bloc(b, '', 12, 21, zb + 14, bx / 2, 23, zb + 23, 'imprime', JOIN, corps_)
            bloc(b, '', 9, 14, zb + 20.5, 13, 19, zb + 23, 'imprime', CUT, corps_)
        bloc(b, '', 9.8, -15.2, z_dessus - 2, bx / 2, 23.2, z_dessus, 'imprime', CUT, couv)
        bloc(b, 'Doliprane', -36, -105 / 2, z_bas + 2, 8, 105 / 2, z_bas + 20, 'palonnier')

        # ===== CONTRÔLE DU VOLUME =====
        bb = root.boundingBox
        L = (bb.maxPoint.x - bb.minPoint.x) * 10
        W = (bb.maxPoint.y - bb.minPoint.y) * 10
        H = (bb.maxPoint.z - bb.minPoint.z) * 10
        if y_vers_le_haut():
            W, H = H, W
        z_hel = z_bras + 20
        yup = y_vers_le_haut()
        conflits = []
        for occ in root.allOccurrences:
            for i in range(occ.bRepBodies.count):
                b = occ.bRepBodies.item(i)
                nom = b.name
                if nom.startswith(('Helice', 'Moteur', 'Moyeu', 'Bras')):
                    continue
                mn, mx = b.boundingBox.minPoint, b.boundingBox.maxPoint
                if yup:   # repère Fusion -> repère drone
                    x1, x2, y1, y2, z1, z2 = mn.x, mx.x, -mx.z, -mn.z, mn.y, mx.y
                else:
                    x1, x2, y1, y2, z1, z2 = mn.x, mx.x, mn.y, mx.y, mn.z, mx.z
                x1, x2, y1, y2, z1, z2 = [v * 10 for v in (x1, x2, y1, y2, z1, z2)]
                if z2 < z_hel - 1 or z1 > z_hel + 2:
                    continue
                for (hx, hy) in moteurs:
                    px = min(max(hx, x1), x2); py = min(max(hy, y1), y2)
                    if math.hypot(px - hx, py - hy) < HELICE_D / 2 + 1:
                        conflits.append(nom)
                        break
        alerte = ('\n\nATTENTION, touche une hélice : ' + ', '.join(sorted(set(conflits)))
                  if conflits else '\n\nHélices dégagées : rien ne touche.')

        app.activeViewport.fit()
        ui.messageBox('MediWing assemblé.\n\nEncombrement : {:.0f} (L) × {:.0f} (l) × {:.0f} (h) mm\n'
                      'Limite du cahier des charges : 300 × 200 × 100 mm\n\n'
                      'Blanc = pièces imprimées en 3D.'.format(L, W, H) + alerte)
    except:
        ui.messageBox('Erreur :\n{}'.format(traceback.format_exc()))
