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

In order to avoid connection problems after updates or reboots of Home Assistant, the KLF200 will be rebooted automatically on hass stop even.