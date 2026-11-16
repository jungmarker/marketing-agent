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
point("p01", "This / not that", "What should I not do before buying a house?", "Before you buy: this, not that", [
  ("BEFORE YOU BUY A HOUSE", "Stand to the right of frame, arms crossed, look at the lens"),
  ("NEW CAR LOAN", "Point up-left at the text, shake your head no"),
  ("NEW CREDIT CARD", "Point at it, shake your head no"),
  ("CHANGING JOBS MID-LOAN", "Point at it, wince"),
  ("GET PRE-APPROVED FIRST", "Point with both hands, nod yes"),
  ("COMMENT \"LENDER\"", "Point down toward the comments")], ask="Comment LENDER", src="credible.com first-time buyer mistakes")

point("p02", "This / not that", "Do I need 20% down?", "Down payment: what you think vs what it is", [
  ("DOWN PAYMENT ON $400,000", "Stand left of frame, look at the lens"),
  ("WHAT YOU THINK: $80,000", "Point up-right, shake your head no"),
  ("3% DOWN: $12,000", "Point, nod yes"),
  ("FHA 3.5%: $14,000", "Point, nod yes"),
  ("VA: $0", "Point, nod yes, raise eyebrows"),
  ("WHICH ONE ARE YOU?", "Shrug toward the lens")], ask="Which one are you?", src="sofi.com: down payment on a $400K house")

point("p03", "Walk up and point", "What are red flags on a Baltimore rowhouse?", "Rowhouse red flags, no talking", [
  ("ROWHOUSE RED FLAGS", "Walk into frame in front of the house, stop, look at the lens"),
  ("BULGING BRICK", "Point at the brick front. Use a real example only on a house you may film"),
  ("RUSTED LINTEL OVER THE WINDOW", "Point up at the window head"),
  ("DOWNSPOUT DUMPING AT THE WALL", "Point down at the downspout"),
  ("STAINS ON THE TOP-FLOOR CEILING", "Point straight up"),
  ("SAVE THIS FOR YOUR NEXT SHOWING", "Point at the lens, nod")],
  verify=[("You have permission to film this house, and you are not implying a defect in someone's home without it", "The owner")], ask="Save this",
  src="biggerpockets.com: Baltimore red flags (bulging brick, lintels, downspouts)")

point("p04", "Numbered list", "What costs are there besides the down payment?", "It's not just the down payment", [
  ("BUYING A HOUSE? BUDGET FOR 4 THINGS", "Stand centre, hold up four fingers"),
  ("1. DOWN PAYMENT", "Point up-left"),
  ("2. CLOSING COSTS", "Point up-right"),
  ("3. INSPECTION", "Point down-left"),
  ("4. MOVING AND THE FIRST REPAIR", "Point down-right"),
  ("MOST PEOPLE ONLY SAVE FOR #1", "Hold up one finger, shake your head")], ask="Comment COSTS", src="amerisave.com first-time buyer questions")

point("p05", "This / not that", "What do I look at during a showing?", "At a showing: look here, not there", [
  ("AT A SHOWING", "Standing inside a staged room"),
  ("THE STAGING", "Point at the furniture, shake your head no"),
  ("THE PAINT COLOR", "Point at the wall, shake your head no"),
  ("THE CEILING", "Point up, nod yes"),
  ("THE BASEMENT WALLS", "Point down, nod yes"),
  ("THE ELECTRICAL PANEL", "Point off to the side, nod yes"),
  ("PAINT IS CHEAP. ROOFS ARE NOT.", "Shrug at the lens")],
  place="Inside a house you may film", verify=[("Permission to film inside", "The owner")], ask="Save this", src="activerain.com rowhome checklist")

point("p06", "Numbered list", "What documents do I need for a mortgage?", "3 things your lender asks for", [
  ("YOUR LENDER WILL ASK FOR 3 THINGS", "Stand right of frame, hold up three fingers"),
  ("PAY STUBS", "Point at the text"),
  ("TWO YEARS OF TAX RETURNS", "Point at the text"),
  ("BANK STATEMENTS", "Point at the text"),
  ("HAVE THEM READY = FASTER PRE-APPROVAL", "Thumbs up"),
  ("COMMENT \"LIST\" FOR THE FULL CHECKLIST", "Point down")],
  verify=[("Your lender's actual document list", "Your lender"), ("You have a checklist to send", "You")], ask="Comment LIST", src="rocketmortgage.com Maryland guide")

point("p07", "This / not that", "What is ground rent?", "Yours / maybe not yours", [
  ("WHAT YOU OWN IN BALTIMORE", "Standing on the sidewalk in front of a rowhouse"),
  ("THE HOUSE: YOURS", "Point at the house, nod"),
  ("THE STEPS: YOURS", "Point at the steps, nod"),
  ("THE LAND UNDER IT: MAYBE NOT", "Point at the ground, tilt your head"),
  ("IT'S CALLED GROUND RENT", "Look at the lens"),
  ("ASK BEFORE YOU OFFER", "Point at the lens")], ask="Comment GROUND", src="activerain.com: ground rent in Baltimore")

point("p08", "This / not that", "Should I get pre-approved before looking?", "The order that works", [
  ("THE ORDER MOST PEOPLE DO IT", "Stand left of frame"),
  ("1. FALL IN LOVE WITH A HOUSE", "Point, shake your head"),
  ("2. THEN CALL A LENDER", "Point, shake your head"),
  ("THE ORDER THAT WORKS", "Step to the other side of frame"),
  ("1. PRE-APPROVAL", "Point, nod"),
  ("2. THEN THE HOUSE", "Point, nod"),
  ("YOU OFFER THE SAME DAY", "Snap, point at the lens")], ask="Comment LENDER", src="rocketmortgage.com")

point("p09", "This / not that", "What credit score do I need?", "Credit score: myth vs minimum", [
  ("CREDIT SCORE TO BUY A HOUSE", "Stand right of frame"),
  ("\"YOU NEED 750\"", "Point, shake your head no"),
  ("FHA: 580", "Point, nod yes"),
  ("CONVENTIONAL: 620", "Point, nod yes"),
  ("HIGHER SCORE = LOWER RATE", "Raise your hand like a lever"),
  ("WHAT'S YOURS?", "Shrug at the lens")],
  verify=[("Minimums at your lender", "Your lender")], ask="What's yours?", src="credible.com")

point("p10", "Numbered list", "First-time buyer programs Baltimore", "Money most Baltimore buyers skip", [
  ("FREE-ISH MONEY BALTIMORE BUYERS SKIP", "Stand centre, palms up"),
  ("CITY FIRST-TIME BUYER INCENTIVE", "Point up-left"),
  ("MARYLAND MORTGAGE PROGRAM", "Point up-right"),
  ("REINVEST BALTIMORE", "Point down-left"),
  ("HOMESTEAD TAX CREDIT", "Point down-right"),
  ("COMMENT \"MONEY\" AND I'LL SEND THE LIST", "Point down")],
  verify=[("All four programs are open and funded this month", "Live Baltimore, Maryland DHCD")], ask="Comment MONEY", src="livebaltimore.com, dhcd.maryland.gov")

point("p11", "This / not that, Spanish", "Antes de comprar casa", "Antes de comprar: sí / no", [
  ("ANTES DE COMPRAR CASA", "De pie a la derecha, mira a la cámara"),
  ("CARRO NUEVO", "Señala, di que no con la cabeza"),
  ("TARJETA NUEVA", "Señala, di que no"),
  ("PRE-APROBACIÓN PRIMERO", "Señala, di que sí"),
  ("PREGUNTA POR LA AYUDA DE LA CIUDAD", "Señala, di que sí"),
  ("COMENTA \"CASA\"", "Señala hacia abajo")],
  verify=[("Read the Spanish once and change anything you would not say", "You")], ask="Comenta CASA", src="Same as p01")

point("p12", "This / not that", "Selling a house: what should I fix?", "Before you list: fix this, skip that", [
  ("SELLING? BEFORE YOU LIST", "Stand in front of the house"),
  ("NEW KITCHEN", "Point, shake your head no"),
  ("THE LEAK YOU KNOW ABOUT", "Point, nod yes"),
  ("PAINT AND A DEEP CLEAN", "Point, nod yes"),
  ("HIDING ANYTHING", "Point, big no"),
  ("ASK ME WHAT'S WORTH IT ON YOUR HOUSE", "Point at the lens")],
  verify=[("This matches the advice you actually give sellers", "You")], ask="DM me your address", src="homelight.com seller guides")

# ---------------- text over one clip ----------------
text("x01", "Question", "How much house on $180K?", "$180K, one clip", ["YOU MAKE $180,000", "THAT'S $15,000 A MONTH", "28% RULE: $4,200 FOR HOUSING", "WHAT THAT BUYS IS IN THE CAPTION"],
  "You walking up to a rowhouse and unlocking the door. 8 seconds, do not look at the camera", verify=[("Price for the caption", LENDER)], ask="See caption", src="bankrate.com")
text("x02", "Question", "Cash for a $400K house", "$400K, one clip", ["$400,000 HOUSE", "20% DOWN: $80,000", "3% DOWN: $12,000", "GUESS WHICH ONE MOST PEOPLE THINK THEY NEED"],
  "Slow push-in on a rowhouse front from across the street. 8 seconds", ask="Comment 400", src="sofi.com")
text("x03", "Nobody tells you", "Ground rent", "Ground rent, one clip", ["I OWN A HOUSE IN BALTIMORE", "I DON'T OWN THE LAND UNDER IT", "IT'S CALLED GROUND RENT", "(SEE CAPTION)"],
  "You sitting on marble steps drinking coffee, looking down the block. 7 seconds", verify=[("Only use the first-person line if it is true for you; otherwise change to MY BUYER", "You")], ask="See caption", src="BAM write-up: caption-payoff clips loop")
text("x04", "Numbered list", "Showing questions", "3 questions, one clip", ["3 QUESTIONS BEFORE ANY OFFER IN BALTIMORE", "1. IS THERE A GROUND RENT?", "2. HOW OLD IS THE ROOF?", "3. WAS THE DECK PERMITTED?"],
  "Walking through an empty rowhouse, phone forward, steady. 9 seconds", verify=[("Permission to film inside", "The owner")], ask="Save this", src="activerain.com")
text("x05", "Question", "Credit score", "Credit score, one clip", ["MINIMUM CREDIT SCORE TO BUY A HOUSE", "FHA: 580", "CONVENTIONAL: 620", "NOT 750"],
  "You at a laptop, close it, pick up keys, walk out. 7 seconds", verify=[("Minimums at your lender", "Your lender")], ask="Comment SCORE", src="credible.com")
text("x06", "Question", "Property tax", "Tax bill, one clip", ["$250,000 ROWHOUSE IN BALTIMORE CITY", "CITY TAX RATE: $2.248 PER $100", "$5,620 A YEAR", "$468 A MONTH. BUDGET FOR IT."],
  "Slow pan down a block of rowhouses. 8 seconds", verify=[("Rate is current", "baltimorecity.gov/finance")], ask="Follow", src="baltimorecity.gov")

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
            md += ["| # | Text on screen | What you do |", "|---|---|---|"] + [f"| {i+1} | {b['screen']} | {b['shot']} |" for i, b in enumerate(v["beats"])]
        if v["verify"]: md += ["", "Verify: " + "; ".join(f"{x['item']} ({x['from'][13:]})" for x in v["verify"])]
        md += [f"", f"Source of the question: {v['source']}", ""]
open(os.path.join(here, "video-bank.md"), "w").write("\n".join(md) + "\n")
print(len(bank), "videos:", {k: sum(1 for v in bank if v["kind"] == k) for k in K}, "| beats:", sum(len(v["beats"]) for v in bank))
