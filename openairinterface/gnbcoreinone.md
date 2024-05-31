# Gnb-and-Core-in-One Setup

Run these instructions if you start from `samiemostafavi/sshd-dind` container at ExPECA testbed, and have it connected to an SDR already with the address `10.30.10.6` and a 10Gbps SFP connection.

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

3) Add more users by edditing the following files according to the instructions below
```
cd ~/oai-cn5g
vim database/oai_db.sql
vim conf/users.conf
```

in the first one (`database/oai_db.sql`), you need to replicate the `INSERT INTO` lines after this block:
```
--
-- Dumping data for table `AuthenticationSubscription`
--
```
For example the result would be addition of the following (for 3 more users with IMSIs `001010000000005`, `001010000000006`, and `001010000000007`)
```
INSERT INTO `AuthenticationSubscription` (`ueid`, `authenticationMethod`, `encPermanentKey`, `protectionParameterId`, `sequenceNumber`, `authenticationManagementField`, `algorithmId`, `encOpcKey`, `encTopcKey`, `vectorGenerationInHss`, `n5gcAuthMethod`, `rgAuthenticationInd`, `supi`) VALUES
    ('001010000000005', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000005');

INSERT INTO `AuthenticationSubscription` (`ueid`, `authenticationMethod`, `encPermanentKey`, `protectionParameterId`, `sequenceNumber`, `authenticationManagementField`, `algorithmId`, `encOpcKey`, `encTopcKey`, `vectorGenerationInHss`, `n5gcAuthMethod`, `rgAuthenticationInd`, `supi`) VALUES
    ('001010000000006', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000006');

INSERT INTO `AuthenticationSubscription` (`ueid`, `authenticationMethod`, `encPermanentKey`, `protectionParameterId`, `sequenceNumber`, `authenticationManagementField`, `algorithmId`, `encOpcKey`, `encTopcKey`, `vectorGenerationInHss`, `n5gcAuthMethod`, `rgAuthenticationInd`, `supi`) VALUES
    ('001010000000007', '5G_AKA', 'fec86ba6eb707ed08905757b1bb44b8f', 'fec86ba6eb707ed08905757b1bb44b8f', '{\"sqn\": \"000000000000\", \"sqnScheme\": \"NON_TIME_BASED\", \"lastIndexes\": {\"ausf\": 0}}', '8000', 'milenage', 'C42449363BBAD02B66D16BC975D77CC1', NULL, NULL, NULL, NULL, '001010000000007');
```
NOTE: in each entry IMSI value is written twice, make sure to modify both of them. Usually the rest can remain unchanged.

in the second one (`conf/users.conf`) these will be added
```
[001010000000005]
fullname = user5
hassip = yes
context = users
host = dynamic
transport=udp

[001010000000006]
fullname = user6
hassip = yes
context = users
host = dynamic
transport=udp

[001010000000007]
fullname = user7
hassip = yes
context = users
host = dynamic
transport=udp
```

You can add more users. Make sure the IMSIs in these two files match the IMSIs of the simcards in Advantech routers.


4) Run core network
```
cd ~/oai-cn5g
docker compose up -d
```

## GNodeB

Following instructions are the instructions in sections 3.1 and 3.2 and 4.1 and 4.2 in [NR_SA_Tutorial_COTS_UE](https://gitlab.eurecom.fr/oai/openairinterface5g/-/blob/develop/doc/NR_SA_Tutorial_COTS_UE.md)
In section 3.1, we use git checkout v4.3.0.0 instead of git checkout v4.6.0.0.

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

Check the USRP is accessible by running `uhd_find_devices`:
```
root@zun-9039e850-dedf-4fb4-98ad-ad1c1205d1f8-65659c4c99-dmvx5:~# uhd_find_devices
[INFO] [UHD] linux; GNU C++ version 9.4.0; Boost_107100; UHD_4.3.0.HEAD-0-g1f8fd345
--------------------------------------------------
-- UHD Device 0
--------------------------------------------------
Device Address:
    serial: 3238B90
    addr: 10.30.10.6
    claimed: False
    fpga: XG
    mgmt_addr: 10.30.10.6
    name: ni-e320-3238B90
    product: e320
    type: e3xx
```

2) Build OAI gnb

Get the code (we use 2024.w18 commit instead of the latest)
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

