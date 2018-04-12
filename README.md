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

        download the tar file from the following link
        https://sourceforge.net/projects/snap7/files/Snap7-IoT/snap7-iot-arm/
        move that file to your home directory in your raspberry pi
        (you can use this software for that : https://winscp.net)
        after that write this code in the command prompt

            tar -zxvf snap7-full-1.4.2.tar.gz
                        (if this is a different version change the version number)

        You can probably also download the zip file from (not tested)
        https://sourceforge.net/projects/snap7/files/1.4.2/
        (this will have an other name so change the name snap7-full-1.4.2 in all the commands)
        Unzip it and move it to the home folder of you raspberry pi

        This will give you a folder with a lot files.

        go to the folder of snap7-full-1.4.2/build/unix

            cd snap7-full-1.4.2/build/unix

        run the following code
            sudo make –f arm_v7_linux.mk all

            or  sudo make –f arm_v6_linux.mk all
             depending on your system

            - Raspberry PI     (ARM V6)
            - Raspberry PI 2   (ARM V7)
            - Raspberry PI 3   (ARM V7)
            - pcDuino          (ARM V7)
            - BeagleBone Black (ARM V7)
            - CubieBoard 2     (ARM V7)
            - UDOO Quad        (ARM V7)

        copy compiled library to your right lib directories

            sudo cp ../bin/arm_v7-linux/libsnap7.so /usr/lib/libsnap7.so
            sudo cp ../bin/arm_v7-linux/libsnap7.so /usr/local/lib/libsnap7.so


    step3 install the python snap7 wrapper

        #install python pip if you don't have it:
        sudo apt-get install python-pip
        sudo pip install python-snap7

    now your system is ready to communicate with a siemens device

    step4 make your ipadress  static
        there are great tutorial out there.

    step5 ping from raspberry to your plc
        commande line : ping 'IP adress plc'

        if you can ping to your device you can probaly make a connection

    step6 make a connection with the plc

