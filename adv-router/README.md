# How to Communicate with Advantech Routers

To configure and see the status of the Advantech routers remotely via command line interface, depending on the functionality you want choose one of the 2 ways:

## 1) Communicate via the script

Download the script on the container which is connected via network to the router. In this instructions we assume the router's IP is `10.42.3.1`.
```
apt-get install jq
curl -LJO -k https://github.com/samiemostafavi/advmobileinfo/raw/main/config_adv.sh
chmod +x config_adv.sh
```

Open the file to modify the parameters, including the password of the router.
```
vim config_adv.sh
./config_adv.sh
```

## 2) Communicate via HTTP request

Get connection information
```
curl "http://10.42.3.1:50500/?query=info"

{"Band":"n78","CSQ":"20","Cell":"7538000","Channel":"650688","Operator":"999 08","PLMN":"99908","RSRP":"-72 dBm","RSRQ":"-11 dB","Registration":"Home Network","Signal Quality":"-11 dB","Signal Strength":"-72 dBm","TAC":"0BC2","Technology":"NR5G"}
```

Turn off the modem
```
curl "http://10.42.3.1:50500/?gsmpwr=0"
```

Turn on the modem
```
curl "http://10.42.3.1:50500/?gsmpwr=1"
```

Check IMSI of the simcard
```
curl "http://10.42.3.1:50500/?query=imsi"

001010000000005
OK
```


Check the bands that the modem can connect to (is capable of connecting to)
```
curl "http://10.42.3.1:50500/?query=policybands"

+QNWPREFCFG: "gw_band",1:2:3:4:5:6:8:9:19
+QNWPREFCFG: "lte_band",1:2:3:4:5:7:8:12:13:14:17:18:19:20:25:26:28:29:30:32:34:38:39:40:41:42:43:46:48:66:71
+QNWPREFCFG: "nsa_nr5g_band",1:2:3:5:7:8:12:14:20:25:28:38:40:41:48:66:71:77:78:79
+QNWPREFCFG: "nr5g_band",1:2:3:5:7:8:12:14:20:25:28:38:40:41:48:66:71:77:78:79
OK
```

Check the bands that the modem is configured to search and connect on each network
The `net` parameter can only be "gw_band", "lte_band", "nsa_nr5g_band", or "nr5g_band".
```
curl "http://10.42.3.1:50500/?query=bands&net=nr5g_band"

+QNWPREFCFG: "nr5g_band",41:78
OK
```

Set the bands for the modem, where the `selectband` parameter can only be "gw_band", "lte_band", "nsa_nr5g_band", or "nr5g_band".
The bands parameters must be colon separated numbers.
```
curl "http://10.42.3.1:50500/?selectband=nr5g_band&bands=1:2:3:5:7:8:12:14:20:25:28:38:41:48:66:71:77:78:79"

OK
```
