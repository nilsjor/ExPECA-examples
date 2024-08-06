# Openairinterface nrUE

## Core network config

In order to connect nrUE, you need to set dnn as `oai` only on the ue uicc configs. DNN `openairinterface` or `ims` does not work. Othewise you will get `DNN_DENIED` on AMF.

You can download these pre-configured config files (NOTE that `oai_db.sql` is different than the one for COTS UEs)
```
curl -o ~/oai-cn5g/conf/users.conf https://raw.githubusercontent.com/KTH-EXPECA/examples/main/openairinterface/users.conf
curl -o ~/oai-cn5g/database/oai_db.sql https://raw.githubusercontent.com/KTH-EXPECA/examples/main/openairinterface/oai_db_nrue.sql
```

---
### Only if you want static IP:

Refer to [here](https://github.com/KTH-EXPECA/examples/blob/main/openairinterface/gnbcoreinone.md) but becareful of the notes below:

1. On the core network side, when you insert `SessionManagementSubscriptionData` entries, make sure that `sst` and `sd` in each entry is mathed with the uicc config of the nr-uesoftmodem command. Othewise you will get `SUBSCRIPTION_DENIED` on AMF, which is a result of failed subscription data retrival on UDR.
An example of an entry in `SessionManagementSubscriptionData`
```
INSERT INTO `SessionManagementSubscriptionData` (`ueid`, `servingPlmnid`, `singleNssai`, `dnnConfigurations`) VALUES
('001010000000001', '00101', '{\"sst\": 1, \"sd\": \"16777215\"}','{\"oai\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 6,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"},\"staticIpAddress\":[{\"ipv4Addr\": \"10.0.1.2\"}]},\"ims\":{\"pduSessionTypes\":{ \"defaultSessionType\": \"IPV4V6\"},\"sscModes\": {\"defaultSscMode\": \"SSC_MODE_1\"},\"5gQosProfile\": {\"5qi\": 2,\"arp\":{\"priorityLevel\": 15,\"preemptCap\": \"NOT_PREEMPT\",\"preemptVuln\":\"PREEMPTABLE\"},\"priorityLevel\":1},\"sessionAmbr\":{\"uplink\":\"1000Mbps\", \"downlink\":\"1000Mbps\"}}}');
```
For this example, the `sst` and `sd` on the `nr-uesoftmodem` command arguments must be set as `--uicc0.nssai_sst 1 --uicc0.nssai_sd 16777215`.


2. *change one parameter*: Moreover, in the config file, you must change one parameter. It can be done via:
```
cd ~/oai-cn5g
sed -i 's/use_local_subscription_info: yes/use_local_subscription_info: no/g' conf/config.yaml
```
---

## Build
```
# Install OAI dependencies
cd ~/openairinterface5g/cmake_targets
./build_oai -I

# Build OAI nrUE
cd ~/openairinterface5g/cmake_targets
./build_oai -w USRP --ninja --nrUE -C
```


## Run


- Make sure you run gnb with `--gNBs.[0].min_rxtxtime 6`.
- Write down `-C 4643040000 -r 106 --numerology 1 --ssb 516` from the gnb logs and use it here, it prints it early.
- Modify `--usrp-args "mgmt_addr=10.30.10.4,addr=10.30.10.4"`
- Modify `--uicc0.imsi 001010000000001` and becareful about `--uicc0.dnn oai --uicc0.nssai_sst 1 --uicc0.nssai_sd 1677721`.
- There two we usually dont change: `--uicc0.opc c42449363bbad02b66d16bc975d77cc1  --uicc0.key fec86ba6eb707ed08905757b1bb44b8f`.

```
cd ~/openairinterface5g/cmake_targets/ran_build/build/
./nr-uesoftmodem --band 79 -C 4643040000 -r 106 --numerology 1 --ssb 516 --sa -E --uicc0.imsi 001010000000001 --uicc0.dnn oai --uicc0.nssai_sst 1 --uicc0.nssai_sd 16777215  --uicc0.opc c42449363bbad02b66d16bc975d77cc1  --uicc0.key fec86ba6eb707ed08905757b1bb44b8f --usrp-args "mgmt_addr=10.30.10.4,addr=10.30.10.4" --ue-fo-compensation --ue-rxgain 115 --ue-txgain 0 --ue-max-power 0
```

## Add Routes

Add core network subnet route via the gateway which is `10.0.1.1` in case of static address:
```
ip route add 192.168.70.128/26 via 10.0.1.1
```

Ping ext-dn
```
ping 192.168.70.135
```

Ping UPF
```
ping 192.168.70.134
```
