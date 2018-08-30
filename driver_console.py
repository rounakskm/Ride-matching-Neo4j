#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 17:50:30 2018

@author: Soumya
"""
import api

def console(user_name,make,plate_no):
    """
    Function responsible for displaying drivers console
    
    Args:
        user_name : Username of the user who logged in.
        make      : Make of the car he is driving
        plate_no  : Plate number of the car he is driving
    Returns:
        This function does not return anything.
    """
    try:
        while True:
            print('\n')
            print('---------------------------')
            print(f'Happy Driving, {user_name}')
            print('1.Check for requests')
            print('2.See drive history')
            print('3.Exit, drive later')
            print('---------------------------')

            user_input = input('Enter your choice.......')
            
            if int(user_input) == 1:
                print('\n')
                print('Checking for requests')
                
                
            elif int(user_input) == 2:
                print('\n')
                print('Drive History...')
                api.drive_history(user_name)
                
            elif int(user_input) == 3:
                print('See ya later.')
                break
            
    except Exception as e:
        print(e)