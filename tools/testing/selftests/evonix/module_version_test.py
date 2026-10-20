#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0
"""Compile the real CRC decision function with load-anyway enabled and disabled."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
MOCK = r'''
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <assert.h>
typedef uint32_t u32;
typedef int32_t s32;
typedef struct { uintptr_t sh_addr; size_t sh_size; } Elf_Shdr;
struct module { int unused; };
struct modversion_info { unsigned long crc; char name[64]; };
struct load_info { Elf_Shdr *sechdrs; struct { unsigned vers; } index; const char *name; };
#define CONFIG_EVONIX_MODULE_LOAD_ANYWAY TEST_POLICY
#define IS_ENABLED(option) (option)
#define pr_warn(...) ((void)0)
#define pr_warn_once(...) ((void)0)
#define pr_debug(...) ((void)0)
static int force_result=-1;
static int try_to_force_load(struct module *mod, const char *name)
{ (void)mod; (void)name; return force_result; }
'''
MAIN = r'''
int main(void) {
    struct module mod={0};
    struct modversion_info version={.crc=123, .name="probe"};
    Elf_Shdr sections[2]={{0},{.sh_addr=(uintptr_t)&version, .sh_size=sizeof(version)}};
    struct load_info info={.sechdrs=sections, .index={.vers=1}, .name="fixture"};
    s32 crc=123;
    assert(check_version(&info,"probe",&mod,&crc)==1);
    crc=124;
    assert(check_version(&info,"probe",&mod,&crc)==TEST_POLICY);
    assert(check_version(&info,"probe",&mod,NULL)==1);
    info.index.vers=0;
    assert(check_version(&info,"probe",&mod,&crc)==0);
    force_result=0;
    assert(check_version(&info,"probe",&mod,&crc)==1);
    return 0;
}
'''


class VersionPolicy(unittest.TestCase):
    def test_crc_policy_and_absent_metadata(self):
        source = (ROOT / "kernel/module/version.c").read_text()
        body = source[source.index("int check_version("):source.index("int check_modstruct_version(")]
        with tempfile.TemporaryDirectory(prefix="ruyi-module-version-") as temp:
            cfile, exe = Path(temp) / "test.c", Path(temp) / "test"
            cfile.write_text(MOCK + body + MAIN)
            for policy in (0, 1):
                with self.subTest(load_anyway=policy):
                    subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                                    f"-DTEST_POLICY={policy}", str(cfile), "-o", str(exe)], check=True)
                    subprocess.run([str(exe)], check=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
