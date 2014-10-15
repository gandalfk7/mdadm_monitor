This script monitors the status of the disks via smartmontools.

Files needed:

mdadm_monitor_config.py
	location: /scripts
	function: the config file, should be completed with your data
	should I touch it?: YES! if you want to receive mails

mdadm_monitor.mailfile
	location: /scripts
	function: the body of the email you'll receive is stored here
	should I touch it?: NO!!!
	
mdadm_monitor.list
	location: /scripts
	function: contains the list of the arrays to test, it gives for granted that those arrays are located in /dev/
	should I touch it?: HELLYEAH! if you want to monitor the arrays

mdadm_monitor.log
	location: /scripts/logs
	function:stores the logs
	should I touch it?: read it sometimes, maybe
