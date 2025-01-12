import configparser
import socket
from io import StringIO

def write_local_host():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            local_host = s.getsockname()[0]
        return local_host
    except Exception as e:
        return f"Error getting local IP: {e}"


def write_server_config(ip):
    # Read the existing INI file
    config = configparser.ConfigParser()
    config.read('config/api_config.ini')

    # Update values
    config['server_work_2']['host'] = ip


    # Debug: Confirm the update
    print("Updated host:", config['server_work_2']['host'])

    # Write changes back to the file
    with open('config/api_config.ini', 'w', encoding='utf-8') as configfile:
        config.write(configfile)

    print("INI file updated successfully.")


if __name__ == '__main__':
    write_server_config(write_local_host())
    pass
