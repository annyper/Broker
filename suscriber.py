import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import paho.mqtt.client as mqtt
import json


class Suscriber(tk.Tk):
    __fig: Figure
    __y: []

    def __init__(self, client_name, broker, suscribe_to, plot_data):
        self.__client = mqtt.Client(client_name)
        self.__client.connect(broker)
        self.__plot_data = plot_data
        print('Subscription in process')
        self.__client.subscribe(suscribe_to)
        self.__fig = Figure(figsize=(5, 5), dpi=100)
        self.__y = [0]
        self.__plot = self.__fig.add_subplot(111)
        self.__plot.plot(self.__y)
        super().__init__()
        self.minsize(500, 350)
        self.title('Centennial College')
        self.columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        frame = Frame(self)
        self.set_frame(frame)
        frame.grid(column=0, row=0, sticky=NSEW)

    def set_frame(self, frame):
        n_columns = 3
        frame.grid_rowconfigure(1, weight=1)
        for i in range(n_columns):
            frame.columnconfigure(i, weight=1)
            frame.grid_columnconfigure(i, weight=1)
        Label(frame, text='Suscriber MQTT',
              font='Calibri 20 bold italic',
              ).grid(column=0, row=0, columnspan=3, sticky=tk.N,
                     padx=5, pady=5)
        self.__canvas = FigureCanvasTkAgg(self.__fig, master=frame)  # A tk.DrawingArea.
        self.__canvas.draw()

        self.__canvas.get_tk_widget().grid(column=0, row=1, columnspan=3, sticky=tk.NSEW,
                                           padx=5, pady=5)

        Button(frame, text='Exit', command=self.exit
               ).grid(column=2, row=3, sticky=tk.NSEW, padx=5, pady=5)

    def onMessage(self, client, userdata, message):
        str_msj: str = message.payload.decode('utf-8')
        message = json.loads(str_msj)
        print(message)
        self.__y.append(message[self.__plot_data])
        self.__plot.plot(self.__y, 'g')
        self.__canvas.draw()

    def exit(self):
        self.__client.disconnect()
        self.quit()
        self.destroy()

    def show(self):
        print('On Message designation')
        self.__client.on_message = self.onMessage
        self.__client.loop_start()
        self.mainloop()


client_name = 'sens_sub'
broker = 'mqtt.eclipseprojects.io'
suscribe_to = 'studentdata'
plot_data = 'beats'
# [{beats:98, timestamp:2022-04-15T07:40:2....}]
sus = Suscriber(client_name, broker, suscribe_to, plot_data)
sus.show()
