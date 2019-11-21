import copy
import datetime
import tkinter as tk
from tkinter import E, N, S, W

import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class CommandButtons(tk.Frame):
    """ TKinter frame with two clickable buttons

    The buttons trigger a Serial write to the gateway they are linked to

    Parameters
    ----------
    parent : TKinter Frame
        parent frame
    gateway : Gateway instance
        Gateway to send commands to

    """

    def __init__(self, parent, gateway, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.gateway = gateway

        self.button_A = tk.Button(self, text="Send 'A'",
                                  command=lambda: self.gateway.send_command('A'))
        self.button_B = tk.Button(self, text="Send 'B'",
                                  command=lambda: self.gateway.send_command('B'))

        self.button_A.grid(row=1, column=1)
        self.button_B.grid(row=1, column=2)

        self.____update_buttons()

    def ____update_buttons(self):
        """ Set the buttons inactive when the gateway is not ready

        """
        if self.gateway.serial.is_ready:
            self.button_A.config(state=tk.NORMAL)
            self.button_B.config(state=tk.NORMAL)
        else:
            self.button_A.config(state=tk.DISABLED)
            self.button_B.config(state=tk.DISABLED)
        # Call this function again after 100 ms
        self.parent.after(100, self.____update_buttons)


class GatewayStatus(tk.Frame):
    """ TKinter frame to monitor the status of the Serial link

    Reading from the Serial link is started in a separate thread with Threading and
    stopped on the destruction of this frame

    Parameters
    ----------
    parent : TKinter Frame
        parent frame
    gateway : Gateway instance
        Gateway to monitor
    field : GS or TM/FPV
    """

    def __init__(self, parent, gateway, field, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.gateway = gateway
        self.field = field

        # Name to separate the buttons
        tk.Label(self,text=self.field).grid(row=0,column=0)
        # Button to open/close the Serial link
        self.button_var = tk.StringVar()
        self.read_button = tk.Button(self, textvariable=self.button_var)
        self.read_button.grid(row=1, column=0)
        # Label to display the gateway's port name
        self.port_var = tk.StringVar()
        self.port_var.set("Port : {}".format(
            self.gateway.serial.ser.port))
        tk.Label(self, textvariable=self.port_var).grid(
            row=0, column=1, sticky=W)
        # Label to display the error status
        self.error_var = tk.StringVar()
        self.error_var.set("")
        tk.Label(self, textvariable=self.error_var).grid(
            row=1, column=1, sticky=W+E)

        self.__update_port()
        self.__update_error()
        self.__update_button()

    def destroy(self):
        """" Catch the destruction of the widget and stop the Serial reading

        If this is not done properly the Threading thread that reads data from
        the Serial link cannot be stopped

        """
        self.gateway.stop_read()
        tk.Frame.destroy(self)

    def __update_port(self):
        """ Update the port name displayed

        """
        self.port_var.set("Port : {}".format(
            self.gateway.serial.ser.port))
        # Call this function again after 100 ms
        self.parent.after(100, self.__update_port)

    def __update_error(self):
        """ Update the error displayed

        """
        failed = self.gateway.serial.failed
        if failed:
            message = self.gateway.serial.error
            self.error_var.set("Status : {}".format(message))
        else:
            self.error_var.set("Status : Ok")
        # Call this function again after 100 ms
        self.parent.after(100, self.__update_error)

    def __update_button(self):
        """ Set the behaviour of the button to open or close the Serial link

        """
        if self.gateway.serial.get_status():
            self.button_var.set("Close link")
            if self.field == "GS":
                self.read_button.config(command=self.gateway.stop_read)
            elif self.field == "TM/FPS":
                self.read_button.config(command=self.gateway.send_command("Close Tx"))
            else:
                print("Change name of field for button")
        else:
            self.button_var.set("Open link")
            if self.field == "GS":
                self.read_button.config(command=self.gateway.start_read)
            elif self.field == "TM/FPS":
                self.read_button.config(command=self.gateway.send_command("Open Tx"))
            else:
                print("Change name of field for button")
        # Call this function again after 100 ms
        self.parent.after(100, self.__update_button)


class LiveTimeGraph(tk.Frame):
    """ TKinter frame that holds a matplotlib graph that is frequently updated

    The graph is plotted against time. The sensor must have a data.time attribute.

    Parameters
    ----------
    parent : TKinter Frame
        parent frame
    gateway : Gateway instance
        Gateway to monitor
    sensor : attribute of a Sensors instance
        sensor to display data from
    field : str
        name of the data field to display

    """
    def __init__(self, parent, gateway, sensor, field, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.gateway = gateway
        self.sensor = sensor
        self.field = field

        self.fig = Figure(figsize=(4, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.grid()
        #self.fig.set_label(self.field)
        #self.fig.tight_layout()
        self.time = []
        self.data = []

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1, column=1)

        ani = animation.FuncAnimation(self.fig, self.__update_data, blit=True, interval=10,
                                      repeat=False, init_func=self.__init_figure)

    def __init_figure(self):
        """ Set the initial values and settings of the figure

        """
        self.ax.set_ylim(0, 50)
        self.ax.set_xlim(0, 10)
        del self.time[:]
        del self.data[:]
        self.line.set_data(self.time, self.data)
        return self.line,

    def __update_data(self, data):
        """ Refresh the figure content

        Parameters
        ----------
        data : unused
            default parameter given by animation.FuncAnimation
        
        Returns
        -------
        tupple
            content of the figure for matplotlib        

        """
        tmin, tmax = self.ax.get_xlim()

        self.time = self.sensor.raw_data['Seconds_since_start']
        self.data = self.sensor.raw_data[self.field]

        if self.time:
            if max(self.time) > tmax:
                self.ax.set_xlim(tmin, 2*tmax)
                self.canvas.draw()

        self.line.set_data(self.time, self.data)

        return self.line,


class SensorIndicator(tk.Frame):
    """ TKinter frame that holds a TKinter square of color and a label for sensor.name

    The box changes color depending on status of sensor. The sensor must have a self.status attribute.

    Parameters
    ----------
    parent : TKinter Frame
        parent frame
    gateway : Gateway instance
        Gateway to monitor
    sensor : attribute of a Sensors instance
        sensor to display status from
    field : str
        name of the sensor to display

    """

    def __init__(self, parent, gateway, sensor, field, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.gateway = gateway
        self.sensor = sensor
        self.field = field

        # Button to make a colored "box" for sensor
        # Style will be reflected on this button
        self.btn = tk.Button(self, text='')
        # self.btn = tk.Button(self)
        self.btn.grid(row=0, column=1)
        # Label to display the gateway's port name
        self.label = tk.Label(self, text=self.field)
        self.label.grid(
            row=0, column=2, padx=5)

        self.__update_button()

    def __update_button(self):
        """ Set the style of the button depending on the status of sensor.

        """
        if self.sensor.data[self.field] is None:
            self.btn.config(bg='grey', state=tk.DISABLED, width=1)
        else:
            if self.sensor.data[self.field]:
                self.btn.config(bg='red', height=1, state=tk.DISABLED, width=1)
            else:
                self.btn.config(bg='green', height=1, state=tk.DISABLED, width=1)
            # Call this function again after 100 ms
        self.parent.after(100, self.__update_button)


class GeneralData(tk.Frame):
    """ TKinter frame that holds a label and displays changeable string

        The label is the name of measured value. The int/scalar shows the value for the value.

        Parameters
        ----------
        parent : TKinter Frame
            parent frame
        gateway : Gateway instance
            Gateway to monitor
        data(sensor?) : data from functions calculating or directly from the TM.
            data to display value from
        field : str
            name of the data to display

    """
    def __init__(self, parent, gateway, data, field, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.gateway = gateway
        self.data = data
        self.field = field

        self.label = tk.Label(self, text=self.field + ": ")
        self.label.grid(row=0, column=1)
        self.data_var = tk.StringVar()
        self.show_data = tk.Label(self, text=self.data_var)
        self.show_data.grid(row=0, column=2)

        self.__update_value()

    def __update_value(self):
        if self.field == "Battery":
            self.data_var.set(self.gateway.data) # This has to be changed to point to battery value.
        elif self.field == "|V|":
            self.data_var.set(self.gateway.data)  # This has to be changed to point to calculated |V|.
        elif self.field == "Longitude":
            self.data_var.set(self.gateway.data)  # This has to be changed to point to longitude value.
        elif self.field == "Latitude":
            self.data_var.set(self.gateway.data)  # This has to be changed to point to latitude value.
        # Add an else of some sort, don't know where to print the error.
        else:
            print("General data could not be categorized")
        self.parent.after(100, self.__update_value)

class EngineControl(tk.Frame):
    """ TKinter frame that holds a label and button with changeable string

    The label is what's being controlled. The button controls output to LoRa.

    Parameters
    ----------
    parent : TKinter Frame
        parent frame
    gateway : Gateway instance (LPS)
        Gateway to monitor
    field : str
        name of controlled LPS function

    """

    def __init__(self, parent, gateway, sensor, field, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.gateway = gateway
        self.sensor = sensor
        self.field = field

        # Button to make a colored "box" for sensor
        # Style will be reflected on this button
        self.text_var = tk.StringVar()
        self.text_var.set("Start")
        self.btn = tk.Button(self, text=self.field, height=4, width=10)
        self.btn.grid(row=0, column=1)
        # Label to display the gateway's port name
        self.label = tk.Label(self, text=self.field)
        self.label.grid(
            row=1, column=1, pady=10)

        self.__update_button()

    def __update_button(self):
        """ Set the behaviour of the button to open or close the Serial link

        """
        if self.gateway.serial.get_status():
            self.text_var.set("Stop")
            if self.field == "Fueling":
                self.btn.config(command=self.gateway.send_command("Start Fuel"))
            elif self.field == "Ignite":
                self.btn.config(command=self.gateway.send_command("Ignite"))
            else:
                print("Change name of field for action")
        else:
            self.text_var.set("Start")
            if self.field == "Fueling":
                self.btn.config(command=self.gateway.send_command("Stop Fuel"))
            elif self.field == "Ignite":
                self.btn.config(command=self.gateway.send_command("Should we send something here?"))
            else:
                print("Change name of field for action")
        # Call this function again after 100 ms
        self.parent.after(100, self.__update_button)
