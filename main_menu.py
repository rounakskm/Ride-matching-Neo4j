#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 02:25:47 2018

@author: Soumya/Arima
"""
import api
import menus

while True:
    print('-----Main Menu-----')
    print('1.Register new user')
    print('2.Login')
    print('3.Exit')
    
    user_input = input('Enter your choice.......')
    
    if int(user_input) == 1:
        print('In Register')
        add_flag = api.add_person()
        if add_flag:
            print ('[+] User added successfully!!!')
        
    elif int(user_input) == 2:
        print('In Login')
        user_name = input('Please enter your username: ')
        password = input('Please enter your password: ')
        flag = api.user_login(user_name, password)
        
        if flag:
            print(f'[+] Login successfull. Welcome {user_name}')
            
            # Ask user for current location
            user_loc = input('Enter your current location: ')
            api.update_current_location(user_name,user_loc)
            # Go to user-menu
            menus.user_menu(user_name)            
            
    elif int(user_input) == 3:
        print("Bye Bye.....")
        break
   
    #print('Do you want to continue')

