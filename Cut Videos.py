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
from matplotlib import animation
from IPython import display
import pandas as pd


#### Fonctions 
def choseVideo():
    root.sourceVideo = filedialog.askopenfilenames(parent=root, title='Chose the video')
def choseResult():
    root.sourceResult = filedialog.askopenfilenames(parent=root, title='Chose the result file')
def continueButton():
        root.destroy()
def to_second(str_time):
    float_time = float(str_time.split(':')[-2])*60+ float(str_time.split(':')[-1])
    return(float_time)

####### Interface graphique de recuperation de la video + csv
root = tk.Tk()
root.title("PDP Video Cutter")
root.geometry("600x400")



# Title
lblTitle = tk.Label(root,text = "PDP Video Cutter", font = ("Arial",30), foreground = "white", background="#43A047")
lblTitle.place(x=0,y=0,width=600)


#Bouttons

b_choseVideo = tk.Button(root, text = "VIDEO", fg="white",font = ("Arial",6), width = 10, height = 4, bg="#FFC107", command = choseVideo)
b_choseVideo.place(x = 100,y = 100)
b_choseVideo['font']= tk.font.Font(weight="bold")
b_choseVideo.width = 100

b_choseResult = tk.Button(root, text = "PDP RESULT",fg="white",font = ("Arial",6), width = 10, height = 4, bg= "#3F51B5",command = choseResult)
b_choseResult.place(x = 400,y = 100)
b_choseResult['font']= tk.font.Font(weight="bold")
b_choseResult.width = 100

b_continue = tk.Button(root, text = "READY",fg="white",font = ("Arial",6), width = 20, height = 1, bg ="#B71C1C", command = continueButton)
b_continue.place(x = 180, y = 340)
b_continue['font']= tk.font.Font(weight="bold")
b_continue.width = 100

root.mainloop()

fileV = root.sourceVideo

fileV = root.sourceVideo
ret = False

res = pd.read_csv(r"C:\Users\malassis\Desktop\Analyse video\Leipzig_1_test_srt_05-06.csv", sep = ',',encoding='latin-1')

err= []

for file in fileV :
    try : 
        cap = cv2.VideoCapture(file)                
        nframe = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = cap.get(cv2.CAP_PROP_FPS)


        filename = file.split("/")[-1][:-7]
        date = file.split("_")[-1][:-4]
        date = "20"+date.split("-")[-1] +"-" +  date.split("-")[-2] + "-"+ date.split("-")[-3] 
        name = file.split("/")[-1].split("_")[0] 

        sub = res[res["subject"] == name][res["date"] == date]

        timer = sub["timer_rel"].tolist()
        timer_end = sub["timer_rel_end"].tolist()
        tr_count = sub["trials_count"].tolist()
        duration = []
        for i in range(len(timer)):
            timer[i] = to_second(timer[i])
            timer_end[i] = to_second(timer_end[i])
            duration.append((timer_end[i]-timer[i])+2)

        
        for n in range(len(duration)):

            img_array=[]
            cur_frame = int(timer[n]*fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, cur_frame)

            for i in range(int(duration[n]*fps)):
                ret,img = cap.read()
                img_array.append(img)
            height, width, layers = img.shape
            size = (width,height)
                
            resDir = 'C:/Users/malassis/Desktop/Analyse video/Videos_final/'+name+'/'+date
            if not os.path.exists(resDir) :
                os.makedirs(resDir)
            resultV= resDir+'/'+filename+'_'+ str(tr_count[n])+'.mp4'
            
            out = cv2.VideoWriter(resultV,cv2.VideoWriter_fourcc(*'mp4v'), fps, size)
            
            for i in range(len(img_array)):
                out.write(img_array[i])
            out.release()
    except: 
        err.append(file)
        print(file)
        pass



