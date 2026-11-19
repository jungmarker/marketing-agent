#!/usr/bin/env python3
"""Builds content/video-bank.json and content/video-bank.md: the question-driven reel bank.
Numbers that are arithmetic on a stated rule are written out; everything that depends on
today's rates, a program's current terms or Nick's own market is a {{placeholder}} or sits
in `verify`. Run: python3 content/build_bank.py"""
import json, os

FRAMES = ["Medium (waist up)", "Medium close (chest up)", "Medium (waist up)", "Close (shoulders up)",
          "Medium wide (knees up)", "Medium close (chest up)", "Medium (waist up)", "Medium close (chest up)"]
LENDER = "Your lender, for the day you post"
bank = []

def talk(id, shape, q, title, lines, verify=(), ask="", place="Front steps or sidewalk of a rowhouse", cut=None, src=""):
    beats = []
    for i, (say, screen) in enumerate(lines):
        beats.append({"say": say, "screen": screen, "framing": FRAMES[i % len(FRAMES)], "angle": "Eye level",
            "move": "Handheld walking" if i == len(lines) // 2 else "Locked on tripod",
            "shot": "Walk toward the phone and stop as you finish" if i == 0 else "Walking along the block, phone at arm's length" if i == len(lines) // 2 else "To camera. Step or turn so the background changes from the last line",
            "location": place, "broll": (cut or {}).get(i), "punch": i % 2 == 1})
    bank.append(dict(id=id, kind="talk", shape=shape, question=q, title=title, beats=beats, verify=list(verify), ask=ask, source=src))

def point(id, shape, q, title, cards, verify=(), ask="", place="In front of a rowhouse", src=""):
    beats = [{"say": "", "screen": screen, "shot": action, "framing": "Medium (waist up), standing to one side so the text has room",
              "angle": "Eye level", "move": "Locked on tripod", "location": place, "broll": None, "punch": False, "seconds": 2.5}
             for screen, action in cards]
    bank.append(dict(id=id, kind="point", shape=shape, question=q, title=title, beats=beats, verify=list(verify), ask=ask, source=src))

def text(id, shape, q, title, stack, clip, verify=(), ask="", src=""):
    beats = [{"say": "", "screen": "\n".join(stack), "shot": clip, "framing": "Wide", "angle": "Eye level", "move": "Locked on tripod",
              "location": "Wherever the clip is", "broll": None, "punch": False, "seconds": 8}]
    bank.append(dict(id=id, kind="text", shape=shape, question=q, title=title, beats=beats, verify=list(verify), ask=ask, source=src))

# ---------------- talking explainers ----------------
talk("t01", "Question", "How much house can I afford on a $180,000 salary?", "$180K income: what can you buy?", [
  ("You make $180,000. Here's what you can buy.", "$180K INCOME"),
  ("That's $15,000 a month before taxes.", "$15,000 / MONTH"),
  ("Lenders like housing at 28% of that.", "THE 28% RULE"),
  ("So your payment tops out near $4,200 a month.", "$4,200 / MONTH"),
  ("At today's rates that's a house around {{price from your lender}}.", "{{PRICE}}"),
  ("Car loans and student loans pull that number down.", "DEBTS COUNT"),
  ("Comment NUMBERS and I'll run yours.", 'COMMENT "NUMBERS"'),
  ("$180,000 goes further in Baltimore than you think.", None)],
  verify=[("Price that a $4,200 payment buys today, with taxes and insurance", LENDER), ("28% front-end and 36% total-debt guideline still fits the loans you see", LENDER)],
  ask="Comment NUMBERS", src="bankrate.com: 28/36 rule on $180K gives $4,200 housing, $5,400 total debt")

talk("t02", "Question", "How much money do you need to buy a $400,000 house?", "$400K house: cash you need", [
  ("How much cash for a $400,000 house?", "$400K HOUSE"),
  ("Not $80,000. That's 20% down, and it's optional.", "20% = $80,000"),
  ("Three percent down is $12,000.", "3% = $12,000"),
  ("FHA is three and a half. $14,000.", "FHA 3.5% = $14,000"),
  ("Then closing costs. In Baltimore City, plan on {{closing cost estimate}}.", "+ CLOSING COSTS"),
  ("And the city has money that can cover part of it.", "CITY HELP EXISTS"),
  ("Comment 400 and I'll send the full breakdown.", 'COMMENT "400"'),
  ("$400,000 house. A lot less than $80,000 to get in.", None)],
  verify=[("Closing cost estimate on a $400,000 Baltimore City purchase", "Your title company"), ("Current first-time buyer incentive amounts", "Live Baltimore and Baltimore City DHCD")],
  ask="Comment 400", src="sofi.com, redfin.com: down payment options on a $400K home")

talk("t03", "Question", "What income do you need for a $400,000 house?", "Income for a $400K house", [
  ("What do you have to make to buy at $400,000?", "INCOME FOR $400K"),
  ("Most estimates land between $100,000 and $135,000.", "$100K to $135K"),
  ("The spread is your down payment, your rate and your debts.", "3 THINGS MOVE IT"),
  ("A $500 car payment can cost you {{buying power lost}} in house.", "DEBT SHRINKS IT"),
  ("So pay down the card before you shop, not after.", None),
  ("Tell me your income and I'll tell you your range.", "DM YOUR NUMBER"),
  ("$400,000 is closer than it sounds.", None)],
  verify=[("Buying power lost per $500 of monthly debt at today's rate", LENDER), ("Income range for $400K today", LENDER)],
  ask="DM your income", src="redfin.com, pennymac.com: $100K to $135K range")

talk("t04", "Question", "What credit score do you need to buy a house?", "The credit score you need", [
  ("You don't need a 750 credit score to buy a house.", "YOU DON'T NEED 750"),
  ("The real minimums are lower than you think.", None),
  ("FHA starts at 580 with three and a half down.", "FHA: 580"),
  ("Conventional usually starts at 620.", "CONVENTIONAL: 620"),
  ("Higher score, lower rate. That's the whole game.", "SCORE = RATE"),
  ("Don't open a new card while you're shopping.", "NO NEW CREDIT"),
  ("Comment SCORE and I'll connect you with a lender.", 'COMMENT "SCORE"'),
  ("580. Not 750.", None)],
  verify=[("580 FHA and 620 conventional minimums at the lenders you send people to", "Your lender")],
  ask="Comment SCORE", src="credible.com, amerisave.com first-time buyer FAQs")

talk("t05", "Nobody tells you", "How much are closing costs in Baltimore City?", "Nobody tells you about Baltimore closing costs", [
  ("Nobody tells you about closing costs in Baltimore City.", "BALTIMORE CLOSING COSTS"),
  ("The city transfer tax is 1.5%.", "CITY: 1.5%"),
  ("The state adds half a percent.", "STATE: 0.5%"),
  ("Then recordation tax, {{recordation rate}}.", "+ RECORDATION"),
  ("Who pays what is negotiable. It's in the contract.", "IT'S NEGOTIABLE"),
  ("First-time buyers get a break on part of it.", "FIRST-TIME BREAK"),
  ("Comment CLOSING for my cost sheet.", 'COMMENT "CLOSING"'),
  ("Closing costs. Now somebody told you.", None)],
  verify=[("Current Baltimore City transfer (1.5%) and state transfer (0.5%) rates", "Baltimore City Finance, or your title company"), ("Recordation rate and the first-time buyer exemption", "Your title company"), ("You have a cost sheet to send", "You")],
  ask="Comment CLOSING", src="baltimorecity.gov finance: transfer tax 1.5%; state 0.5%")

talk("t06", "Question", "How much is property tax on a Baltimore City house?", "The tax bill on a $250K rowhouse", [
  ("What's the tax bill on a $250,000 Baltimore rowhouse?", "TAX ON $250K"),
  ("The city rate is $2.248 per $100.", "$2.248 PER $100"),
  ("On $250,000 assessed, that's $5,620 a year.", "$5,620 / YEAR"),
  ("About $468 a month, inside your mortgage payment.", "$468 / MONTH"),
  ("It's the highest rate in Maryland. Prices are lower to match.", None),
  ("And one free form can cap how fast it climbs.", "ONE FORM"),
  ("Follow. That form is the next video.", "FOLLOW FOR PART 2"),
  ("$468 a month. Budget for it.", None)],
  verify=[("City rate still $2.248 per $100 this fiscal year", "baltimorecity.gov/finance/real-property-taxes"), ("State property tax is extra; say so in the caption with the current rate", "SDAT")],
  ask="Follow for part 2", src="baltimorecity.gov: $2.248 per $100 (FY2025)")

talk("t07", "Negative command, softened", "What is the homestead tax credit in Baltimore?", "The one form every Baltimore owner needs", [
  ("One free form can cap your Baltimore property tax.", "ONE FREE FORM"),
  ("It's the homestead tax credit.", "HOMESTEAD CREDIT"),
  ("It caps how fast your city assessment can rise. 4% a year.", "4% CAP"),
  ("You apply once, with the state. It's free.", "APPLY ONCE. FREE."),
  ("Skip it and your tax bill can jump when values do.", None),
  ("You have to live in the house. That's the rule.", "OWNER-OCCUPIED"),
  ("Comment HOMESTEAD and I'll send the link.", 'COMMENT "HOMESTEAD"'),
  ("One form. Do it this week.", None)],
  verify=[("4% Baltimore City homestead cap is current (the mayor has proposed changes for 2027)", "SDAT and Baltimore City Finance")],
  ask="Comment HOMESTEAD", src="baltimorecity.gov, thebanner.com: 4% cap, one-time application")

talk("t08", "Numbered list", "What first-time homebuyer programs does Baltimore have?", "3 pots of money for Baltimore buyers", [
  ("3 pots of money for first-time buyers in Baltimore.", "3 POTS OF MONEY"),
  ("One. The city's first-time buyer incentive. {{current amount}}.", "1. CITY INCENTIVE"),
  ("It's forgiven if you stay five years.", "FORGIVEN IN 5 YEARS"),
  ("Two. The Maryland Mortgage Program. Help with the down payment.", "2. MARYLAND MORTGAGE PROGRAM"),
  ("Three. Reinvest Baltimore. Up to {{current amount}} on certain homes.", "3. REINVEST BALTIMORE"),
  ("Some of these stack.", "THEY STACK"),
  ("Comment MONEY and I'll send what you qualify for.", 'COMMENT "MONEY"'),
  ("3 pots. Most buyers never ask.", None)],
  verify=[("First-Time Homebuyers Incentive current amount and funding left", "Live Baltimore / Baltimore City DHCD"), ("Reinvest Baltimore down payment amount and eligible homes", "Maryland DHCD"), ("Which programs can be combined", "An MMP-approved lender")],
  ask="Comment MONEY", src="livebaltimore.com, dhcd.maryland.gov (Reinvest Baltimore, July 2026)")

talk("t09", "Permission", "Do you need 20% down to buy a house?", "You don't need 20% down", [
  ("You don't need 20% down to buy a house.", "YOU DON'T NEED 20%"),
  ("Conventional loans go as low as 3%.", "3% CONVENTIONAL"),
  ("FHA is three and a half.", "3.5% FHA"),
  ("VA is zero, if you served.", "0% VA"),
  ("Under 20, you pay mortgage insurance. It comes off later.", "PMI COMES OFF"),
  ("Waiting years to save 20 can cost more than the insurance.", None),
  ("Comment DOWN and I'll show you your options.", 'COMMENT "DOWN"'),
  ("20% is a choice. Not a rule.", None)],
  verify=[("Loan minimums at your lenders", "Your lender")], ask="Comment DOWN", src="bankrate.com, sofi.com")

talk("t10", "Question", "What is PMI and when does it go away?", "PMI, in 20 seconds", [
  ("PMI isn't forever. Here's when it comes off.", "PMI ISN'T FOREVER"),
  ("It's insurance for the lender when you put down under 20%.", "UNDER 20% DOWN"),
  ("You pay it monthly, on top of the mortgage.", "MONTHLY"),
  ("On a conventional loan it drops off once you own enough.", "IT DROPS OFF"),
  ("On FHA it works differently. Ask before you pick.", "FHA IS DIFFERENT"),
  ("It's the price of buying years sooner.", None),
  ("Questions? Comment PMI.", 'COMMENT "PMI"')],
  verify=[("How and when PMI is removed on the loans you see, in one sentence you are comfortable saying", "Your lender")], ask="Comment PMI", src="amerisave.com FAQ")

talk("t11", "Question", "How much earnest money do I need?", "Earnest money, explained on a stoop", [
  ("You can lose your earnest money. Here's how not to.", "EARNEST MONEY"),
  ("It's a deposit you put down when your offer is accepted.", "A DEPOSIT"),
  ("In Baltimore it's usually {{typical amount here}}.", "{{TYPICAL AMOUNT}}"),
  ("At closing it counts toward your down payment.", "IT COUNTS AT CLOSING"),
  ("Back out for a reason in the contract, you get it back.", None),
  ("Back out for no reason, you can lose it.", "YOU CAN LOSE IT"),
  ("Read the contingencies. That's where your money lives.", None)],
  verify=[("Typical earnest money deposit in your deals", "Your own recent contracts")], ask="Save this", src="credible.com: 1% to 3% nationally")

talk("t12", "Question", "How long does it take to buy a house in Maryland?", "How long buying really takes", [
  ("Nobody tells you how long buying a house takes.", "HOW LONG IT TAKES"),
  ("Pre-approval. {{days}}.", "PRE-APPROVAL"),
  ("Finding the house. That part's on you.", "THE SEARCH"),
  ("Offer to keys is usually {{days to close}}.", "OFFER TO KEYS"),
  ("So start {{months}} before your lease ends.", "START EARLY"),
  ("Comment TIMELINE for my week-by-week.", 'COMMENT "TIMELINE"')],
  verify=[("Your own typical pre-approval and contract-to-close times", "Your last ten deals")], ask="Comment TIMELINE", src="karashaffer.evrealestate.com: 2 to 4 months for first-time buyers")

talk("t13", "A or B", "Is it better to rent or buy in Baltimore?", "Rent or buy in Baltimore?", [
  ("Rent or buy in Baltimore? Same monthly money.", "RENT or BUY?"),
  ("Rent here runs around {{current median rent}}.", "RENT: {{AMOUNT}}"),
  ("That payment buys a rowhouse around {{price}}.", "BUY: {{PRICE}}"),
  ("Renting wins if you're leaving inside three years.", "UNDER 3 YEARS: RENT"),
  ("Buying wins if you're staying five.", "5+ YEARS: BUY"),
  ("In between, it's the house, not the math.", None),
  ("Which one are you? Rent or buy?", None)],
  verify=[("Current median rent for the area you name", "Bright MLS rentals or a named source in the caption"), ("Price that payment buys today", LENDER)],
  ask="Rent or buy?", src="stacker.com, zillow.com rent-vs-buy pieces")

talk("t14", "A or B", "FHA or conventional loan?", "FHA or conventional?", [
  ("FHA or conventional? Here's how I'd pick.", "FHA or CONVENTIONAL?"),
  ("FHA. Lower credit score, three and a half down.", "FHA: 580 / 3.5%"),
  ("Conventional. Better score, as low as three down.", "CONV: 620 / 3%"),
  ("FHA's insurance tends to stick around longer.", "FHA INSURANCE STAYS"),
  ("Some rowhouses won't pass an FHA appraisal as they sit.", "CONDITION MATTERS"),
  ("So the house can pick the loan for you.", None),
  ("Which one are you leaning? FHA or conventional?", None)],
  verify=[("How you describe FHA mortgage insurance and appraisal standards", "Your lender")], ask="FHA or conventional?", src="credible.com, bankrate.com")

talk("t15", "A or B", "Pre-qualified or pre-approved?", "Pre-qualified or pre-approved?", [
  ("Pre-qualified or pre-approved? One of them means nothing.", "PRE-QUALIFIED or PRE-APPROVED?"),
  ("Pre-qualified is a guess from what you told them.", "PRE-QUALIFIED = A GUESS"),
  ("Pre-approved means they checked your pay and your credit.", "PRE-APPROVED = CHECKED"),
  ("Sellers here want the second one with your offer.", "SELLERS WANT THIS"),
  ("It takes {{time}} and it's free.", "FREE"),
  ("Get it before the first showing, not after you fall in love.", None),
  ("Pre-approved. That's the one.", None)],
  verify=[("How long pre-approval takes with your lender", "Your lender")], ask="Comment LENDER", src="rocketmortgage.com Maryland guide")

talk("t16", "Cold open demo", "What should I look for in a Baltimore rowhouse?", "The first thing I check in a rowhouse", [
  ("First thing I check in a Baltimore rowhouse.", "FIRST THING I CHECK"),
  ("The ceiling on the top floor.", "LOOK UP"),
  ("Stains up here mean the flat roof has leaked.", "STAINS = ROOF"),
  ("Then I ask how old the roof is.", "HOW OLD IS IT?"),
  ("A roof is the most expensive thing on this house.", None),
  ("Then the basement. Same question, other direction.", "THEN THE BASEMENT"),
  ("Follow. I'll show you the basement next.", "FOLLOW FOR PART 2"),
  ("Look up first. Every time.", None)],
  place="Inside a rowhouse you have permission to film: top floor, then basement stairs",
  cut={2: "Slow pan across a top-floor ceiling. 4 seconds", 5: "Walking down the basement stairs, phone forward. 4 seconds"},
  verify=[("You have the owner's permission to film inside", "The seller or your listing agreement")], ask="Follow for part 2", src="activerain.com: what to check before you buy a Baltimore rowhome")

talk("t17", "Numbered list", "What questions should I ask at a showing?", "3 questions at every Baltimore showing", [
  ("3 questions I ask at every Baltimore showing.", "3 QUESTIONS"),
  ("One. Is there a ground rent?", "1. GROUND RENT?"),
  ("Two. How old is the roof?", "2. ROOF AGE?"),
  ("Three. Was that deck built with a permit?", "3. PERMITS?"),
  ("Unpermitted work becomes your problem at closing.", None),
  ("Save this for your next showing.", "SAVE THIS"),
  ("3 questions. Ask all of them.", None)],
  verify=[], ask="Save this", src="activerain.com, biggerpockets.com Baltimore red-flag threads")

talk("t18", "Nobody tells you", "Do I have to sign something before touring homes?", "The paper you sign before a showing", [
  ("Nobody tells you there's paperwork before your first showing.", "BEFORE YOUR FIRST SHOWING"),
  ("You sign a buyer agreement with your agent first.", "BUYER AGREEMENT"),
  ("It says what I do and how I get paid.", "WHAT I DO. HOW I'M PAID."),
  ("It's negotiable. Read it. Ask me anything in it.", "IT'S NEGOTIABLE"),
  ("It can be for one house or for months.", None),
  ("A good agent walks you through it line by line.", None),
  ("Paperwork first. Now you know.", None)],
  verify=[("Your brokerage's current buyer agreement terms and how you may describe them", "Long & Foster compliance")], ask="Questions? DM me", src="karashaffer.evrealestate.com: agreement before touring")

talk("t19", "Question", "How much does it cost to sell a house in Maryland?", "What it costs to sell here", [
  ("What does it cost to sell a house in Baltimore?", "COST TO SELL"),
  ("More than the commission.", None),
  ("Transfer and recordation taxes. Who pays is in the contract.", "TRANSFER TAXES"),
  ("Your mortgage payoff.", "PAYOFF"),
  ("Repairs the buyer asks for after inspection.", "REPAIRS"),
  ("All in, sellers here net about {{net percent}} of the price.", "{{NET %}}"),
  ("Comment NET and I'll run your number before you list.", 'COMMENT "NET"'),
  ("Know your net before the sign goes up.", None)],
  verify=[("Typical seller net as a percent of price in your deals", "Your own closing statements"), ("How you may describe commission", "Long & Foster compliance")], ask="Comment NET", src="bankrate.com, homelight.com: cost to sell in Maryland")

talk("t20", "Contrarian", "Can I sell my house as-is in Maryland?", "As-is doesn't mean what you think", [
  ("Selling as-is in Maryland doesn't mean what you think.", "AS-IS?"),
  ("It means you won't make repairs.", "NO REPAIRS"),
  ("It doesn't mean you can hide what you know.", "YOU STILL DISCLOSE"),
  ("Maryland has you disclose or disclaim, in writing.", "DISCLOSE OR DISCLAIM"),
  ("Buyers can still inspect. They can still walk.", None),
  ("Priced right, as-is sells. Priced wrong, it sits.", None),
  ("As-is. Not as-secret.", None)],
  verify=[("Wording on Maryland disclosure and disclaimer requirements", "Your broker or a real estate attorney")], ask="Thinking of selling? DM me", src="homelight.com: selling as-is in Maryland")

talk("t21", "Nobody tells you", "What is ground rent in Baltimore?", "Nobody tells you about Baltimore ground rent", [
  ("Nobody tells you about Baltimore ground rent.", "GROUND RENT"),
  ("You can own the rowhouse and not the land.", "YOU OWN THE HOUSE. NOT THE LAND."),
  ("Somebody else owns the dirt. You pay them rent.", None),
  ("Usually it's small. Maybe {{$100}} a year.", "{{$100}} / YEAR"),
  ("But nobody mails you a reminder.", "NO BILL. NO REMINDER."),
  ("So before any offer, I ask one thing.", None),
  ("Is there a ground rent on this house?", "ASK THIS FIRST"),
  ("Comment GROUND and I'll send you how to check.", 'COMMENT "GROUND"'),
  ("That's ground rent. Now somebody told you.", None)],
  verify=[("Typical annual amount", "Your title company")], ask="Comment GROUND", src="Already on your slate as the 2026-11-13 reel, with full shot directions")

talk("t22", "Nobody tells you, Spanish", "¿Cuánto necesito para comprar una casa de $400,000?", "Casa de $400K: cuánto necesitas", [
  ("¿Cuánto necesitas para una casa de $400,000?", "CASA DE $400K"),
  ("No son $80,000. Eso es el 20%, y es opcional.", "20% = $80,000"),
  ("Con el 3% son $12,000.", "3% = $12,000"),
  ("Con FHA, tres y medio. $14,000.", "FHA 3.5% = $14,000"),
  ("Y Baltimore tiene ayuda para el enganche.", "HAY AYUDA"),
  ("Comenta CASA y te mando los números.", 'COMENTA "CASA"'),
  ("$400,000. Mucho menos de lo que crees para entrar.", None)],
  verify=[("Read the Spanish out loud once; change any word you would not say", "You"), ("Current incentive amounts", "Live Baltimore")], ask="Comenta CASA", src="Same figures as t02")

# ---------------- no-talk pointing videos ----------------
# One continuous take. You hold each move for its seconds; the text is added on top in the edit.
# Screen positions are as the viewer sees them. Facing the phone, the RIGHT side of the screen is on your LEFT.
SIDE = {"right": " It's on the right of the screen, so point to your left.", "left": " It's on the left of the screen, so point to your right."}
def cue_list(cues):
    out, t = [], 0.0
    last = len(cues) - 1
    for i, c in enumerate(cues):
        secs, txt, pos, do = c[:4]; keep = len(c) > 4 and c[4]
        hint = next((v for k, v in SIDE.items() if pos.endswith(k)), "") if "Point" in do or "point" in do else ""
        out.append({"at": round(t, 1), "secs": secs, "text": txt, "pos": pos, "do": do + hint, "keep": bool(keep)})
        t += secs
    end_last = out[last]["at"] if out else 0
    for i, c in enumerate(out):
        c["end"] = round(end_last if c["keep"] and i < last else c["at"] + c["secs"], 1)
    out[last]["end"] = round(t, 1)
    return out, round(t, 1)

def point(id, shape, q, title, setup, cues, verify=(), ask="", src=""):
    cl, total = cue_list(cues)
    beat = {"say": "", "screen": cl[0]["text"], "cues": cl, "seconds": total, "stand": setup["stand"],
            "shot": "One continuous take, about %d seconds. Do the moves below in order and hold each one for its count." % round(total),
            "framing": setup.get("framing", "Medium wide (knees up), with empty space on the side where the text goes"),
            "angle": "Eye level", "move": "Locked on tripod", "location": setup["where"], "broll": None, "punch": False}
    bank.append(dict(id=id, kind="point", shape=shape, question=q, title=title, beats=[beat], setup=setup, verify=list(verify), ask=ask, source=src))

def text(id, shape, q, title, stack, clip, verify=(), ask="", src="", secs=2.2):
    cues = [(secs if i < len(stack) - 1 else secs + 1.5, line, "r%d" % (i + 1), "Keep doing the same thing. The line adds under the last one.", i < len(stack) - 1) for i, line in enumerate(stack)]
    cl, total = cue_list(cues)
    setup = {"where": "Wherever the clip is", "stand": "center", "phone": "Tripod or a steady hand. Vertical.", "clip": clip}
    beat = {"say": "", "screen": stack[0], "cues": cl, "seconds": total, "stand": "center", "shot": clip, "framing": "Wide", "angle": "Eye level",
            "move": "Locked on tripod", "location": "Wherever the clip is", "broll": None, "punch": False}
    bank.append(dict(id=id, kind="text", shape=shape, question=q, title=title, beats=[beat], setup=setup, verify=list(verify), ask=ask, source=src))

TRIPOD = "Tripod at chest height, phone vertical, about 7 feet away so you're framed from the knees up."
point("p01", "This / not that", "What should I not do before buying a house?", "Before you buy: don't / do",
  {"where": "Sidewalk in front of a rowhouse", "stand": "center", "phone": TRIPOD, "wear": "Solid color top"},
  [(3.0, "BEFORE YOU BUY A HOUSE IN BALTIMORE", "top", "Stand in the middle, arms crossed, serious look straight at the lens."),
   (2.5, "DON'T: BUY A NEW CAR", "top-right", "Point up at it with your left hand and shake your head."),
   (2.5, "DON'T: OPEN A NEW CREDIT CARD", "top-right", "Same spot. Wag your finger at it."),
   (2.5, "DON'T: SWITCH JOBS", "top-right", "Point at it, then grimace at the lens."),
   (3.0, "DO: GET PRE-APPROVED FIRST", "top-left", "Swing both hands across to point at it. Big nod, thumbs up."),
   (3.0, 'COMMENT "LENDER" FOR MINE', "mid", "Point down at the bottom of the screen, where the comments are.")],
  ask="Comment LENDER", src="credible.com first-time buyer mistakes")

point("p02", "This / not that", "Do I need 20% down?", "Down payment: what you think vs what it is",
  {"where": "Sidewalk in front of a rowhouse", "stand": "center", "phone": TRIPOD, "wear": "Solid color top"},
  [(3.0, "DOWN PAYMENT ON A $400,000 HOUSE?", "top", "Hand on your chin, thinking face, looking at the lens."),
   (2.5, "WHAT YOU THINK: $80,000", "top-left", "Point at it with your right hand, eyes wide, shake your head.", True),
   (2.5, "3% DOWN: $12,000", "top-right", "Point at it with your left hand and nod.", True),
   (2.5, "FHA 3.5%: $14,000", "mid-right", "Point a little lower on the same side and nod.", True),
   (2.5, "VA: $0", "low-right", "Point lower again. Eyebrows up, both hands.", True),
   (3.0, "WHICH ONE ARE YOU?", "top", "Shrug at the lens with both palms up.")],
  verify=[("3%, 3.5% FHA and 0% VA minimums at your lender", "Your lender")], ask="Which one are you?", src="sofi.com: down payment on a $400K house")

point("p03", "Walk up and point", "What are red flags on a Baltimore rowhouse?", "Rowhouse red flags: where to look",
  {"where": "Public sidewalk facing a rowhouse front with a chimney visible. Your own listing is safest.", "stand": "left",
   "phone": "Tripod across the sidewalk, about 10 feet back, so the whole front of the house is in frame behind you.",
   "framing": "Wide: you on the left of the frame, the house front filling the right"},
  [(3.0, "ROWHOUSE RED FLAGS: WHERE TO LOOK", "top", "Walk in from the left edge of the frame, stop, look at the lens."),
   (3.0, "BRICK BULGING OUT?", "mid-right", "Turn and point at the middle of the brick front."),
   (3.0, "RUST ON THE STEEL ABOVE WINDOWS?", "top-right", "Point up at the top edge of a window."),
   (3.0, "DOWNSPOUT DUMPING AT THE WALL?", "low-right", "Point down at where the downspout meets the ground."),
   (3.0, "CHIMNEY CRUMBLING?", "top-right", "Point straight up at the chimney."),
   (3.0, "SAVE THIS FOR YOUR NEXT SHOWING", "top", "Turn back, point at the lens, nod.")],
  verify=[("The text asks questions so you are not saying this house has the defect. Film a house you have permission to film.", "The owner, or use your listing")],
  ask="Save this", src="biggerpockets.com: Baltimore red flags (bulging brick, lintels, downspouts, chimneys)")

point("p04", "Numbered list", "What costs are there besides the down payment?", "It's not just the down payment",
  {"where": "Sidewalk or a front porch", "stand": "center", "phone": TRIPOD},
  [(3.0, "BUYING A HOUSE? SAVE FOR 4 THINGS", "top", "Hold up four fingers at the lens."),
   (2.5, "1. DOWN PAYMENT", "top-left", "Point up at it with your right hand.", True),
   (2.5, "2. CLOSING COSTS", "top-right", "Point up at it with your left hand.", True),
   (2.5, "3. HOME INSPECTION", "mid-left", "Point out at it, chest height, right hand.", True),
   (2.5, "4. MOVING + FIRST REPAIR", "mid-right", "Point out at it, chest height, left hand.", True),
   (3.0, "MOST PEOPLE ONLY SAVE FOR #1", "top", "Hold up one finger and shake your head.")],
  ask="Comment COSTS", src="amerisave.com first-time buyer questions")

point("p05", "This / not that", "What do I look at during a showing?", "At a showing: look here, not there",
  {"where": "Inside a furnished living room you have permission to film", "stand": "center",
   "phone": "Tripod in a corner of the room, chest height, so the couch, a wall and the ceiling are in frame."},
  [(3.0, "AT A SHOWING, LOOK HERE", "top", "Stand in the middle of the room, arms open."),
   (2.5, "NOT THE COUCH", "mid-left", "Point at the furniture and shake your head."),
   (2.5, "NOT THE PAINT", "mid-right", "Point at a painted wall and shake your head."),
   (2.5, "YES: THE CEILING", "top", "Point straight up and nod."),
   (2.5, "YES: WHERE FLOOR MEETS WALL", "low-left", "Crouch and point at the bottom of a wall. Nod."),
   (3.0, "PAINT IS CHEAP. ROOFS AREN'T.", "top", "Stand back up and shrug at the lens.")],
  verify=[("Permission to film inside", "The owner")], ask="Save this", src="activerain.com rowhome checklist")

point("p06", "Numbered list", "What documents do I need for a mortgage?", "3 things your lender asks for",
  {"where": "Kitchen table or desk, papers in front of you", "stand": "right", "phone": TRIPOD + " Stand on the right so the list builds on the left."},
  [(3.0, "YOUR LENDER WILL ASK FOR 3 THINGS", "top", "Hold up three fingers."),
   (2.5, "PAY STUBS", "top-left", "Point at it with your right hand. Nod.", True),
   (2.5, "W-2s OR TAX RETURNS", "mid-left", "Point a little lower. Nod.", True),
   (2.5, "BANK STATEMENTS", "low-left", "Point lower again. Nod.", True),
   (2.5, "HAVE THEM READY = FASTER PRE-APPROVAL", "top", "Thumbs up at the lens."),
   (3.0, 'COMMENT "LIST" FOR THE FULL CHECKLIST', "mid", "Point down at the comments.")],
  verify=[("Your lender's actual document list and how many months of statements", "Your lender"), ("You have a checklist ready to send", "You")], ask="Comment LIST", src="rocketmortgage.com Maryland guide")

point("p07", "This / not that", "What is ground rent?", "What you own in Baltimore",
  {"where": "Sidewalk next to rowhouse marble steps", "stand": "left", "phone": TRIPOD + " The steps and the front door should be on the right side of the frame."},
  [(3.0, "WHAT YOU OWN WHEN YOU BUY IN BALTIMORE", "top", "Stand beside the steps and look at the lens."),
   (2.5, "THE HOUSE: YOURS", "top-right", "Point at the front of the house behind you. Nod."),
   (2.5, "THE STEPS: YOURS", "mid-right", "Point at the marble steps. Nod."),
   (3.0, "THE GROUND UNDER IT: MAYBE NOT", "mid", "Point straight down at the sidewalk. Tilt your head, confused face."),
   (2.5, "IT'S CALLED GROUND RENT", "top", "Look at the lens, eyebrows up."),
   (3.0, "ASK BEFORE YOU OFFER", "top", "Point at the lens.")],
  ask="Comment GROUND", src="activerain.com: ground rent in Baltimore")

point("p08", "This / not that", "Should I get pre-approved before looking?", "The order that works",
  {"where": "Sidewalk or porch", "stand": "center", "phone": TRIPOD},
  [(2.5, "HOW MOST PEOPLE DO IT", "top-left", "Point at it with your right hand, unimpressed face.", True),
   (2.5, "1. FALL IN LOVE WITH A HOUSE", "mid-left", "Hands on your heart, dreamy look.", True),
   (2.5, "2. THEN CALL A LENDER", "low-left", "Shrug and grimace.", True),
   (2.5, "HOW IT SHOULD GO", "top-right", "Take a step to your left and point at it with your left hand.", True),
   (2.5, "1. GET PRE-APPROVED", "mid-right", "Point at it and nod.", True),
   (2.5, "2. THEN FIND THE HOUSE", "low-right", "Point at it, thumbs up.", True),
   (3.0, "SO YOU CAN OFFER THE SAME DAY", "top", "Snap your fingers and point at the lens.")],
  ask="Comment LENDER", src="rocketmortgage.com")

point("p09", "This / not that", "What credit score do I need?", "Credit score: myth vs minimum",
  {"where": "Sidewalk or porch", "stand": "center", "phone": TRIPOD},
  [(3.0, "CREDIT SCORE YOU NEED TO BUY A HOUSE", "top", "Hand on your chin."),
   (2.5, '"YOU NEED 750"', "top-left", "Point at it with your right hand, cross your arms in an X.", True),
   (2.5, "FHA: 580", "top-right", "Point at it with your left hand and nod.", True),
   (2.5, "CONVENTIONAL: 620", "mid-right", "Point a little lower and nod.", True),
   (2.5, "HIGHER SCORE = LOWER RATE", "top", "Raise one hand slowly like a lever."),
   (3.0, "WHAT'S YOURS?", "top", "Shrug and point at the lens.")],
  verify=[("580 FHA and 620 conventional minimums at your lender", "Your lender")], ask="What's yours?", src="credible.com")

point("p10", "Numbered list", "First-time buyer programs Baltimore", "Money Baltimore buyers never ask for",
  {"where": "Sidewalk in front of a rowhouse", "stand": "center", "phone": TRIPOD},
  [(3.0, "MONEY MOST BALTIMORE BUYERS NEVER ASK FOR", "top", "Palms up, raised eyebrows."),
   (2.5, "CITY FIRST-TIME BUYER INCENTIVE", "top-left", "Point at it with your right hand.", True),
   (2.5, "MARYLAND MORTGAGE PROGRAM", "top-right", "Point at it with your left hand.", True),
   (2.5, "REINVEST BALTIMORE", "mid-left", "Point at it, chest height.", True),
   (2.5, "HOMESTEAD TAX CREDIT", "mid-right", "Point at it, chest height.", True),
   (3.0, 'COMMENT "MONEY" FOR THE LIST', "low-left", "Point down at the comments.")],
  verify=[("All four programs are open and funded this month", "Live Baltimore, Maryland DHCD")], ask="Comment MONEY", src="livebaltimore.com, dhcd.maryland.gov")

point("p11", "This / not that, Spanish", "Antes de comprar casa", "Antes de comprar: sí / no",
  {"where": "Sidewalk in front of a rowhouse", "stand": "center", "phone": TRIPOD},
  [(3.0, "ANTES DE COMPRAR CASA EN BALTIMORE", "top", "Brazos cruzados, mirada seria a la cámara."),
   (2.5, "NO: CARRO NUEVO", "top-right", "Señálalo con la mano izquierda y di que no con la cabeza."),
   (2.5, "NO: TARJETA NUEVA", "top-right", "Mismo lugar. Mueve el dedo: no."),
   (3.0, "SÍ: PRE-APROBACIÓN PRIMERO", "top-left", "Señala con las dos manos al otro lado. Asiente, pulgar arriba."),
   (3.0, 'COMENTA "CASA"', "mid", "Señala hacia abajo, a los comentarios.")],
  verify=[("Read the Spanish once and change anything you would not say", "You")], ask="Comenta CASA", src="Same as Before you buy")

point("p12", "This / not that", "Selling a house: what should I fix?", "Before you list: fix / skip",
  {"where": "In front of a house", "stand": "center", "phone": TRIPOD},
  [(3.0, "SELLING? BEFORE YOU LIST", "top", "Stand in front of the house, hands on hips."),
   (2.5, "SKIP: A NEW KITCHEN", "top-left", "Point at it with your right hand, shake your head."),
   (2.5, "FIX: THE LEAK YOU KNOW ABOUT", "top-right", "Point at it with your left hand, nod."),
   (2.5, "DO: PAINT + A DEEP CLEAN", "mid-right", "Point a little lower, nod."),
   (2.5, "NEVER: HIDE A PROBLEM", "mid-left", "Point at it, cross your arms in an X."),
   (3.0, "ASK ME WHAT'S WORTH IT ON YOURS", "top", "Point at the lens.")],
  verify=[("Matches the advice you actually give sellers", "You")], ask="DM me your address", src="homelight.com seller guides")

# ---------------- text over one clip ----------------
text("x01", "Question", "How much house on $180K?", "$180K, one clip", ["YOU MAKE $180,000", "THAT'S $15,000 A MONTH", "28% RULE: $4,200 FOR HOUSING", "WHAT THAT BUYS IS IN THE CAPTION"],
  "You walking up to a rowhouse and unlocking the door. Don't look at the camera. Keep moving the whole time.", verify=[("Price for the caption", LENDER)], ask="See caption", src="bankrate.com")
text("x02", "Question", "Cash for a $400K house", "$400K, one clip", ["$400,000 HOUSE", "20% DOWN: $80,000", "3% DOWN: $12,000", "GUESS WHICH ONE MOST PEOPLE THINK THEY NEED"],
  "Slow walk toward a rowhouse front from across the street, phone in your hand, steady.", ask="Comment 400", src="sofi.com")
text("x03", "Nobody tells you", "Ground rent", "Ground rent, one clip", ["I OWN A HOUSE IN BALTIMORE", "I DON'T OWN THE LAND UNDER IT", "IT'S CALLED GROUND RENT", "(READ THE CAPTION)"],
  "You sitting on marble steps with a coffee, looking down the block. Tripod across the sidewalk.", verify=[("Use the first-person lines only if true for you; otherwise MY BUYER OWNS A HOUSE", "You")], ask="See caption", src="BAM write-up: caption-payoff clips loop")
text("x04", "Numbered list", "Showing questions", "3 questions, one clip", ["3 QUESTIONS BEFORE ANY OFFER IN BALTIMORE", "1. IS THERE A GROUND RENT?", "2. HOW OLD IS THE ROOF?", "3. WAS THE DECK PERMITTED?"],
  "Walking slowly through an empty rowhouse, phone held forward at chest height.", verify=[("Permission to film inside", "The owner")], ask="Save this", src="activerain.com")
text("x05", "Question", "Credit score", "Credit score, one clip", ["MINIMUM CREDIT SCORE TO BUY A HOUSE", "FHA: 580", "CONVENTIONAL: 620", "NOT 750"],
  "You at a laptop: close it, pick up keys, walk out of frame. Tripod beside the table.", verify=[("Minimums at your lender", "Your lender")], ask="Comment SCORE", src="credible.com")
text("x06", "Question", "Property tax", "Tax bill, one clip", ["$250,000 ROWHOUSE IN BALTIMORE CITY", "CITY TAX RATE: $2.248 PER $100", "$5,620 A YEAR", "$468 A MONTH. BUDGET FOR IT."],
  "Slow walk down a block of rowhouses, phone pointed at the fronts.", verify=[("Rate is current", "baltimorecity.gov/finance")], ask="Follow", src="baltimorecity.gov")

FOOT = "—\nNick Jungmarker | REALTOR® | Long & Foster Real Estate\n(301) 875-7182 | jungmarker.com\nEqual Housing Opportunity \U0001F3E0"
for v in bank:
    for i, b in enumerate(v["beats"]): b["id"] = "b%02d" % (i + 1)
    v["verify"] = [{"item": a, "from": "Get it from: " + b, "done": False} for a, b in v["verify"]]
    v["caption"] = v["question"] + "\n\n" + {"talk": "The short answer is in the video.", "point": "No talking needed.", "text": "The rest of the answer:\n{{write two sentences here}}"}[v["kind"]] + "\n\n" + (v["ask"] or "Follow for more") + ".\n\n" + FOOT
    spoken = sum(len(b["say"].split()) for b in v["beats"]) * 60 / 165
    v["seconds"] = round(spoken if v["kind"] == "talk" else sum(b.get("seconds", 2.5) for b in v["beats"]))
here = os.path.dirname(os.path.abspath(__file__))
json.dump(bank, open(os.path.join(here, "video-bank.json"), "w"), indent=1, ensure_ascii=False)

K = {"talk": "Talk to camera", "point": "No talking: point at text", "text": "No talking: text over one clip"}
md = ["# Video bank", "", f"{len(bank)} reels built from the questions people search about buying and selling in Baltimore.",
      "Every `{{placeholder}}` and every item under Verify needs a real answer before that reel is posted.", ""]
for kind in ("talk", "point", "text"):
    md += [f"## {K[kind]}", ""]
    for v in [x for x in bank if x["kind"] == kind]:
        md += [f"### {v['id']} · {v['title']}", f"*Question:* {v['question']}  ", f"*Shape:* {v['shape']} · about {v['seconds']}s · ask: {v['ask'] or 'follow'}", ""]
        if kind == "talk":
            md += ["| # | Say | On screen |", "|---|---|---|"] + [f"| {i+1} | {b['say']} | {b['screen'] or ''} |" for i, b in enumerate(v["beats"])]
        else:
            st = v.get("setup", {})
            md += [f"**Where:** {st.get('where','')}  ", f"**Phone:** {st.get('phone','')}  ", f"**You stand:** {st.get('stand','center')} of the frame" + ("  " if kind == "point" else "  "),
                   (f"**The clip:** {st.get('clip')}" if st.get("clip") else ""), "",
                   "| Time | Text on screen | Where the text is | What you do |", "|---|---|---|---|"]
            md += [f"| {c['at']:.1f}s | {c['text']} | {c['pos']} | {c['do']} |" for c in v["beats"][0]["cues"]]
        if v["verify"]: md += ["", "Verify: " + "; ".join(f"{x['item']} ({x['from'][13:]})" for x in v["verify"])]
        md += [f"", f"Source of the question: {v['source']}", ""]
open(os.path.join(here, "video-bank.md"), "w").write("\n".join(md) + "\n")
print(len(bank), "videos:", {k: sum(1 for v in bank if v["kind"] == k) for k in K}, "| beats:", sum(len(v["beats"]) for v in bank))
