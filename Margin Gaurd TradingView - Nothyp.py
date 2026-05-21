indicator("Prop Firm Margin Guard - nothyp", shorttitle="Margin Guard - Nothyp", overlay=true)

// INPUTS
grpAcc = "Account Settings"
accountSize = input.float(5000, "Account Size ($)", minval=100, step=1000, group=grpAcc)
leverage = input.int(50, "Leverage (1:X)", minval=1, maxval=2000, group=grpAcc)

grpMgn = "Margin Guard Settings"
guardPct = input.float(
     70.0,
     "Guard Threshold (%)",
     minval=10,
     maxval=99,
     step=1,
     group=grpMgn)

hardPct = input.float(
     80.0,
     "Hard Limit (%)",
     minval=10,
     maxval=99,
     step=1,
     group=grpMgn)

grpDisp = "Display"
showTable = input.bool(true, "Show Margin Table", group=grpDisp)

tablePos = input.string(
     "top_right",
     "Table Position",
     options=["top_right","top_left","bottom_right","bottom_left"],
     group=grpDisp)

// SYMBOL
sym = syminfo.ticker

// CONTRACT SIZE
contractSize =
     str.contains(sym, "XAU") or str.contains(sym, "GOLD") ? 100.0 :
     str.contains(sym, "OIL") or str.contains(sym, "WTI") or str.contains(sym, "USOIL") ? 1000.0 :
     100000.0

// USD DETECTION
isUSDQuote =
     str.endswith(sym, "USD") or
     str.contains(sym, "XAUUSD") or
     str.contains(sym, "USOIL")

isUSDBase = str.startswith(sym, "USD")

priceUSD =
     isUSDQuote ? close :
     isUSDBase ? 1.0 :
     close

// MARGIN
marginPerLot = (contractSize * priceUSD) / leverage

guardAmount = accountSize * (guardPct / 100)
hardAmount = accountSize * (hardPct / 100)

maxLotsGuard = guardAmount / marginPerLot
maxLotsHard = hardAmount / marginPerLot

buyingPower = accountSize * leverage

// COLORS
safeColor = color.new(#00e676, 0)
warnColor = color.new(#ffea00, 0)
dangerColor = color.new(#ff1744, 0)
accentColor = color.new(#e91e8c, 0)
cyanColor = color.new(#00e5ff, 0)

// TABLE POSITION
pos =
     tablePos == "top_right" ? position.top_right :
     tablePos == "top_left" ? position.top_left :
     tablePos == "bottom_right" ? position.bottom_right :
     position.bottom_left

// TABLE
var table dash = table.new(
     pos,
     2,
     11,
     bgcolor=color.new(#0d0d0d, 35),
     border_color=color.new(color.gray, 60),
     border_width=1)

if barstate.islast and showTable

    table.cell(dash, 0, 0, "MARGIN GUARD 1", text_color=accentColor)
    table.cell(dash, 1, 0, "Nothyp", text_color=color.gray)

    table.cell(dash, 0, 1, "Pair")
    table.cell(dash, 1, 1, sym, text_color=cyanColor)

    table.cell(dash, 0, 2, "Account")
    table.cell(dash, 1, 2, "$" + str.tostring(accountSize))

    table.cell(dash, 0, 3, "Leverage")
    table.cell(dash, 1, 3, "1:" + str.tostring(leverage))

    table.cell(dash, 0, 4, "Buying Power")
    table.cell(dash, 1, 4, "$" + str.tostring(buyingPower))

    table.cell(dash, 0, 6, "Margin / Lot")
    table.cell(dash, 1, 6, "$" + str.tostring(marginPerLot, "#.00"))

    table.cell(dash, 0, 7, "Guard")
    table.cell(dash, 1, 7, "$" + str.tostring(guardAmount))

    table.cell(dash, 0, 8, "MAX LOTS")
    table.cell(
         dash,
         1,
         8,
         str.tostring(maxLotsGuard, "#.##") + " lots",
         text_color=safeColor)

    table.cell(dash, 0, 9, "Hard Limit")
    table.cell(
         dash,
         1,
         9,
         str.tostring(maxLotsHard, "#.##") + " lots",
         text_color=dangerColor)

// WATERMARK
var label wm = na

if barstate.islast
    label.delete(wm)

    wm := label.new(
         bar_index,
         high + (high - low) * 5,
         "Nothyp — Margin Guard | Max: " +
         str.tostring(maxLotsGuard, "#.##") +
         " lots on " + sym,
         style=label.style_label_center,
         textcolor=color.gray,
         color=color.new(color.black, 100))
