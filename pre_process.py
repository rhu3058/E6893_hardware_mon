#!/usr/bin/env python

import pyspark
import sys
import os
from datetime import datetime


Log_level = "error"
sc = pyspark.SparkContext()
errors = {}
processed_data = []
events = []

for file in os.listdir(sys.path[0]):
  if "treatment" in file:
    resume_time =[]
    lines = sc.textFile(file)
    resumed = lines.filter(lambda x: "resume" in x.lower())
    resume_time =  resumed.map(lambda x: datetime.strptime(x.split(" ")[0], '%M-%d-%y %H:%M:%S')).collect()
  if file.split(".")[-1] == "log":
    lines = sc.textFile(file)
    error_messages = lines.filter(lambda x: Log_level in x.lower())
    data = error_messages.map(lambda x: (re.match(r"\(([A-Za-z0-9_]+)\)", x).groups()[0],datetime.strptime(x.split(" ")[0], '%m-%d-%y %H:%M:%S'))).collect()
    for c,i in enumerate(data):
      for resume_t in resume_time:
        if (resume_t - i[1]).seconds>0:
          data[c].append(str((resume_t - i[1]).seconds/60))

for event in data:
    with open(event+".event.csv","a") as f:
      f.write(event[1]+","+event[2]+'\n')
