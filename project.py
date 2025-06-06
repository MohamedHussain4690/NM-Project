
import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Set


class ZoneType(Enum):
    """Enum representing different urban zone types"""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    RECREATIONAL = "recreational"
    MIXED_USE = "mixed_use"
    SPECIAL_PURPOSE = "special_purpose"


class TrafficDirection(Enum):
    """Enum representing traffic flow directions"""
    ONE_WAY = "one_way"
    TWO_WAY = "two_way"


class IoTSensorType(Enum):
    """Types of IoT sensors available in the urban planning system"""
    TRAFFIC = "traffic"
    AIR_QUALITY = "air_quality"
    NOISE = "noise"
    WEATHER = "weather"
    PEDESTRIAN = "pedestrian"
    WATER_LEVEL = "water_level"
    ENERGY_USAGE = "energy_usage"


class GeoCoordinate:
    """Class to represent a geographical coordinate pair"""

    def __init__(self, latitude: float, longitude: float):
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Invalid latitude: {latitude}. Must be between -90 and 90.")
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Invalid longitude: {longitude}. Must be between -180 and 180.")

        self.latitude = latitude
        self.longitude = longitude

    def __str__(self) -> str:
        return f"({self.latitude}, {self.longitude})"

    def distance_to(self, other: 'GeoCoordinate') -> float:
        """Calculate simple Euclidean distance between two coordinates"""
        # Note: In a production system, you'd use the Haversine formula for better accuracy
        lat_diff = self.latitude - other.latitude
        long_diff = self.longitude - other.longitude
        return (lat_diff**2 + long_diff**2)**0.5


class IoTSensor:
    """Class representing an IoT sensor in the urban environment"""

    def __init__(self, sensor_id: str, sensor_type: IoTSensorType, location: GeoCoordinate):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.location = location
        self.last_reading = None
        self.last_reading_time = None
        self.status = "online"

    def update_reading(self, value, timestamp=None):
        """Update sensor reading with a new value"""
        self.last_reading = value
        self.last_reading_time = timestamp or datetime.now()

    def to_dict(self) -> Dict:
        """Convert sensor data to dictionary for serialization"""
        return {
            "sensor_id": self.sensor_id,
            "type": self.sensor_type.value,
            "location": {
                "latitude": self.location.latitude,
                "longitude": self.location.longitude
            },
            "last_reading": self.last_reading,
            "last_reading_time": self.last_reading_time.isoformat() if self.last_reading_time else None,
            "status": self.status
        }


class Building:
    """Class representing a building in the urban layout"""

    def __init__(self, building_id: str, name: str, polygon: List[GeoCoordinate],
                 height: float, floors: int, zone_type: ZoneType):
        self.building_id = building_id
        self.name = name
        self.polygon = polygon  # Building footprint as a polygon
        self.height = height  # in meters
        self.floors = floors
        self.zone_type = zone_type
        self.attributes = {}  # Additional attributes like year built, energy efficiency, etc.

    @property
    def floor_area(self) -> float:
        """Calculate approximate floor area in square meters"""
        # This is a simplified calculation. In production, use proper polygon area algorithms
        # For a simple polygon, we can use the Shoelace formula
        area = 0
        j = len(self.polygon) - 1

        for i in range(len(self.polygon)):
            area += (self.polygon[j].longitude + self.polygon[i].longitude) * \
                   (self.polygon[j].latitude - self.polygon[i].latitude)
            j = i

        return abs(area / 2.0)

    @property
    def total_area(self) -> float:
        """Calculate total building area across all floors"""
        return self.floor_area * self.floors

    def to_dict(self) -> Dict:
        """Convert building data to dictionary for serialization"""
        return {
            "building_id": self.building_id,
            "name": self.name,
            "polygon": [{"lat": p.latitude, "lng": p.longitude} for p in self.polygon],
            "height": self.height,
            "floors": self.floors,
            "zone_type": self.zone_type.value,
            "floor_area": self.floor_area,
            "total_area": self.total_area,
            "attributes": self.attributes
        }


class Road:
    """Class representing a road in the urban layout"""

    def __init__(self, road_id: str, name: str, path: List[GeoCoordinate],
                 width: float, traffic_direction: TrafficDirection):
        self.road_id = road_id
        self.name = name
        self.path = path  # Line segments forming the road
        self.width = width  # in meters
        self.traffic_direction = traffic_direction
        self.attributes = {}  # Additional attributes like speed limit, road type, etc.

    @property
    def length(self) -> float:
        """Calculate road length by summing segments"""
        total_length = 0
        for i in range(len(self.path) - 1):
            total_length += self.path[i].distance_to(self.path[i+1])
        return total_length

    def to_dict(self) -> Dict:
        """Convert road data to dictionary for serialization"""
        return {
            "road_id": self.road_id,
            "name": self.name,
            "path": [{"lat": p.latitude, "lng": p.longitude} for p in self.path],
            "width": self.width,
            "traffic_direction": self.traffic_direction.value,
            "length": self.length,
            "attributes": self.attributes
        }


class Zone:
    """Class representing a zoning area in the urban layout"""

    def __init__(self, zone_id: str, name: str, polygon: List[GeoCoordinate],
                 zone_type: ZoneType):
        self.zone_id = zone_id
        self.name = name
        self.polygon = polygon  # Polygon defining zone boundaries
        self.zone_type = zone_type
        self.buildings = set()  # Building IDs in this zone
        self.attributes = {}  # Additional zoning attributes

    def add_building(self, building_id: str):
        """Add a building to this zone"""
        self.buildings.add(building_id)

    def remove_building(self, building_id: str):
        """Remove a building from this zone"""
        if building_id in self.buildings:
            self.buildings.remove(building_id)

    def to_dict(self) -> Dict:
        """Convert zone data to dictionary for serialization"""
        return {
            "zone_id": self.zone_id,
            "name": self.name,
            "polygon": [{"lat": p.latitude, "lng": p.longitude} for p in self.polygon],
            "zone_type": self.zone_type.value,
            "buildings": list(self.buildings),
            "attributes": self.attributes
        }


class UrbanPlan:
    """Main class representing an urban plan with all related elements"""

    def __init__(self, plan_id: str, name: str, description: str):
        self.plan_id = plan_id
        self.name = name
        self.description = description
        self.buildings = {}  # Dict of building_id: Building
        self.roads = {}  # Dict of road_id: Road
        self.zones = {}  # Dict of zone_id: Zone
        self.sensors = {}  # Dict of sensor_id: IoTSensor
        self.created_at = datetime.now()
        self.last_modified = datetime.now()

    def add_building(self, building: Building):
        """Add a building to the urban plan"""
        self.buildings[building.building_id] = building
        self.last_modified = datetime.now()

    def add_road(self, road: Road):
        """Add a road to the urban plan"""
        self.roads[road.road_id] = road
        self.last_modified = datetime.now()

    def add_zone(self, zone: Zone):
        """Add a zone to the urban plan"""
        self.zones[zone.zone_id] = zone
        self.last_modified = datetime.now()

    def add_sensor(self, sensor: IoTSensor):
        """Add an IoT sensor to the urban plan"""
        self.sensors[sensor.sensor_id] = sensor
        self.last_modified = datetime.now()

    def remove_building(self, building_id: str):
        """Remove a building from the urban plan"""
        if building_id in self.buildings:
            del self.buildings[building_id]
            # Remove building from its zone
            for zone in self.zones.values():
                zone.remove_building(building_id)
            self.last_modified = datetime.now()

    def get_buildings_by_zone_type(self, zone_type: ZoneType) -> List[Building]:
        """Get all buildings of a specific zone type"""
        return [b for b in self.buildings.values() if b.zone_type == zone_type]

    def get_sensors_by_type(self, sensor_type: IoTSensorType) -> List[IoTSensor]:
        """Get all sensors of a specific type"""
        return [s for s in self.sensors.values() if s.sensor_type == sensor_type]

    def to_dict(self) -> Dict:
        """Convert the entire urban plan to a dictionary for serialization"""
        return {
            "plan_id": self.plan_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "last_modified": self.last_modified.isoformat(),
            "buildings": {bid: building.to_dict() for bid, building in self.buildings.items()},
            "roads": {rid: road.to_dict() for rid, road in self.roads.items()},
            "zones": {zid: zone.to_dict() for zid, zone in self.zones.items()},
            "sensors": {sid: sensor.to_dict() for sid, sensor in self.sensors.items()}
        }

    def save_to_json(self, filename: str):
        """Save the urban plan to a JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, filename: str) -> 'UrbanPlan':
        """Load an urban plan from a JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)

        plan = cls(data['plan_id'], data['name'], data['description'])
        plan.created_at = datetime.fromisoformat(data['created_at'])
        plan.last_modified = datetime.fromisoformat(data['last_modified'])

        # Load buildings
        for bid, bdata in data['buildings'].items():
            polygon = [GeoCoordinate(p['lat'], p['lng']) for p in bdata['polygon']]
            building = Building(
                bid, bdata['name'], polygon, bdata['height'],
                bdata['floors'], ZoneType(bdata['zone_type'])
            )
            building.attributes = bdata['attributes']
            plan.buildings[bid] = building

        # Load roads
        for rid, rdata in data['roads'].items():
            path = [GeoCoordinate(p['lat'], p['lng']) for p in rdata['path']]
            road = Road(
                rid, rdata['name'], path, rdata['width'],
                TrafficDirection(rdata['traffic_direction'])
            )
            road.attributes = rdata['attributes']
            plan.roads[rid] = road

        # Load zones
        for zid, zdata in data['zones'].items():
            polygon = [GeoCoordinate(p['lat'], p['lng']) for p in zdata['polygon']]
            zone = Zone(
                zid, zdata['name'], polygon, ZoneType(zdata['zone_type'])
            )
            zone.buildings = set(zdata['buildings'])
            zone.attributes = zdata['attributes']
            plan.zones[zid] = zone

        # Load sensors
        for sid, sdata in data['sensors'].items():
            location = GeoCoordinate(sdata['location']['latitude'], sdata['location']['longitude'])
            sensor = IoTSensor(
                sid, IoTSensorType(sdata['type']), location
            )
            sensor.last_reading = sdata['last_reading']
            if sdata['last_reading_time']:
                sensor.last_reading_time = datetime.fromisoformat(sdata['last_reading_time'])
            sensor.status = sdata['status']
            plan.sensors[sid] = sensor

        return plan


class UrbanPlanningSystem:
    """Main system class for the AI-Powered Urban Planning and Design system"""

    def __init__(self):
        self.plans = {}  # Dict of plan_id: UrbanPlan
        self.active_plan_id = None

    def create_new_plan(self, name: str, description: str) -> str:
        """Create a new urban plan and set it as active"""
        plan_id = str(uuid.uuid4())
        new_plan = UrbanPlan(plan_id, name, description)
        self.plans[plan_id] = new_plan
        self.active_plan_id = plan_id
        return plan_id

    def load_plan(self, plan_id: str) -> bool:
        """Set an existing plan as active"""
        if plan_id in self.plans:
            self.active_plan_id = plan_id
            return True
        return False

    def get_active_plan(self) -> Optional[UrbanPlan]:
        """Get the currently active urban plan"""
        if self.active_plan_id and self.active_plan_id in self.plans:
            return self.plans[self.active_plan_id]
        return None

    def save_plan_to_file(self, plan_id: str, filename: str) -> bool:
        """Save a specific plan to a JSON file"""
        if plan_id in self.plans:
            self.plans[plan_id].save_to_json(filename)
            return True
        return False

    def load_plan_from_file(self, filename: str) -> str:
        """Load a plan from a JSON file and add it to available plans"""
        plan = UrbanPlan.load_from_json(filename)
        self.plans[plan.plan_id] = plan
        return plan.plan_id


# Example usage demonstration that runs automatically without input
def demonstrate_system():
    # Create a new urban planning system
    system = UrbanPlanningSystem()

    # Create a new plan
    plan_id = system.create_new_plan(
        "Aalim Smart City Development",
        "AI-driven urban planning for sustainable development near Aalim College"
    )

    # Get the active plan
    plan = system.get_active_plan()

    # Create zones
    residential_zone = Zone(
        str(uuid.uuid4()),
        "Aalim Residential Area",
        [
            GeoCoordinate(13.0010, 80.2500),
            GeoCoordinate(13.0020, 80.2500),
            GeoCoordinate(13.0020, 80.2520),
            GeoCoordinate(13.0010, 80.2520)
        ],
        ZoneType.RESIDENTIAL
    )

    commercial_zone = Zone(
        str(uuid.uuid4()),
        "Aalim Commercial Hub",
        [
            GeoCoordinate(13.0030, 80.2530),
            GeoCoordinate(13.0040, 80.2530),
            GeoCoordinate(13.0040, 80.2550),
            GeoCoordinate(13.0030, 80.2550)
        ],
        ZoneType.COMMERCIAL
    )

    # Add zones to plan
    plan.add_zone(residential_zone)
    plan.add_zone(commercial_zone)

    # Create buildings
    residential_building = Building(
        str(uuid.uuid4()),
        "Aalim Smart Apartments",
        [
            GeoCoordinate(13.0012, 80.2505),
            GeoCoordinate(13.0015, 80.2505),
            GeoCoordinate(13.0015, 80.2510),
            GeoCoordinate(13.0012, 80.2510)
        ],
        45.0,  # height in meters
        15,    # floors
        ZoneType.RESIDENTIAL
    )

    commercial_building = Building(
        str(uuid.uuid4()),
        "Aalim Tech Park",
        [
            GeoCoordinate(13.0032, 80.2535),
            GeoCoordinate(13.0038, 80.2535),
            GeoCoordinate(13.0038, 80.2545),
            GeoCoordinate(13.0032, 80.2545)
        ],
        60.0,  # height in meters
        20,    # floors
        ZoneType.COMMERCIAL
    )

    # Add buildings to plan and respective zones
    plan.add_building(residential_building)
    plan.add_building(commercial_building)
    residential_zone.add_building(residential_building.building_id)
    commercial_zone.add_building(commercial_building.building_id)

    # Create roads
    main_road = Road(
        str(uuid.uuid4()),
        "Aalim Main Avenue",
        [
            GeoCoordinate(13.0010, 80.2510),
            GeoCoordinate(13.0040, 80.2540)
        ],
        15.0,  # width in meters
        TrafficDirection.TWO_WAY
    )

    # Add road to plan
    plan.add_road(main_road)

    # Add IoT sensors
    traffic_sensor = IoTSensor(
        str(uuid.uuid4()),
        IoTSensorType.TRAFFIC,
        GeoCoordinate(13.0025, 80.2525)
    )
    traffic_sensor.update_reading({"vehicle_count": 150, "average_speed": 30})

    air_quality_sensor = IoTSensor(
        str(uuid.uuid4()),
        IoTSensorType.AIR_QUALITY,
        GeoCoordinate(13.0020, 80.2515)
    )
    air_quality_sensor.update_reading({"pm25": 35, "pm10": 65, "ozone": 0.04})

    # Add sensors to plan
    plan.add_sensor(traffic_sensor)
    plan.add_sensor(air_quality_sensor)

    # Save the plan to a JSON file
    plan.save_to_json("aalim_smart_city_plan.json")

    # Print summary of the created plan
    print(f"{'=' * 50}")
    print(f"AI-POWERED URBAN PLANNING AND DESIGN SYSTEM")
    print(f"{'=' * 50}")
    print(f"Plan Name: {plan.name}")
    print(f"Description: {plan.description}")
    print(f"Created: {plan.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 50}")
    print(f"URBAN ELEMENTS SUMMARY:")
    print(f"{'=' * 50}")
    print(f"Zones: {len(plan.zones)}")
    print(f"Buildings: {len(plan.buildings)}")
    print(f"Roads: {len(plan.roads)}")
    print(f"IoT Sensors: {len(plan.sensors)}")
    print(f"{'=' * 50}")

    # Print detailed information about the buildings
    print(f"BUILDING DETAILS:")
    print(f"{'=' * 50}")
    for bid, building in plan.buildings.items():
        print(f"Building: {building.name}")
        print(f"  Type: {building.zone_type.value}")
        print(f"  Floors: {building.floors}")
        print(f"  Height: {building.height} meters")
        print(f"  Floor Area: {building.floor_area:.2f} sq meters")
        print(f"  Total Area: {building.total_area:.2f} sq meters")
        print(f"--------------------------------------------------")

    # Print IoT sensor readings
    print(f"REAL-TIME SENSOR DATA:")
    print(f"{'=' * 50}")
    for sid, sensor in plan.sensors.items():
        print(f"Sensor: {sensor.sensor_id} ({sensor.sensor_type.value})")
        print(f"  Location: {sensor.location}")
        print(f"  Last Reading: {sensor.last_reading}")
        print(f"  Reading Time: {sensor.last_reading_time}")
        print(f"  Status: {sensor.status}")
        print(f"--------------------------------------------------")

    print("\nUrban plan successfully created and saved to 'aalim_smart_city_plan.json'")


# Execute the demonstration automatically
if __name__ == "__main__":
    demonstrate_system()
