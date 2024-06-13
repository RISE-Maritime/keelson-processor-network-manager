# Keelson Processor Network-Manager

Keelson processor for requesting platform configuration and data link tester

```bash
Network-manager, is a tool for checking network health check and stresses test. More coming soon!

options:
  -h, --help            show this help message and exit
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        Log level 10=DEBUG, 20=INFO, 30=WARN, 40=ERROR, 50=CRITICAL 0=NOTSET (default: 30)
  --mode {peer,client}, -m {peer,client}
                        The zenoh session mode. (default: peer)
  --connect CONNECT     Endpoints to connect to, in case multicast is not working. ex. tcp/localhost:7447 (default: None)
  -r REALM, --realm REALM
                        Unique id for a domain/realm ex. rise (default: rise)
  -e ENTITY_ID, --entity-id ENTITY_ID
                        Entity being a unique id representing an entity within the realm ex, boatswain (default: None)
  --trigger {ping,ping_up_down,ping_up,ping_down}
                        Lave empty to only activate the queryable, or specify the test to trigger (default: None)
  --ping-common-key PING_COMMON_KEY
                        Specify the common key expression to each platform {realm}/v{major_version}/{entity_id} (default: None)
  --start-mb START_MB   Start the stress test with this amount of MB (default: 0.0)
  --end-mb END_MB       End the stress test with this amount of MB (default: 10.0)
  --step-mb STEP_MB     Increment the stress test by this amount of MB (default: 1.0)
```

## Functions (TODO:)

### Latency checks

- [X] Query: Latency Ping, Upload, Down & Upload
- [X] Run functions; Latency Ping, Upload, Down & Upload

### Speed test

- [ ] Find max transfer rate in Megabits/second upload and download

### Background/Automated Health Checks

- [ ] Platform of interest getting disconnected from network (Publish ALARM)
  - Should only use a very small amount of network recourses
- [ ] Dependent on available network recourses publish a message telling the messages to be priority and limits

### Platform (Maybe?)

- [ ] Query: Platform description and static configuration


## Quick start

```bash
# Boatswain
python3 bin/main.py --log-level 10 --realm rise --entity-id boatswain 
python3 bin/main.py --log-level 10 --realm rise --entity-id boatswain --trigger ping --ping-common-key rise/v0/ted 
python3 bin/main.py --log-level 10 --realm rise --entity-id boatswain --trigger ping_up_down --ping-common-key rise/v0/ted 

# Ted 
python3 bin/main.py --log-level 10 --realm rise --entity-id ted --trigger ping --ping-common-key rise/v0/boatswain 

python3 bin/main.py --log-level 10 --realm rise --entity-id ted --trigger ping_up_down --ping-common-key rise/v0/ted 
python3 bin/main.py --log-level 10 --realm rise --entity-id ted --trigger ping_up_down --ping-common-key rise/v0/boatswain 


```

## System configuration

Computer should have timeserver NTP configured to **ntp.se**

## Get going with development

Setup for development environment on your own computer:

1) Install [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
   - Docker desktop will provide you with an UI for monitoring and controlling docker containers and images along debugging 
   - If you want to learn more about docker and its building blocks of images and containers checkout [Docker quick hands-on in guide](https://docs.docker.com/guides/get-started/)
2) Start up of **Zenoh router** either in your computer or any other computer within your local network 

   ```bash
    # Navigate to folder containing docker-compose.zenoh-router.yml
  
    # Start router with log output 
    docker-compose -f containing docker-compose.zenoh-router.yml up

    # If no obvious errors, stop container "ctrl-c"

    # Start container and let it run in the background/detached (append -d) 
    docker-compose -f containing docker-compose.zenoh-router.yml up -d
   ```

    [Link to --> docker-compose.zenoh-router.yml](docker-compose.zenoh-router.yml)

1) Now the Zenoh router is hopefully running in the background and should be available on localhost:8000. This can be example tested with [Zenoh Rest API ](https://zenoh.io/docs/apis/rest/) or continue to next step running Python API
2) Set up python virtual environment  `python >= 3.11`
   1) Install package `pip install -r requirements.txt`
3)  Now you are ready to explore some example scripts in the [exploration folder](./exploration/) 
    1)  Sample are coming from:
         -   [Zenoh Python API ](https://zenoh-python.readthedocs.io/en/0.10.1-rc/#quick-start-examples)


[Zenoh CLI for debugging and problem solving](https://github.com/RISE-Maritime/zenoh-cli)

