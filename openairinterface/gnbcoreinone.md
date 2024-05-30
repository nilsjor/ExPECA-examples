# Gnb-and-Core-in-One Setup

## Core Network

The following instructions are taken from [NR_SA_Tutorial_OAI_CN5G](https://gitlab.eurecom.fr/oai/openairinterface5g/-/blob/develop/doc/NR_SA_Tutorial_OAI_CN5G.md). Check if there is any updates.

1) Start updating and installing requirements
```
apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    --no-install-recommends \
    apt-utils \
    software-properties-common \
    build-essential \
    pkg-config screen git wget curl tar vim unzip net-tools
```

2) Download core network
```
wget -O ~/oai-cn5g.zip https://gitlab.eurecom.fr/oai/openairinterface5g/-/archive/develop/openairinterface5g-develop.zip?path=doc/tutorial_resources/oai-cn5g
unzip ~/oai-cn5g.zip
mv ~/openairinterface5g-develop-doc-tutorial_resources-oai-cn5g/doc/tutorial_resources/oai-cn5g ~/oai-cn5g
rm -r ~/openairinterface5g-develop-doc-tutorial_resources-oai-cn5g ~/oai-cn5g.zip
```
and
```
cd ~/oai-cn5g
docker compose pull
```

3) Add more users by edditing the following files
```
cd ~/oai-cn5g
vim database/oai_db.sql
vim conf/users.conf
```

4) Run core network
```
cd ~/oai-cn5g
docker compose up -d
```

## GNodeB

Following instructions are the instructions in sections 3.1 and 3.2 and 4.1 and 4.2 in [NR_SA_Tutorial_COTS_UE](https://gitlab.eurecom.fr/oai/openairinterface5g/-/blob/develop/doc/NR_SA_Tutorial_COTS_UE.md)
In section 3.1, use git checkout v4.3.0.0 instead of git checkout v4.6.0.0.

1) Install UHD 4.3.0.0
```
cd ~
apt install -y autoconf automake build-essential ccache cmake cpufrequtils doxygen ethtool g++ git inetutils-tools libboost-all-dev libncurses5 libncurses5-dev libusb-1.0-0 libusb-1.0-0-dev libusb-dev python3-dev python3-mako python3-numpy python3-requests python3-scipy python3-setuptools python3-ruamel.yaml
git clone https://github.com/EttusResearch/uhd.git ~/uhd
cd ~/uhd
git checkout v4.3.0.0
cd host
mkdir build
cd build
cmake ../
make -j $(nproc)
make install
ldconfig
uhd_images_downloader
```

2) Build OAI gnb

Get the code
```
cd ~
git clone https://gitlab.eurecom.fr/oai/openairinterface5g.git ~/openairinterface5g
cd ~/openairinterface5g
# git checkout develop
# tested commit:
git checkout 2024.w18
```

Apply the changes specified [here](https://github.com/samiemostafavi/autoran/blob/main/docs/oai-e320.md) by downloading these files
```
curl -o ~/openairinterface5g/radio/USRP/usrp_lib.cpp https://raw.githubusercontent.com/KTH-EXPECA/examples/main/openairinterface/usrp_lib.cpp
curl -o ~/openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf https://raw.githubusercontent.com/KTH-EXPECA/examples/main/openairinterface/gnb.sa.band78.fr1.106PRB.usrpb210.conf
```

Then build the code
```
# Install OAI dependencies
cd ~/openairinterface5g/cmake_targets
./build_oai -I

# Build OAI gNB
cd ~/openairinterface5g/cmake_targets
./build_oai -w USRP --ninja --gNB -C
```

Modify the USRP address (e.g. 10.30.10.6) in the line with `sdr_addrs=`
```
vim ~/openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf
```

3) Run gnb
```
./nr-softmodem -O ../../../targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf --sa --usrp-tx-thread-config 1 -E
```

