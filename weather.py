#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  weather_for_conky.py
#  same as weather.py, but small fix for static location and print to use with conky
#  
#  Copyright 2013 Raymond Aarseth <raymond@lappy>
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
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#

import requests
import time
import json
def main():
	"""same as weather.py, but small fix for static location and print to use with conky"""
	
	clientid="ClientId"
	loc= "bergen,no"
	r = requests.get("http://api.aerisapi.com/observations/"+ loc +"?client_id="+clientid)
	response = r.json()
	print response
	ob = response['response']['ob']
	out = "%s | %dc" % (ob['weather'].lower(), ob['tempC'])
	out=out.capitalize()
	print out
	r.close()
	
	
if __name__ == '__main__':
	main()

