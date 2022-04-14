import json
import math
import random
import threading
import time
import tkinter as tk
from tkinter import Canvas, Frame, BOTH
import paho.mqtt.client as mqtt


def onMessage(client, userdata, message):
    str_msj: str = message.payload.decode('utf-8')
    message = json.loads(str_msj)


class SensorSimulator:

    def __init__(self, max_in=3720, min_in=3610, size_in=10, period=10):
        self.max = max_in
        self.min = min_in
        self.size = size_in
        self.size2 = size_in
        self.base = ((self.max - self.min) / 2) + self.min
        self.delta = (self.max - self.min) / 100
        self.value = {'base': self.base,  # mean
                      'delta': 0.5,  # Delta
                      'period': period}  # Period
        self.signal = self.generateSignal()

    # Private Method for random values generation
    def __randomGenerator(self):
        return random.uniform(0, 1)

    # Class property for random scaled number based on min and max input
    @property
    def randomGen(self):
        return (self.max - self.min) * self.__randomGenerator() + self.min

    # Method for general normalization of a list
    @staticmethod
    def normalize(list1):
        n_list = [(_ - min(list1)) / (max(list1) - min(list1)) for _ in list1]
        return n_list

    # Method for Sin function generation
    def sin_signal(self):
        return (self.max - self.min) * math.sin(2 * math.pi * self.__randomGenerator() * 360) + self.min

    # Method for random function generation
    def ran_signal(self) -> float:
        self.value['period'] -= 1
        if self.value['period'] == 0:
            self.value['period'] = random.randint(2, 10)
            self.value['delta'] *= -1  # flip the incrementer
        self.value['base'] += self.value['delta']
        return self.value['base']

    # Main method for summation of the three signals, normalization, scaling and list of values generation
    def generateSignal(self):
        sin = [self.sin_signal() for _ in range(self.size)]
        noise = [self.randomGen for _ in range(self.size)]
        saw_tooth = [self.ran_signal() for _ in range(self.size)]
        norm = self.normalize(list((i + j + k) for (i, j, k) in zip(noise, saw_tooth, sin)))
        output = [_ * (self.max - self.min) + self.min for _ in norm]
        return output

    def generateNextValue(self):
        sin = self.sin_signal()
        noise = self.randomGen
        saw_tooth = self.ran_signal()
        norm = (sin + noise + saw_tooth) / 3
        if max(self.signal) - min(self.signal) != 0:
            norm = (norm - min(self.signal)) / (max(self.signal) - min(self.signal))
        else:
            norm = norm - min(self.signal)
        output = norm * (self.max - self.min) + self.min
        return output

    def set_next_frame(self):
        self.signal.append(self.generateNextValue())
        self.signal.pop(0)


class DynamicDisplay(Frame):
    entryValue = 0
    height = 3900

    def __init__(self):
        super().__init__()
        self.sensor = SensorSimulator()
        self.initUI()
        self.update()

    def initUI(self):
        self.master.title('Dynamic Display - Oscar Gonzalez 301185878')
        self.pack(fill=BOTH, expand=1)
        canvas = Canvas(self)

        def startBtn():
            start = threading.Thread(target=changeValue())
            start.setDaemon(True)

        def changeValue():
            for i in range(500):
                point1 = self.height - self.sensor.signal[0]
                point2 = self.height - self.sensor.signal[1]
                point3 = self.height - self.sensor.signal[2]
                point4 = self.height - self.sensor.signal[3]
                point5 = self.height - self.sensor.signal[4]
                point6 = self.height - self.sensor.signal[5]
                point7 = self.height - self.sensor.signal[6]
                point8 = self.height - self.sensor.signal[7]
                point9 = self.height - self.sensor.signal[8]
                point10 = self.height - self.sensor.signal[9]

                print(point1, point2, point3, point4, point5, point6, point7, point8, point9, point10)

                canvas.coords(line1, 100, point2, 50, point1)
                canvas.coords(line2, 150, point3, 100, point2)
                canvas.coords(line3, 200, point4, 150, point3)
                canvas.coords(line4, 250, point5, 200, point4)
                canvas.coords(line5, 300, point6, 250, point5)
                canvas.coords(line6, 350, point7, 300, point6)
                canvas.coords(line7, 400, point8, 350, point7)
                canvas.coords(line8, 450, point9, 400, point8)
                canvas.coords(line9, 500, point10, 450, point9)

                time.sleep(0.5)
                self.sensor.set_next_frame()
                print('Loop #{}'.format(i))

                root.update()

        button1 = tk.Button(text='Simulate', width=10, command=lambda: startBtn())
        canvas.create_window(300, 440, window=button1)

        line1 = canvas.create_line(100, 0, 50, 0, fill="#f50", dash=(4, 2))
        line2 = canvas.create_line(150, 0, 100, 0, fill="#f50", dash=(4, 2))
        line3 = canvas.create_line(200, 0, 150, 0, fill="#f50", dash=(4, 2))
        line4 = canvas.create_line(250, 0, 200, 0, fill="#f50", dash=(4, 2))
        line5 = canvas.create_line(300, 0, 250, 0, fill="#f50", dash=(4, 2))
        line6 = canvas.create_line(350, 0, 300, 0, fill="#f50", dash=(4, 2))
        line7 = canvas.create_line(400, 0, 350, 0, fill="#f50", dash=(4, 2))
        line8 = canvas.create_line(450, 0, 400, 0, fill="#f50", dash=(4, 2))
        line9 = canvas.create_line(500, 0, 450, 0, fill="#f50", dash=(4, 2))

        # Creating the frame
        canvas.create_line(50, 80, 50, 400, fill="black")
        canvas.create_line(30, 380, 530, 380, fill="black")
        canvas.create_line(45, 290, 55, 290, fill="black")
        canvas.create_line(45, 180, 55, 180, fill="black")
        canvas.pack(fill=BOTH, expand=1)


if __name__ == '__main__':
    client_name = 'sens_sub'
    broker = 'mqtt.eclipseprojects.io'

    client = mqtt.Client(client_name)
    client.connect(broker)

    print('Subscription in process')
    client.subscribe('group1')
    client.on_message = onMessage
    time.sleep(2)

    client.loop_forever()

    # root = tk.Tk()
    # ex = DynamicDisplay()
    # root.geometry('650x500+0+0')
    # root.mainloop()
