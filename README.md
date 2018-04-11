# demo_snap7_raspian
This is a project to find out what is possible when we connect a raspberry pi with a Siemens PLC

Origin:
    My company (an automatisation company) asked me to look in to the new Siemens IOT2000
    https://w3.siemens.com/mcms/pc-based-automation/en/industrial-iot/pages/default.aspx
    because we did have an IOT2000. I used a raspberry pi3 that I had laying at home.

The Goal of the demo:
    create a connection from the raspberry Pi to a Siemens PLC
    test that connection
    read and write from the PLC without changing the program of the PLC
    write some small application that can be usefull in the industry
    Give a presentation to the company about the possibilities of a IOT gate

The different steps
    step 1 install raspian
        the first step is to install raspian (Stretch Lite) on the SD-card for the raspberry pi.
        https://www.raspberrypi.org/downloads/raspbian/
        The reason why I used raspian is because I'm personally familiar with it.
        (I do not explain all the steps because there is a lot of documentation on the internet how to do this)

    step 2 get the snap7 libary on the raspbarry pi

        https://sourceforge.net/projects/snap7/files/Snap7-IoT/snap7-iot-arm/


        You can probably also download the zip file from here unzip 
        https://sourceforge.net/projects/snap7/files/1.4.2/
