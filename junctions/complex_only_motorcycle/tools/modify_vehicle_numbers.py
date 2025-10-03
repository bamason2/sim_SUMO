import xml.etree.ElementTree as ET

def modify_vehicle_numbers(xml_file, output_file, default_num, LcSpeedGain_num, lcPushy_num, 
                           lcStrategic_num, lcCooperative_num, mingap_num, jmDriveAfterYellowTime_num):
    """
    Modify the number of vehicles in each <flow> tag of an XML file based on function arguments.
        'names': ['default', 'LcSpeedGain ', 'lcPushy ', 'lcStrategic ','lcCooperative ','mingap', 'jmDriveAfterYellowTime'],

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
    # new_numbers = {
    #     "pkw": pkw_num,
    #     "bus": bus_num,
    #     "bike": bike_num,
    #     "scooter": scooter_num
    # }
    new_numbers = {
        "default": default_num,
        "LcSpeedGain": LcSpeedGain_num,
        "lcPushy": lcPushy_num,
        "lcStrategic": lcStrategic_num,
        "lcCooperative": lcCooperative_num,
        "mingap": mingap_num,
    }
    #colors = {"baseline": "#1f77b4", "aggressive": "#ff7f0e", "jumpystyle": "#2ca02c", "chaotic": "#d62728"}

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
modify_vehicle_numbers(input_xml, output_xml, default_num=50, LcSpeedGain_num=120, 
                       lcPushy_num=40, lcStrategic_num=350, lcCooperative_num=60, 
                       mingap_num=80, jmDriveAfterYellowTime_num=90)
