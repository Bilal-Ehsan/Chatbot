import os

from colorama import Fore
from keras.models import load_model
from keras.preprocessing import image
import numpy as np
from tkinter import filedialog

import bot


model = load_model('model.h5')


def classify_image():
    file = filedialog.askopenfile(mode='r', filetypes=[('image files', '.jpg .jpeg .png')])
    image_path = os.path.abspath(file.name)
        
    test_image = image.load_img(image_path, target_size=(224, 224))
    test_image = image.img_to_array(test_image)
    test_image = np.expand_dims(test_image, axis=0)

    prediction = model.predict(test_image)
    
    if prediction[0][0] > prediction[0][1]:
        print(Fore.LIGHTMAGENTA_EX + 'That\'s an image of Batman!\n')
        bot.speak('That\'s an image of Batman!')
    else:
        print(Fore.LIGHTMAGENTA_EX + 'That\'s an image of Superman!\n')
        bot.speak('That\'s an image of Superman!')
