# A tool to get a local copy of clinical logs
# Author: Runfeng.Huang@iba-group.com
# v1.0

import os 
import sys
import logging
from datetime import date
import ftplib
from datetime import datetime 
import tkinter as tk
import json
from threading import Thread
import re
from tkinter import filedialog
import tkinter.messagebox as tkmessagebox
import webbrowser


#####          Log          #####
#log_level = logging.DEBUG
log_level = logging.INFO
#log_level = logging.WARNING
#log_level = logging.ERROR


#create log directory
log_directory = os.path.join(sys.path[0], "log")
if not os.path.exists(log_directory):
    os.mkdir(log_directory)
log_path = os.path.join(log_directory,'log_grabber.log')
#log config
logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(log_path)], level=log_level,format='%(asctime)s %(message)s')
#####          Log          #####

#####          config          #####
config = {"ftp_host":"","ftp_login_name":"","ftp_login_password":"", "log_file_save_dir":sys.path[0],"clinical_log_dir":"/TCS/runtimeStore/log/output"}
#check config
config_path = os.path.join(sys.path[0], "config.json")
if os.path.exists(config_path):
    with open(config_path,'r') as f: #
        saved_config = json.load(f)
    for config_item_name in config.keys():
        if saved_config.get(config_item_name):
            config.update({config_item_name:saved_config[config_item_name]})
else:
    with open('config.json', 'w') as fp:
        json.dump(config, fp, indent = 4)
if not os.path.exists(config["log_file_save_dir"]):
    config.update({"log_file_save_dir":sys.path[0]})
#####          config          #####


class ftp_handler():
    def __init__(self):
        self.conn = None
    def connect(self,host,login_name,login_password):
        try:
            self.conn = ftplib.FTP(host)
            return self.conn.login(login_name,login_password)
        except ftplib.error_perm:
            logging.error("Wrong password or login name, Unable to connect: "+host)
            return "530 Login incorrect"
        except Exception as e:
            logging.error(e)
            logging.error("Unable to connect: "+host)
            raise
    def cwd(self,path):
        logging.debug(path)
        logging.debug(self.conn.pwd())
        self.conn.cwd(path)
    def list_file_name(self):
        return self.conn.nlst()
    def list_dir(self):
        data = []
        self.conn.dir(data.append)
        for i in data:
            logging.debug(i)
        return data
    def get_file(self,file,path = ''):
        """ File has to be the name of the file """
        try:
            with open(os.path.join(path,file), 'wb') as fp:
                self.conn.retrbinary(f'RETR {file}', fp.write)
        except Exception as e:
            logging.error(f"unable to get file:{self.conn.pwd()+'/'+file}")
            logging.error(e)
        pass
    def upload_file(self,file,path = ''):
        """ File has to be the name of the file """
        try:
            with open(os.path.join(path,file), 'rb') as fp:
                self.conn.retrbinary(f'STOR {file}', fp)
        except Exception as e:
            logging.error(f"unable to upload file:{file}")
            logging.error(e)
    def close(self):
        try:
            self.conn.quit()
            logging.info("FTP connection closed")
        except Exception as e:
            logging.debug(e)


class mcrs3(ftp_handler):
    def __init__(self,config):
        self.config = config
        self.host = self.config["ftp_host"]
        self.log_type_list = ['batch-importer', 'beam-access-point', 'beam-common-process',\
        'bms-tcr-service-screens', 'data-recorder', 'dosimetry-manager', 'mmsfe', \
        'notif-server', 'pms-controller', 'poss-positioning', 'poss-proximity', \
        'process-monitor', 'scanningcontroller-gateway', 'srcundaq', 'status-panel', 'treat-proc', 'yum']
        super().__init__()
    def get_all_log_files_name(self):
        self.log_files_found = []
        self.cwd(self.config["clinical_log_dir"])
        files_found = self.list_file_name()
        for file in files_found:
            if file.split(".")[-1] == "log":
                self.log_files_found.append(file)
        return self.log_files_found
    def get_desired_log_names(self,desired_log_types = []):
        desired_log_names = []
        words_re = re.compile("|".join(desired_log_types))
        self.cwd(self.config["clinical_log_dir"])
        for file in self.log_files_found:
            if words_re.search(file):
                logging.debug("- "+file)
                desired_log_names.append(file)
        return desired_log_names
    def download_desired_logs(self,desired_log_types = [],subfolder = ""):
        downloaded = []
        self.cwd(self.config["clinical_log_dir"])
        for file in self.get_desired_log_names(desired_log_types):
            print(os.path.join(self.config["log_file_save_dir"],subfolder))
            self.get_file(file,path = os.path.join(self.config["log_file_save_dir"],subfolder))
            downloaded.append(file)
        return downloaded
    def config_set(self,**configs):
        self.config.update(configs)
        with open('config.json', 'w') as fp:
            json.dump(self.config, fp, indent = 4)


class log_grabber_UI(tk.Frame):
    def __init__(self, parent, mcrs):
        super().__init__(parent)
        self.mcrs = mcrs
        self.log_file_save_dir = tk.StringVar()
        self.desired_log_types = []
        self.login_frame_init()
        self.log_types_checkbutton_frame_init()
        self.get_logs_button_init()
        self.status_info_box_init()

        self.grid(row = 0, column = 0, sticky = 'nswe')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        #parent.rowconfigure(0, weight=1)


    def login_frame_init(self):
        self.login_frame = tk.LabelFrame(self,text = "Login")
        self.login_frame .grid(row = 0, column = 0, sticky = 'nswe')
        self.host_label = tk.Label(self.login_frame, text = 'Host:', height = 1, font = 12 )
        self.host_entry = tk.Entry(self.login_frame,font = 12)
        self.host_entry.delete(0,'end')
        self.host_entry.insert(0,self.mcrs.config["ftp_host"])
        self.login_label = tk.Label(self.login_frame, text = 'Login:', height = 1, font = 12 )
        self.login_entry = tk.Entry(self.login_frame,font = 12)
        self.login_entry.delete(0,'end')
        self.login_entry.insert(0,self.mcrs.config["ftp_login_name"])
        self.password_label = tk.Label(self.login_frame, text = 'Password:', height = 1, font = 12)
        self.password_entry = tk.Entry(self.login_frame,show="*",font = 12)
        self.password_entry.delete(0,'end')
        self.password_entry.insert(0,self.mcrs.config["ftp_login_password"])
        self.save_to_label = tk.Label(self.login_frame, text = 'Save logs to:', height = 1, font = 12 )
        self.save_to_entry = tk.Entry(self.login_frame,width = 50,font = 12)
        self.save_to_entry.delete(0,'end')
        self.save_to_entry.insert(0,self.mcrs.config["log_file_save_dir"])
        self.save_to_but = tk.Button(self.login_frame, 
                   text="Browse", 
                   command=self.browse_dir_button_callback)  

        self.host_label.grid(row = 0, column = 0, sticky = 'nswe')
        self.host_entry.grid(row = 0, column = 1, sticky = 'nswe',columnspan = 2)
        self.login_label.grid(row = 1, column = 0, sticky = 'nswe')
        self.login_entry.grid(row = 1, column = 1, sticky = 'nswe',columnspan = 2)
        self.password_label.grid(row = 2, column = 0, sticky = 'nswe') 
        self.password_entry.grid(row = 2, column = 1, sticky = 'nswe',columnspan = 2)
        self.save_to_label.grid(row = 3, column = 0, sticky = 'nswe')
        self.save_to_entry.grid(row = 3, column = 1, sticky = 'nswe')
        self.save_to_but.grid(row = 3, column = 2, sticky = 'nswe')
        self.login_frame.columnconfigure(0, weight=0)
        self.login_frame.columnconfigure(1, weight=1)

    def log_types_checkbutton_frame_init(self):
        self.log_types_frame = tk.LabelFrame(self,text = "Select desired log types")
        self.log_types_frame.grid(row = 1, column = 0, sticky = 'nswe')
        self.log_types_checkbuttons = {}
        for c,i in enumerate(self.mcrs.log_type_list):
            value = tk.BooleanVar(value=False)
            check_button = tk.Checkbutton(self.log_types_frame, text=i,font = 9, 
                variable=value,
                onvalue=True, offvalue=False)
            self.log_types_checkbuttons.update({check_button:value})
            #print(check_button.cget("text"))
            check_button.grid(row = c%6, column = c//6, stick = 'w')
    def get_logs_button_init(self):
        self.get_logs_button = tk.Button(self, 
                   text="Get and Save Selected Logs", font = 12,
                   command=self.get_logs_button_callback)
        self.get_logs_button.grid(row = 2, column = 0, sticky = 'nswe',padx = 10,pady =3)
    def get_logs(self):
        self.get_logs_button.config(state= "disable")
        ftp_host = self.host_entry.get()
        ftp_login_name = self.login_entry.get()
        ftp_login_password = self.password_entry.get()
        log_file_save_dir = self.save_to_entry.get()
        today = date.today()
        sub_save_folder_name = today.strftime("%Y-%b-%d")
        if not (ftp_host and ftp_login_name and ftp_login_password):
            tkmessagebox.showerror("Note","Please enter login info")
            self.get_logs_button.config(state= "normal")
            return
        if log_file_save_dir:
            if not os.path.exists(log_file_save_dir):
                try:
                    os.mkdir(log_file_save_dir)
                except Exception as e:
                    logging.error(e)
                    self.status_info_add_line(f"Can not save to {log_file_save_dir}.")
                    self.get_logs_button.config(state= "normal")
                    return
        self.mcrs.config_set(ftp_host=ftp_host,ftp_login_name=ftp_login_name,log_file_save_dir=log_file_save_dir,ftp_login_password=ftp_login_password)
        #create sub folder named after today's date
        actual_save_path = os.path.join(log_file_save_dir,sub_save_folder_name)
        if not os.path.exists(actual_save_path):
            os.mkdir(actual_save_path)
        self.desired_log_types = []
        for k,v in self.log_types_checkbuttons.items():
            if v.get():
                self.desired_log_types.append(k.cget("text"))
        logging.debug(self.desired_log_types)
        try:
            self.status_info_add_line(f"connecting to {ftp_host}...")
            result = self.mcrs.connect(host=ftp_host,login_name=ftp_login_name,login_password=ftp_login_password)
            #530 Login incorrect
            self.status_info_add_line(str(result))
            self.mcrs.get_all_log_files_name()
            self.status_info_add_line("Downloading")
            downloaded = self.mcrs.download_desired_logs(self.desired_log_types,subfolder = sub_save_folder_name)
            self.status_info_add_line("Downloaded to "+actual_save_path+":")
            for i in downloaded:
                self.status_info_add_line(i)
            self.status_info_add_line("Done")
            webbrowser.open(actual_save_path) #open the folder
        except Exception as e:
            logging.error(e)
            self.status_info_add_line(e)
            self.get_logs_button.config(state= "normal") # incase
            #raise e
        self.get_logs_button.config(state= "normal")
        self.mcrs.close()
    def get_logs_button_callback(self):
        #using thread to avoid freeze GUI while requesting data
        get_log_thread = Thread(target=self.get_logs)
        get_log_thread.start()
    def status_info_box_init(self):
        self.status_text_frame = tk.LabelFrame(self,text = "Status")
        self.status_text_frame.grid(row = 3, column = 0, sticky = 'nswe')
        self.status_text = tk.Text(self.status_text_frame,height= 10)
        self.status_text.grid(row = 0, column = 0, sticky = 'nswe')
        self.status_text.config(state="disable")
        self.status_text_frame.columnconfigure(0, weight=1)
        self.status_text_frame.rowconfigure(0, weight=1)
        self.scrollb = tk.Scrollbar(self.status_text_frame, command=self.status_text.yview)
        self.scrollb.grid(row=0, column=1, sticky='nsew')
        self.status_text.config(yscrollcommand=self.scrollb.set)
    def status_info_add_line(self,text):
        self.status_text.config(state="normal")
        self.status_text.insert('end', str(text)+"\n")
        self.status_text.see("end")
        self.status_text.config(state="disable")
    def browse_dir_button_callback(self):
        self.save_to_entry.delete(0,'end')
        dir = filedialog.askdirectory()
        self.log_file_save_dir.set(dir)
        self.save_to_entry.insert(0, dir)
        #print(dir)



def on_closing():
    try:
        pass
    except Exception as e:
        logging.info(e)

    root.destroy()


root = tk.Tk()
root.title("Log Grabber")
mcrs = mcrs3(config)
result = mcrs.connect(host=config['ftp_host'],login_name=config['ftp_login_name'],login_password=config['ftp_login_password'])
mcrs.get_all_log_files_name()
mcrs.download_desired_logs(mcrs.log_type_list,subfolder = "")

#log_grabber = log_grabber_UI(root, mcrs)
#config = {"ftp_host":"","ftp_login_name":"","ftp_login_password":"", "log_file_save_dir":sys.path[0],"clinical_log_dir":"/TCS/runtimeStore/log/output"}
#root.protocol("WM_DELETE_WINDOW", on_closing)
#root.mainloop()
