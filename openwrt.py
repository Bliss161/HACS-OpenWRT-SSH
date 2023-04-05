import re
import logging
from datetime import datetime

import aioasuswrt.asuswrt as _AsusWrt
import aioasuswrt.connection as _Connection

_LOGGER = logging.getLogger(__name__)

_Connection._PATH_EXPORT_COMMAND = "PATH=$PATH:/usr/sbin:/usr/bin:/sbin:/bin"

_AsusWrt._ARP_CMD = "cat /proc/net/arp" # arp -n ||
_AsusWrt._ARP_REGEX = re.compile(
    r"(?P<ip>([0-9]{1,3}[\.]){3}[0-9]{1,3})\s+"
    r"[^\s]+\s+"
    r"[^\s]+\s+"
    r"(?P<mac>(([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})))\s+"
    r"[^\s]+\s+"
    r"[^\s]+"
)

_AsusWrt._LEASES_CMD = "cat {}/d[hn][cs][pm]*.leases"
_AsusWrt._LEASES_REGEX = re.compile(
    r"\w+\s+"
    r"(?P<mac>(([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})))\s+"
    r"(?P<ip>([0-9]{1,3}[\.]){3}[0-9]{1,3})\s+"
    r"(?P<host>([^\s]+))\s*"
    r".*"
)

_AsusWrt._IP_NEIGH_REGEX = re.compile(
    r"(?P<ip>([0-9]{1,3}[\.]){3}[0-9]{1,3})\s+"
    r"\w+\s+"
    r"(?P<interface>[^\s]+)\s+"
    r"\w+\s+"
    r"(?P<mac>(([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})))\s+"
    r"(?P<status>(\w+))"
)

#_AsusWrt._CLIENTLIST_CMD = 'echo {}'

class OpenWrt(_AsusWrt.AsusWrt):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    async def async_get_nvram(self, to_get, use_cache=True):
        """Get OpenWrt router info from uci."""
        info = {}
        try:
            if to_get == "MODEL":
                return {"model": await self.connection.async_run_command("uci get env.var.prod_friendly_name")}
            if to_get == "FIRMWARE":
                return {"firmver": await self.connection.async_run_command("uci get version.@version[0].marketing_name"), "buildno": await self.connection.async_run_command("uci get version.@version[0].marketing_version")}
        except Exception as exc:
            _LOGGER.warning("Error calling method async_get_nvram(%s): %s", info_type, exc)

        return info

    async def async_get_connected_devices(self, use_cache=True):
        """Retrieve data from OpenWrt.
        Calls various commands on the router and returns the superset of all
        responses. Some commands will not work on some routers.
        """
        now = datetime.utcnow()
        if (
            use_cache
            and self._dev_cache_timer
            and self._cache_time > (now - self._dev_cache_timer).total_seconds()
        ):
            return self._devices_cache

        devices = {}
        dev = await self.async_get_arp()
        devices.update(dev)
        dev = await self.async_get_neigh(devices)
        devices.update(dev)
        if not self.mode == "ap":
            dev = await self.async_get_leases(devices)
            devices.update(dev)

        filter_devices = await self.async_filter_dev_list(devices)
        ret_devices = {
            key: dev
            for key, dev in filter_devices.items()
            if not self.require_ip or dev.ip is not None
        }

        self._devices_cache = ret_devices
        self._dev_cache_timer = now

        return ret_devices