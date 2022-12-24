# E6893_hardware_mon
log based hardware monitoring
The log server is not accessible externally.
The data_process.py can be run separately since the processed data is included. 
data_process.py reads "xxx.event.logs" and predicts the downtime for the latest event, and the result is saved to "output.csv", which can be displayed by the "project.html"
