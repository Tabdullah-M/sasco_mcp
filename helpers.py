import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path


def read_fuel_station_records(city: str = None) -> List[Dict[str, Any]]:
    """
    Read fuel station records from the الوسطى Excel file and optionally filter by region.
    
    Args:
        region: Specific region to filter by (e.g., 'Central', 'East'). If None, returns all stations.
        
    Returns:
        List of dictionaries containing fuel station data with the following fields:
        - fuel_station: Name of the station
        - station_status: Whether the station is currently working
        - rfid: Boolean indicating RFID availability
        - smart_cars: Boolean indicating smart cars support
        - diesel: Boolean indicating if diesel is available
        - district: The district (الحي) where the station is located
        - region: The region from the Excel file
    """
    records_path = "data"    
    # Read the specific الوسطى file
    excel_file = records_path / "محطات- الوسطى.xlsx"
    if not excel_file.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_file}")
    
    all_stations = []

    try:
        # Read the Excel file - header is in row 2 (0-indexed)
        df = pd.read_excel(excel_file, header=2)
                
        df = df.drop(columns=['Unnamed: 13', 'Region.1','# of Sites', 'RFID.1', 'Smart Card.1', 'Unnamed: 0', 'SN'], errors='ignore')
        
        # Process each row
        for i, row in df.iterrows():
                
            # Extract relevant columns and normalize the data
            station_data = {
                'region': _get_column_value(row, ['Region', 'region']),
                'city': _get_column_value(row, ['City', "المدينة","city"]),
                'fuel_station': _get_column_value(row, ['Fuel Station Name', 'fuel_station', 'station_name', 'اسم المحطة']),
                'station_status': _normalize_status(_get_column_value(row, ['Status', 'status of the station', 'station_status', 'حالة المحطة'])),
                'rfid': _normalize_boolean(_get_column_value(row, ['Control Service Type', 'RFID', 'rfid'])),
                'smart_cars': _normalize_boolean(_get_column_value(row, ['Smart Card', 'smart cars', 'smart_cars', 'السيارات الذكية'])),
                'diesel': _normalize_boolean(_get_column_value(row, ['Diesel', 'diesel', 'ديزل'])),
                'district': _get_column_value(row, [ 'اسم الحي', 'الحي', 'district', 'area','اسم الحي ']),
                
            }
            # If the station is out of service (status is False) skip it 
            if station_data['station_status'].lower() == 'Not Working'.lower():
                break 

            # Filter by city if specified
            if city and station_data['city']:
                if city.lower() not in station_data['city'].lower():
                    continue
            
            # Only add if we have at least a fuel station name
            if station_data['fuel_station'] and pd.notna(station_data['fuel_station']):
                all_stations.append(station_data)
                
    except Exception as e:
        print(f"Error reading file: {excel_file}: {str(e)}")
    
    return all_stations

def _get_column_value(row: pd.Series, possible_columns: List[str]) -> Any:
    """
    Get value from row using multiple possible column names.
    
    Args:
        row: Pandas Series representing a row
        possible_columns: List of possible column names to try
        
    Returns:
        The value found, or None if no matching column is found
    """
    for col in possible_columns:
        if col in row.index and pd.notna(row[col]):
            return row[col]
    return None

def _normalize_boolean(value: Any) -> Optional[bool]:
    """
    Normalize various boolean representations to True/False/None.
    
    Args:
        value: The value to normalize
        
    Returns:
        Boolean value or None if cannot be determined
    """
    if pd.isna(value) or value is None:
        return None
    
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        value = value.lower().strip()
        if value in ['true', 'yes', 'نعم', '1', 'موجود', 'متوفر']:
            return 'متوفر'
        elif value in ['false', 'no', 'لا', '0', 'غير موجود', 'غير متوفر']:
            return 'غير متوفر'
    
    if isinstance(value, (int, float)):
        return bool(value)
    
    return None

def _normalize_status(value: Any) -> Optional[str]:
    """
    Normalize station status values.
    
    Args:
        value: The status value to normalize
        
    Returns:
        Normalized status string or None
    """
    if pd.isna(value) or value is None:
        return None
    
    if isinstance(value, str):
        value = value.lower().strip()
        if value in ['working', 'active', 'يعمل', 'نشط', 'فعال', 'Automated', 'automated']:
            return 'Working'
        elif value in ['not working', 'inactive', 'لا يعمل', 'غير نشط', 'معطل', 'Not Automated', 'not automated']:
            return 'Not Working'
    
    return str(value)

if __name__ == '__main__':
    # Test each function
    print("Testing fuel station records functions...")
    print("=" * 50)
    
    try:
        # Test 1: read_fuel_station_records() with specific region
        print("1. Testing read_fuel_station_records() with region 'Central'...")
        stations = read_fuel_station_records('Riyadh')
        print(f"Found {len(stations)} stations total")
        
        if stations:
            print("\nFirst station example:")
            for key, value in stations[0].items():
                print(f"  {key}: {value}")
        
        print("\n" + "-" * 30)
        
    except Exception as e:
        print(f"Error testing read_fuel_station_records(): {e}")
        print("-" * 30) 
