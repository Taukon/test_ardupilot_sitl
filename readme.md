### docker build
```
$ docker build mavlink -t test_mavlink
$ docker build mavproxy -t test_mavproxy
$ docker build ardupilot_sitl -t test_ardupilot_sitl
$ docker build ardupilot_sitl_gui -t test_ardupilot_sitl_gui
```

### start test
```
$ python test_integrate.py
$ python test_divide.py
```