from pyparticleio.ParticleCloud import ParticleCloud

def _event_call_back(event_data):
    print("Event CallBack: " + str(event_data))

if __name__ == '__main__':
    c = ParticleCloud(username_or_access_token="")

    devices = c.devices_list
    device = [d for d in devices if d.name == "photon-07"][0]
 
    device.subscribe('Light sensor', _event_call_back)
    device.getData('')
    value = input("Enter any key to stop waiting:\n")

    print("Unsubscribing....")
    device.unsubscribe('Light sensor')

    print("Wait for the notification that the listener is unsubscribed....")
    value = input("Enter any key to stop waiting:\n")

    print("Done")
