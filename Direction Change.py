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

def to_second(str_time):
    float_time = float(str_time.split(':')[-2])*60+ float(str_time.split(':')[-1])
    return(float_time)

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return abs((np.rad2deg(np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)))-180))

def choseResult():
    root.sourceResult = filedialog.askopenfilenames(parent=root, title='Chose the result file')

def continueButton():
        root.destroy()

root = tk.Tk()
root.title("PDP Video Cutter")
root.geometry("600x400")

pj = pd.read_csv(r'C:\Users\malassis\Desktop\Analyse video\Pages Jaunes\PagesJaunes2.csv')

def getValue(fileID,variable):
    return pj[pj["traj"]==fileID][variable].to_list()[0]




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

    try: 
        ###### Creation du data set de la trajectoire 
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

        # fig, traj = plt.subplots(2)


        csvID = file
        timer = to_second(getValue(csvID,"timer_rel"))
        timer_end = to_second(getValue(csvID,"timer_rel_end"))
        duration = timer_end- timer

        rsi = int(0.1+float(getValue(csvID,'RSI')))

        calc_duration = 2*float(getValue(csvID,'RSI')) + float(getValue(csvID,'rt2')) + float(getValue(csvID,'rt1'))

        diff = int((calc_duration-duration)*25)
        csvID = file[:-4]+'.csv'
        rs1 = int(0.1+float(getValue(csvID,'RSI'))*25*2)
        t1 = rs1+int(float(getValue(csvID,'rt1'))*25*2)
        rs2 = t1 + rs1 - diff
        t2 = rs2 + int(float(getValue(csvID,'rt2'))*25*2) 



        agl = []
        change = []

        r1=(-50,-50)
        r2=(-50+100,-50)
        r3=(-50+200,-50)
        r4=(-50,-50+100)
        r5=(-50+100,-50+100)
        r6=(-50+200,-50+100)

        # traj[1].add_patch(Rectangle(r1,100,100, fill = False ))
        # traj[1].add_patch(Rectangle(r2,100,100, fill = False))
        # traj[1].add_patch(Rectangle(r3,100,100, fill = False))
        # traj[1].add_patch(Rectangle(r4,100,100, fill = False))
        # traj[1].add_patch(Rectangle(r5,100,100, fill = False))
        # traj[1].add_patch(Rectangle(r6,100,100, fill = False))

        touch = [0,0,0,0,0,0]


        for i in range(len(x_t)-6) :
            if i%2 ==0 : 
                a1 = [x_t[i+2]-x_t[i+4],y_t[i+2]-y_t[i+4]]
                a2 = [x_t[i]-x_t[i+2],y_t[i]-y_t[i+2]]
                b = [x_t[i+4]-x_t[i+6],y_t[i+4]-y_t[i+6]]
                ang1 = angle_between(a1, b)
                ang2 = angle_between(a2, b)
                
                if ang1 < 100  :
                    change_b = True
                    ang = ang1
                elif ang2 < 100 and not change:
                    change_b = True
                    ang = ang2
                else : 
                    change_b = False
                    ang=ang2
                agl.append(ang)

            if change_b :
                change.append(True)
                if x_t[i+1]> r1[0] and x_t[i+1] <r1[0]+100 and y_t[i+1]>r1[1] and y_t[i+1]<r1[1]+100 : 
                    touch[0] +=  1
                if x_t[i+1]> r2[0] and x_t[i+1] <r2[0]+100 and y_t[i+1]>r2[1] and y_t[i+1]<r2[1]+100 : 
                    touch[1] += 1
                if x_t[i+1]> r3[0] and x_t[i+1] <r3[0]+100 and y_t[i+1]>r3[1] and y_t[i+1]<r3[1]+100 : 
                    touch[2] += 1
                if x_t[i+1]> r4[0] and x_t[i+1] <r4[0]+100 and y_t[i+1]>r4[1] and y_t[i+1]<r4[1]+100 : 
                    touch[3] += 1
                if x_t[i+1]> r5[0] and x_t[i+1] <r5[0]+100 and y_t[i+1]>r5[1] and y_t[i+1]<r5[1]+100 : 
                    touch[4] += 1
                if x_t[i+1]> r6[0] and x_t[i+1] <r6[0]+100 and y_t[i+1]>r6[1] and y_t[i+1]<r6[1]+100 : 
                    touch[5] += 1
            else : 
                change.append(False)

        headers = ["subject","group","date","phase_test","session","block","trials_count","set_num","session_type","seq_type","seq_num","pos_1","pos_2","pos_2_cons","pos_2_inc","rep2","accuracy","RSI","loc","frames_bin","change_bin","n_frames","n_change","trial_stage"]
        propRES = pd.DataFrame(columns=headers)

        for h in headers[:-6]:
            propRES[h]= [getValue(csvID,h)]*36

        
        propRES["loc"] = [1,2,3,4,5,6]*6
        propRES["trial_stage"] = ["RSI_1"]*6 + ["rt1"]*6 + ["RSI_2"]*6 + ["rt2"]*6 + ["POST"]*6 + ["TOT"]*6


        n_frames=[0,0,0,0,0,0]
        n_change=[0,0,0,0,0,0]

        for i in range(len(x_t)):
            last_pos = ""
            if x_t[i]> r1[0] and x_t[i] <r1[0]+100 and y_t[i]>r1[1] and y_t[i]<r1[1]+100 : #Si dans hitbox loc1
                n_frames[0] += 1
                if i< len(x_t)-6:
                    if change[max(0,i)] : 
                        n_change[0] += 1
            elif x_t[i]> r2[0] and x_t[i] <r2[0]+100 and y_t[i]>r2[1] and y_t[i]<r2[1]+100 : #Si dans hitbox loc2
                n_frames[1] += 1
                if i< len(x_t)-6:
                    if change[max(0,i)] : 
                        n_change[1] += 1
            elif x_t[i]> r3[0] and x_t[i] <r3[0]+100 and y_t[i]>r3[1] and y_t[i]<r3[1]+100 : #Si dans hitbox loc3
                n_frames[2] += 1
                if i< len(x_t)-6:
                    if change[max(0,i)] : 
                        n_change[2] += 1
            elif x_t[i]> r4[0] and x_t[i] <r4[0]+100 and y_t[i]>r4[1] and y_t[i]<r4[1]+100 : #Si dans hitbox loc4
                n_frames[3] += 1
                if i< len(x_t)-6:
                    if change[max(0,i)] : 
                        n_change[3] += 1            
            elif x_t[i]> r5[0] and x_t[i] <r5[0]+100 and y_t[i]>r5[1] and y_t[i]<r5[1]+100 : #Si dans hitbox loc5
                n_frames[4] += 1
                if i< len(x_t)-6:
                    if change[max(0,i)] : 
                        n_change[4] += 1 
            elif x_t[i]> r6[0] and x_t[i] <r6[0]+100 and y_t[i]>r6[1] and y_t[i]<r6[1]+100 : #Si dans hitbox loc6
                n_frames[5] += 1
                if i< len(x_t)-6:
                    if change[max(0,i)] : 
                        n_change[5] += 1 
            


            if i==rs1 : # RSI1
                propRES["n_frames"].loc[propRES["trial_stage"]=="RSI_1"] = n_frames
                propRES["n_change"].loc[propRES["trial_stage"]=="RSI_1"] = n_change


                tot_frames = np.array(n_frames)
                tot_change = np.array(n_change)

                n_frames=[0,0,0,0,0,0]
                n_change=[0,0,0,0,0,0]

            elif i==t1 : # RT1
                propRES["n_frames"].loc[propRES["trial_stage"]=="rt1"] = n_frames
                propRES["n_change"].loc[propRES["trial_stage"]=="rt1"] = n_change

                tot_frames += np.array(n_frames)
                tot_change += np.array(n_change)

                n_frames=[0,0,0,0,0,0]
                n_change=[0,0,0,0,0,0]

            elif i==rs2 : # RSI2
                propRES["n_frames"].loc[propRES["trial_stage"]=="RSI_2"] = n_frames
                propRES["n_change"].loc[propRES["trial_stage"]=="RSI_2"] = n_change


                tot_frames += np.array(n_frames)
                tot_change += np.array(n_change)

                n_frames=[0,0,0,0,0,0]
                n_change=[0,0,0,0,0,0]

            elif i==t2 : #RT2
                propRES["n_frames"].loc[propRES["trial_stage"]=="rt2"] = n_frames
                propRES["n_change"].loc[propRES["trial_stage"]=="rt2"] = n_change
                

                tot_frames += np.array(n_frames)
                tot_change += np.array(n_change)

                n_frames=[0,0,0,0,0,0]
                n_change=[0,0,0,0,0,0]
                
            elif i==len(x_t)-1 : # Post
                propRES["n_frames"].loc[propRES["trial_stage"]=="POST"] = n_frames
                propRES["n_change"].loc[propRES["trial_stage"]=="POST"] = n_change

                tot_frames += np.array(n_frames)
                tot_change += np.array(n_change)

                n_frames=[0,0,0,0,0,0]
                n_change=[0,0,0,0,0,0]

        propRES["n_frames"].loc[propRES["trial_stage"]=="TOT"] = tot_frames
        propRES["frames_bin"]= True
        propRES["frames_bin"].loc[propRES["n_frames"]==0] = False
        
        propRES["n_change"].loc[propRES["trial_stage"]=="TOT"] = tot_frames
        propRES["change_bin"]= True
        propRES["change_bin"].loc[propRES["n_change"]==0] = False

        table.append(propRES)
    except:
        err.append(file)

    



 
print(err)

pd.DataFrame(err).to_csv("erreur_prop.csv")

table = pd.concat(table)

table.to_csv("prop_frame_loc-Alex.csv",sep=";", index=False)
