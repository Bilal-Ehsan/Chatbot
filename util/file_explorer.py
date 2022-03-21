from tkinter import *
from tkinter import ttk

from azure_services import custom_vision, image_analysis, face_analysis
from image_classification import classify_image


def image_browser(func):
    win = Tk()
    win.geometry('700x350')

    label = Label(
        win,
        text='Click on the button below to browse for your image! (Close me when complete)',
        font=('Arial', 12), 
        wraplength=500
    )

    label.pack(pady=75)

    if func == 'classify_image':
        ttk.Button(win, text='Browse', command=classify_image, cursor='hand2').pack()
    elif func == 'custom_vision':
        ttk.Button(win, text='Browse', command=custom_vision, cursor='hand2').pack()
    elif func == 'image_analysis':
        ttk.Button(win, text='Browse', command=image_analysis, cursor='hand2').pack()
    elif func == 'face_analysis':
        ttk.Button(win, text='Browse', command=face_analysis, cursor='hand2').pack()

    win.mainloop()
