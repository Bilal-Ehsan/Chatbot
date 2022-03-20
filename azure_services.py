import os

from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from colorama import Fore
from msrest.authentication import ApiKeyCredentials

import bot


project_id = 'cd1354f5-ce8c-4217-808d-17ccf2ac8acc'
cv_endpoint = 'https://customvisioncw-prediction.cognitiveservices.azure.com/'

model_name = 'weapons'


def custom_vision():
    image_path = os.path.join('temp', 'gauntlet_1.jpg')

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
