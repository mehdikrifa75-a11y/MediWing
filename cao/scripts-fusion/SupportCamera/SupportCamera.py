# MediWing – Équerre caméra (Camera Module 3) + télémètre VL53L1X pour Fusion 360

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
BLOC_L, BLOC_W, BLOC_H = 12.0, 20.0, 11.5   # bloc entre les flasques (largeur = écart des flasques)
VIS_Z = 5.5                                 # hauteur des trous M2 latéraux (À MESURER sur les flasques)
VIS_D = 1.8                                 # trou pour vis M2 (se taraude dans le plastique)
PL_L, PL_W, PL_EP = 56.0, 28.0, 2.5         # plaque vers l'avant
PL_Z = 3.5                                  # hauteur du dessous de la plaque
CAM_X = -26.0                               # centre de la caméra (devant le bloc)
CAM_TROUS = (21.0, 12.5)                    # entraxe des trous du Camera Module 3 (M2)
VL_X = -48.0                                # centre du VL53L1X
VL_ENTRAXE = 9.0                            # À MESURER sur ton module
TROU = 2.2
# -------------------------------------

def run(context):
    try:
        c = nouveau_document(); c.name = 'Equerre camera'
        s = bloc(c, 0, -BLOC_W / 2, 0, BLOC_L, BLOC_W / 2, BLOC_H); s.name = 'Equerre camera + VL53L1X'
        bloc(c, -PL_L, -PL_W / 2, PL_Z, 0, PL_W / 2, PL_Z + PL_EP, JOIN, s)
        sk = c.sketches.add(c.xZConstructionPlane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(
            sk.modelToSketchSpace(P(BLOC_L / 2, 0, VIS_Z)), cm(VIS_D / 2))
        ext = c.features.extrudeFeatures
        inp = ext.createInput(sk.profiles.item(0), CUT)
        inp.setSymmetricExtent(adsk.core.ValueInput.createByReal(cm(BLOC_W + 2)), True)
        inp.participantBodies = [s]
        ext.add(inp)
        dx, dy = CAM_TROUS[0] / 2, CAM_TROUS[1] / 2
        trous = [(CAM_X + sx * dx, sy * dy, TROU) for sx in (-1, 1) for sy in (-1, 1)]
        trous += [(VL_X, -VL_ENTRAXE / 2, TROU), (VL_X, VL_ENTRAXE / 2, TROU)]
        cercles(c, trous, PL_Z, PL_Z + PL_EP, CUT, s)
        fin(c, 'Équerre caméra créée. Impression : plaque à plat sur le plateau, bloc vers le haut.')
    except:
        adsk.core.Application.get().userInterface.messageBox('Erreur :\n' + traceback.format_exc())
