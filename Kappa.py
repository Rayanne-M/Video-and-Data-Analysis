import numbers
from turtle import circle
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
from matplotlib.patches import Rectangle
import pandas as pd
import random

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
                
def getValueV(fileID,variable):
    v = pj[pj["video_file"]==fileID][variable].to_list()[0]
    return v
def getValue(fileID,variable):
    v = pj[pj["traj"]==fileID][pj["RSI"]==1][pj["session_type"]=="srt"][variable].to_list()[0]
    return v





root = tk.Tk()
root.title("Pages Jaunes")
root.geometry("600x400")

# Title
lblTitle = tk.Label(root,text = "PDP Video Cutter", font = ("Arial",30), foreground = "white", background="#43A047")
lblTitle.place(x=0,y=0,width=600)


#Bouttons

b_choseResult = tk.Button(root, text = "PDP result",fg="white",font = ("Arial",6), width = 10, height = 2, bg= "#3F51B5",command = choseResult)
b_choseResult.place(x = 50,y = 100)
b_choseResult['font']= tk.font.Font(weight="bold")
b_choseResult.width = 100


b_continue = tk.Button(root, text = "Ready",fg="white",font = ("Arial",6), width = 8, height = 1, bg ="#B71C1C", command = continueButton)
b_continue.place(x = 250, y = 340)
b_continue['font']= tk.font.Font(weight="bold")
b_continue.width = 100

root.mainloop()

fileR = root.sourceResult

trajDir = r'C:/Users/malassis/Desktop/Analyse video/Trajectoire/CSV'

pj = pd.read_csv(r'C:\Users\malassis\Desktop\Analyse video\Pages Jaunes\PagesJaunes2.csv')
table = pd.DataFrame()

random_numbers = random.sample(range(0,len(fileR)), 100)
cacahuete=0
o=0
liste_csv=[]
while o < len(random_numbers):
    try:
        vid = fileR[random_numbers[cacahuete]]
        file=getValueV(vid,"traj")
        pouet = str(getValue(file,"RSI"))

        cacahuete= cacahuete+1
        ###### Creation du data set de la trajectoire 
        fig, traj = plt.subplots(1)

        x =  []
        y =  []
        p1= []
        p2=  []
        p3 = []
        p4 = []
        p5 = []
        p6 = []

        res = pd.read_csv(file, sep = ',', header=[1, 2],encoding='latin-1')
        pos=res["pointer"]
        pos.loc[pos["likelihood"] < 0.98, "x"] = np.nan
        pos.loc[pos["likelihood"] < 0.98, "y"] = np.nan 

        pos.interpolate(method="linear", inplace= True)
        ### Double frame number
        line_ins = 1 # Number of lines to insert
        res_dict = {col: [y for val in pos[col] for y in [val] + [np.nan]*line_ins][:-line_ins] for col in pos.columns}
        pos = pd.DataFrame(res_dict)
        print(pos)
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

        csvID = file[:-4]+'.csv'
        timer = to_second(getValue(csvID,"timer_rel"))
        timer_end = to_second(getValue(csvID,"timer_rel_end"))
        duration = timer_end- timer

        calc_duration = 2*float(getValue(csvID,'RSI')) + float(getValue(csvID,'RT_2')) + float(getValue(csvID,'RT_1'))

        diff = int((calc_duration-duration)*25)
        csvID = file[:-4]+'.csv'
        r1 = int(0.1+float(getValue(csvID,'RSI'))*25*2)
        t1 = r1+int(float(getValue(csvID,'RT_1'))*25*2)
        r2 = t1 + r1 - diff
        t2 = r2 + int(float(getValue(csvID,'RT_2'))*25*2) 

        traj.plot(p_t[0][0],p_t[0][1],"ro")
        traj.plot(p_t[1][0],p_t[1][1],"ro")
        traj.plot(p_t[2][0],p_t[2][1],"ro")
        traj.plot(p_t[3][0],p_t[3][1],"ro")
        traj.plot(200,0,"ro")
        traj.plot(200,100,"ro")
        traj.add_patch(Rectangle((-50,-50),100,100, fill = False ))
        traj.add_patch(Rectangle((-50+100,-50),100,100, fill = False))
        traj.add_patch(Rectangle((-50+200,-50),100,100, fill = False))
        traj.add_patch(Rectangle((-50,-50+100),100,100, fill = False))
        traj.add_patch(Rectangle((-50+100,-50+100),100,100, fill = False))
        traj.add_patch(Rectangle((-50+200,-50+100),100,100, fill = False))

        #traj.plot(x_t,y_t) # anticipation
        traj.plot(x_t[t1:r2+1],y_t[t1:r2+1])
        traj.invert_yaxis()
        traj.set_aspect('equal', adjustable='box')

        agl = []
        change= False
        print(x_t)
        for i in range(len(x_t)-6) :
            if i > t1 and i< r2+1 : 
                if i%2 ==0 : 
                    a1 = [x_t[i+2]-x_t[i+4],y_t[i+2]-y_t[i+4]]
                    a2 = [x_t[i]-x_t[i+2],y_t[i]-y_t[i+2]]
                    b = [x_t[i+4]-x_t[i+6],y_t[i+4]-y_t[i+6]]
                    ang1 = angle_between(a1, b)
                    ang2 = angle_between(a2, b)
                    
                    if ang1 < 100  :
                        traj.plot(x_t[i+4],y_t[i+4], "go")
                        change = True
                        ang = ang1
                    elif ang2 < 100 and not change:
                        traj.plot(x_t[i+3],y_t[i+3], "yo")
                        change = True
                        ang = ang2
                    else : 
                        change = False
                        ang=ang2
                    agl.append(ang)
                    print(ang)



        fig.tight_layout()
        

        nameID = getValue(csvID,'subject')
        dateID = getValue(csvID, 'date')[:-5]

        filename = csvID.split('DLC')[0]
        filename = filename.split('/')[-1]
        resDir = 'C:/Users/malassis/Desktop/Analyse video/Kappa'
        if not os.path.exists(resDir) :
            os.makedirs(resDir)

        plt.savefig(resDir + '/'+ str(o) + '-generalised.png')  
        plt.close()
        liste_csv.append(file)
        o = o+1
    except:
        cacahuete = max(cacahuete-1,0)
        random_numbers[cacahuete]= random.sample(range(0,len(fileR)), 1)[0]


pd.DataFrame(liste_csv).to_csv("liste_kappa.csv",sep=",", index=False)







    
                    

                







                
                    

        


    
        