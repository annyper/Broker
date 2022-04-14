import matplotlib.pyplot as plt
import random
import tkinter as tk
from tkinter import messagebox
from tkinter import *
from tkinter.ttk import *
import threading, time
from threading import Timer
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class DataGenerator:
    __base_bottom: float
    __base_top: float
    __delta: float
    __cycle: float
    __x: float
    __next_i: float
    __type_graph: str

    def __init__(self, type_graph, base_line_bottom: float = 0, base_line_top: float = 1,
                 delta: float = 6):
        self.__type_graph = type_graph
        if self.__type_graph.casefold() == 'Sound'.casefold():
            base_line_bottom = abs(base_line_bottom)
            base_line_top = abs(base_line_top)
        if base_line_bottom < base_line_top:
            self.__base_bottom = base_line_bottom
            self.__base_top = base_line_top
        else:
            self.__base_bottom = base_line_top
            self.__base_top = base_line_bottom
        self.__delta = delta
        self.__cycle = random.uniform(0, 2 * abs(self.__base_top - self.__base_bottom))
        self.__x = (self.__base_top + self.__base_bottom) / 2
        self.__direction = 1

    def random(self) -> float:
        if self.__type_graph.casefold() == 'Humidity'.casefold():
            return self.__random_h()
        if self.__type_graph.casefold() == 'Temperature'.casefold():
            return self.__random_t()
        if self.__type_graph.casefold() == 'Sound'.casefold():
            return self.__random_s()
        return 0

    def __random_s(self) -> float:
        self.__next_inc()
        if abs(self.__x) < self.__base_bottom \
                or abs(self.__x) > self.__base_top:
            self.__direction *= -1
            self.__next_inc()
        if self.__direction < 0:
            if self.__x < 0:
                self.__x += self.__next_i * self.__delta
            else:
                self.__x -= self.__next_i * self.__delta
        else:
            if self.__x < 0:
                self.__x -= self.__next_i * self.__delta
            else:
                self.__x += self.__next_i * self.__delta
        self.__x *= -1
        return self.__x

    def __random_t(self) -> float:
        self.__next_inc()
        while self.__x + self.__next_i < self.__base_bottom \
                or self.__x + self.__next_i > self.__base_top:
            self.__cycle = random.uniform(abs(self.__base_top - self.__base_bottom) / 2,
                                          abs(self.__base_top - self.__base_bottom))
            self.__direction *= -1
            self.__next_inc()
        self.__cycle -= self.__delta
        self.__x += self.__next_i
        return self.__x

    def __random_h(self) -> float:
        self.__next_inc()
        while self.__cycle <= 0 \
                or self.__x + self.__next_i < self.__base_bottom \
                or self.__x + self.__next_i > self.__base_top:
            self.__cycle = random.uniform(0, 2 * abs(self.__base_top - self.__base_bottom))
            self.__direction *= -1
            self.__next_inc()
        self.__cycle -= self.__delta
        self.__x += self.__next_i
        return self.__x

    def __normalized_value(self) -> float:
        if abs(self.__base_top - self.__base_bottom) <= 1:
            return random.random() / 100
        if abs(self.__base_top - self.__base_bottom) <= 10:
            return random.random() / 10
        if abs(self.__base_top - self.__base_bottom) >= 100:
            return random.random() * 10
        return random.random()

    def __next_inc(self):
        self.__next_i = self.__normalized_value() * (-1) ** random.randint(1, 2)
        if self.__direction < 0:
            if self.__next_i > 0:
                next_inc = self.__next_i / 4
        else:
            if self.__next_i < 0:
                next_inc = self.__next_i / 4

class Ana(tk.Tk):
    __fig: Figure
    __y: []

    def __init__(self):
        self.__dg = DataGenerator('humidity', 0, 0.5, 0.01)
        self.__t_hsensor = None
        self.__t_ssensor = None
        self.__fig = Figure(figsize=(5, 5), dpi=100)
        self.__y = [0]
        self.__plot = self.__fig.add_subplot(111)
        self.__plot.plot(self.__y)
        super().__init__()
        self.minsize(500, 350)
        self.title('Centennial College')
        self.columnconfigure(0, minsize='500')
        self.grid_rowconfigure(0, weight=1, minsize='350')
        self.grid_columnconfigure(0, weight=1)

        frame = Frame(self)
        self.set_frame(frame)
        frame.grid(column=0, row=0, sticky=NSEW)

    def set_frame(self, frame):
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        n_rows = 3
        n_columns = 2
        for i in range(n_rows):
            frame.grid_rowconfigure(i, weight=1)
        for i in range(n_columns):
            frame.grid_columnconfigure(i, weight=1)
        Label(frame, text='Sensor simulator',
              font='Calibri 20 bold italic',
              ).grid(column=0, row=0, columnspan=3, sticky=tk.N,
                     padx=5, pady=5)
        self.__canvas = FigureCanvasTkAgg(self.__fig, master=frame)  # A tk.DrawingArea.
        self.__canvas.draw()

        self.__canvas.get_tk_widget().grid(column=0, row=1, columnspan=3, sticky=tk.NSEW,
                                           padx=5, pady=5)
        Button(frame, text='Humidity sensor', command=self.hsensor
               ).grid(column=0, row=3, sticky=tk.NSEW, padx=5, pady=5)
        Button(frame, text='Sound sensor', command=self.ssensor
               ).grid(column=1, row=3, sticky=tk.NSEW, padx=5, pady=5)
        Button(frame, text='Exit', command=self.exit
               ).grid(column=2, row=3, sticky=tk.NSEW, padx=5, pady=5)

    def hsensor(self):
        if self.__t_ssensor is not None:
            self.__t_ssensor.cancel()
        if self.__t_hsensor is not None:
            self.__t_hsensor.cancel()
        self.__y.clear()
        self.__plot.clear()
        self.__dg = DataGenerator('humidity', 0, 0.5, 0.01)
        self.__t_hsensor = threading.Timer(0.5, self.hsensor_run)
        self.__t_hsensor.daemon = True
        self.__t_hsensor.start()

    def hsensor_run(self):
        self.__y.append(self.__dg.random())
        self.__plot.plot(self.__y, 'r')
        self.__canvas.draw()
        self.__t_hsensor = threading.Timer(0.5, self.hsensor_run)
        self.__t_hsensor.start()


    def ssensor(self):
        if self.__t_hsensor is not None:
            self.__t_hsensor.cancel()
        if self.__t_ssensor is not None:
            self.__t_ssensor.cancel()
        self.__y.clear()
        self.__plot.clear()
        self.__dg = DataGenerator('Sound', 0, 1, 6)
        self.__t_ssensor = threading.Timer(0.5, self.ssensor_run)
        self.__t_ssensor.daemon = True
        self.__t_ssensor.start()

    def ssensor_run(self):
        self.__y.append(self.__dg.random())
        self.__plot.plot(self.__y, 'g')
        self.__canvas.draw()
        self.__t_ssensor = threading.Timer(0.5, self.ssensor_run)
        self.__t_ssensor.start()

    def exit(self):
        if self.__t_ssensor is not None:
            self.__t_ssensor.cancel()
        if self.__t_hsensor is not None:
            self.__t_hsensor.cancel()
        self.quit()
        self.destroy()

    def show(self):
        self.mainloop()

ana = Ana()
ana.show()