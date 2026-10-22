import cv2
import time
from deepface import DeepFace

def main():
    # --------------------------------------------------
    # 1. INITIALIZE WEBCAM
    # --------------------------------------------------

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        print("Could not open webcam. Trying default backend...")
        camera.release()
        camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("ERROR: Could not access the webcam.")
        return

    # --------------------------------------------------
    # 2. INITIALIZE FACE DETECTOR
    # --------------------------------------------------

    cascade_path = (
        cv2.data.haarcascades
        + "haarcascade_frontalface_default.xml"
    )

    face_detector = cv2.CascadeClassifier(cascade_path)

    if face_detector.empty():
        print("ERROR: Could not load face detection model.")
        camera.release()
        return

    print("\nMusicAI Facial-Expression Analyzer started.")
    print("The first analysis may take longer.")
    print("Press Q in the webcam window to exit.\n")

    # --------------------------------------------------
    # 3. ANALYSIS SETTINGS
    # --------------------------------------------------

    frame_count = 0

    # Analyze periodically rather than on every frame.
    analysis_interval = 15

    current_expression = "Waiting for analysis"
    current_score = None

    analysis_status = "Initializing"
    last_analysis_time = 0

    # Keep the previous prediction visible between analyses.
    analysis_in_progress = False

    try:
        while True:

            # ------------------------------------------
            # READ WEBCAM FRAME
            # ------------------------------------------

            success, frame = camera.read()

            if not success or frame is None:
                print("WARNING: Could not read webcam frame.")
                time.sleep(0.1)
                continue

            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            frame_count += 1

            # ------------------------------------------
            # DETECT FACE
            # ------------------------------------------

            faces = face_detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(60, 60)
            )

            if len(faces) == 0:
                current_expression = "No face detected"
                current_score = None
                analysis_status = "Waiting for face"

            else:
                # Draw a rectangle around the largest detected face.
                x, y, width, height = max(
                    faces,
                    key=lambda face: face[2] * face[3]
                )

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + width, y + height),
                    (0, 255, 0),
                    2
                )

                # --------------------------------------
                # RUN DEEPFACE PERIODICALLY
                # --------------------------------------

                if (
                    frame_count % analysis_interval == 0
                    and not analysis_in_progress
                ):
                    analysis_in_progress = True
                    analysis_status = "Analyzing expression"

                    try:
                        results = DeepFace.analyze(
                            img_path=frame,
                            actions=["emotion"],
                            detector_backend="opencv",
                            enforce_detection=False,
                            silent=True
                        )

                        # Support the list-based result format.
                        if isinstance(results, list):
                            result = results[0] if results else {}
                        else:
                            result = results

                        emotions = result.get("emotion", {})

                        if emotions:
                            # Highest-scoring expression category.
                            current_expression = max(
                                emotions,
                                key=emotions.get
                            )

                            # DeepFace scores are generally expressed
                            # as percentages, not calibrated probabilities.
                            current_score = float(
                                emotions[current_expression]
                            )

                            analysis_status = "Analysis complete"
                            last_analysis_time = time.time()

                        else:
                            current_expression = "Unavailable"
                            current_score = None
                            analysis_status = "No expression scores"

                    except Exception as error:
                        current_expression = "Analysis error"
                        current_score = None
                        analysis_status = "Analysis failed"

                        print(
                            "Expression analysis error:",
                            str(error)
                        )

                    finally:
                        analysis_in_progress = False

            # ------------------------------------------
            # DISPLAY RESULTS
            # ------------------------------------------

            cv2.putText(
                frame,
                f"Expression: {current_expression}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            if current_score is not None:
                cv2.putText(
                    frame,
                    f"Model score: {current_score:.1f}%",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )

            cv2.putText(
                frame,
                f"Status: {analysis_status}",
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "Press Q to quit",
                (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "MusicAI - Facial Expression Analysis",
                frame
            )

            # ------------------------------------------
            # HANDLE KEYBOARD AND WINDOW EVENTS
            # ------------------------------------------

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                print("Closing facial-expression analyzer...")
                break

            try:
                if cv2.getWindowProperty(
                    "MusicAI - Facial Expression Analysis",
                    cv2.WND_PROP_VISIBLE
                ) < 1:
                    break
            except cv2.error:
                break

    except KeyboardInterrupt:
        print("\nStopped by user.")

    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("Webcam released.")
        print("MusicAI facial-expression test finished.")


if __name__ == "__main__":
    main()
