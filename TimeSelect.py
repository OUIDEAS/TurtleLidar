# Change time on Turtle
import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar, DateEntry
from tkinter.font import Font
import datetime

def doublezero(TIME):
    if TIME < 10:
        out = '0' + str(TIME)
    else:
        out = str(TIME)
    return out

class App(tk.Frame):
    def __init__(self):
        super().__init__()

        self.date = None
        self.tme = None

        now = datetime.datetime.now()

        self.hourstr=tk.StringVar(self, doublezero(now.hour))
        self.hour = tk.Spinbox(self,from_=0,to=23,wrap=True,textvariable=self.hourstr,width=2,state="readonly", font=Font(size=24, weight='bold'))
        self.minstr=tk.StringVar(self, doublezero(now.minute))

        self.min = tk.Spinbox(self,from_=0,to=59,wrap=True,textvariable=self.minstr,width=2, font=Font(size=24, weight='bold'), state="readonly")    # ,state="readonly"
        self.secstr=tk.StringVar(self, doublezero(now.second))
        self.sec = tk.Spinbox(self,from_=0,to=59,wrap=True,textvariable=self.secstr,width=2, font=Font(size=24, weight='bold'), state="readonly")

        self.last_valueSec = ""
        self.last_value = ""
        self.minstr.trace("w",self.trace_var)
        self.secstr.trace("w",self.trace_varsec)

        # self.text = tk.Label(self, text="Time:")
        # self.text.grid()
        self.hour.grid(row=0,column=0)
        self.min.grid(row=0,column=1)
        self.sec.grid(row=0,column=2)

        # Enter Button
        s = ttk.Style()
        s.configure('my.TButton', font=('Helvetica', 20))
        ttk.Button(root, text='Change Date and Time',command=self.end, style='my.TButton').pack(padx=10, pady=10)

        # Calendar
        self.cal = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2, font=Font(size=18, weight='bold'))
        self.cal.pack(padx=10, pady=10)

    def trace_var(self,*args):
        if self.last_value == "59" and self.minstr.get() == "0":
            self.hourstr.set(int(self.hourstr.get())+1 if self.hourstr.get() !="23" else 0)
        self.last_value = self.minstr.get()

    def trace_varsec(self,*args):
        if self.last_valueSec == "59" and self.secstr.get() == "0":
            self.minstr.set(int(self.minstr.get())+1 if self.minstr.get() !="59" else 0)
            if self.last_value == "59":
                self.hourstr.set(int(self.hourstr.get())+1 if self.hourstr.get() !="23" else 0)
        self.last_valueSec = self.secstr.get()

    def get_time(self):
        H = self.hourstr.get()
        M = self.minstr.get()
        S = self.secstr.get()

        Time = doublezero(int(H)) + ":" + doublezero(int(M)) + ":" + doublezero(int(S))
        return Time

    def end(self):
        self.date = self.cal.get_date()
        self.tme = self.get_time()
        # print(self.date)
        # print(self.tme)
        self.master.destroy()


if __name__ == "__main__":
    from subprocess import call
    import os
    import platform

    root = tk.Tk()
    root.title("Set Date and Time")
    root.geometry("400x200")
    gui = App()
    gui.pack()

    # App(root).pack(padx=10, pady=10)
    root.mainloop()
    # print(gui.date)
    # print(gui.tme)
    if gui.date is not None and gui.tme is not None:
        timeCMD = str(gui.date) + ' ' + str(gui.tme)
        print(timeCMD)
        setTimeCMD = "ssh 192.168.4.1 sudo date --set '" + timeCMD + "'"
        setTimeCMD1 = "sudo date --set '" + timeCMD + "'"
        print(setTimeCMD)
        if platform.system() == 'Linux':
            call(setTimeCMD1, shell=True)
            call(setTimeCMD, shell=True)
        else:
            print("Why are you not running this on a pi?")
    else:
        print("Date and/or time not given")
