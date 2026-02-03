import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os

# Chemins
IMAGE_PATH = os.path.join("static", "uploads", "PHOTO_CV.jpg")  # ton image
OUTPUT_PATH = os.path.join("static", "uploads", "test_annotated.jpg")
MODEL_PATH = "pose_landmarker_full.task"

# Télécharger le modèle une fois si besoin
if not os.path.exists(MODEL_PATH):
    import urllib.request
    url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/1/pose_landmarker_full.task"
    urllib.request.urlretrieve(url, MODEL_PATH)

# Charger l'image
image_bgr = cv2.imread(IMAGE_PATH)
if image_bgr is None:
    raise FileNotFoundError(f"Impossible de lire {IMAGE_PATH}")
image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

# Options du landmarker
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=False,
)
detector = vision.PoseLandmarker.create_from_options(options)

mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

# Détection
result = detector.detect(mp_image)

annotated = image_bgr.copy()
h, w, _ = annotated.shape

# Couleurs bien visibles (BGR)
LINE_COLOR = (0, 255, 255)   # jaune
POINT_COLOR = (0, 0, 255)    # rouge
LINE_THICKNESS = 4
POINT_RADIUS = 6

pose_landmarks = result.pose_landmarks[0]

# 1) Dessin des lignes (squelette)
for connection in vision.PoseLandmarksConnections.POSE_LANDMARKS:
    start = pose_landmarks[connection.start]
    end = pose_landmarks[connection.end]

    x1, y1 = int(start.x * w), int(start.y * h)
    x2, y2 = int(end.x * w), int(end.y * h)

    # petit contour noir pour mieux voir sur fond clair
    cv2.line(annotated, (x1, y1), (x2, y2), (0, 0, 0), LINE_THICKNESS + 2)
    cv2.line(annotated, (x1, y1), (x2, y2), LINE_COLOR, LINE_THICKNESS)

# 2) Dessin des points
for lm in pose_landmarks:
    x = int(lm.x * w)
    y = int(lm.y * h)
    cv2.circle(annotated, (x, y), POINT_RADIUS + 2, (0, 0, 0), -1)   # contour noir
    cv2.circle(annotated, (x, y), POINT_RADIUS, POINT_COLOR, -1)     # point rouge
