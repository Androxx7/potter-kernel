import pathlib, sys
ok = []

def rep(p, old, new, tag):
    f = pathlib.Path(p)
    s = f.read_text()
    if old not in s:
        print("FALHOU:", tag)
        sys.exit(1)
    f.write_text(s.replace(old, new, 1))
    ok.append(tag)

# ---------------------------------------------------------------
# 1) O PLL do cluster perf clampa em 2208 MHz.
#    clock-pll.c faz: if (rate > pll->max_rate) rate = pll->max_rate;
#    enquanto max_rate = 2208000000. Sobe pro ceiling do chip.
# ---------------------------------------------------------------
rep("drivers/clk/msm/clock-cpu-8953.c",
    ".max_rate = 2208000000UL,",
    ".max_rate = 2400000000UL,",
    "PLL max_rate 2208 -> 2400")

# ---------------------------------------------------------------
# 2) cpr3_open_loop_voltage_as_ceiling() sobrescreve o ceiling do DT
#    com o open-loop do fuse (950mV). O DT pede 1140.
#    Passa a manter o MAIOR dos dois, e alinha o open-loop ao ceiling
#    pra nao ser reduzido de volta pelo clamp seguinte.
# ---------------------------------------------------------------
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

# ---------------------------------------------------------------
# 3) No CPR4 em HW closed-loop, new_volt = aggr_corner.open_loop_volt
#    (o valor do fuse). Troca pro ceiling, que agora carrega o DT.
# ---------------------------------------------------------------
rep("drivers/regulator/cpr3-regulator.c",
    "\t\telse if (ctrl->ctrl_type == CPR_CTRL_TYPE_CPR4\n"
    "\t\t\t && ctrl->supports_hw_closed_loop)\n"
    "\t\t\tnew_volt = aggr_corner.open_loop_volt;",
    "\t\telse if (ctrl->ctrl_type == CPR_CTRL_TYPE_CPR4\n"
    "\t\t\t && ctrl->supports_hw_closed_loop)\n"
    "\t\t\tnew_volt = aggr_corner.ceiling_volt;",
    "voto do rail usa ceiling (nao o fuse)")

for t in ok:
    print("OK:", t)
print("TOTAL:", len(ok))
