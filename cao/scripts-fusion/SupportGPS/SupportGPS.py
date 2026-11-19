# MediWing – Support du GPS BN-880 pour Fusion 360

import adsk.core, adsk.fusion, traceback, math

def cm(v):
    return v / 10.0

def P(x, y, z=0.0):
    return adsk.core.Point3D.create(cm(x), cm(y), cm(z))

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

def tous(sk):
    c = adsk.core.ObjectCollection.create()
    for p in sk.profiles:
        c.add(p)
    return c

def nouveau_document():
    app = adsk.core.Application.get()
    app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    root = design.rootComponent
    try:
        yup = (app.preferences.generalPreferences.defaultModelingOrientation ==
               adsk.core.DefaultModelingOrientations.YUpModelingOrientation)
    except:
        yup = False
    m = adsk.core.Matrix3D.create()
    if yup:
        m.setToRotation(-math.pi / 2, adsk.core.Vector3D.create(1, 0, 0),
                        adsk.core.Point3D.create(0, 0, 0))
    return root.occurrences.addNewComponent(m).component

NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation

def rect(sk, x1, y1, x2, y2):
    sk.sketchCurves.sketchLines.addTwoPointRectangle(P(x1, y1), P(x2, y2))

def bloc(c, x1, y1, z1, x2, y2, z2, op=NEW, corps=None):
    sk = c.sketches.add(c.xYConstructionPlane)
    rect(sk, x1, y1, x2, y2)
    return extruder(c, sk.profiles.item(0), z1, z2 - z1, op, corps).bodies.item(0)

def cercles(c, liste, z1, z2, op, corps=None):
    sk = c.sketches.add(c.xYConstructionPlane)
    for (x, y, d) in liste:
        sk.sketchCurves.sketchCircles.addByCenterRadius(P(x, y), cm(d / 2))
    return extruder(c, tous(sk), z1, z2 - z1, op, corps)

def fin(c, texte):
    app = adsk.core.Application.get()
    app.activeViewport.fit()
    app.userInterface.messageBox(texte + '\n\nExport : clic droit sur le corps > '
                                 'Enregistrer en tant que maillage (STL).')

# ---------- PARAMÈTRES (mm) ----------
BASE_L, BASE_W, BASE_EP = 12.0, 30.0, 3.0
MONT_EP, MONT_H = 3.0, 15.0
PLAT_L, PLAT_W, PLAT_EP = 35.0, 32.0, 2.0
GPS = 29.0                 # logement (BN-880 28 mm + jeu)
REB_EP, REB_H = 1.5, 3.0
ENCOCHE = 8.0              # passage du câble côté avant
COL = (2.0, 4.5)           # passages de collier
FLECHE_P = 0.6             # flèche AVANT gravée
# -------------------------------------

def run(context):
    try:
        c = nouveau_document(); c.name = 'Support GPS'
        xm = BASE_L - MONT_EP
        z_p = BASE_EP + MONT_H
        x_fin = xm + PLAT_L
        xr = x_fin - (GPS + 2 * REB_EP)
        s = bloc(c, 0, -BASE_W / 2, 0, BASE_L, BASE_W / 2, BASE_EP); s.name = 'Support GPS'
        bloc(c, xm, -PLAT_W / 2, BASE_EP, BASE_L, PLAT_W / 2, z_p, JOIN, s)
        bloc(c, xm, -PLAT_W / 2, z_p, x_fin, PLAT_W / 2, z_p + PLAT_EP, JOIN, s)
        sk = c.sketches.add(c.xYConstructionPlane)
        rect(sk, xr, -(GPS / 2 + REB_EP), x_fin, GPS / 2 + REB_EP)
        rect(sk, xr + REB_EP, -GPS / 2, x_fin - REB_EP, GPS / 2)
        prof = [p for p in sk.profiles if p.profileLoops.count == 2][0]
        extruder(c, prof, z_p + PLAT_EP, REB_H, JOIN, s)
        bloc(c, xr - 1, -ENCOCHE / 2, z_p + PLAT_EP, xr + REB_EP + 1, ENCOCHE / 2,
             z_p + PLAT_EP + REB_H, CUT, s)
        # passages de collier dans la base
        sk = c.sketches.add(c.xYConstructionPlane)
        for sy in (-1, 1):
            cy = sy * (BASE_W / 2 - 3.5)
            rect(sk, 3 - COL[0] / 2, cy - COL[1] / 2, 3 + COL[0] / 2, cy + COL[1] / 2)
        extruder(c, tous(sk), 0, BASE_EP, CUT, s)
        # flèche AVANT (pointe vers -X)
        sk = c.sketches.add(c.xYConstructionPlane)
        pts = [P(0.8, 0), P(6.5, -3.5), P(6.5, 3.5)]
        for i in range(3):
            sk.sketchCurves.sketchLines.addByTwoPoints(pts[i], pts[(i + 1) % 3])
        extruder(c, sk.profiles.item(0), BASE_EP - FLECHE_P, FLECHE_P, CUT, s)
        fin(c, 'Support GPS v2 créé. Impression : base à plat, supports sous le plateau.')
    except:
        adsk.core.Application.get().userInterface.messageBox('Erreur :\n' + traceback.format_exc())
