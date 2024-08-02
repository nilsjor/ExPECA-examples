# Openairinterface nrUE

Build
```
# Install OAI dependencies
cd ~/openairinterface5g/cmake_targets
./build_oai -I

# Build OAI gNB
cd ~/openairinterface5g/cmake_targets
./build_oai -w USRP --ninja --nrUE -C
```

Run
```
cd ~/openairinterface5g/cmake_targets/ran_build/build/
./nr-uesoftmodem --band 79 -C 4643040000 -r 106 --numerology 1 --ssb 516 --sa -E --uicc0.imsi 001010000000001 --uicc0.nssai_sd 1 --uicc0.dnn openairinterface --usrp-args "mgmt_addr=10.30.10.14,addr=10.30.10.14" --ue-fo-compensation --ue-rxgain 120 --ue-txgain 0 --ue-max-power 0 --edaf-addr /tmp/edaf
```
