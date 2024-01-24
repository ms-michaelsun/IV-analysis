import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from tkinter import *
from scipy.optimize import curve_fit
from tkinter import messagebox
from tkinter import filedialog
import os

def load():
    try:
        global df, label_data
        file = root.filename = filedialog.askopenfilename(initialdir=os.getcwd(), title='Select a file',
                                                   filetypes=(('csv files', '*.csv'), ('all files', '*.*')))
        df = pd.read_csv(file)
        df['Absolute'] = np.absolute(df['Current'])
        ax = sns.lineplot(x='Voltage', y='Current', data=df)
        ax.set(xlabel="Voltage (V)", ylabel="Current (A)")
        plt.show()
        label_data.grid_forget()
        label_data = Label(root, text=file)
        label_data.grid(row=1, column=0, columnspan=3)
    except FileNotFoundError:
        messagebox.showerror('Error 404', 'File not found!')

def load_area():
    try:
        global area
        area = float(e2.get())
        label = Label(root, text="Area of device (cm2): " + e2.get()).grid(row=3, column=1)
    except ValueError:
        print("Must be a number!")

def plot_log():
    try:
        global df
        df['Absolute'] = np.absolute(df['Current'])
        ax = sns.lineplot(x='Voltage', y='Absolute', data=df)
        ax.set_yscale('log')
        ax.set(xlabel="Voltage (V)", ylabel="Log Current (A)")
        plt.show()
    except FileNotFoundError:
        print("File not found!")
    except NameError:
        print("Load a file first!")

def plot_density():
    try:
        global df
        df['Current Density'] = df['Current']/area
        ax = sns.lineplot(x='Voltage', y='Current Density', data=df)
        ax.set(xlabel="Voltage (V)", ylabel="Current Density (A/cm2)")
        plt.show()
    except FileNotFoundError:
        print("File not found!")
    except NameError:
        print("File or area missing.")

def plot_density_log():
    try:
        global df
        df['Current Density'] = np.absolute(df['Current']/area)
        ax = sns.lineplot(x='Voltage', y='Current Density', data=df)
        ax.set(xlabel="Voltage (V)", ylabel="Log Current Density (A/cm2)")
        ax.set_yscale('log')
        plt.show()
    except FileNotFoundError:
        print("File not found!")
    except NameError:
        print("File or area missing.")

def shunt():
    try:
        shunt = df[df['Voltage'].between(-0.05, 0.05)]
    except FileNotFoundError:
        print("File not found!")
    ax = sns.lineplot(x='Voltage', y='Current', data=shunt)
    ax.set(xlabel="Voltage (V)", ylabel="Current (A)")
    plt.show()

    def func(x, a, b):
        return a * x + b

    guess = [1, 1]
    global Rshunt
    popt, pcov = curve_fit(func, shunt['Voltage'], shunt['Current'], p0=guess)
    slope, intercept = popt
    Rshunt = (1 / slope) * area
    label = Label(root, text = "Shunt Resistance: " + str(round(Rshunt, 2)) + " ohm.cm2").grid(row = 6, column = 1)

def series():
    global e3, e4
    try:
        x1 = float(e3.get())
        x2 = float(e4.get())
    except ValueError:
        print("Must be a number!")

    assert x1 > df['Voltage'].min() - 0.1, "Lower bound out of range!"
    assert x2 < df['Voltage'].max() + 0.1, "Upper bound out of range!"
    try:
        series = df[df['Voltage'].between(x1, x2)]
    except FileNotFoundError:
        print("File not found!")
    except AttributeError:
        print("Define ranges")
    ax = sns.lineplot(x='Voltage', y='Current', data=series)
    ax.set(xlabel="Voltage (V)", ylabel="Current (A)")
    plt.show()

    def func(x, a, b):
        return a * x + b

    guess = [1, 1]
    global Rseries
    popt, pcov = curve_fit(func, series['Voltage'], series['Current'], p0=guess)
    slope, intercept = popt
    Rseries = (1/slope) * area
    label = Label(root, text = "Series Resistance: " + str(round(Rseries, 2)) + " ohm.cm2").grid(row = 8, column = 1)

def fit():
    global e5, e6
    try:
        x1 = float(e5.get())
        x2 = float(e6.get())
    except ValueError:
        print("Must be a number!")

    assert x1 > df['Voltage'].min(), "Lower bound out of range!"
    assert x2 < df['Voltage'].max(), "Upper bound out of range!"
    try:
        df['Vd'] = df['Voltage'] - (np.abs((df['Current'] / area) * Rseries))
        df['Abs_current'] = np.abs(df['Current'] / area)
        exp = df[df['Voltage'].between(x1, x2)]
    except FileNotFoundError:
        print("File not found!")
    except AttributeError:
        print("Define ranges")

    def func(x, J0, n):
        return J0 * (np.exp(x / (n * 0.026)) - 1) + x / Rshunt

    global J0, n, err1, err2, label7
    guess = [1e-7, 1]
    bnds = ((0, 1), (np.inf, 3))
    popt, pcov = curve_fit(func, exp['Vd'], exp['Abs_current'], p0=guess, bounds=bnds)
    J0, n = popt
    err1, err2 = np.sqrt(np.diag(pcov))

    x = np.linspace(x1, x2, 10000)
    y = np.abs(func(x, J0, n))

    fig, (ax1, ax2) = plt.subplots(1, 2)
    sns.lineplot(x='Vd', y='Abs_current', data=exp, alpha=0.6, label="Experimental", ax=ax1)
    sns.lineplot(x=x, y=y, alpha=0.6, linestyle='--', label="Fitted", ax=ax1)
    ax1.set(xlabel="Voltage (V)", ylabel="Current (A)")

    sns.lineplot(x='Vd', y='Abs_current', data=exp, alpha=0.6, label="Experimental", ax=ax2)
    sns.lineplot(x=x, y=y, alpha=0.6, linestyle='--', label="Fitted", ax=ax2)
    ax2.set_yscale('log')
    ax2.set(xlabel="Voltage (V)", ylabel="Current (A)")
    plt.show()


    label7.grid_forget()
    label7 = Label(root, text=("Rseries: " + str(round(Rseries, 2)) + " ohm.cm2" +
                               "\nRshunt: " + str(round(Rshunt/1000, 2)) + " kohm.cm2" +
                               "\nJ0: " + '{:.3g}'.format(J0) + " A/cm2" + " (std error = " + '{:.3g}'.format(err1) + ")" +
                               "\nn: " + str(round(n, 2)) + " (std error = " + str(round(err2, 1)) + ")"), font=('Arial', 15))
    label7.grid(row=12, column=0, columnspan=3)


root = Tk()
root.title("I-V curve analysis (dark)")
root.geometry('600x400')
sns.color_palette("colorblind")
sns.set_style("whitegrid")

label_data = Label(root, text='')
label_data.grid(row=1, column=1)

label2 = Label(root, text="Enter area of device (cm2): ")
label2.grid(row=2, column=0)
e2 = Entry(root, width=10, borderwidth=5)
e2.grid(row=2, column=1)

label3 = Label(root, text = "from x = ").grid(row = 7, column = 1)
e3 = Entry(root, width = 5)
e3.grid(row = 7, column = 2)
label4 = Label(root, text = "to ").grid(row = 7, column = 3)
e4 = Entry(root, width = 5)
e4.grid(row = 7, column = 4)

label5 = Label(root, text = "from x = ").grid(row = 9, column = 1)
e5 = Entry(root, width = 5)
e5.grid(row = 9, column = 2)
label6 = Label(root, text = "to ").grid(row = 9, column = 3)
e6 = Entry(root, width = 5)
e6.grid(row = 9, column = 4)

label7 = Label(root, text='')
label7.grid(row=10, column=1)

button1 = Button(root, text="Load data", command=load)
button1.grid(row=0, column=1)

button2 = Button(root, text="Load", command=load_area)
button2.grid(row=2, column=2)

button3 = Button(root, text="Plot log scale", command=plot_log)
button3.grid(row=4, column=0)

button4 = Button(root, text="Plot current density", command=plot_density)
button4.grid(row=4, column=1)

button5 = Button(root, text="Plot current density (log scale)", command=plot_density_log)
button5.grid(row=4, column=2)

button6 = Button(root, text="Shunt Resistance", command=shunt)
button6.grid(row=6, column=0)

button7 = Button(root, text="Series Resistance", command=series)
button7.grid(row=7, column=0)

button8 = Button(root, text="I-V fit", command=fit)
button8.grid(row=9, column=0)


root.mainloop()
