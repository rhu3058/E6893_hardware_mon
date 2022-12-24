from sklearn.linear_model import LinearRegression 
import pandas as pd 
import numpy as np 
import json
import os
import datetime
import sys

event_data_list = {}
event_list = []
event_time_list = []
event_downtime_list = []


for event in os.listdir(sys.path[0]):
	if len(event.split("."))>2:
		if event.split(".")[-2] == "event":
			data = pd.read_csv(event)
			event_data_list.update({event.split('.')[0]:data})
	#print(data)
def predict_downtime(event,Df):
	Df=Df[['Date','downtime']] 
	Df= Df.dropna()
	Df['d_10'] = Df['downtime'].shift(1).rolling(window=5).mean()
	Df= Df.dropna()
	#print(Df)
	X = Df[['d_10']] 
	X.head()
	y = Df['downtime']
	y.head()
	train_ratio = 1
	train_ratio = int(train_ratio*len(Df)) 
	# Train dataset 
	X_train = X[:train_ratio] 
	y_train = y[:train_ratio]  
	linear = LinearRegression().fit(X_train,y_train)
	predicted_time = str(linear.predict(X[-1:])[0])
	event_time = Df["Date"].iloc[-1]
	print(event,predicted_time)
	event_list.append(event)
	event_time_list.append(event_time)
	event_downtime_list.append(predicted_time)



for k,v in event_data_list.items():
	predict_downtime(k,v)


index_max = max(range(len(event_time_list)), key=event_time_list.__getitem__)

with open("output.csv", "w") as f:
	f.write("cause, downtime\n"+event_list[index_max]+","+event_time_list[index_max]+" - "+event_downtime_list[index_max]+"\n")
print(event_list,event_time_list,event_downtime_list)