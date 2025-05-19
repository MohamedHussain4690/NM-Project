Project: Urban Planning and Design

This project introduces a complete and modular AI-Powered Urban Planning and Design System to enable smart, data-based decisions in the development of cities, with a specific usage around Aalim College. The system simulates sophisticated urban infrastructures like buildings, roads, zones, and IoT sensors within an integrated and expandable Python environment. It is a core utility for smart city simulation, analysis, and future planning.

Features – Key Functionalities:
1.Modular Urban Plan Modeling: Manage, create, and analyze multiple urban plans with buildings, roads, zones, and IoT sensors.
      2.Dynamic Zoning: Enables multiple types of zones (residential, commercial, industrial, recreational, mixed-use, special purpose) with the option to               associate buildings with zones.
      3.IoT Sensor Integration: Emulates real-time monitoring of the environment by sensors that track traffic flow, air quality, noise, pedestrians, water               levels, and energy consumption.
      4.Geospatial Intelligence: Models geographic coordinates with distance computations and estimated area calculation for land use analytics.


Technology Used – Languages, Tools, and Libraries
Programming Language: Python 3.11+

Libraries & Tools:
uuid, datetime, enum, typing, and json for core functionality and serialization
Object-oriented design principles for modularity and extensibility

How It Works – Project Workflow:
      1.Plan Creation: The system begins by initializing a new urban plan with metadata (name, description).
      2.Zone Definition: The users create geographic zones with polygon boundaries and assign them types (residential, commercial, etc.).
      3.Building & Road Integration: Buildings and roads are created with defined geometries and properties like height, floors, road width, and traffic flow.
      4.Sensor Deployment: IoT sensors are deployed at precise coordinates and fed with simulated or real-time sensor values.
      5.Data Aggregation: All elements are interrelated, supporting sophisticated queries such as filtering buildings based on zone type or tracking traffic             information by sensor.
      6.Demonstration Script: An pre-coded script (demonstrate_system) automatically demonstrates all functionality by emulating a smart city area surrounding             Aalim College.

