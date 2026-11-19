# MediWing – Support du loquet de largage (servo MG90S) pour Fusion 360

import adsk.core, adsk.fusion, traceback

# ---------- PARAMÈTRES (mm) ----------
PL_L = 70.0        # plaque : longueur
PL_W = 45.0        # plaque : largeur
PL_EP = 3.0        # plaque : épaisseur
R_ANGLE = 3.0      # rayon des coins de la plaque
SERVO_L = 23.2     # découpe du corps du servo (MG90S 22,8 + jeu)
SERVO_W = 12.6     # (MG90S 12,2 + jeu)
AXE_X = -14.0      # position de l'axe du servo (le bout du palonnier tombe en X = 0)
AXE_BOUT = 6.0     # distance axe -> bout du corps du servo, côté axe
VIS_ENTRAXE = 27.8 # entraxe des trous des pattes du servo
VIS_D = 1.8        # trous pour les vis autotaraudeuses du servo
COL_L = 4.5        # passages de collier : longueur
COL_W = 2.0        # passages de collier : largeur
COL_X = 27.0       # passages de collier : position en X (±)
COL_Y = 12.0       # passages de collier : position en Y (±)
RAIL_W = 5.0       # rails sur le dessus : largeur
RAIL_H = 5.0       # rails : hauteur (écartent la plaque du châssis)
# -------------------------------------

def cm(v):
    return v / 10.0

def P(x, y, z=0.0):
    return adsk.core.Point3D.create(cm(x), cm(y), cm(z))

def rect(sk, x1, y1, x2, y2):
    sk.sketchCurves.sketchLines.addTwoPointRectangle(P(x1, y1), P(x2, y2))

def tous_profils(sk):
    c = adsk.core.ObjectCollection.create()
    for p in sk.profiles:
        c.add(p)
    return c

def extruder(comp, prof, z0, h, op, corps=None):
    ext = comp.features.extrudeFeatures
    inp = ext.createInput(prof, op)
    inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByReal(cm(h))),
        adsk.fusion.ExtentDirections.PositiveExtentDirection)
    if z0:
        inp.startExtent = adsk.fusion.OffsetStartDefinition.create(
            adsk.core.ValueInput.createByReal(cm(z0)))
    if corps is not None:
        inp.participantBodies = [corps]
    return ext.add(inp)

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        root = design.rootComponent
        xy = root.xYConstructionPlane
        NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
        CUT = adsk.fusion.FeatureOperations.CutFeatureOperation

        # ===== 1. PLAQUE =====
        sk = root.sketches.add(xy); sk.name = 'Plaque'
        rect(sk, -PL_L / 2, -PL_W / 2, PL_L / 2, PL_W / 2)
        plaque = extruder(root, sk.profiles.item(0), 0, PL_EP, NEW).bodies.item(0)
        plaque.name = 'Support loquet'

        # coins arrondis (4 arêtes verticales)
        aretes = adsk.core.ObjectCollection.create()
        for e in plaque.edges:
            a, b = e.startVertex.geometry, e.endVertex.geometry
            if abs(a.x - b.x) < 1e-6 and abs(a.y - b.y) < 1e-6:
                aretes.add(e)
        if R_ANGLE > 0 and aretes.count:
            fil = root.features.filletFeatures
            fi = fil.createInput()
            rayon = adsk.core.ValueInput.createByReal(cm(R_ANGLE))
            try:
                fi.edgeSetInputs.addConstantRadiusEdgeSet(aretes, rayon, True)
            except AttributeError:
                fi.addConstantRadiusEdgeSet(aretes, rayon, True)
            fil.add(fi)

        sk2 = root.sketches.add(xy); sk2.name = 'Decoupes'
        x1 = AXE_X - AXE_BOUT                 # bout du servo côté axe
        x2 = x1 + SERVO_L
        rect(sk2, x1, -SERVO_W / 2, x2, SERVO_W / 2)
        xc = (x1 + x2) / 2                     # centre de la découpe
        cercles = sk2.sketchCurves.sketchCircles
        for xv in (xc - VIS_ENTRAXE / 2, xc + VIS_ENTRAXE / 2):
            cercles.addByCenterRadius(P(xv, 0), cm(VIS_D / 2))
        for sx in (-1, 1):
            for sy in (-1, 1):
                cx, cy = sx * COL_X, sy * COL_Y
                rect(sk2, cx - COL_L / 2, cy - COL_W / 2, cx + COL_L / 2, cy + COL_W / 2)
        extruder(root, tous_profils(sk2), 0, PL_EP, CUT, plaque)

        # ===== 3. RAILS SUR LE DESSUS =====
        sk3 = root.sketches.add(xy); sk3.name = 'Rails'
        rect(sk3, -PL_L / 2, PL_W / 2 - RAIL_W, PL_L / 2, PL_W / 2)
        rect(sk3, -PL_L / 2, -PL_W / 2, PL_L / 2, -PL_W / 2 + RAIL_W)
        extruder(root, tous_profils(sk3), PL_EP, RAIL_H, JOIN, plaque)

        sk4 = root.sketches.add(xy); sk4.name = 'Reperes (axe servo, languette)'
        sk4.sketchPoints.add(P(AXE_X, 0))
        sk4.sketchPoints.add(P(0, 0))

        app.activeViewport.fit()
        ui.messageBox('Support du loquet créé : plaque {:.0f} × {:.0f} × {:.0f} mm + rails {:.0f} mm.\n'
                      'Impression : plaque à plat, rails vers le haut, sans supports.\n'
                      'Export : clic droit sur le corps > Enregistrer en tant que maillage (STL).'
                      .format(PL_L, PL_W, PL_EP, RAIL_H))
    except:
        if ui:
            ui.messageBox('Erreur :\n{}'.format(traceback.format_exc()))
