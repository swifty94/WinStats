import datetime
import socket
from subprocess import check_output
import subprocess as sp
import psutil
import os, csv
import logging
import time
global sysname
sysname = socket.gethostname()
FORMAT = '%(asctime)s  %(levelname)s : %(module)s -> %(funcName)s -> %(message)s'
logging.basicConfig(filename=f"{sysname}_SystemInformation.log", level=logging.INFO, format=FORMAT)

class SystemInformation(object):
    
    @staticmethod
    def get_pid(name):
        """
        \n Accepting process name as param
        \n Returning PID of given process name (int)
        \n >>> print(SystemInformation.get_pid("mysqld"))
        \n >>> 1426
        """
        try:        
            for process in psutil.process_iter():
                try:
                    proc = process.as_dict(attrs=['pid', 'name'])
                    if name in proc['name']:
                        pid = proc['pid']
                        logging.info(f"Found PID {pid} for {name}")
                        return int(pid) 
                except (psutil.NoSuchProcess, psutil.AccessDenied , psutil.ZombieProcess) :
                    pass            
        except Exception as e:
            logging.exception(f"EXCEPTION: {e} \n Full stack trace: \n", exc_info=1)
    
    @staticmethod
    def get_ram_usage(pid):
        """
        \n Accepting process PID as param
        \n Returning RAM usage of given PID (float)
        \n >>> print(SystemInformation.get_ram_usage("1426"))
        \n >>> 2.02
        """
        try:
            process = psutil.Process(pid)
            ram = round(process.memory_percent(),2)
            logging.info(f"Calculated RAM {ram} for PID {pid}")
            return float(ram)
        except Exception as e:
            logging.exception(f"EXCEPTION: {e} \n Full stack trace: \n", exc_info=1)

    @staticmethod
    def get_cpu_usage(pid):
        """
        \n Accepting process PID as param
        \n Returning cpu usage of given PID in percent out of total (float)
        \n >>> print(SystemInformation.get_cpu_usage("1426"))
        \n >>> 0.5
        """
        try:
            process = psutil.Process(pid)            
            cpu = process.cpu_times()[0]
            logging.info(f"Calculated CPU usage {cpu} for PID {pid}")
            return float(cpu)
        except Exception as e:
            logging.exception(f"EXCEPTION: {e} \n Full stack trace: \n", exc_info=1)

    @staticmethod
    def evaluate_data():
        """
        \n Evaluating all system related data to a single dict
        \n Dict to be used in SystemInformation.create_report() method
        \n Return - dict
        """
        try:
        # General system related info
            ram = psutil.virtual_memory()
            total_ram = round((ram.total / 1024 / 1024),2)
            free_ram = round((ram.available / 1024 / 1024),2)
            used_ram = round((ram.used / 1024 / 1024),2)
            cpu_total = psutil.cpu_count(logical=True)
            cpu_loadavg = round([x / cpu_total * 100 for x in psutil.getloadavg()][0],2)
            acs_8080 = sp.getoutput("netstat -an|grep -c 8080")
            acs_8181 = sp.getoutput("netstat -an|grep -c 8181")
            acs_8443 = sp.getoutput("netstat -an|grep -c 8443")
            mysql = sp.getoutput("netstat -an|grep -c 3306")
            oracle = sp.getoutput("netstat -an|grep -c 1521")
            logging.info('General system info obtained')
        except Exception as e:
            logging.exception(f"EXCEPTION: {e} \n Full stack trace: \n", exc_info=1)
        # Process specific details
        try:
            iis_pid = SystemInformation.get_pid("w3wp.exe")
            iis_ram = SystemInformation.get_ram_usage(iis_pid)
            iis_cpu = SystemInformation.get_cpu_usage(iis_pid)
            java_pid = SystemInformation.get_pid("java.exe")
            java_ram = SystemInformation.get_ram_usage(java_pid)
            java_cpu = SystemInformation.get_cpu_usage(java_pid)
            mysqld_pid = SystemInformation.get_pid("mysqld.exe")
            mysqld_ram = SystemInformation.get_ram_usage(mysqld_pid)            
            mysqld_cpu = SystemInformation.get_cpu_usage(mysqld_pid)
        except Exception as e:
            logging.exception(f"EXCEPTION: {e} \n Full stack trace: \n", exc_info=1)

        try:
            dictionary = {}
            now = datetime.datetime.now()
            timestampt = now.strftime("%Y-%m-%d-%H:%M:%S")
            fieldnames = ['timestampt','total_ram','free_ram','used_ram','cpu_total','cpu_loadavg','acs_8080','acs_8181','acs_8443','mysql','oracle','iis_ram','iis_cpu','java_ram','java_cpu','mysqld_ram','mysqld_cpu']
            for var in fieldnames:
                dictionary[var] = eval(var)
            
            logging.info('Data for report generated')
            return dictionary
        except Exception as e:
            logging.exception(f"EXCEPTION: {e} \n Full stack trace: \n", exc_info=1)

    @classmethod  
    def create_report(cls):
        """
        \n Creating CSV report of the system health based on SystemInformation.evaluate_data() method outcome
        \n Return - None
        """
        try:            
            report = f"{sysname}_statistics.csv"
            file_exists = os.path.isfile(report)
            fieldnames = ['timestampt','total_ram','free_ram','used_ram','cpu_total','cpu_loadavg','acs_8080','acs_8181','acs_8443','mysql','oracle','iis_ram','iis_cpu','java_ram','java_cpu','mysqld_ram','mysqld_cpu']
            data = SystemInformation.evaluate_data()
            with open(report, 'a', newline='') as csvreport:
                write = csv.DictWriter(csvreport, delimiter=',', lineterminator='\n', fieldnames=fieldnames)
                if not file_exists:
                    write.writeheader()
                write.writerow(data)
                logging.info(f"Done. Report saved to file {report}")
        except Exception as e:
            logging.exception(f"EXCEPTION: {e} \n Full stack trace: \n", exc_info=1)


if __name__ == "__main__":
    while True:
        try:
            logging.info('Main loop start')
            node = SystemInformation()
            node.create_report()
            logging.info('Main loop pause')
            time.sleep(30)            
        except Exception as e:
            logging.exception(f'Exception in main loop {e}')