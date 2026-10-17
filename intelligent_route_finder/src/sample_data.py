"""
Sample Datasets and Network Generators
======================================
Designed for M.Tech DSA Project: Intelligent Route Finder
Shortest-Path Optimization Using Graph Algorithms and Min-Heap.

Provides realistic benchmark networks:
1. Smart City Transit / Metro Network (14 stations, multi-route connections)
2. Logistics & Delivery Hubs Network (12 distribution centers & hubs)
3. University Campus Navigation Network (11 academic buildings & facilities)
4. Partitioned / Disconnected Network (Mainland + Isolated Island to test unreachable destinations)
"""

from typing import Dict, List, Tuple
from .graph import Graph


def create_smart_metro_network() -> Graph:
    """
    Creates a comprehensive Smart City Transit & Metro Network.
    Coordinates represent relative 2D positions for realistic spatial mapping.
    """
    g = Graph(name="Metro Transit Network (Smart City)", directed=False)

    # Vertices with 2D coordinates and metadata
    stations = [
        ("Central Station", 50.0, 50.0, "Terminal", "Central transit interchange hub"),
        ("Tech Park", 80.0, 75.0, "Commercial", "IT corridor and tech enterprise zone"),
        ("Financial District", 70.0, 30.0, "Commercial", "Banking & trade headquarters"),
        ("Airport Terminal", 95.0, 90.0, "Airport", "International flight terminal"),
        ("University Square", 25.0, 65.0, "Education", "Main academic zone & student center"),
        ("Waterfront Pier", 15.0, 35.0, "Recreation", "Coastal ferry & leisure boulevard"),
        ("North Gate", 50.0, 85.0, "Suburban", "Northern arterial gateway"),
        ("South End", 45.0, 15.0, "Residential", "Southern residential sector"),
        ("West Ridge", 10.0, 80.0, "Suburban", "Western residential hill district"),
        ("East Bay", 90.0, 45.0, "Industrial", "Cargo port & logistics depot"),
        ("Innovation Valley", 75.0, 60.0, "Tech Hub", "Research labs & startup incubators"),
        ("Midtown Junction", 40.0, 40.0, "Interchange", "Cross-city tram connector"),
        ("Cultural Plaza", 30.0, 45.0, "Civic", "Theaters, museums & historic center"),
        ("Medical Center", 60.0, 65.0, "Healthcare", "Specialty hospital & trauma hub"),
    ]

    for name, x, y, cat, desc in stations:
        g.add_vertex(name, x=x, y=y, category=cat, description=desc)

    # Weighted edges (distance in kilometers)
    routes = [
        ("Central Station", "Tech Park", 6.5, "Metro Line 1 (Blue)"),
        ("Central Station", "Financial District", 4.2, "Metro Line 2 (Red)"),
        ("Central Station", "Midtown Junction", 3.0, "Metro Line 3 (Yellow)"),
        ("Central Station", "North Gate", 5.8, "Metro Line 1 (Blue)"),
        ("Central Station", "Medical Center", 3.5, "Central Loop"),
        ("Tech Park", "Airport Terminal", 4.8, "Airport Express"),
        ("Tech Park", "Innovation Valley", 2.4, "Silicon Avenue"),
        ("Tech Park", "North Gate", 5.1, "Ring Expressway"),
        ("Financial District", "East Bay", 3.9, "Harbor Way"),
        ("Financial District", "South End", 4.6, "Metro Line 2 (Red)"),
        ("Financial District", "Midtown Junction", 3.8, "Commerce Blvd"),
        ("Airport Terminal", "East Bay", 8.2, "Outer Orbital"),
        ("University Square", "West Ridge", 3.7, "College Hill Rd"),
        ("University Square", "North Gate", 6.0, "Northern Connector"),
        ("University Square", "Cultural Plaza", 3.2, "Arts Parkway"),
        ("Waterfront Pier", "Cultural Plaza", 2.8, "Bayview Drive"),
        ("Waterfront Pier", "Midtown Junction", 4.5, "Old Town Tramway"),
        ("Waterfront Pier", "South End", 5.2, "Coastal Highway"),
        ("South End", "Midtown Junction", 4.0, "Greenbelt Way"),
        ("Innovation Valley", "Medical Center", 2.2, "Healthcare Lane"),
        ("Innovation Valley", "East Bay", 5.5, "Freight Corridor"),
        ("Cultural Plaza", "Midtown Junction", 2.0, "Civic Avenue"),
        ("Medical Center", "North Gate", 4.3, "Health Expressway"),
    ]

    for u, v, w, road in routes:
        g.add_edge(u, v, w, road_name=road)

    return g


def create_logistics_network() -> Graph:
    """
    Creates an e-commerce / supply chain distribution network.
    Weights represent average transit time in minutes.
    """
    g = Graph(name="E-Commerce Logistics Network", directed=False)

    hubs = [
        ("Central Fulfillment Hub", 50.0, 50.0, "Warehouse", "Primary automated fulfillment warehouse"),
        ("North Sort Center", 50.0, 80.0, "Sortation", "Sorting facility north division"),
        ("South Sort Center", 50.0, 20.0, "Sortation", "Sorting facility south division"),
        ("East Freight Depot", 80.0, 50.0, "Freight", "Heavy cargo & railway transfer yard"),
        ("West Cross-Dock", 20.0, 50.0, "Cross-Dock", "Rapid transshipment cross-dock"),
        ("Airport Cargo Gate", 85.0, 85.0, "Air Hub", "Air freight express portal"),
        ("Downtown Delivery Node", 40.0, 45.0, "Last-Mile", "Micro-fulfillment downtown depot"),
        ("Suburban Depot Alpha", 20.0, 80.0, "Last-Mile", "North-west last-mile depot"),
        ("Suburban Depot Beta", 80.0, 20.0, "Last-Mile", "South-east last-mile depot"),
        ("Harbor Logistics Yard", 85.0, 35.0, "Maritime", "Sea freight shipping docks"),
        ("Highway Transit Point", 20.0, 25.0, "Transfer", "Interstate freight staging"),
        ("Regional Distribution Ctr", 65.0, 65.0, "Warehouse", "Secondary regional warehouse"),
    ]

    for name, x, y, cat, desc in hubs:
        g.add_vertex(name, x=x, y=y, category=cat, description=desc)

    routes = [
        ("Central Fulfillment Hub", "North Sort Center", 22.0, "Corridor N1"),
        ("Central Fulfillment Hub", "South Sort Center", 24.0, "Corridor S1"),
        ("Central Fulfillment Hub", "East Freight Depot", 20.0, "Corridor E1"),
        ("Central Fulfillment Hub", "West Cross-Dock", 21.0, "Corridor W1"),
        ("Central Fulfillment Hub", "Downtown Delivery Node", 12.0, "Express Link 0"),
        ("Central Fulfillment Hub", "Regional Distribution Ctr", 15.0, "Feeder R1"),
        ("North Sort Center", "Airport Cargo Gate", 18.0, "Aero Expressway"),
        ("North Sort Center", "Suburban Depot Alpha", 25.0, "Perimeter Rd"),
        ("East Freight Depot", "Airport Cargo Gate", 28.0, "Outer Loop"),
        ("East Freight Depot", "Harbor Logistics Yard", 16.0, "Port Expressway"),
        ("East Freight Depot", "Suburban Depot Beta", 22.0, "Industrial Bypass"),
        ("South Sort Center", "Suburban Depot Beta", 24.0, "Southern Ring"),
        ("South Sort Center", "Highway Transit Point", 19.0, "Interstate Highway"),
        ("West Cross-Dock", "Highway Transit Point", 18.0, "State Route 9"),
        ("West Cross-Dock", "Suburban Depot Alpha", 23.0, "West Parkway"),
        ("Downtown Delivery Node", "West Cross-Dock", 17.0, "Metro Arterial"),
        ("Downtown Delivery Node", "South Sort Center", 19.0, "South Connector"),
        ("Regional Distribution Ctr", "Airport Cargo Gate", 21.0, "Direct Airlink"),
        ("Regional Distribution Ctr", "East Freight Depot", 14.0, "Freight Access"),
    ]

    for u, v, w, road in routes:
        g.add_edge(u, v, w, road_name=road)

    return g


def create_campus_network() -> Graph:
    """
    Creates a university campus navigation graph.
    Weights represent walking distance in meters (m).
    """
    g = Graph(name="University Campus Map", directed=False)

    buildings = [
        ("Main Gate", 10.0, 50.0, "Entrance", "Primary security gate and visitor entry"),
        ("Admin Block", 25.0, 50.0, "Administrative", "Registrar and dean's offices"),
        ("Central Library", 40.0, 65.0, "Academic", "Multi-floor research library"),
        ("Computer Science Dept", 55.0, 75.0, "Academic", "CS & AI labs, server rooms"),
        ("Electrical Dept", 60.0, 55.0, "Academic", "Electronics and IoT labs"),
        ("Mechanical Workshop", 75.0, 50.0, "Academic", "Heavy machinery and CAD labs"),
        ("Student Union & Cafe", 40.0, 35.0, "Amenities", "Dining hall and recreation center"),
        ("Sports Complex", 25.0, 20.0, "Sports", "Track, gymnasium and swimming pool"),
        ("Hostel Block A", 85.0, 80.0, "Residential", "Undergraduate dormitories"),
        ("Hostel Block B", 85.0, 25.0, "Residential", "Postgraduate dormitories"),
        ("Research Park", 70.0, 85.0, "Research", "Incubation center and sponsored research"),
    ]

    for name, x, y, cat, desc in buildings:
        g.add_vertex(name, x=x, y=y, category=cat, description=desc)

    pathways = [
        ("Main Gate", "Admin Block", 150.0, "Main Palm Avenue"),
        ("Admin Block", "Central Library", 180.0, "Scholar Walk"),
        ("Admin Block", "Student Union & Cafe", 160.0, "South Promenade"),
        ("Central Library", "Computer Science Dept", 200.0, "Turing Pathway"),
        ("Central Library", "Electrical Dept", 170.0, "Faraday Walk"),
        ("Central Library", "Student Union & Cafe", 140.0, "Central Quad"),
        ("Computer Science Dept", "Research Park", 120.0, "Silicon Corridor"),
        ("Computer Science Dept", "Hostel Block A", 240.0, "North Dorm Way"),
        ("Research Park", "Hostel Block A", 190.0, "Innovators Lane"),
        ("Electrical Dept", "Mechanical Workshop", 160.0, "Engineering Walk"),
        ("Student Union & Cafe", "Sports Complex", 190.0, "Athletics Lane"),
        ("Student Union & Cafe", "Hostel Block B", 260.0, "East Quad Path"),
        ("Mechanical Workshop", "Hostel Block B", 210.0, "South Dorm Way"),
        ("Sports Complex", "Main Gate", 280.0, "Perimeter Jogging Track"),
    ]

    for u, v, w, road in pathways:
        g.add_edge(u, v, w, road_name=road)

    return g


def create_disconnected_network() -> Graph:
    """
    Creates a graph with two disjoint components (Mainland + Isolated Island).
    Essential for testing unreachable vertices, infinite distances, and edge case resilience.
    """
    g = Graph(name="Partitioned Network (Testing Disconnected)", directed=False)

    # Component 1: Mainland
    mainland = [
        ("Mainland Port", 20.0, 50.0, "Mainland", "Coastal shipping town"),
        ("Capital City", 35.0, 70.0, "Mainland", "Metropolitan capital"),
        ("Inland Hub", 45.0, 40.0, "Mainland", "Agricultural transit center"),
        ("Border Outpost", 55.0, 80.0, "Mainland", "Northern border station"),
    ]
    for name, x, y, cat, desc in mainland:
        g.add_vertex(name, x=x, y=y, category=cat, description=desc)

    g.add_edge("Mainland Port", "Capital City", 35.0, "Route 101")
    g.add_edge("Capital City", "Inland Hub", 28.0, "Central Highway")
    g.add_edge("Capital City", "Border Outpost", 42.0, "Northern Pass")
    g.add_edge("Mainland Port", "Inland Hub", 22.0, "Coast Express")

    # Component 2: Isolated Island (Zero connection to Mainland!)
    island = [
        ("Island Lighthouse", 85.0, 75.0, "Island", "Isolated lighthouse station"),
        ("Island Village", 90.0, 45.0, "Island", "Offshore fishing village"),
        ("Island Airport (Closed)", 80.0, 25.0, "Island", "Decommissioned airfield"),
    ]
    for name, x, y, cat, desc in island:
        g.add_vertex(name, x=x, y=y, category=cat, description=desc)

    g.add_edge("Island Lighthouse", "Island Village", 15.0, "Cliff Road")
    g.add_edge("Island Village", "Island Airport (Closed)", 20.0, "Island Highway")

    return g


def get_all_sample_graphs() -> Dict[str, Graph]:
    """Returns dictionary of all sample graphs ready for loading in UI or tests."""
    return {
        "Smart Metro Transit (14 Stations)": create_smart_metro_network(),
        "Logistics & Delivery Hubs (12 Nodes)": create_logistics_network(),
        "University Campus Map (11 Buildings)": create_campus_network(),
        "Disconnected Graph (Mainland & Island)": create_disconnected_network(),
    }
