#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 02:46:40 2018

@author: Soumya/Arima
"""
# Importing libraries
import datetime 
from py2neo import Graph, Node
import map_api 
import sys
import operator
import time

import prediction

# Making Graph object and connecting to server
# We can also add authintication here, will do later

user = ''
p = ''
try:
    f = open("credentials").read()
    user = f.split("\n")[0] + ":"
    p = f.split("\n")[1] + "@"
except IOError:
    print("Credentials file not found. Going with default credentials...")
    pass

try:
    graph = Graph("bolt://{}{}localhost:7687".format(user, p))
    #selector = NodeSelector(graph)
except:
    print('[-] Couldnt connect to graph!!!')
    
cost_per_unit_distance = {}

def add_person():
    """
    Function responsible for adding a user to the database.
    
    Args:
        Function requires no arguments
        
    Returns:
        This function returns True if Person successfully added, 
        else Flase.
    """
    
    try:
        # Create Node for that person
        person = Node('Person')
        
        # Ask user for data and add it in a dictionary
        print('[+] Please enter the following:')
        person['first_name'] = input('First name: ')
        person['last_name'] = input ('Last name: ')
        person['phone_no'] = input('Phone number: ') 
        person['address'] = input('Address: ')
        person['email'] = input('Email: ')
        person['user_name'] = input('Username: ')
        person['password'] = input('Password: ')
        dob = input('Enter DOB (yyyy-mm-dd): ')
        person['dob']  = datetime.date(int(dob[:4]), int(dob[5:7]), int(dob[8:]))
        
        # Current date and time. Use attributes like year, month, date to extract
        person['joined'] = datetime.datetime.now()
        
        # Payment options for now only adding card(credit/debit doesnt matter)
        # We can later add things like paypal and other wallets
        # Leave these attributes blank, we will take this info from user 
        # By calling the add payment method
        # Just hold payment method added flag to false upon creation.
        person['can_pay'] = False
        person['card_no'] = 0
        person['card_exp'] = ''
        person['card_cvv'] = 0
        person['card_type'] = ''
        person['name_on_card'] = ''
        
        # Details about work location so that we can give daily commute 
        # feature (optional can be removed)
        person['work_location'] = ''
        
        person['current_location'] = ''
        
        # Does the person drive as well?
        # False at first can be changed by other function later
        # When we change this attribute make sure to add a relationship between
        # the person and a car node by calling register_car()
        # One person can have multiple cars
        person['is_driver'] = False
        
        # Create that node in the database
        graph.create(person)
        return True
        
    except:
        print('[-] Could not add user. Something went wrong!')
        return False


def add_car(user_name):
    """
    Function responsible for adding a car to the database.
    
    Args:
        user_name : Username of the user who logged in.
        
    Returns:
        This function does not return anything.
    """
    
    try:
        # Create Node for that person
        car = Node('Car')
        
        # Ask user for data and add it in a dictionary
        print('[+] Please enter the following:')
        car['id'] = input('Car id: ')
        car['make'] = input ('Make of the car: ')
        car['model_no'] = input('model_no/name: ') 
        car['year_bought'] = int(input('Year purchased: '))
        car['plate_no'] = input('License plate no: ')
        car['max_capacity'] = int(input('Number of seats: '))
        car['color'] = input('Color of the car: ')
        car['active'] = False
    
        # Create a relationship with the user who added the car
        # query to create relationship
        
        graph.create(car)
        
        query = """
        MATCH (p:Person),(c:Car)
        WHERE p.user_name = {user_name}
        and c.plate_no = {plate_no}
        CREATE (p)-[:OWNS]->(c)
        SET p.is_driver = True
        """
        graph.run(query, user_name=user_name, plate_no=car['plate_no'])
        print('[+] Car aded successfully!!!')
    
    except Exception as e :
        print (e)
        print('[-] Could not create car. Something went wrong!!!')


def user_login(user_name, password):
    """
    Function responsible for loging in a ueser.
    
    Args:
        user_name : Username of the user to be logged in.
        password  : Password of the user to be logged in.
        
    Returns:
        This function returns true if login is successfull 
        else returns false.
    """
    try:
        # Query to retrieve password of corresponding username
        query = """
        MATCH (p:Person)
        WHERE p.user_name = {user_name}
        RETURN p.password as password
        """
    
        data = graph.run(query, user_name=user_name)
        data = data.data()
        
        if len(data) > 0:
            correct_pass = data[0]['password']
        else:
            print('User with username does not exist')
            return False
        
        count = 0
        while count < 3:
            if password == correct_pass:
                print('[+] Login successfull !')
                return True
            else:
                print('[+] Login failed, please try again')
                count += 1
        return False
    except:
        print('[-] Something went wrong!')
    
def cars_owned_by(user_name):
    """
    Function responsible for giving info of cars owned by the user.
    
    Args:
        user_name : Username of the user to be logged in.
        
    Returns:
        This function returns the cars owned by a user
        as a record object (which we loop over later).
    """
    query = """
    match (p:Person)-[:OWNS] ->(c:Car) 
    WHERE p.user_name = {user_name} 
    RETURN c.make as make, c.plate_no as plate_no
    """
    
    data = graph.run(query, user_name=user_name)

    return data


def cars_count(user_name):
    """
    Function responsible for returning number of cars owned by the user.
    
    Args:
        user_name : Username of the user to be logged in.
        
    Returns:
        This function returns the number of cars owned by a user.
    """
    
    query ="""
    MATCH (p:Person)-[:OWNS]->(c:Car) 
    WHERE p.user_name = {user_name} 
    RETURN count(c) as car_count
    """
    
    data = graph.run(query, user_name=user_name)

    return data.data()[0]['car_count']


def car_active_change(user_name, plate_no, status):
    """
    Function responsible for changing the active status of the car.
    
    Args:
        user_name : Username of the user to be logged in.
        plate_no  : Plate number of the car owned by the user
                    It is ensured that the car is owned by the user before
                    function call
        status    : The status we want it to be
        
    Returns:
        This function does not return anything.
    """

    query = """ 
    MATCH (p:Person)-[r:OWNS]->(c:Car)
    WHERE p.user_name = {user_name}
    and c.plate_no = {plate_no}
    SET c.active = {status}
    """
    
    graph.run(query, user_name=user_name, plate_no=plate_no, status=status)


def update_current_location(user_name,location):
    """
    Function responsible for updating the current location of the person.
    
    Args:
        user_name : Username of the user to be logged in.
        location  : Location where the user is at rite now,
                    Could be a tuple (longitude,latitude)
                    Or could be the name of a place on the map.
    Returns:
        This function does not return anything.
    """
    
    query = """ 
    MATCH (p:Person)
    WHERE p.user_name = {user_name}
    SET p.current_location = {loc}
    """
    
    graph.run(query, user_name = user_name, loc = location)
    

def drove(driver_name,passenger_name,drop_location):
    """
    Function responsible for updating the current location of the person.
    Call this function when a driver confirms pickup
    
    Args:
        driver_name    : Username of the driver.
        passenger_name : Username of the passenger.
        
        
    Returns:
        This function does not return anything.
    """
    # Creating the driver-Drove-passenger relationship
    query = """
    MATCH (p:Person) 
    WHERE p.user_name = {driver_name} 
    MATCH (p1:Person) 
    WHERE p1.user_name = {passenger_name} 
    CREATE (p)-[d:DROVE]->(p1)
    """
    graph.run(query,
              driver_name = driver_name,
              passenger_name = passenger_name)
    
    # Creating the query for adding attributes to the relation created
    query ="""
    match (p1:Person)-[d:DROVE]->(p2:Person) 
    where p1.user_name = {driver_name} 
    and p2.user_name = {passenger_name} 
    set d.pickup_location = p2.current_location,
    d.drop_location = {drop_location},
    d.pickup_time = {pickup_time}
    """
    now = datetime.datetime.now()
    
    graph.run(query,
              driver_name = driver_name,
              passenger_name = passenger_name,
              drop_location = drop_location,
              pickup_time = now.ctime())
    
    
def add_drop_time(driver_name,passenger_name):
    """
    Function responsible for updating the drop time for a passenger.
    Call when passenger is dropped. 
    
    Args:
        driver_name    : Username of the driver.
        passenger_name : Username of the passenger.
        
        
    Returns:
        This function does not return anything.
    """
    # Creating the query for adding attributes to the relation created
    query ="""
    match (p1:Person)-[d:DROVE]->(p2:Person) 
    where p1.user_name = {driver_name} 
    and p2.user_name = {passenger_name} 
    set d.drop_time = {drop_time}
    """
    now = datetime.datetime.now()
    
    graph.run(query,
              driver_name = driver_name,
              passenger_name = passenger_name,
              drop_time = now.ctime())
    
    
def change_ride_status(driver_name,passenger_name,status):
    """
    Function responsible for changing the status of the ride. 
    
    Args:
        driver_name    : Username of the driver.
        passenger_name : Username of the passenger.
        
        
    Returns:
        This function does not return anything.
    """
    # Creating the query for adding attributes to the relation created
    query ="""
    match (p1:Person)-[d:DROVE]->(p2:Person) 
    where p1.user_name = {driver_name} 
    and p2.user_name = {passenger_name} 
    set d.ride_status = {status}
    """
    
    graph.run(query,
              driver_name = driver_name,
              passenger_name = passenger_name,
              ride_status = status)
    
    
def add_fare(driver_name,passenger_name,fare):
    """
    Function responsible for changing the status of the ride. 
    
    Args:
        driver_name    : Username of the driver.
        passenger_name : Username of the passenger.
        
        
    Returns:
        This function does not return anything.
    """
    # Creating the query for adding attributes to the relation created
    query ="""
    match (p1:Person)-[d:DROVE]->(p2:Person) 
    where p1.user_name = {driver_name} 
    and p2.user_name = {passenger_name} 
    set d.ride_fare = {ride_fare}
    """
    
    graph.run(query,
              driver_name = driver_name,
              passenger_name = passenger_name,
              ride_fare = fare)


def rate_drive(driver_name,passenger_name):
    """
    Function responsible for rating a ride. 
    
    Args:
        driver_name : Username of the driver.
        
    Returns:
        This function returns the average rating of a driver.
    """
    try:
        rating = input('Rate your ride (1-5): ')
        
        query ="""
        match (p1:Person)-[d:DROVE]->(p2:Person) 
        where p1.user_name = {driver_name} 
        and p2.user_name = {passenger_name} 
        set d.rating = {rating}
        """
        
        graph.run(query, 
                  driver_name = driver_name,
                  passenger_name = passenger_name,
                  rating = rating)
        print("Thank you for rating")
        
    except Exception as e:
        print(e)
        print('Something went wrong while rating')

    
def driver_rating(driver_name):
    """
    Function responsible for calculating the avg rating of a driver. 
    
    Args:
        driver_name    : Username of the driver.
        
    Returns:
        This function returns the average rating of a driver.
    """
    # Creating the query for adding attributes to the relation created
    query ="""
    match (p1:Person)-[d:DROVE]->() 
    where p1.user_name = {driver_name} 
    return avg(d.rating) as avg_rating
    """
    driver_rating = graph.run(query, driver_name = driver_name)
    
    rating = 4
    if driver_rating.data()[0]['avg_rating']:
        rating = driver_rating.data()[0]['avg_rating']

    return rating


def ride_history(passenger_name):
    """
    Function responsible for displaying all the rides taken by the user. 
    
    Args:
        passenger_name : Username of the passenger.
        
    Returns:
        This function prints the list of rides taken by the passenger.
    """
    query = """
    MATCH (passenger:Person)<-[drive:DROVE]-(driver:Person)-[:OWNS]->(car:Car) 
    WHERE passenger.user_name = {passenger_name} 
    RETURN drive.pickup_location as pickup_loc, 
    drive.drop_location as drop_loc,  
    driver.first_name as driver,
    drive.rating as rating,
    drive.ride_fare as fare,
    car.make as car,
    car.plate_no as plate_no
    """
    data = graph.run(query, passenger_name = passenger_name)
    
    for i,d in enumerate(data):
        # +1 as enumerate starts from 0
        print('\n')
        print(str(i+1)+'. '+'From: '+d['pickup_loc']+' To: '+d['drop_loc'])
        print('Driven by: '+d['driver'])
        print('License Plate: '+d['plate_no'])
        print('Car: '+d['car'])
        
        # Attributes that do not exist on the edge yet, will be returned 
        # as None so we can do a check before printing them

        # Rating Given
        if d['rating'] is not None:
            print('Rated: '+str(d['rating'])+'/5')
            
        # Amount paid
        if d['fare'] is not None:
            print('Amount Paid: '+str(d['fare']))
            
        
def drive_history(driver_name):
    """
    Function responsible for displaying the drives completed by the driver. 
    
    Args:
        driver_name : Username of the driver.
        
    Returns:
        This function returns .
    """
    query = """
    MATCH (passenger:Person)<-[drive:DROVE]-(driver:Person)-[:OWNS]->(car:Car)
    WHERE driver.user_name = {driver_name} 
    RETURN drive.pickup_location as pickup_loc, 
    drive.drop_location as drop_loc,  
    passenger.first_name as passenger,
    drive.rating as rating,
    drive.ride_fare as fare,
    car.make as car,
    car.plate_no as plate_no
    """
    data = graph.run(query, driver_name = driver_name)
    
    for i,d in enumerate(data):
        # +1 as enumerate starts from 0
        print(str(i+1)+'. '+'From: '+d['pickup_loc']+' To: '+d['drop_loc'])
        print('Drove: '+d['passenger'])
        print('License Plate: '+d['plate_no'])
        print('Car: '+d['car'])
        
        # Attributes that do not exist on the edge yet, will be returned 
        # as None so we can do a check before printing them

        # Rating Given
        if d['rating'] is not None:
            print('Rated: '+str(d['rating'])+'/5')
            
        # Amount paid
        if d['fare'] is not None:
            print('Amount Paid: '+str(d['fare']))


def initialize_fare():
    """
    Initializes a base fare pricing scheme
    """
    cost_per_unit_distance[('',25)] = 2.5
    cost_per_unit_distance[(26,60)] = 2.0
    cost_per_unit_distance[(60,150)] = 1.5
    cost_per_unit_distance[(150,'')] = 1.15
        
initialize_fare()


def calculate_fare(pickup_location, drop_location):
    """
    Performs calculation of fare based on the given pickup location and requested
    drop location
    """
    distance = map_api.calculate_distance(pickup_location, drop_location)
    fare = 0

    for key in cost_per_unit_distance:
        lower = 0
        upper = sys.maxsize
        if key[0]:
            lower = key[0]
        if key[1]:
            upper = key[1]

        if distance >= lower and distance <= upper:
            fare = cost_per_unit_distance[key]*distance

    return fare


def upload_csv_person(file_name):
    """
    Uploading the user/driver profile information
    """
    data = open(file_name).read()

    for line in data.split("\n")[1:]:
        if (line):
            rows = line.split("\t")
            person = Node('Person')
            person['first_name'] = rows[1]
            person['last_name'] = rows[2]
            person['phone_no'] = rows[5]
            person['address'] = rows[4]
            person['email'] = rows[3]
            person['user_name'] = rows[6]
            person['password'] = rows[7]
            dob = rows[8]
            person['dob']  = datetime.date(int(dob.split("/")[2]), int(dob.split("/")[0]), int(dob.split("/")[1]))
            

            person['joined'] = datetime.datetime.now()
            
            person['can_pay'] = True
            person['card_no'] = rows[9]
            person['card_type'] = rows[10]
            exp_date = rows[13]
            person['card_exp'] = datetime.date(int(exp_date.split("/")[2]), int(exp_date.split("/")[0]), int(exp_date.split("/")[1]))
            person['card_cvv'] = rows[12]
            person['name_on_card'] = rows[11]

            person['work_location'] = ''
            
            person['current_location'] = rows[15]
            
            if rows[14] == 'TRUE':
                person['is_driver'] = True
            else:
                person['is_driver'] = False

            graph.create(person)

#upload_csv_person('data/ActiveUsersT.txt')


def upload_cars(file_name):
    """
    Uploading cars information
    """
    data = open(file_name).read()

    for line in data.split("\n")[1:]:
        if (line):
            car = Node('Car')
            rows = line.split("\t")
            car['id'] = rows[0]
            car['make'] = rows[1]
            car['model_no'] = rows[2]
            car['year_bought'] = rows[3]
            car['plate_no'] = rows[4]
            car['max_capacity'] = int(rows[5])
            car['color'] = rows[6]
            if rows[7] == "TRUE":
                car['active'] = True
            else:
                car['active'] = False

            graph.create(car)

#upload_cars('data/MOCK_DATA_CARS_T.txt')


def upload_user_car_relationship(file_name):
    """
    Uploading historic car relationship information
    """
    data = open(file_name).read()

    for line in data.split("\n")[1:]:
        if (line):
            rows = line.split("\t")
            query = """
            MATCH (p:Person),(c:Car)
            WHERE p.user_name = {user_name}
            and c.id = {car_id}
            CREATE (p)-[:OWNS]->(c)
            SET p.is_driver = True
            """
            graph.run(query, user_name=rows[0], car_id=rows[1])

#upload_user_car_relationship('data/driver-car-relationship.txt')


def upload_historic_user_drive_history(file_name):
    """
    Uploading historic user driving history information
    """
    data = open(file_name).read()

    for line in data.split("\n")[1:]:
        if (line):
            rows = line.split("\t")
            query = """
            MATCH (passenger:Person)
            WHERE passenger.user_name = {passenger_name}
            MATCH (driver:Person)
            WHERE driver.user_name = {driver_name}
            CREATE (passenger)<-[drive:DROVE 
            { pickup_location: {start_location}, 
            drop_location: {end_location},
            rating: {driver_rating},
            pickup_time: {start_time},
            drop_time: {end_time},
            ride_status: {status},
            ride_fare: {fare} }]-(driver)
            """
            data = graph.run(query, passenger_name=rows[1], driver_name=rows[0], 
                start_location=rows[2], end_location=rows[3], driver_rating=rows[4],
                start_time=rows[5], end_time=rows[6], status=rows[7], fare=int(rows[8]))

#upload_historic_user_drive_history('data/load_relationship_data.txt')


def lookup_drivers(user_name):
    """
    Performs a simple lookup on the graph database to find the closest drivers
    near the passenger looking up for rides
    """
    query ="""
    match (p:Person)
    where p.user_name = {user_name} 
    RETURN properties(p)
    """

    user_location = graph.run(query, user_name=user_name).data()

    user_location = user_location[0]['properties(p)']
    query ="""
    match (p:Person)
    where p.is_driver = True
    RETURN properties(p)
    """

    find_drivers = graph.run(query).data()

    drivers = {}
    
    start_time = time.time()

    for driver in find_drivers:
        drivers[map_api.calculate_distance(user_location['current_location'], driver['properties(p)']['current_location'])] = driver['properties(p)']

    print("TIME TO CREATE DICTIONARY: ", time.time()-start_time)

    drivers = sorted(drivers.items(), key=operator.itemgetter(0))
    print(drivers[0])

    print(map_api.calculate_distance(user_location['current_location'], '2477'))

    #print(map_api.calculate_distance(user_location['current_location'], drivers[10]['current_location']))
    return drivers[:10]


def match_drivers(user_name):
    """
    Performing match on drivers who are available and have no passengers currently
    """
    closest_drivers = lookup_drivers(user_name)

    available_drivers = []
    available_drivers_with_riders = []

    for driver in closest_drivers:
        u_name = driver[1]['user_name']
        query ="""
        match (p1:Person)-[d:DROVE]->(p2:Person) 
        where p1.user_name = {driver_name}
        RETURN properties(d), properties(p2)
        """
        result = graph.run(query, driver_name=u_name).data()

        is_another_ride = False
        current_ride = []
        current_person = []
        for i in range(0, len(result)):
            if 'status' not in result[i]['properties(d)']:
                is_another_ride = True
                current_ride.append(result[i]['properties(d)'])
                current_person.append(result[i]['properties(p2)'])

        if is_another_ride:
            if len(current_ride) < 3: # Currently hardcoded. Need to compare it with car capaacity
                available_drivers_with_riders.append((driver, (current_ride, current_person)))
        else:
            available_drivers.append(driver)

    # Finding the predicted rating based current input
    match_by_rating_prediction = {}
    for driver in available_drivers:
        X = []
        X.append(int(driver_rating(driver[1]['user_name'])))
        X.append(driver[0])
        X.append(0)
        y = prediction.predict(X)
        match_by_rating_prediction[y] = driver

    # Sort by predicted rating
    ordered_by_rating = sorted(match_by_rating_prediction.items(), key=operator.itemgetter(0))

    return ordered_by_rating


def match_all_drivers(user_name, source, destination):
    """
    Performing match on all types of rides, both drivers who have no passenger/drivers who
    have passenger in them currently (pooling rides)
    """
    closest_drivers = lookup_drivers(user_name)

    available_all_drivers = []

    for driver in closest_drivers:
        u_name = driver[1]['user_name']
        query ="""
        match (p1:Person)-[d:DROVE]->(p2:Person) 
        where p1.user_name = {driver_name}
        RETURN properties(d), properties(p2)
        """
        result_d, result_p = graph.run(query, driver_name=u_name).data()

        is_another_ride = False
        current_ride = []
        current_person = []
        for i in range(0, len(result_d)):
            if 'status' not in result_d[i]['properties(d)']:
                is_another_ride = True
                current_ride.append(result_d[i]['properties(d)'])
                current_person.append(result_p[i]['properties(p2)'])

        if is_another_ride:
            if len(current_ride) < 3: # Currently hardcoded. Need to compare it with car capaacity
                available_all_drivers.append((driver, (current_ride, current_person)))
        else:
            available_all_drivers.append(driver)

    # Finding the predicted rating based current input
    match_by_rating_prediction = {}
    for driver in available_all_drivers:
        X = []
        X.append(int(driver_rating(driver[1]['user_name'])))
        X.append(driver[0])

        # Adding the reroute distance to calculate the currently pooling riders
        query = """
        MATCH (passenger:Person)<-[drive:DROVE]-(driver:Person)-[:OWNS]->(car:Car)
        WHERE driver.user_name = {driver_name} 
        RETURN drive.pickup_location as pickup_loc, 
        drive.drop_location as drop_loc,  
        passenger.first_name as passenger
        """
        data = graph.run(query, driver_name = driver[1]['user_name'])
        
        previous_source = 0
        previous_drop = 0
        reroute_distance = 0
        for i,d in enumerate(data):
            if (previous_source == 0) and (previous_drop == 0):
                previous_source = int(d['pickup_loc'])
                previous_drop = int(d['drop_loc'])
            else:
                reroute_distance += path_distance_from_node_2(previous_source, previous_drop, int(d['pickup_loc']), int(d['drop_loc']))
                previous_source = int(d['pickup_loc'])
                previous_drop = int(d['drop_loc'])

        reroute_distance += path_distance_from_node_2(previous_source, previous_drop, source, destination)

        X.append(reroute_distance)
        y = prediction.predict(X)
        match_by_rating_prediction[y] = driver

    # Sort by predicted rating
    ordered_by_rating = sorted(match_by_rating_prediction.items(), key=operator.itemgetter(0))

    return ordered_by_rating


def check_driver_pool_availability(user_name):
    """
    Check Driver avaialbility for passenger limit
    """
    query ="""
    match (p1:Person)-[d:DROVE]->(p2:Person) 
    where p1.user_name = {driver_name}
    RETURN properties(d), properties(p2)
    """
    result_d = graph.run(query, driver_name=u_name).data()

    query ="""
    match (p1:Person)-[d:OWNS]->(c:Car) 
    where p1.user_name = {driver_name}
    RETURN properties(c)
    """
    car_props = graph.run(query, driver_name=u_name).data()

    if (car_props[0]['properties(c)'] > len(result_d)):
        return True

    return False


def check_driver_availability(user_name):
    """
    Check if driver has car currently
    """
    query ="""
    match (p1:Person)-[d:OWNS]->(c:Car) 
    where p1.user_name = {driver_name}
    RETURN properties(c)
    """
    car_props = graph.run(query, driver_name=u_name).data()

    if (car_props):
        return True

    return False


def driver_passenger_history(driver_name, passenger_name):
    """
    Return average rating given to a driver by a specific passenger 
    """
    query = """
    MATCH (passenger:Person)<-[drive:DROVE]-(driver:Person)
    WHERE driver.user_name = {driver_name} and
    passenger.user_name = {passenger_name}
    RETURN drive.rating as rating
    """
    data = graph.run(query, driver_name = driver_name, passenger_name=passenger_name)

    average_rating = 0
    for i,d in enumerate(data):
        # Rating Given
        if d['rating'] is not None:
            average_rating += d['rating']
    average_rating = average_rating/1.0*i

    return average_rating


def passenger_rating_history(passenger_name):
    """
    Average rating given by the passenger in his/her ride history 
    """
    query = """
    MATCH (passenger:Person)<-[drive:DROVE]-()
    passenger.user_name = {passenger_name}
    RETURN drive.rating as rating
    """
    data = graph.run(query, passenger_name = passenger_name)

    average_rating = 0
    for i,d in enumerate(data):
        # Rating Given
        if d['rating'] is not None:
            average_rating += d['rating']
    average_rating = average_rating/1.0*i

    return average_rating



def driver_acceptable_score(driver_name, passenger_name):
    """
    Returns a boolean based on a heuristics of whether a given driver will be
    acceptable by the passenger based on the driver-passenger history
    """
    user_specific_average_rating_all = passenger_rating_history(passenger_name)
    user_specific_average_driver_rating = driver_passenger_history(driver_name, passenger_name)

    average_driver_rating = driver_rating(driver_name)

    if ((user_specific_average_rating_all > (average_driver_rating - 0.5)) 
        or (user_specific_average_driver_rating > (average_driver_rating - 1))):
        return True
    return False


def current_user_location(user_name):
    """
    Returns the current user location
    """
    query = """
    MATCH (p:Person)
    WHERE p.user_name = {user_name}
    RETURN p.current_location as location
    """
    data = graph.run(query, user_name = user_name).data()

    return data[0]['location']

def get_user_properties(user_name):
    """
    Returns user profile information/properties given the user name 
    """
    query = """
    MATCH (p:Person)
    WHERE p.user_name = {user_name}
    RETURN properties(p)
    """
    data = graph.run(query, user_name = user_name).data()

    return data[0]['properties(p)']

#match_drivers('rstearng')
