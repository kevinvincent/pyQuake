# Copyright 2012 Kevin Vincent
# Author: "Kevin Vincent" <kevin.vincent15@bcp.org>
#
# Hosted on: https://github.com/kevinvincent/pyQuake/blob/master/quake2.py
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# See the GNU General Public License for more details.

"""
PyQuake is a earthquake data file analysis and simulation application.

USAGE INSTRUCTIONS:
This is a self contained application that is used to graph the data of
and eathquake data file using the turtle graphics module which is required.

Optimization:
PyQuake has two optimization "profiles" speed and animation. These when
selected will either make a quick graph or will draw one slow with
good animation.

Sample Size:
This feature will only graph the nth number as selected by the slider on the
main GUI.

File Format:
The file format is an ascii file with earthquake data in the following format:
   1.9999994e+02   4.4340977e-09
   2.0000994e+02   2.3202048e-08

Enjoy!

    Class pyQuake: Contains main methods to graph and parse file.
    Class mainGUI: Contains methods for the main window - including graphing code.
    Class reportDaemon: Contains methods for report window and saving it.
"""

#------------------------------------------------------------------------------#

import datetime
from tkinter import *
from tkinter import filedialog
from tkinter.messagebox import showerror
from time import *
from turtle import *

#------------------------------------------------------------------------------#

class pyQuake:
    """
    Main Class:
    Contains Graph Methods and a Parse Method.
    """
    currentX = 0;

    def __init__(self,speedOfTurtle,tracerSpeed,tracerDelay,screenWidth):
        """
        This constructor Inits pyQuake class with turtle graphics module settings.

        Args:
          speedOfTurtle: 'slowest','slow','medium','fast,'fastest'.
          tracerSpeed: speed of animation 1(slowest) - 1000(fastest).
          tracerDelay: turtle windwow refresh rate.
              larger number = faster but less smooth animation
          screenWidth: self-explanatory.
        """
        speed(speedOfTurtle)
        tracer(tracerSpeed, tracerDelay)
        screensize(screenWidth,)

    def prepareGraph(self):
        """
        Opens window or clears existing and makes blue 0 line on graph 500000 pixels long
        """
        setup( width = 800, height = 600, startx = 400, starty = 50)
        self.currentX = 0
        up()
        goto(0,0)
        down()
        clear()
        color("blue")
        forward(50000)
        forward(-50000)

    def beginCountdown(self):
        """
        Gives user time to switch to Turtle Window
        """
        counter = 10
        while counter != 0:
            goto(0,counter*20)
            write(' Simulating in '+str(counter))
            sleep(1)
            counter-=1


    def parseLine(self,line):
        """
        Takes a two column line and returns the second column
        as an int.

        Args:
          line: line to parse
        """
        toParse = str(line)
        num = line[17:]
        num = float(num)
        return num;

    def convertToPrintable(self,rawData):
        """
        Raw Data is too small to draw ex:'.04545123'
        Moves decimal points to create larger number

        Args:
          rawData: raw number from file after being parsed

        Returns:
          Converted number.
        """

        return rawData*(10**2);

    def printSpike(self,value,sampleSize):
        """
        Method that gets parsed number, converts it to printable
        and actually draws the lines.

        Colors line depending on spike size.

        Args:
          value: the y value of the point to graph after parsing
        """

        global currentX;
        self.currentX+=sampleSize*(10**-1);
        toGoY = self.convertToPrintable(value);

        if(toGoY > 60 or toGoY < -60):
            color("red")
        elif(toGoY > 35 or toGoY < -35):
            color("orange")
        else:
            color("green")

        goto(self.currentX,toGoY)

#------------------------------------------------------------------------------#

class mainGUI:
    """
    Main Window Class:
    Contains methods to interact with the main GUI and all of its widgets
    """

    def setType(self):
        """
        Method that gets optimization radio button setting
        and sets a global variable acoordingly
        """
        global optimization;
        selection = choiceVar.get()
        if selection == 1:
            optimization = "speed"
        else:
            optimization = "animation"

    def askForFile(self):
        """
        Opens select file dialog, gets filepath, and also sets the selected file label on GUI.
        """
        global filepath;

        #Acceptable File Types
        mask =[("Ascii earthquake data files","*.ascii")]

        filepath = filedialog.askopenfilename(filetypes=mask)

        lastSlashIndex = 0
        currentIndex = 0

        for char in filepath:
            if char == "/":
                lastSlashIndex = currentIndex;
            currentIndex+=1;

        selectedFile.config(text=".."+filepath[lastSlashIndex:]+"\n")




    def runSim(self):
        """
        Main process that runs when Start Simulation button is pressed.
        Does the actual graphing and then opens up report window with
        details to be presented.
        """

        error = False

        try:
            if optimization == 'any value it isnt set anyway':
                pass;
        except NameError:
            showerror("Optimization Error","Please select optimization type!\n")
            error = True;
        try:
            open(filepath)
        except IOError:
            showerror("File Selection Error","Please select a data file!\n")
            error = True

        if not error:
            # Init main class and with correct Optimization
            if(optimization == 'speed'):
                quake = pyQuake(0,1000,25,50000)
            elif(optimization == 'animation'):
                quake = pyQuake(0,50,15,50000)

            # Init Graph
            quake.prepareGraph();

            # Init Max, Min, numOfDataPoints, sumOfData variables
            maxSpike = 0
            minSpike = 0
            numOfDataPoints = 0
            sumOfData = 0

            #Sample Size and File
            global sampleSize;
            sampleSize = sampleVar.get();
            fileName = filepath;

            try:
                with open(fileName) as dataFile:
                    #quake.beginCountdown();

                    for indexOfLine, line in enumerate(dataFile):
                        if indexOfLine%sampleSize == 0:
                            toPrint = quake.parseLine(line)
                            quake.printSpike(toPrint,sampleSize)

                            #calulate max and min data point
                            if toPrint > maxSpike:
                                maxSpike = toPrint;
                            if toPrint < minSpike:
                                minSpike = toPrint;

                            #calculate average later
                            numOfDataPoints+=1
                            sumOfData+=toPrint
            except IOError:
                print("Please enter a valid data file.")
                raise;

            #Finished: Give Report
            report = reportDaemon(numOfDataPoints,maxSpike,minSpike,sumOfData);

            #Enter Main Loop
            mainloop()

#------------------------------------------------------------------------------#

class reportDaemon:

    def __init__(self,numOfDataPoints,maxSpike,minSpike,sumOfData):
        """
        Inits Report GUI with the widgets containing information about the simulation
        """
        reportWindow = Toplevel();
        reportWindow.title("Report")

        reportWindow.geometry('+25+250')

        #Main Heading
        simFin = Label( reportWindow, text="  Simulation Finished:\n  "+str(datetime.datetime.now())+"    \n" )
        simFin.grid();

        #Num Of Data Points
        numOfAll = Label( reportWindow, text="  Number of data points plotted:\n  "+str(numOfDataPoints))
        numOfAll.grid();

        #Max
        maxOfAll = Label( reportWindow, text="  Max data point:\n  "+str(maxSpike))
        maxOfAll.grid();

        #Min
        minOfAll = Label( reportWindow, text="  Min data point:\n  "+str(minSpike))
        minOfAll.grid();

        #Average
        aveOfAll = Label( reportWindow, text="  Average data point:\n  "+str(sumOfData/numOfDataPoints))
        aveOfAll.grid();

        #Make contents for saving report
        global reportSaveContents;
        reportSaveContents = "Simulation finished on: "+str(datetime.date.today())+"\n"+"With Settings:\n"+"\tOptimization: "+str(optimization)+"\n"+"\tSample Size: "+str(sampleSize)+"\n"+"\tFile: "+str(filepath)+"\n\n"+"Number of data points plotted:\n"+str(numOfDataPoints)+"\n"+"Max data point:\n"+str(maxSpike)+"\n"+"Min data point:\n"+str(minSpike)+"\n"+"Average data point:\n"+str(sumOfData/numOfDataPoints)


        #Save button
        save = Button(reportWindow, text="Save Report...", command=self.saveReport)
        save.grid(row=5)

    def saveReport(self):
        """
        Opens save file dialog and writes to selected filename the report data.
        """
        try:
            saveFile = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
            saveFile.write(reportSaveContents)
            saveFile.close()
        except Exception:
            pass;

#------------------------------------------------------------------------------#

#MAIN GUI

#Create Main Window object
gui = Tk()
gui.title("PyQuake")

#Create a pyQuake Object
quake = mainGUI();

#Create tkinter vars - for getting information from GUI
choiceVar = IntVar();
sampleVar = IntVar();
filePathVar = StringVar();
filepath = "";


"""
Here on out: Gui organization and widgets
"""

#Main Heading
heading = Label( gui, text="Earthqake Analysis and Simulation" )
heading.grid(row=0,column=0);

#Horizontal Line
line=Frame(height=1,width=250,bg="black")
line.grid()

#Optimization Heading
opType = Label( gui, text="\nOptimization Type:" )
opType.grid(row=3,column=0);

#Optimization Radio Buttons
speedRadio = Radiobutton(gui, text="Speed", variable=choiceVar, value=1, command=quake.setType)
speedRadio.grid(row=4,column=0)

animationRadio = Radiobutton(gui, text="Animation", variable=choiceVar, value=2, command=quake.setType)
animationRadio.grid(row=5,column=0)

#Sample Size Heading
samp = Label( gui, text="\nSample Size:" )
samp.grid(row=7,column=0);

#Sample Size Slider
sampleSize = Scale(gui, from_=1, to=10, orient=HORIZONTAL, variable=sampleVar)
sampleSize.grid(row=8,column=0)

#Space Heading
space = Label( gui, text="" )
space.grid(row=9,column=0);

#Select a File Button
fileButton = Button(gui, text="Select File...", command=quake.askForFile)
fileButton.grid(row=10,column=0)

#Selected File Heading
selectedFile = Label( gui, text="No File Selected\n" )
selectedFile.grid(row=11,column=0);

#Horizontal Line
line=Frame(height=1,width=250,bg="black")
line.grid()

#Start Simulation Button
start = Button(gui, text="Start Simulation", command=quake.runSim)
start.grid()

#Start the Main loop
gui.mainloop()
