//@version=5
indicator("PF Margin Gaurd - nothyp2", shorttitle="Margin Guard - nothyp2", overlay=true)

// ACCOUNT
grpAcc = "① Account Settings"

accountSize = input.float(
     5000,
     "Account Size ($)",
     minval=100,
     step=1000,
     group=grpAcc)

leverage = input.int(
     50,
     "Leverage (1:X)",
     minval=1,
     maxval=2000,
     group=grpAcc)

guardPct = input.float(
     70.0,
     "Margin Threshold (%)",
     minval=10,
     maxval=99,
     step=1,
     group=grpAcc)

hardPct = input.float(
     80.0,
     "Hard Limit (%)",
     minval=10,
     maxval=99,
     step=1,
     group=grpAcc)

// RISK
grpRisk = "② Risk Per Trade"

riskDollar = input.float(
     0.0,
     "Risk Amount ($)",
     minval=0,
     step=10,
     group=grpRisk)

riskPct = input.float(
     1.0,
     "Risk Amount (%)",
     minval=0,
     maxval=100,
     step=0.1,
     group=grpRisk)

// TRADE
grpTrade = "③ Trade Setup"

tradeDir = input.string(
     "LONG",
     "Direction",
     options=["LONG","SHORT"],
     group=grpTrade)

entryPrice = input.float(
     0.0,
     "Entry Price",
     minval=0,
     step=0.00001,
     group=grpTrade)

slPrice = input.float(
     0.0,
     "Stop Loss Price",
     minval=0,
     step=0.00001,
     group=grpTrade)

// DISPLAY
grpDisp = "④ Display"

tablePos = input.string(
     "top_right",
     "Table Position",
     options=["top_right","top_left","bottom_right","bottom_left"],
     group=grpDisp)

// VALUES
effectiveEntry =
     entryPrice <= 0 ? close : entryPrice

effectiveRiskDollar =
     riskDollar > 0 ?
     riskDollar :
     accountSize * (riskPct / 100)

effectiveRiskPct =
     riskDollar > 0 ?
     (riskDollar / accountSize) * 100 :
     riskPct

sym = syminfo.ticker

contractSize =
     str.contains(sym, "XAU") or str.contains(sym, "GOLD") ? 100.0 :
     str.contains(sym, "OIL") or str.contains(sym, "WTI") or str.contains(sym, "USOIL") ? 1000.0 :
     100000.0

isUSDQuote =
     str.endswith(sym, "USD") or
     str.contains(sym, "XAUUSD") or
     str.contains(sym, "USOIL")

isUSDBase =
     str.startswith(sym, "USD")

priceUSD =
     isUSDQuote ? effectiveEntry :
     isUSDBase ? 1.0 :
     effectiveEntry

marginPerLot =
     (contractSize * priceUSD) / leverage

slValid =
     slPrice > 0

slDistance =
     slValid ?
     math.abs(effectiveEntry - slPrice) :
     na

pipSize =
     syminfo.mintick

pipValuePerLot =
     isUSDQuote ?
     pipSize * contractSize :
     isUSDBase ?
     (pipSize * contractSize) / close :
     pipSize * contractSize

slDistancePips =
     slValid ?
     slDistance / pipSize :
     na

lotsByRisk =
     slValid ?
     effectiveRiskDollar / (slDistancePips * pipValuePerLot) :
     na

guardAmount =
     accountSize * (guardPct / 100)

hardAmount =
     accountSize * (hardPct / 100)

maxLotsGuard =
     guardAmount / marginPerLot

maxLotsHard =
     hardAmount / marginPerLot

chosenLots =
     slValid ?
     math.min(lotsByRisk, maxLotsGuard) :
     maxLotsGuard

marginUsed =
     chosenLots * marginPerLot

marginUsedPct =
     (marginUsed / accountSize) * 100

// COLORS
safeColor = color.new(#00e676, 0)
warnColor = color.new(#ffea00, 0)
dangerColor = color.new(#ff1744, 0)
accentColor = color.new(#e91e8c, 0)
cyanColor = color.new(#00e5ff, 0)
silverColor = color.silver
mutedColor = color.new(color.gray, 30)

statusColor =
     marginUsedPct < guardPct ? safeColor :
     marginUsedPct < hardPct ? warnColor :
     dangerColor

statusEmoji =
     marginUsedPct < guardPct ? "✅" :
     marginUsedPct < hardPct ? "⚠️" :
     "❌"

statusText =
     marginUsedPct < guardPct ? "SAFE" :
     marginUsedPct < hardPct ? "WARNING" :
     "DANGER"

actualRiskDollar =
     slValid ?
     chosenLots * slDistancePips * pipValuePerLot :
     na

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
     14,
     bgcolor=color.new(#0a0c12, 30),
     border_color=color.new(color.gray, 65),
     border_width=1)

if barstate.islast

    table.cell(dash,0,1,"Account")
    table.cell(
     dash,1,1,
     "$"+str.tostring(accountSize)+"  1:"+str.tostring(leverage))


    table.cell(dash,0,5,"Entry")
    table.cell(
         dash,1,5,
         entryPrice<=0?
         str.tostring(close,"#.#####"):
         str.tostring(effectiveEntry,"#.#####"))

    table.cell(dash,0,6,"Stop Loss")
    table.cell(
         dash,1,6,
         slValid?
         str.tostring(slPrice,"#.#####"):
         "Not Set")

    table.cell(dash,0,10,"$ at Risk")
    table.cell(
     dash,1,10,
     slValid?
     "$"+str.tostring(actualRiskDollar,"#.00"):
     "Set SL",
     text_color=warnColor)

    table.cell(dash,0,8,"LOT SIZE")
    table.cell(
         dash,1,8,
         slValid?
         str.tostring(chosenLots,"#.##")+" lots":
         str.tostring(maxLotsGuard,"#.##")+" max",
         text_color=safeColor)

    table.cell(dash,0,9,"Margin Used")
    table.cell(
         dash,1,9,
         str.tostring(marginUsedPct,"#.0")+"%",
         text_color=statusColor)

    table.cell(dash,0,12,"80% Margin")
    table.cell(
         dash,1,12,
         str.tostring(maxLotsHard,"#.##")+" lots",
         text_color=dangerColor)

    table.cell(
         dash,0,13,
         statusEmoji+" "+statusText,
         text_color=statusColor)

    table.cell(
         dash,1,13,
         marginUsedPct < guardPct ?
         "Below Guard" :
         marginUsedPct < hardPct ?
         "Reduce Lots" :
         "Breached💀",
         text_color=statusColor)

// ALERTS
alertcondition(
     marginUsedPct >= hardPct,
     "OVER Hard Limit",
     "Margin above hard limit")

alertcondition(
     marginUsedPct >= guardPct and marginUsedPct < hardPct,
     "Warning Zone",
     "Margin warning zone")
     
     
     
     
     
// nothyp FX Project 2