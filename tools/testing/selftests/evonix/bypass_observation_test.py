#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0
"""Exercise the compiled Duchamp observation function without charger writes."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
MOCK = r'''
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <errno.h>
#include <sys/types.h>
#define HZ 100UL
#define EVX_NAV 2
#define EVX_SMART "battery/smart_chg"
#define EVX_USB "usb/"
#define POWER_SUPPLY_STATUS_NOT_CHARGING 3
#define POWER_SUPPLY_PROP_STATUS 0
#define POWER_SUPPLY_PROP_CURRENT_NOW 1
#define time_after(a,b) ((long)((b)-(a)) < 0)
#define time_after_eq(a,b) ((long)((a)-(b)) >= 0)
#define mutex_lock(p) ((void)(p))
#define mutex_unlock(p) ((void)(p))
#define sysfs_emit(buf,...) snprintf(buf,4096,__VA_ARGS__)
struct device { int unused; };
struct device_attribute { int unused; };
static int evx_state_lock;
static bool evx_owned=true;
static unsigned long evx_neutral_since, evx_last_sample, jiffies;
static int state=2, status=3, online=1, suspended, vbus=5000, battery_ua;
static int failure, calls;
static int evx_read_int(const char *path, int *value)
{
    calls++;
    if (!strcmp(path,EVX_SMART)) *value=state;
    else if (!strcmp(path,EVX_USB "online")) *value=online;
    else if (!strcmp(path,EVX_USB "input_suspend")) *value=suspended;
    else if (!strcmp(path,EVX_USB "pmic_vbus")) *value=vbus;
    else assert(0);
    return failure == calls ? -EIO : 0;
}
static int evx_supply_property(const char *name, int property, int *value)
{
    calls++;
    if (!strcmp(name,"primary_chg")) {
        assert(property==POWER_SUPPLY_PROP_STATUS); *value=status;
    } else {
        assert(!strcmp(name,"bms") && property==POWER_SUPPLY_PROP_CURRENT_NOW);
        *value=battery_ua;
    }
    return failure == calls ? -ENODEV : 0;
}
'''
MAIN = r'''
static int sample(unsigned long ticks) {
    char buf[4096]; jiffies=ticks; calls=0;
    assert(bypass_charging_active_show(NULL,NULL,buf)==2);
    return buf[0]=='1';
}
static void reset(void) {
    evx_neutral_since=evx_last_sample=0; failure=0; evx_owned=true;
    state=2; status=3; online=1; suspended=0; vbus=5000; battery_ua=0;
}
int main(void) {
    unsigned i;
    reset();
    assert(!sample(100) && !sample(200) && !sample(300) && sample(400));
    assert(!sample(701)); /* A gap cannot count as continuous confirmation. */
    for(i=1;i<=6;i++) {
        reset(); assert(!sample(100)); failure=i;
        assert(!sample(400)); failure=0;
        assert(!sample(500) && !sample(600) && !sample(700) && sample(800));
    }
    for(i=0;i<12;i++) {
        reset(); assert(!sample(100) && !sample(200) && !sample(300) && sample(400));
        switch(i) {
        case 0: evx_owned=false; break;
        case 1: state=0; break;
        case 2: status=0; break;
        case 3: status=1; break;
        case 4: status=2; break;
        case 5: status=4; break;
        case 6: online=0; break;
        case 7: suspended=1; break;
        case 8: vbus=4399; break;
        case 9: vbus=6001; break;
        case 10: battery_ua=-100001; break;
        case 11: battery_ua=100001; break;
        }
        assert(!sample(500) && !evx_neutral_since);
        if(i<2) assert(calls==1);
    }
    reset(); battery_ua=-100000; vbus=4400;
    assert(!sample(100) && !sample(200) && !sample(300) && sample(400));
    reset(); battery_ua=100000; vbus=6000;
    assert(!sample(100) && !sample(200) && !sample(300) && sample(400));
    return 0;
}
'''


class Observation(unittest.TestCase):
    def test_observation_errors_gaps_and_boundaries(self):
        source = (ROOT / "drivers/misc/evonix_oem_bypass.c").read_text()
        start = source.index("static ssize_t bypass_charging_active_show")
        end = source.index("static DEVICE_ATTR_RO(bypass_charging_active)", start)
        with tempfile.TemporaryDirectory(prefix="duchamp-observation-") as temp:
            cfile, exe = Path(temp) / "test.c", Path(temp) / "test"
            cfile.write_text(MOCK + source[start:end] + MAIN)
            subprocess.run(["cc", "-std=c11", "-O2", "-Wall", "-Wextra",
                            "-Wno-unused-parameter", "-Werror",
                            "-fsanitize=undefined,bounds", "-fno-sanitize-recover=all",
                            str(cfile), "-o", str(exe)], check=True)
            subprocess.run([str(exe)], check=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
