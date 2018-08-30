#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 02:46:40 2018

@author: Arima/Soumya
"""
# Importing libraries
import datetime 
from py2neo import Graph, Node, Relationship

from argparse import ArgumentParser
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
except:
    print('[-] Couldnt connect to graph!!!')


'''
Upload data to the graph database
'''

def upload_data(junctions, roads):

    remove_all_junction_nodes('Junction')

    is_success = True
    try:
        for junction in junctions.split("\n"):
            if junction:
                vals = junction.split(" ")
                add_node(vals[0], vals[1], vals[2])
        print('[+] Added all the loaded junctions')
    except:
        is_success = False
    

    if(is_success):
    # Add relationships only if the node addition was successful
        for road in roads.split("\n"):
            if road:
                vals = road.split(" ")
                add_road(vals[1], vals[2], vals[3])
        print('[+] Added all the loaded roads')


'''
Detach and remove all the nodes from the graph of type
'''
def remove_all_junction_nodes(var):

    try:
        query = """
        MATCH (n:Junction) 
        DETACH DELETE n
        """
        graph.run(query)
        return True
    except:
        print('[-] Could not remove the nodes of type {}'.format(var))
        return False
'''
Adding nodes to generate the City node locations representing road junctions

'''

def add_node(node_id, node_x, node_y):

    try:
        # Create Node for that person
        city_node = Node('Junction')
        # Populating new node information 
        city_node['node_id'] = node_id
        city_node['node_x'] = node_x
        city_node['node_y'] = node_y

        graph.create(city_node)
        return True

    except:
        print('[-] Could not add city junction. Something went wrong!')
        #traceback.print_exc()
        return False


'''
Adding road links between city junction
'''

def add_road(node_id1, node_id2, length):

    try:
        query = """
        MATCH (s:Junction) 
        WHERE s.node_id = {node_id1} 
        MATCH (d:Junction) 
        WHERE d.node_id = {node_id2}
        CREATE (s)-[r:ROAD {len:{length}}]->(d)
        """
        graph.run(query, node_id1=node_id1, node_id2=node_id2, length=length)
        return True

    except:
        print('[-] Could not add road. Something went wrong adding relationship!')
        #traceback.print_exc()
        return False


'''
Find the shortest path between two nodes using Djkstras
'''
def return_shortest_path(node1, node2):

    try:
        query = """
        MATCH (start:Junction {node_id: {node_id1}}), (end:Junction {node_id: {node_id2}})
        CALL apoc.algo.dijkstra(start, end, 'ROAD', 'len') YIELD path, weight
        RETURN path, weight
        """
        route = graph.evaluate(query, node_id1=node1, node_id2=node2)
        # print(route.start_node['node_id'])
        # print(route.nodes)
        # print(route.relationships[1].nodes)
        # print(route.relationships[1]['len'])
        return route
    except:
        print('[+] Error finding the shortest path')
        return "No route found"


'''
Given a route, calculate the total distance from source to destination
'''
def calculate_path_distance(path):

    distance = 0.0

    for road in path.relationships:
        distance += float(road['len'])

    return distance


'''
Given a starting point, ending point calculate distance between source and destination
'''
def calculate_distance(start, end):

    path = return_shortest_path(start, end)

    distance = calculate_path_distance(path)

    return distance


'''
Time to pickup rider
Curretly implementing a simple logic off calculating based on a 
average speed unique amoung all nodes in the city 
Not considering the Traffic
'''
def calculate_time_to_pickup(distance):
    
    return distance*15.0/60


'''
Evaluate reroute distance for the path on adding an additional source and destination
'''
def path_distance_from_node(path, source, destination):

    route1 = return_shortest_path(path.start_node['node_id'], source)
    route1_dist = calculate_path_distance(route1)

    route2 = return_shortest_path(source, path.end_node['node_id'])
    route2_dist = calculate_path_distance(route2)

    route3 = return_shortest_path(path.end_node['node_id'], destination)
    route3_dist = calculate_path_distance(route3)

    original_distance1 = calculate_path_distance(path)

    rerouted_distance1 = route1_dist + route2_dist

    original_distance2 = calculate_path_distance(return_shortest_path(source, destination))

    rerouted_distance2 = route2_dist + route3_dist

    return original_distance1, rerouted_distance1, original_distance2, rerouted_distance2


'''
Evaluate reroute distance for the on route source, destination on adding an additional source and destination
'''
def path_distance_from_node_2(onroute_source, onroute_destination, new_source, new_destination):

    path = return_shortest_path(onroute_source, onroute_destination)

    return path_distance_from_node(path, new_source, new_destination)


def reroute_possibility(d_original1, d_reroute1, d_original2, d_reroute2):

    extra_d1 = d_reroute1 - d_original1

    extra_d2 = d_reroute2 - d_original2

    print("EXTRA DISTANCE COVERED FOR USER 1: ", extra_d1)

    print("EXTRA DISTANCE COVERED FOR USER 2: ", extra_d2)

    return (extra_d1 < 0.2*d_original1 and extra_d2 < 0.4*d_original2)



'''
Ride-pooling possibility
'''

def route_intersection_score(u1_source, u1_dest, u2_source, u2_dest):

    u1_route = return_shortest_path(u1_source, u1_dest)

    u2_route = return_shortest_path(u2_source, u2_dest)

    checkpoint = 0
    match_roads = 0
    match_distance = 0
    for u1_path in u1_route.relationships:
        count = 0
        for u2_path in u2_route.relationships:
            if (count < checkpoint):
                count += 1
                continue
            else:
                if ((u1_path.nodes[0]['node_id'] == u2_path.nodes[0]['node_id']) and (u1_path.nodes[1]['node_id'] == u2_path.nodes[1]['node_id'])):
                    match_roads += 1
                    match_distance += float(u1_path['len'])
                    checkpoint = count + 1
                    break
                count += 1

    return match_roads, match_distance



if __name__ == '__main__':

    parser = ArgumentParser(description="Load map to graph")

    parser.add_argument('-j', '--junctions_file', help='Enter the file containing the junction nodes ', required=False, default=None)
    parser.add_argument('-r', '--roads_file', help='Enter the file containing the roads connecting junctions ', required=False, default=None)
    result = parser.parse_args()

    if (result.junctions_file and result.roads_file):
        try:
            junctions = open(result.junctions_file).read()
            roads = open(result.roads_file).read()
        except IOError:
            print("Error reading input files...")
        
        upload_data(junctions, roads)

    path = return_shortest_path('29', '46')

    print(path)
    print(route_intersection_score('29', '46', '34', '46'))

    d_original1, d_reroute1, d_original2, d_reroute2 = path_distance_from_node(path, '34', '51')

    print(reroute_possibility(d_original1, d_reroute1, d_original2, d_reroute2))



