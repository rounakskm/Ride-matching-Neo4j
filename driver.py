
"""
Created on Mon Aug 7 02:46:40 2018

@author: Arima/Soumya
"""

import api
import getpass
import time
from py2neo import Graph, Node

user_name = input('Enter driver user_name: ')
pswd = getpass.getpass('Password:')

api.user_login(user_name, pswd)

#api.update_current_location('dmaccarter7d', '4947')

driver = api.get_user_properties(user_name)

source = driver['current_location']
print('Your current location : ', source)

status = False

passenger_uname = ""
passenger_pickup_location = 0

while not status:
    time.sleep(1)
    query = """
    MATCH (passenger:Person)-[ride:REQUEST]->(driver:Person)
    WHERE driver.user_name = {driver_name}
    RETURN ride.pickup_location as pickup_location,
    passenger.user_name as user_name
    """
    requests = api.graph.run(query, driver_name=user_name).data()

    if requests:
        for i,d in enumerate(requests):
            print('User', str(i+1), 'located at pickup location :', d['pickup_location'])
            passenger_pickup_location = d['pickup_location']
            passenger_uname = d['user_name']
            accept = input('Enter "Y" to accept this ride ? ')
            if (accept == "Y" or accept == "y"):
                query = """
                MATCH (passenger:Person)-[ride:REQUEST]->(driver:Person)
                WHERE driver.user_name = {driver_name}
                SET ride.is_accept = {flag}
                """
                api.graph.run(query, driver_name=user_name, flag='Yes')
                status = True


print('Routing to pickup the user ', passenger_uname)

driver_approaching_path = api.map_api.return_shortest_path(driver['current_location'], passenger_pickup_location)

drop_loc = ""
flag = True

while flag:
    query = """
    MATCH (driver:Person)
    WHERE driver.user_name = {driver_name}
    RETURN driver.current_location as current_location
    """
    result = api.graph.run(query, driver_name=user_name)
    loc = result.data()[0]['current_location']
    print('Approaching point', loc, '....')

    if loc == passenger_pickup_location:
        print('Picking up user !!!')
        time.sleep(10)
        query = """
        MATCH (driver:Person)-[d:DROVE]->(passenger:Person)
        WHERE driver.user_name = {driver_name}
        and passenger.user_name = {passenger_name}
        and d.pickup_location = {pickup_location}
        RETURN d.drop_location as drop_location
        """
        result = api.graph.run(query, driver_name=user_name, passenger_name=passenger_uname, pickup_location=passenger_pickup_location)
        drop_loc = result.data()[0]['drop_location']

    if loc == drop_loc:
        print('Dropping user at destination !!!')
        flag = False

    time.sleep(0.5)
