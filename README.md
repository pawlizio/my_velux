# my_velux
Custom component of velux (KLF200) integration for Home Assistant

Copy this repository into HACS as custom_component for Integration category.
In your configuration.yaml add the IP and Password (Printed on the back of KLF200) information as follows: 

    my_velux:
      host: "192.168.xxx.xxx"
      password: !secret velux_password

For troubleshooting enable logger for pyvlx at your configuration.yaml as follows: 

    logger:
      default: warning
      logs:
        pyvlx: debug
