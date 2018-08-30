#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 20:20:33 2018

@author: Soumya/Arima
"""
import api
from driver_console import console
def user_menu(user_name):
    """
    Function responsible for displaying user-menu
    once the user is logged in.
    
    Args:
        user_name : Username of the user who logged in.
        
    Returns:
        This function does not return anything.
    """
    try:
        while True:
            print('\n')
            print('---------------------------')
            print(f'Hello {user_name}')
            print('1.Book a ride')
            print('2.Drive for ride-share')
            print('3.See ride history')
            print('4.Logout')
            print('---------------------------')
            
            user_input = input('Enter your choice.......')
            
            if int(user_input) == 1:
                print('\n')
                print('Finding you a ride')
                
                
            elif int(user_input) == 2:
                print('\n')
                print('Drive mode initiated')
                
                print('1.Add a new Car')
                print('2.Select car')
                drive_input = input("Enter your choice......")
                if int(drive_input) ==1:
                    api.add_car(user_name)
                    
                    
                elif int(drive_input) ==2:
                    # Check if user owns a car or not 
                    # If no ask to add car
                    if api.cars_count(user_name) <= 0:
                        print('You need to add a car first!')
                        # Call add car method
                        api.add_car(user_name)
                
                    else:
                        data = api.cars_owned_by(user_name)
                        data = data.data()
                        print('\n')
                        print('Cars...')
                        for i,d in enumerate(data):
                            # +1 as enumerate starts from 0
                            print(str(i+1)+'. '+d['make']+' Plate no:'+d['plate_no']) 
                        car_choice = int(input('Choose car...'))
                        # Change car active to true 
                        api.car_active_change(user_name,
                                              data[car_choice-1]['plate_no'],
                                              True)
                        print('Driving the '+ data[car_choice-1]['make'])
                        
                        # Start Driver console
                        console(user_name,
                                data[car_choice-1]['make'],
                                data[car_choice-1]['plate_no'])                      
                        
            elif int(user_input) == 3:
                print('-----Ride History-----')
                api.ride_history(user_name)
                
            elif int(user_input) == 4:
                print("Logging out.....")
                break
    except:
        print("Something went down.")
    
