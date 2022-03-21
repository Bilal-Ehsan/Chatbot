import os

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.face import FaceClient
from colorama import Fore
from msrest.authentication import ApiKeyCredentials
from msrest.authentication import CognitiveServicesCredentials
from tkinter import filedialog

from azure.faces import show_similar_faces
from azure.vision import show_image_analysis
import bot


project_id = 'cd1354f5-ce8c-4217-808d-17ccf2ac8acc'
cv_endpoint = 'https://customvisioncw-prediction.cognitiveservices.azure.com/'

cog_endpoint = 'https://image-analysis-bilal.cognitiveservices.azure.com/'

model_name = 'weapons'


def custom_vision():
    file = filedialog.askopenfile(mode='r', filetypes=[('image files', '.jpg .jpeg .png')])
    image_path = os.path.abspath(file.name)

    # Create an instance of the prediction service
    credentials = ApiKeyCredentials(in_headers={'Prediction-key': os.getenv("CV_KEY")})
    custom_vision_client = CustomVisionPredictionClient(endpoint=cv_endpoint, credentials=credentials)

    # Open the image, and use the custom vision model to classify it
    image_contents = open(image_path, 'rb')
    classification = custom_vision_client.classify_image(project_id, model_name, image_contents.read())

    # The results include a prediction for each tag, in descending order of probability - get the first one
    prediction = classification.predictions[0].tag_name

    if prediction == 'shield':
        print(Fore.LIGHTMAGENTA_EX + 'That\'s Captain America\'s shield!\n')
        bot.speak('That\'s Captain America\'s shield!')
    elif prediction == 'mjolnir':
        print(Fore.LIGHTMAGENTA_EX + 'That\'s Thor\'s hammer!\n')
        bot.speak('That\'s Thor\'s hammer!')
    else:
        print(Fore.LIGHTMAGENTA_EX + 'That\'s Thanos\' gauntlet!\n')
        bot.speak('That\'s Thanos\' gauntlet!')


def image_analysis():
    file = filedialog.askopenfile(mode='r', filetypes=[('image files', '.jpg .jpeg .png')])
    image_path = os.path.abspath(file.name)

    # Specify the features we want to analyze
    features = ['description', 'tags', 'adult', 'objects', 'faces']

    # Get a client for the computer vision service
    computervision_client = ComputerVisionClient(cog_endpoint, CognitiveServicesCredentials(os.getenv("COG_KEY")))

    # Get an analysis from the computer vision service
    image_stream = open(image_path, 'rb')
    analysis = computervision_client.analyze_image_in_stream(image_stream, visual_features=features)

    show_image_analysis(image_path, analysis)


def face_analysis():
    # Create a face detection client
    face_client = FaceClient(cog_endpoint, CognitiveServicesCredentials(os.getenv("COG_KEY")))

    # Get the ID of the first face in image 1
    file = filedialog.askopenfile(mode='r', filetypes=[('image files', '.jpg .jpeg .png')])
    image_one_path = os.path.abspath(file.name)
    image_one_stream = open(image_one_path, 'rb')
    image_one_faces = face_client.face.detect_with_stream(image=image_one_stream)
    face_one = image_one_faces[0]

    # Get the face IDs in a second image
    file = filedialog.askopenfile(mode='r', filetypes=[('image files', '.jpg .jpeg .png')])
    image_two_path = os.path.abspath(file.name)
    image_two_stream = open(image_two_path, 'rb')
    image_two_faces = face_client.face.detect_with_stream(image=image_two_stream)
    image_two_face_ids = list(map(lambda face: face.face_id, image_two_faces))

    # Find faces in image 2 that are similar to the one in image 1
    similar_faces = face_client.face.find_similar(face_id=face_one.face_id, face_ids=image_two_face_ids)

    # Show the face in image 1, and similar faces in image 2
    show_similar_faces(image_one_path, face_one, image_two_path, image_two_faces, similar_faces)
