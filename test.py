
def test():
    device1 = Devices(name="device1", category="cover")
    device2 = Devices(name="device2", category="toast")
    device3 = Devices(name="device3", category="blind")
    device4 = Devices(name="device4", category="cover")

    categories = {
        "cover",
        "blind"
    }

    devices = [device1, device2, device3, device4]
    
    return [
                SomfyCover(
                    cover, api="api", optimistic=False
                ).name
                for cover in devices
                if cover.category in categories
            ]

class Devices():
    def __init__(self, name, category):
        self.name = name
        self.category = category

class SomfyCover():
    def __init__(self, device, api, optimistic):
            """Initialize the Somfy device."""
            self.name = "Velux %s" % device.name
            self.cover = device
            self.optimistic = optimistic
            self._closed = None

print(test())