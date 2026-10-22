import cv2

def main():
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        print("Could not open webcam. Trying default camera backend...")
        camera.release()
        camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("ERROR: Could not access the webcam.")
        return

    cascade_path = (
        cv2.data.haarcascades
        + "haarcascade_frontalface_default.xml"
    )

    face_detector = cv2.CascadeClassifier(cascade_path)

    if face_detector.empty():
        print("ERROR: Could not load face detection model.")
        camera.release()
        return

    window_name = "MusicAI - Webcam Test"

    print("Webcam test started.")
    print("Keep the webcam window open.")
    print("Click the webcam window and press Q to exit.")

    try:
        while True:
            success, frame = camera.read()

            if not success or frame is None:
                print("WARNING: No webcam frame received. Retrying...")
                cv2.waitKey(100)
                continue

            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = face_detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(60, 60)
            )

            for (x, y, width, height) in faces:
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + width, y + height),
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    "Face detected",
                    (x, max(y - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

            cv2.putText(
                frame,
                f"Faces detected: {len(faces)}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "Press Q to quit",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            cv2.imshow(window_name, frame)

            # Process window events and read the pressed key.
            key = cv2.waitKey(30) & 0xFF

            if key == ord("q"):
                print("Q pressed. Closing webcam...")
                break

            # Exit if the user manually closes the OpenCV window.
            if cv2.getWindowProperty(
                window_name,
                cv2.WND_PROP_VISIBLE
            ) < 1:
                print("Webcam window closed.")
                break

    except KeyboardInterrupt:
        print("\nWebcam stopped by user.")

    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("Webcam released. Test finished.")


if __name__ == "__main__":
    main()