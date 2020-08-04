# my_velux
Custom component of velux integration for Home Assistant

Copy this into your custom_components\my_velux folder and update your configuration.yaml as follows:


    my_velux:
      host: "192.168.xxx.xxx"
      password: !secret velux_password

For troubleshooting enable logger for pyvlx within your configuration.yaml as follows: 

    logger:
      default: warning
      logs:
        pyvlx: debug
