#! /usr/bin/env python

import subprocess
import os
import time
import sys
import logging
import smtplib
#import smart_monitor_config
from mdadm_monitor_config import *

warning = 0					#this is the variable that triggers the mail, if it's 0 there are no prob, if it's 1 the we have a problem

#sendmail
def sendemail(from_addr, to_addr_list, cc_addr_list,
              subject, message,
              login, password,
              smtpserver='smtp.gmail.com:587'):
    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message
    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()

#define log variables
logger = logging.getLogger('mdadm_monitor')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('/scripts/logs/mdadm_monitor.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
##

#prepare logfile
date = str(os.popen("date").read())		#read the time+date from the os
open('/scripts/mdadm_monitor.mailfile', 'w').close() 	#open file and erase it's content
file = open("/scripts/mdadm_monitor.mailfile", "r+") 	#open file for writing
file.write(date + "\n")				#write the date in the file

#gets the list of the disks to check
fileName=open("/scripts/mdadm_monitor.list")          #open the vm list file
dirty_arrays = [i for i in fileName.readlines()]        #acquire the lines dirty with newlines and spaces
arrays = [item.rstrip() for item in dirty_arrays]          #strips the newline from the elements in the list

#MAIN LOOP:
logger.info("starting md checks")			#logs the start of the main loop
for array in arrays:
	logger.info("checking array: " + array)		#logs the check
	arraystatus = str(os.popen("mdadm -D /dev/" + array + ' | grep \"State :\"').read()) #gets the status of the disk from smartmontools
#	file.write(disk + " status is: " + diskstatus + "\n")
#	diskstatus = "PASSED fail"
	if "#" in array: 
		logger.warning("skipped array: " + array)
		array_nocheck = array.replace("#","")
		arraystatus = str(os.popen("mdadm -D /dev/" + array_nocheck + ' | grep \"State :\"').read())
		file.write(array_nocheck + " array has been skipped from the check, is this ok? mdstat -D: " + "\n")
                arraystatus = str(os.popen("mdadm -D /dev/" + array_nocheck).read())
		file.write(arraystatus + "\n")
		mdstats = str(os.popen("cat /proc/mdstat").read())
                file.write(mdstats + "\n")
		warning = 1
		continue
	#diskstatus = str(os.popen("smartctl -H /dev/" + disk + ' | grep -i \"SMART overall-health self-assessment test result: \"').read())
#TEST	arraystatus = "clean, degraded, recovering"     #uncomment this line to trigger a test  
	if "clean" in arraystatus and not "degraded" in arraystatus and not "recovering" in arraystatus: logger.info(array + " is OK and reports: " + arraystatus)
	else: 
		logger.critical("WARNING ARRAY: " + array + " STATUS: " + arraystatus)
		file.write(array + " IS NOT OK, status: " + "\n")
		file.write(arraystatus + "\n")
		arraystatus = str(os.popen("mdadm -D /dev/" + array).read())
		file.write(arraystatus + "\n")
                mdstats = str(os.popen("cat /proc/mdstat").read())
		file.write(mdstats + "\n")
		warning = 1

file.close() 

with open ("/scripts/mdadm_monitor.mailfile", "r") as myfile:		#reopen the logfile
	mailbody = myfile.read().replace('\n', ' \r ')		#read the logfile and store it in mailbody
myfile.close()

#send email:

#warning = 1

if warning <> 0:
	sendemail(from_addr  = mail_from, 
         	to_addr_list = mail_to,
          	cc_addr_list = mail_cc, 
          	subject      = mail_subj, 
          	message      = str(mailbody), 
          	login        = mail_login, 
          	password     = mail_pass)
