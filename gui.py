from client import Client
from tkinter import messagebox
from tkinter import *
from typing import Any, Optional
import asyncio, os, keys, webbrowser
MAIN_TITLE = 'DisneyClient'
loop = asyncio.get_event_loop()
client = Client(loop=loop)

class App(Frame):

    def __init__(self, master=None, loop=None):
        super().__init__(master)
        self.master = master
        self.master.protocol('WM_DELETE_WINDOW', self.close)
        self.loop = loop or asyncio.get_event_loop()
        self.is_next_frame = False
        self.grid()
        self.create_widgets()
        self.updater_task = self.loop.create_task(self.updater())

    def create_widgets(self):
        if not self.is_next_frame:
            self.main_frame = Frame(self)
            self.main_frame.grid()
            self.key_label = Label((self.main_frame), text='Enter your key')
            self.key_label.grid(row=0, column=0, pady=5)
            self.key_text = StringVar()
            self.key_entry = Entry((self.main_frame), textvariable=(self.key_text))
            self.key_entry.grid(row=1, column=0)
            self.key_entry.bind('<Return>', self.connect)
            self.connect_button = Button((self.main_frame), text='Connect', command=(self.connect),
              height=5,
              width=19)
            self.connect_button.grid(row=2, column=0, pady=5)
            self.bottom_text = StringVar()
            self.bottom_text.set('v' + keys.client_version)
            self.bottom_label = Label((self.main_frame), textvariable=(self.bottom_text))
            self.bottom_label.grid(row=3, column=0)
        else:
            self.main_frame.destroy()
            self.master.geometry('344x194')
            self.next_frame = Frame(self)
            self.next_frame.grid()
            self.log_text = Text((self.next_frame), height=12, width=24)
            self.log_text.grid(row=0, column=0, padx=5, pady=5, sticky=NW)
            self.check_btn_var = IntVar(value=1)
            self.check_btn = Checkbutton((self.next_frame), text='Close program after update', variable=(self.check_btn_var))
            self.check_btn.grid(row=0, column=1, pady=5, sticky=NW)
            self.check_btn_var2 = IntVar(value=1)
            self.check_btn2 = Checkbutton((self.next_frame), text='Open game after update', variable=(self.check_btn_var2))
            self.check_btn2.grid(row=0, column=1, pady=25, sticky=NW)
            self.check_btn_var3 = IntVar(value=0)
            self.check_btn3 = Checkbutton((self.next_frame), text='Run program continuously', variable=(self.check_btn_var3))
            self.check_btn3.grid(row=0, column=1, pady=45, sticky=NW)
            self.update_button = Button((self.next_frame), text='Update', command=(self.start_client),
              height=5,
              width=19)
            self.update_button.grid(row=0, column=1, padx=20, pady=75, sticky=NW)

    def connect(self, event=None):
        keys.client_vip_id = self.key_text.get()
        self.connect_button['state'] = DISABLED
        self.focus()
        self.bottom_text.set('Connecting...')
        self.loop.create_task(client.connect())

    def start_client(self):
        self.update_button['state'] = DISABLED
        self.update_log_text(clear=True)
        self.loop.create_task(client.parse_data())

    def show_info(self, text: str, mode: str='warning', url: str='', destroy: bool=False, reset_btn: bool=True):
        if mode == 'askupdate':
            message = messagebox.askyesno(MAIN_TITLE, text)
            if message and url:
                webbrowser.open(url)
        elif mode == 'warning':
            message = messagebox.showwarning(MAIN_TITLE, text)
        else:
            if mode == 'error':
                message = messagebox.showerror(MAIN_TITLE, text)
        if destroy:
            self.close()
        if reset_btn:
            self.connect_button['state'] = NORMAL
            self.bottom_text.set('v' + keys.client_version)

    def update_log_text(self, text: str='', clear: bool=False):
        self.log_text.config(state=NORMAL)
        if not clear:
            self.log_text.insert(END, text + '\n')
        else:
            self.log_text.delete(1.0, END)
        self.log_text.config(state=DISABLED)

    async def updater(self):
        while True:
            self.master.update()
            await asyncio.sleep(0.008333333333333333)

    def close(self):
        if client.parser_task is not None:
            client.parser_task.cancel()
        self.updater_task.cancel()
        self.loop.stop()
        self.destroy()


root = Tk()
root.title(MAIN_TITLE)
root.geometry('150x150')
root.resizable(False, False)
root.columnconfigure(0, weight=1)
app = App(master=root, loop=loop)
loop.run_forever()
loop.close()