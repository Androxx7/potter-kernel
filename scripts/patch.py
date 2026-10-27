import pathlib, sys
ok=[]

def rep(p, old, new, tag):
    f=pathlib.Path(p); s=f.read_text()
    if old not in s:
        print("FALHOU:", tag); sys.exit(1)
    f.write_text(s.replace(old,new,1)); ok.append(tag)

# 1) PLL do cluster perf clampa em 2208 -> libera 2400
rep("drivers/clk/msm/clock-cpu-8953.c",
    ".max_rate = 2208000000UL,",
    ".max_rate = 2400000000UL,",
    "pll max_rate 2208 -> 2400")

# 2) open-loop sobrescreve o ceiling do DT. passa a respeitar o maior dos dois
rep("drivers/regulator/cpr3-util.c",
    "\tfor (i = 0; i < vreg->corner_count; i++)\n"
    "\t\tvreg->corner[i].ceiling_volt\n"
    "\t\t\t= vreg->corner[i].open_loop_volt;",
    "\tfor (i = 0; i < vreg->corner_count; i++) {\n"
    "\t\tif (vreg->corner[i].open_loop_volt > vreg->corner[i].ceiling_volt)\n"
    "\t\t\tvreg->corner[i].ceiling_volt\n"
    "\t\t\t\t= vreg->corner[i].open_loop_volt;\n"
    "\t\tvreg->corner[i].open_loop_volt\n"
    "\t\t\t= vreg->corner[i].ceiling_volt;\n"
    "\t}",
    "ceiling = max(dt, open_loop)")

# 3) voto do rail: usa ceiling em vez do open-loop do fuse
rep("drivers/regulator/cpr3-regulator.c",
    "\t} else {\n"
    "\t\tnew_volt = aggr_corner.open_loop_volt;\n"
    "\t\taggr_corner.last_volt = aggr_corner.open_loop_volt;\n"
    "\t}",
    "\t} else {\n"
    "\t\tnew_volt = aggr_corner.ceiling_volt;\n"
    "\t\taggr_corner.last_volt = aggr_corner.open_loop_volt;\n"
    "\t}",
    "voto do rail usa ceiling")

for t in ok: print("OK:", t)
