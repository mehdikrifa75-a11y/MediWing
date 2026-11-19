# MediWing – Pied d'atterrissage (à imprimer 4 fois, en TPU) pour Fusion 360

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
H = 17.0            # hauteur totale (dessous du bras -> sol) : 2 mm de plus que le servo couché
COL_D, COL_EP = 24.0, 2.0
TUBE_D = 10.0
PATIN_D, PATIN_EP = 16.0, 2.0
TROUS = 12.0        # entraxe des vis du moteur (F2004 : 12 × 12)
TROU = 2.2          # M2
CREUX = 6.0         # tube creux Ø6 (allège le pied)
# -------------------------------------

def run(context):
    try:
        c = nouveau_document(); c.name = 'Pied'
        p = cercles(c, [(0, 0, PATIN_D)], 0, PATIN_EP, NEW).bodies.item(0); p.name = 'Pied'
        cercles(c, [(0, 0, TUBE_D)], PATIN_EP, H - COL_EP, JOIN, p)
        cercles(c, [(0, 0, COL_D)], H - COL_EP, H, JOIN, p)
        e = TROUS / 2
        cercles(c, [(e, e, TROU), (-e, e, TROU), (e, -e, TROU), (-e, -e, TROU)],
                H - COL_EP, H, CUT, p)
        cercles(c, [(0, 0, CREUX)], PATIN_EP, H, CUT, p)
        fin(c, 'Pied créé : hauteur {:.1f} mm. À imprimer 4 fois en TPU, retourné : collerette posée sur le plateau.'
            .format(H))
    except:
        adsk.core.Application.get().userInterface.messageBox('Erreur :\n' + traceback.format_exc())
