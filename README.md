# HACS OpenWert SSH

Home Assistant integration to connect to OpenWrt modems with non standard web ui's over ssh.

Based on https://github.com/home-assistant/core/tree/dev/homeassistant/components/asuswrt to work with Technicolor TG800vac in a more generic way.
Let me know if your device is supported or not, I will try and add more as info comes in!

## aioasuswrt calls

* get_api
* get_nvram_info
* async_get_connected_devices()
* AsusWrt


## Unavaliable

* nvram
* /tmp/dnsmasq.leases
* head -c20 /proc/dmu/temperature
* head -c20 /proc/dmu/temperature
* wl -i eth1 phy_tempsense
* wl -i eth5 phy_tempsense
* wl -i eth2 phy_tempsense
* wl -i eth6 phy_tempsense

## Avaliable

* /tmp/dhcp.leases (different format)
* /sys/class/hwmon/hwmon0/device/temp1_input
* /sys/class/hwmon/hwmon1/device/temp1_input
* sysctl -a
	* kernel.hostname
	* kernel.version
* uci show
    * env.var.prod_friendly_name
	* version.@version[0].product
	* version.@version[0].marketing_name
	* version.@version[0].marketing_version