FROM  centos:centos7
#FROM  --platform=linux/amd64 centos:centos7 

WORKDIR /usr/app

RUN yum update -y && \
    yum install -y python3 && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install python-dotenv && \
    python3 -m pip install -U PyVISA-py PyVISA


#====install rpm & deltarpm====================// 
RUN yum install -y rpm && \
    yum provides applydeltarpm && \
    yum install -y deltarpm && \
    yum install -y unzip 

WORKDIR /usr/app/low_voltage/

COPY low_voltage/lv-HMP .
COPY low_voltage/lv-HMP/.hmp_env .hmp_env
RUN ls -la

#===rpm and zip packages (provided by Pierre) are in driver directory====//
COPY low_voltage/driver/ .

##===install the rsvisa-centos_.rpm package==============//
RUN rpm -ivh --nodeps rsvisa-centos_5.12.1-1.x86_64.rpm && \
    unzip NILinux2019DeviceDrivers.zip && \
    rpm -ivh --nodeps ni-software-2019-19.2.0.49152-0+f0.el7.noarch.rpm 

#===other packages====//
RUN yum install -y libusb && \
    yum install -y libivivisa0 && \
    yum install -y ni-icp.noarch && \
    yum install -y ni-visa && \
    touch /tmp/smap_install_ni_anyway && \
    yum install -y ni-daqmx && \
    yum install -y kernel-devel

COPY requirements ./requirements
RUN python3 -m pip install --no-cache-dir -r requirements/docker.txt

#COPY setup.py .
#RUN python3 -m pip install -e .

