import re, os

os.chdir(os.path.expanduser("~/GitHub/iiko-DS/DS/_audit/platform/_src"))

def show(fn, pattern, ctx=0, limit=40):
    print("=====", fn.replace("_", "-"))
    try:
        lines = open(fn, encoding="utf-8", errors="replace").read().splitlines()
    except Exception as e:
        print("   ERR", e)
        return
    rx = re.compile(pattern)
    shown = 0
    for i, l in enumerate(lines):
        if rx.search(l):
            for j in range(max(0, i - ctx), min(len(lines), i + ctx + 1)):
                print(f"   {j+1}| {lines[j]}")
            shown += 1
            if shown >= limit:
                break

show("mw_sys_shape.scss", r"corner|full|: *[0-9]+px")
show("mw_sys_state.scss", r"opacity|:")
show("mw_typescale.scss", r"'(body-large|body-medium|label-small|label-large|title-large|title-medium|title-small)-(size|line-height|weight)':")
show("am_m3_button.scss", r"touch-target")
show("am_list_list.scss", r"72px|padding|height")
show("am_expansion__m3-expansion.scss", r"height|shape")
show("am_expansion__expansion-variables.scss", r"height|:")
show("am_expansion_expansion-panel-header.scss", r"padding: 0 24px|title|description")
