import xml.etree.ElementTree as ET

def modify_vehicle_numbers(xml_file, output_file, pkw_num, bus_num, bike_num, scooter_num):
    """
    Modify the number of vehicles in each <flow> tag of an XML file based on function arguments.

    :param xml_file: Path to the input XML file.
    :param output_file: Path to save the modified XML.
    :param pkw_num: New number for passenger cars (pkw).
    :param bus_num: New number for buses.
    :param bike_num: New number for bikes.
    :param scooter_num: New number for scooters.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Dictionary mapping vehicle types to the new numbers
    new_numbers = {
        "pkw": pkw_num,
        "bus": bus_num,
        "bike": bike_num,
        "scooter": scooter_num
    }

    # Iterate over all <flow> elements
    for flow in root.findall('flow'):
        vehicle_type = flow.get('type')  # Get vehicle type
        if vehicle_type in new_numbers:
            flow.set('number', str(new_numbers[vehicle_type]))  # Update the number attribute

    # Save the modified XML
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"Updated XML saved to {output_file}")

# Example Usage
input_xml = "routes.xml"      # Replace with your actual XML file path
output_xml = "modified_routes.xml"

# Example: Pass new values as function arguments
modify_vehicle_numbers(input_xml, output_xml, pkw_num=50, bus_num=120, bike_num=40, scooter_num=350)
