#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  vpnKillSwitch.py
#  A script I use to automatically disable sensitive software if my VPN goes down.
#  it checks both WAN and interfaces to check for VPN status (to be safe)
#  Copyright 2013 Raymond Aarseth 
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

import commands, os, threading, urllib2, sys
import socket
import subprocess
from subprocess import call
from time import time, gmtime, strftime,localtime,sleep
from geolocate import locate
from random import choice
import httplib, urllib
import requests
from termcolor import colored

location_nor = "true"
shut = False
pusher = False


def push(message):
	global pusher
	if pusher:
		pusher = False
		host =(socket.gethostname())
		message = host+ ": " + message
		conn = httplib.HTTPSConnection("api.pushover.net:443")
		conn.request("POST", "/1/messages.json",
		urllib.urlencode({
	    "token": "token",
	    "user": "user",
	    "message": message,
		}), { "Content-type": "application/x-www-form-urlencoded" })
		pusher =True
def close():
	print colored("KIilling deluge","yellow")
	os.system("pkill deluged")
	sleep(.3)
	output = commands.getstatusoutput("pgrep deluged")
	s= os.path.getsize('vpnlogg')
	if s > 5000:
		logg  = open("vpnlogg","w")
	else:
		logg  = open("vpnlogg","a")
	sleep(1)
	status, output = commands.getstatusoutput("pgrep deluged")
	print colored("Tried to kill Deluge, cheking if dead:", "yellow")
	if output !="":
		print colored("\t not dead, trying force","red")
		os.system("kill -9 " + output)
	logg.write("closed at " + strftime("%a, %d %b %Y %X", localtime()) + "\n")
	print colored("\t Deluge is dead","green")
	logg.close()

def openT():
	print colored("opening Deluged and deluge-web")
	status, output = commands.getstatusoutput("pgrep deluged")
	if output == "":
		os.system("deluged &")
	status, outputweb = commands.getstatusoutput("pgrep deluge-web")
	if outputweb == "":
		os.system("deluge-web &")
	s= os.path.getsize('vpnlogg')
	if s > 5000:
		logg  = open("vpnlogg","w")
	else:
		logg  = open("vpnlogg","a")
	logg.write("opened at " + strftime("%a, %d %b %Y %X", localtime()) + "\n")
	logg.close()
	print colored("opened deluged and deluge-web", "green")


def closeVPN():
	print colored("Closing VPN", "yellow")
	status, output = commands.getstatusoutput("sudo nmcli -p con status | grep PIA")
	if output != "" :
		out = output.split()
		if "PIA" in out[0]:
			uuid =  out[3]
			cmd = "sudo nmcli con down uuid ".split()
			cmd.append(uuid) 
			sub = subprocess.Popen(cmd, stdout=subprocess.PIPE)
			output = sub.communicate()[0]
			print colored("closed VPN", "red")
			time.sleep(30)
	else:
		return
		
def internet_on():
	"""checks if internet is on by open a connection to a google server and waiting 1 sec to check for connection. else return false"""
	status, output = commands.getstatusoutput("ping google.com -c 2")
	if ("unknown host" not in output and "Host Unreachable" not in output) and output != "":
		return True
	else:
		print colored("network unrechable", "red")
		print colored("Restarting vpn and see if that helps","yellow")
		closeVPN()
		sleep(60)
		return False

	
def loca():
	""" gets the location, and sets global var location_nor to true if in norway (and closes deluge), and false if not """
	global location_nor
	global shut
	while not (shut):
		try:
			if internet_on():
				loc = locate()
				if isinstance(loc,basestring):
					if "norway" in loc:
						close()
						location_nor = True
					else:
						location_nor = False
			sleep(30)
		
		except Exception,e:
			logg = open("vpnlogg","a")
			logg.write("error: " + str(e) + "\n")
			return 
	if os.path.isfile("/home/vagrant/vagrant.pid"):
		os.remove("/home/vagrant/vagrant.pid")
def ovpn():
	"""starter VPN-tilkobling. må fylle inn UUID'er manuelt
	Bruk 'nmcli -p con' for å finne UUID'er. vil så velge tilfeldig mellom disse. 
	må ha minst en.
	kan kanskje automatiserers?
	"""
	global pusher
	print colored("Starting VPN")
        uuids = ["UUID","UUID1","UUID2" ]

	uuid = choice(uuids)
	commands.getstatusoutput("sudo nmcli con up uuid " + uuid)
	#os.system("sudo nmcli con up uuid " + uuid)
	cnt = 0
	while not checkVPN():
		sleep(3)
		cnt = cnt + 1
		if cnt >= 30:
			break
	if  checkVPN():
		print colored("VPN is running","green")
		openT()
		pusher = True
		push(" VPN is running")
	else:
		print colored("Failed to start VPN","red")
def checkVPN():
	status, output = commands.getstatusoutput("ls /sys/class/net/ | grep -E 'tun|ppp'")
	return ("ppp" in output) or ("tun" in output)



def main():
	""" Starts location check
		then checks if vpn is connected. Closes deluge if no VPN.
		opens deluge if VPN connected AND Location outside norway.			
	"""
	pid = str(os.getpid())
	pidfile = "/home/vagrant/interface.pid"

	if os.path.isfile(pidfile):
	    print colored("%s already exist" % pidfile, "yellow")
	    pidn = open(pidfile,"r").read()
	    status, output = commands.getstatusoutput("ps -p " + str(pidn) +" -o comm=")
	    print output
	    if "python" not in output:
	    	os.remove(pidfile)

	else:
	    file(pidfile, 'w').write(pid)
	
	if not checkVPN():
		thread = threading.Thread(target=ovpn)
                thread.start()
		sleep(15)

	threadL = threading.Thread(target=loca)
	threadL.start()
	global location_nor
	global pusher
	pusher = True
	#push(" started script ")
	try:
		if not os.path.isfile("vpnlogg"):
			logg = open("vpnlogg","w")
			logg.close()
			s= os.path.getsize('vpnlogg')
		
		while(True):
			try:
				#check if deluge is running
				status, output = commands.getstatusoutput("pgrep deluged")
				#check if VPN is runnung
				if not checkVPN():
					#delugeCheck and close if no VPN.
					if output !="": 
						close()
						sleep(1)
                                        print colored("No VPN running!","red")
                                        push(" No VPN")
                                        pusher = False

					#try to start VPN.
					ovpn()
					sleep(10)
				#start deluge if VPN is running, loaction is not in norway, and deluge not running
				if (checkVPN()) and output =="" and not location_nor:
					thread = threading.Thread(target=openT)
					thread.start()
					sleep(5)
				sleep(.1)
			except Exception,e:
				logg = open("logg","a")
				logg.write("error: " + str(e) + "\n")
				
		os.unlink(pidfile)			
	except KeyboardInterrupt:
		global shut
		close()
	        print colored("killing. please wait up to 30 secs to make sure everything closes correctly ","yellow")
		print shut
		shut = True
		threadL.join()
		os.unlink(pidfile)
		os.remove(pidfile)
	        exit(3)
	except Exception,e:
		close()
		os.unlink(pidfile)
		if os.path.isfile(pidfile):
			os.remove(pidfile)
		logg = open("logg","a")
		logg.write("FATAL ERROR: " + str(e) + "  FORCE CLOSE" )
		#status, output = commands.getstatusoutput("/home/vagrant/interface.py")
		exit(2)
if __name__ == '__main__':
	main()
