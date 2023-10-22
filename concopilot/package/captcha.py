# -*- coding: utf-8 -*-

import requests
import base64
import tkinter as tk

from typing import Callable


def request_captcha(session: requests.Session, captcha_url):
    response=session.get(captcha_url)
    return tk.PhotoImage(data=base64.encodebytes(response.content))


def get_request_fn(session: requests.Session, captcha_url):
    return lambda : request_captcha(session, captcha_url)


class CaptchaClient:
    def __init__(
        self,
            request_fn: Callable[[], tk.PhotoImage],
            width=240,
            height=160,
            captcha_width=48,
            captcha_height=20,
            button_width=60
    ):
        self.request_fn=request_fn

        captcha_x=captcha_width
        captcha_y=int(height/2-1.5*captcha_height)

        self.root=tk.Tk()
        self.root.title('Captcha')
        self.root.minsize(width, height)
        self.root.maxsize(width, height)
        self.captcha_img_widget=tk.Label(self.root)
        self.captcha_img_widget.bind('<Button-1>', lambda event : self.refresh_captcha())
        self.captcha_img_widget.place(x=captcha_x, y=captcha_y)

        self.captcha_text_widget=tk.Text(self.root, borderwidth=0)
        self.captcha_text_widget.bind('<Return>', lambda event : self.on_submit())
        self.captcha_text_widget.place(x=captcha_x+captcha_width+8, y=captcha_y+2, height=captcha_height, width=width-captcha_width-2*captcha_x-8)

        self.button=tk.Button(self.root, text='Submit', command=self.on_submit)
        self.button.place(x=(width-button_width)/2, y=int(height/2+0.5*captcha_height), height=captcha_height, width=button_width)

        self.captcha_text=''

        self.refresh_captcha()

    def refresh_captcha(self):
        img=self.request_fn()
        self.captcha_img_widget.configure(image=img)
        self.captcha_img_widget.image=img

    def on_submit(self):
        self.captcha_text=self.captcha_text_widget.get('1.0', 'end-1c')
        self.root.destroy()

    def open(self):
        self.root.mainloop()
