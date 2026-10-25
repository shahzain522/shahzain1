
import cv2
import json
import sqlite3
import numpy as np
from pathlib import Path
from datetime import datetime

from database import check_in_employee

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "hcm_lite.db"
FACE_DIR = BASE_DIR / "face_data"
MODEL_PATH = BASE_DIR / "face_model.yml"
LABELS_PATH = BASE_DIR / "face_labels.json"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_face_detector():
    detector_path = (
        cv2.data.haarcascades
        + "haarcascade_frontalface_default.xml"
    )

    detector = cv2.CascadeClassifier(detector_path)

    if detector.empty():
        raise RuntimeError(
            f"Face detector load nahi hua: {detector_path}"
        )

    return detector


def capture_face_samples(company_id, employee_id, samples=30):
    folder = FACE_DIR / f"{company_id}_{employee_id}"
    folder.mkdir(parents=True, exist_ok=True)

    detector = get_face_detector()
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not camera.isOpened():
        camera.release()
        raise RuntimeError("Camera open nahi ho raha. Camera permission/check karo.")
    count = 0

    try:
        if not camera.isOpened():
            raise RuntimeError("Camera open nahi ho raha.")

        while count < samples:
            ok, frame = camera.read()

            if not ok:
                raise RuntimeError("Camera se frame nahi mila.")

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = detector.detectMultiScale(
                gray,
                scaleFactor=1.3,
                minNeighbors=5,
                minSize=(100, 100)
            )

            for x, y, w, h in faces:
                face = cv2.resize(
                    gray[y:y + h, x:x + w],
                    (200, 200)
                )

                cv2.imwrite(
                    str(folder / f"{count}.jpg"),
                    face
                )
                count += 1
                break

            cv2.putText(
                frame,
                f"Samples: {count}/{samples}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            cv2.imshow("Face Registration - Q to quit", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()

    if count == 0:
        raise RuntimeError(
            "Face detect nahi hua. Camera aur lighting check karein."
        )

    return count


def train_face_model():
    if not FACE_DIR.exists():
        raise ValueError("Pehle face samples capture karein.")

    if not hasattr(cv2, "face"):
        raise RuntimeError(
            "OpenCV face module missing hai. "
            "opencv-contrib-python install karein."
        )

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    images = []
    labels = []
    label_map = {}
    label_id = 0

    for folder in sorted(FACE_DIR.iterdir()):
        if not folder.is_dir():
            continue

        folder_images = []

        for image_path in folder.glob("*.jpg"):
            image = cv2.imread(
                str(image_path),
                cv2.IMREAD_GRAYSCALE
            )

            if image is not None:
                folder_images.append(image)

        if not folder_images:
            continue

        for image in folder_images:
            images.append(image)
            labels.append(label_id)

        label_map[str(label_id)] = folder.name
        label_id += 1

    if not images:
        raise ValueError(
            "Koi valid face image nahi mili. Pehle face register karein."
        )

    recognizer.train(images, np.array(labels))
    recognizer.save(str(MODEL_PATH))

    LABELS_PATH.write_text(
        json.dumps(label_map),
        encoding="utf-8"
    )

    return len(images)


def recognize_and_mark_attendance(company_id):
    if not MODEL_PATH.exists() or not LABELS_PATH.exists():
        raise ValueError(
            "Pehle face samples capture karke model train karein."
        )

    if not hasattr(cv2, "face"):
        raise RuntimeError(
            "OpenCV face module missing hai. "
            "opencv-contrib-python install karein."
        )

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(str(MODEL_PATH))

    label_map = json.loads(
        LABELS_PATH.read_text(encoding="utf-8")
    )

    detector = get_face_detector()
    camera = cv2.VideoCapture(0)
    matched_employee = None

    try:
        if not camera.isOpened():
            raise RuntimeError("Camera open nahi ho raha.")

        while True:
            ok, frame = camera.read()

            if not ok:
                raise RuntimeError("Camera se frame nahi mila.")

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = detector.detectMultiScale(
                gray,
                scaleFactor=1.3,
                minNeighbors=5,
                minSize=(100, 100)
            )

            for x, y, w, h in faces:
                face = cv2.resize(
                    gray[y:y + h, x:x + w],
                    (200, 200)
                )

                label, confidence = recognizer.predict(face)
                text = "Unknown"

                if confidence < 60 and str(label) in label_map:
                    try:
                        saved_company, employee_id = map(
                            int,
                            label_map[str(label)].split("_")
                        )

                        if saved_company == int(company_id):
                            with get_connection() as conn:
                                employee = conn.execute(
                                    """
                                    SELECT id
                                    FROM employees
                                    WHERE id = ?
                                      AND company_id = ?
                                      AND status = 'Active'
                                    """,
                                    (employee_id, company_id)
                                ).fetchone()

                            if employee is not None:
                                matched_employee = employee_id
                                text = "Recognized"

                    except (ValueError, TypeError):
                        pass

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    text,
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

            cv2.imshow("Face Attendance - Q to quit", frame)

            if matched_employee is not None:
                cv2.waitKey(800)
                break

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()

    if matched_employee is None:
        return "Face recognize nahi hua."

    with get_connection() as conn:
        employee = conn.execute(
            """
            SELECT id, full_name
            FROM employees
            WHERE id = ?
              AND company_id = ?
              AND status = 'Active'
            """,
            (matched_employee, company_id)
        ).fetchone()

    if employee is None:
        return "Active employee record nahi mila."

    try:
        result = check_in_employee(
            company_id,
            matched_employee
        )

        return (
            f"Attendance marked: {employee['full_name']} "
            f"at {result['check_in']} ({result['status']})"
        )

    except ValueError as exc:
        return str(exc)


if __name__ == "__main__":
    print("Face Attendance module ready.")
    print("Isay app.py se call karein.")
