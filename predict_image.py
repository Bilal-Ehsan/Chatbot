import os

from colorama import Fore
from keras.models import load_model
from keras.preprocessing import image
import numpy as np
from tkinter import *
from tkinter import ttk, filedialog

import bot


model = load_model('model.h5')


def predict_image():
    file = filedialog.askopenfile(mode='r', filetypes=[('image files', '.jpg .png')])

    if file:
        file_path = os.path.abspath(file.name)
        
        test_image = image.load_img(file_path, target_size=(224, 224))
        test_image = image.img_to_array(test_image)
        test_image = np.expand_dims(test_image, axis=0)

        prediction = model.predict(test_image)
        
        if prediction[0][0] > prediction[0][1]:
            print(Fore.LIGHTMAGENTA_EX + 'That\'s an image of Batman!\n')
            bot.speak('That\'s an image of Batman!')
        else:
            print(Fore.LIGHTMAGENTA_EX + 'That\'s an image of Superman!\n')
            bot.speak('That\'s an image of Superman!')


def image_browser():
    win = Tk()
    win.geometry('700x350')

    label = Label(
        win,
        text='Click on the button below to browse for your image! (Close me when complete)',
        font=('Arial', 13), 
        wraplength=500
    )

    label.pack(pady=75)
    ttk.Button(win, text='Browse', command=predict_image, cursor='hand2').pack()

    win.mainloop()
