import os
from fastmcp import FastMCP
from helpers import read_fuel_station_records
import logfire as logger
from dotenv import load_dotenv

load_dotenv() 
logger.configure(
    send_to_logfire="if-token-present",
    token=os.getenv("LOGFIRE_TOKEN"), 
    service_name="sasco-mcp",
    environment="production",  # or "development", "staging", etc.
    console=logger.ConsoleOptions(),  # For local development, False for production
    distributed_tracing=False,
)

def create_mcp_server():
    mcp = FastMCP("Sasco MCP server")
    
    @mcp.tool()
    async def get_fuel_stations(city: str = None) -> str:
        """Get fuel station records from the 'DH37I region.
        
        WHEN TO USE:
        - User asks about fuel stations, gas stations, or E-7'* 'DHBH/
        - User wants to find fuel stations in a specific city
        - User needs information about station services (RFID, smart cars, diesel)
        
        WORKFLOW:
        1. User can optionally specify a city to filter results
        2. Use this tool to get list of fuel stations
        3. Show station information including services and status
        
        Args:
            city: Optional city name to filter stations (e.g., "'D1J'6", "Riyadh")
                 If None, returns all stations from 'DH37I region
        
        Returns:
            List of fuel stations with:
            - fuel_station: Name of the station
            - station_status: Whether the station is currently working
            - rfid: RFID availability status
            - smart_cars: Smart cars support status
            - diesel: Diesel availability status
            - district: The district where the station is located
            - city: The city where the station is located
            - region: The region ('DH37I)
        """
        logger.info(f"Starting get_fuel_stations tool - city: {city}")
        try:
            stations = read_fuel_station_records(city)
            logger.info(f"Successfully completed get_fuel_stations tool - found {len(stations)} stations")
            return stations
        except FileNotFoundError as e:
            logger.error(f"File not found error in get_fuel_stations tool: {str(e)}")
            return f"Error: Required Excel file not found: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in get_fuel_stations tool: {str(e)}")
            return f"Error: Unexpected error occurred: {str(e)}"
    
    return mcp

if __name__ == "__main__":
    mcp = create_mcp_server()
    port = int(os.environ.get('PORT', 8000))
    mcp.run('http', host='0.0.0.0', port=port)