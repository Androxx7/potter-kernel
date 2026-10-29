import pathlib, sys
root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
print("root:", root)
ok = []

def rep(rel, old, new, tag):
    f = root / rel
    if not f.is_file():
        print("SEM ARQUIVO:", rel); sys.exit(1)
    s = f.read_text()
    if old not in s:
        print("FALHOU:", tag); sys.exit(1)
    f.write_text(s.replace(old, new, 1))
    ok.append(tag)

rep("drivers/clk/msm/clock-cpu-8953.c",
    ".max_rate = 2208000000UL,",
    ".max_rate = 2400000000UL,",
    "PLL max_rate 2208 -> 2400")

rep("drivers/regulator/cpr3-util.c",
    "\tfor (i = 0; i < vreg->corner_count; i++)\n"
    "\t\tvreg->corner[i].ceiling_volt\n"
    "\t\t\t= vreg->corner[i].open_loop_volt;",
    "\tfor (i = 0; i < vreg->corner_count; i++) {\n"
    "\t\tif (vreg->corner[i].ceiling_volt < vreg->corner[i].open_loop_volt)\n"
    "\t\t\tvreg->corner[i].ceiling_volt\n"
    "\t\t\t\t= vreg->corner[i].open_loop_volt;\n"
    "\t\tvreg->corner[i].open_loop_volt\n"
    "\t\t\t= vreg->corner[i].ceiling_volt;\n"
    "\t}",
    "ceiling = max(DT, open_loop)")

rep("drivers/regulator/cpr3-regulator.c",
    "\t\t\tnew_volt = aggr_corner.open_loop_volt;",
    "\t\t\tnew_volt = aggr_corner.ceiling_volt;",
    "voto do rail usa ceiling (nao o fuse)")

for t in ok:
    print("OK:", t)
print("TOTAL:", len(ok))

import os
n = 0
for dp, dn, fns in os.walk(root):
    for fn in fns:
        if fn.startswith("Makefile"):
            p = os.path.join(dp, fn)
            try:
                s = open(p).read()
            except Exception:
                continue
            if "-Wno-error-implicit-function-declaration" in s:
                open(p, "w").write(s.replace("-Wno-error-implicit-function-declaration", "-Wno-error=implicit-function-declaration"))
                n += 1
print("makefiles corrigidos:", n)
