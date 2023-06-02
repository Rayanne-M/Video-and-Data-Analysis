import numbers
import cv2
import os
import numpy as np
import math
import tkinter as tk
from tkinter import filedialog
import csv
import datetime
import tkinter.font
import matplotlib.pyplot as plt
import statistics as stat
from matplotlib.animation import FuncAnimation
from IPython import display
from matplotlib.patches import Rectangle,Ellipse
import pandas as pd
import scipy
from scipy import spatial


pd.options.mode.chained_assignment = None  # default='warn'

def to_second(str_time):
    float_time = float(str_time.split(':')[-2])*60+ float(str_time.split(':')[-1])
    return(float_time)


def angle(a,b,c) : 
    ab = np.array(b)-np.array(a)
    bc = np.array(c)- np.array(b) 
    ang = np.dot(ab,bc)/ (math.dist(a,b)*math.dist(b,c))
    return abs(np.rad2deg(np.arccos(ang))-180)

def choseResult():
    root.sourceResult = filedialog.askopenfilenames(parent=root, title='Chose the result file')

def continueButton():
        root.destroy()

root = tk.Tk()
root.title("PDP Video Cutter")
root.geometry("600x400")

pj = pd.read_csv(r'C:\Users\malassis\Desktop\Analyse video\Pages Jaunes\PagesJaunes2.csv')

def getValue(fileID,variable):
    return pj[pj["traj"]==fileID][variable].item()


# Title
lblTitle = tk.Label(root,text = "PDP Video Cutter", font = ("Arial",30), foreground = "white", background="#43A047")
lblTitle.place(x=0,y=0,width=600)


#Bouttons

b_choseResult = tk.Button(root, text = "PDP RESULT",fg="white",font = ("Arial",6), width = 10, height = 4, bg= "#3F51B5",command = choseResult)
b_choseResult.place(x = 400,y = 100)
b_choseResult['font']= tk.font.Font(weight="bold")
b_choseResult.width = 100

b_continue = tk.Button(root, text = "READY",fg="white",font = ("Arial",6), width = 20, height = 1, bg ="#B71C1C", command = continueButton)
b_continue.place(x = 180, y = 340)
b_continue['font']= tk.font.Font(weight="bold")
b_continue.width = 100

root.mainloop()

csvFiles = root.sourceResult

table = []
err=[]
#csvID = r'C:\Users\malassis\Desktop\Analyse video\Trajectoire\zira_14-12.csv'

for file in csvFiles : 
    ###### Creation du data set de la trajectoire 
    try : 
        csvID = file
        if getValue(csvID,"pos_2") != "":

            res = pd.read_csv(file, sep = ',', header=[1, 2],encoding='latin-1')
            pos=res["pointer"]
            pos.loc[pos["likelihood"] < 0.98, "x"] = np.nan
            pos.loc[pos["likelihood"] < 0.98, "y"] = np.nan 

            pos.interpolate(method="linear", inplace= True)
            ### Double frame number
            line_ins = 1 # Number of lines to insert
            res_dict = {col: [y for val in pos[col] for y in [val] + [np.nan]*line_ins][:-line_ins] for col in pos.columns}
            pos = pd.DataFrame(res_dict)
            pos.interpolate(method="linear", inplace= True)            
            
            p1 = [float(getValue(file,"p1x")),float(getValue(file,"p1y"))]
            p2 = [float(getValue(file,"p2x")),float(getValue(file,"p2y"))]
            p4 = [float(getValue(file,"p4x")),float(getValue(file,"p4y"))]
            p5 = [float(getValue(file,"p5x")),float(getValue(file,"p5y"))]

            pts=np.array([p1,p2,p4,p5])

            pts1 = np.float32([p1,p2,p4,p5])
            pts2 = np.float32([[0, 0], [100, 0],[0,100], [100, 100]])

            # Apply Perspective Transform Algorithm
            m = cv2.getPerspectiveTransform(pts1, pts2)
            p_t=[]
            for pt in pts : 
                x_p = pt[0]
                y_p = pt[1]
                p_t.append([
                        (m[0,0]*x_p + m[0,1]*y_p + m[0,2])/
                        (m[2,0]*x_p + m[2,1]*y_p + m[2,2]),
                        (m[1,0]*x_p + m[1,1]*y_p + m[1,2])/
                        (m[2,0]*x_p + m[2,1]*y_p + m[2,2])
                        ])
            x_t =(m[0,0]* pos["x"] + m[0,1]* pos["y"] + m[0,2])/(m[2,0]* pos["x"] + m[2,1]* pos["y"] + m[2,2])
            y_t =(m[1,0]* pos["x"] + m[1,1]* pos["y"] + m[1,2])/(m[2,0]* pos["x"] + m[2,1]* pos["y"] + m[2,2])
            pos["x"] = x_t
            pos["y"] = y_t

            ####### Fin de la creation du dataset : pos["x"] et pos["y"]


            csvID = file
            timer = to_second(getValue(csvID,"timer_rel"))
            timer_end = to_second(getValue(csvID,"timer_rel_end"))
            duration = timer_end- timer

            calc_duration = 2*float(getValue(csvID,'RSI')) + float(getValue(csvID,'rt2')) + float(getValue(csvID,'rt1'))

            diff = int((calc_duration-duration)*25)
            csvID = file[:-4]+'.csv'
            
            rs1 = int(0.1+float(getValue(csvID,'RSI'))*25*2) # Stage : RSI_1
            t1 = rs1+int(float(getValue(csvID,'rt1'))*25*2) # Stage : rt1
            rs2 = t1 + rs1 - diff # Stage RSI_2
            t2 = rs2 + int(float(getValue(csvID,'rt2'))*25*2) # Stage rt2


            headers = ["subject","date","session","block","trials_count","session_type","seq_type","set_num","seq_num","pos_1","pos_2","pos_2_cons","pos_2_inc","RSI","distance","trial_stage"]
            propRES = pd.DataFrame(columns=headers)

            stage_l = [rs1,t1,rs2,t2]
            stage_m = [0,rs1,t1,rs2]

            stage_n = ["RSI_1", "RT_1","RSI_2","RT_2"]
            distance = [0,0,0,0]
            for stage,j,stage_min in zip(stage_l, [0,1,2,3], stage_m) : 
                for i in range(stage-stage_min):
                    distance[j] += math.dist([x_t[stage+i],y_t[stage+i]],[x_t[stage_min+i],y_t[stage_min+i]])

            data = { 
                    "subject": [getValue(csvID,"subject")],
                    "date": [getValue(csvID,"date")],
                    "session": [getValue(csvID,"session")],
                    "block": [getValue(csvID,"block")],
                    "trials_count": [getValue(csvID,"trials_count")],
                    "session_type": [getValue(csvID,"session_type")],
                    "seq_type": [getValue(csvID,"seq_type")],
                    "set_num": [getValue(csvID,"set_num")],
                    "seq_num": [getValue(csvID,"seq_num")],
                    "pos_1": [getValue(csvID,"pos_1")],
                    "pos_2": [getValue(csvID,"pos_2")],
                    "pos_2_cons": [getValue(csvID,"pos_2_cons")],
                    "pos_2_inc": [getValue(csvID,"pos_2_inc")],
                    "RSI": [getValue(csvID,"RSI")],
                    "RSI_1": distance[0],
                    "RT_1" : distance[1],
                    "RSI_2": distance[2],
                    "RT_2": distance[3] 
                }

            temp_df = pd.DataFrame(data)
            propRES = propRES.append(temp_df)

            table.append(propRES)
    except:
        err.append(file)
        print(file)

print(err)

pd.DataFrame(err).to_csv("erreur_distance.csv")

table = pd.concat(table)

table.to_csv("Distance.csv",sep=";", index=False)
