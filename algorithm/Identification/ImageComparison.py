import cv2
import face_recognition

def identify_faces(card_image_path, profile_image_path):
    card_image = face_recognition.load_image_file(card_image_path)
    profile_image = face_recognition.load_image_file(profile_image_path)

    card_face_locations = face_recognition.face_locations(card_image)
    profile_face_locations = face_recognition.face_locations(profile_image)

    if len(card_face_locations) == 0:
        similarity_percentage = 0
        message = "No face found in the card image."
    else:
        card_face_encoding = face_recognition.face_encodings(card_image)[0]
        profile_face_encoding = face_recognition.face_encodings(profile_image)[0]

        face_distance = face_recognition.face_distance([card_face_encoding], profile_face_encoding)
        similarity_percentage = (1 - face_distance[0]) * 100

        if similarity_percentage >= 55:
            message = "Congratulations! You have completed the identification process."
        else:
            message = "Sorry. Please try again."

    return "{:.2f}".format(similarity_percentage), message