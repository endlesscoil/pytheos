def gimme_instance():
    import pytheos.discovery

    services = pytheos.discovery.discover()

    if not services:
        print("No services detected!")
    else:
        services[0].connect()

    return services[0]
