
"""
Created on Mon Aug 7 02:46:40 2018

@author: Arima/Soumya
"""

import api
import getpass
import time

user_name = input('Enter user_name: ')
pswd = getpass.getpass('Password:')

api.user_login(user_name, pswd)

#api.update_current_location('dmaccarter7d', '4947')

person = api.get_user_properties(user_name)

source = person['current_location']
print('Your current location : ', source)

dest = input('Where would you like to go? :')

print('Looking for rides ..... ')

available_drivers = api.match_drivers(user_name)

driver = None
for i in range(0, range(available_drivers)):
	driver = available_drivers[i][1][1]

print('Matching you to closest driver ', driver['user_name'])



driver_approaching_path = api.map_api.return_shortest_path(driver['current_location'], person['current_location'])

a = len(driver_approaching_path.nodes) - 1
d = 0
while (d < a):
	i = 0
	distance = int(round(api.map_api.calculate_distance(driver_approaching_path.nodes[d]['node_id'], driver_approaching_path.nodes[d+1]['node_id'])))
	while (i < distance):
		print('Approaching point', driver_approaching_path.nodes[d+1]['node_id'], '....')
		time.sleep(0.5)
		i += max(5, distance/5)
	api.update_current_location(driver['user_name'],driver_approaching_path.nodes[d+1]['node_id'])
	print('Reached checkpoint', driver_approaching_path.nodes[d+1]['node_id'])
	d += 1

print('Picking up user !!!')
api.drove(driver['user_name'], user_name, dest)

#api.change_ride_status(driver['user_name'], user_name, "Driving")

ride_path = api.map_api.return_shortest_path(source, dest)
#Keep Updating as you reach a node
a = len(ride_path.nodes) - 1
d = 0
while (d < a):
	i = 0
	distance = int(round(api.map_api.calculate_distance(ride_path.nodes[d]['node_id'], ride_path.nodes[d+1]['node_id'])))
	while (i < distance):
		print('Approaching point', ride_path.nodes[d+1]['node_id'], '....')
		time.sleep(0.5)
		i += max(5, distance/5)
	api.update_current_location(driver['user_name'],ride_path.nodes[d+1]['node_id'])
	api.update_current_location(user_name,ride_path.nodes[d+1]['node_id'])
	print('Reached point', ride_path.nodes[d+1]['node_id'])
	d += 1
print('Dropping user at destination !!!')
#api.update_current_location(user_name,location):


api.add_drop_time(driver['user_name'], user_name)

#api.change_ride_status(driver['user_name'], user_name, 'Completed')

fare = api.calculate_fare(source, dest)

print('Fare :', fare)
api.add_fare(driver['user_name'], user_name, fare)

api.rate_drive(driver['user_name'], user_name)

