# Velux
Custom component of velux (KLF200) integration for Home Assistant

Copy this repository into HACS as custom_component for Integration category.

Component can be setup via Integrations page.

For troubleshooting enable logger for pyvlx at your configuration.yaml as follows: 

    logger:
      default: warning
      logs:
        pyvlx: debug
        custom_components.velux: debug

In order to avoid connection problems after updates or reboots of Home Assistant create an automation as follows:

    alias: KLF reboot on hass stop event
    description: Reboots the KLF200 in order to avoid SSL Handshake issue
    trigger:
      - platform: homeassistant
        event: shutdown
    condition: []
    action:
      - service: velux.reboot_gateway
        data: {}
    mode: single