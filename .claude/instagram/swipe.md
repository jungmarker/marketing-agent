# Swipe file: real estate short-form, 2026-11-12

1,084 Shorts across 29 accounts (9 subscribers to 4.3M). Ranked by multiple over
each account's own median of its newest 40 Shorts. Raw rows: `captured.tsv`.
Account list: `accounts.txt`. Rebuild with `.claude/skills/ig-viral/shorts_pull.py`.

**What this is and is not.** Instagram was not readable (login wall, and the
skill never logs in), so this is YouTube Shorts from creators who cross-post
their Reels. The "hook" is each Short's title, not the spoken first line;
captions could not be pulled. View counts are YouTube's, not Instagram's.
Multiples on accounts with a median under about 300 views are inflated by the
tiny baseline. Treat format findings as solid-ish and exact multiples as rough.

## What over-indexes

Base rate: 156 of 1,084 (14%) beat their account median by 3x or more.

| title shape | reached 3x | rate | read |
|---|---|---|---|
| A versus B / "X or Y?" (#17 Head To Head) | 22 of 67 | 33% | strongest repeatable signal, across 10+ accounts |
| Leading number list ("4 suburbs under $250K") (#11) | 12 of 49 | 24% | works when the list is local and has a price or place in it |
| Question as title (#16) | 36 of 220 | 16% | no better than base rate on its own; the winners are *local why* questions |
| Dollar figure in the title | 7 of 71 | 10% | below base rate. A price alone is not a hook |
| "Stop / Don't / Never" (#2 Negative Command) | 2 of 39 | 5% | the standard agent-advice opener under-performs here |

Hook score (47 vs 46) and title length (8 vs 8 words) do not separate the top
third from the bottom third. The topic and shape did; polish did not.

## Read by hand (the classifier named only 23% of titles)

1. **"What nobody tells you about [place]"**, in Spanish. Two of the top two
   rows (702x, 221x, @ViviendoEnFlorida). #3 Nobody Tells You, pointed at a
   town instead of at a process. The classifier misses it because it is Spanish.
2. **Local "explained" curiosity that is not about houses.** Maryland speed
   cameras 18.6x, why DC has no high-rises 14.1x, hidden costs of retiring in
   Maryland 7.3x (@LivingInDC, 1,350 subs). Not in hooks.json. Worth adding as
   "Local Why".
3. **Show the defect.** Inspectors walk up to the thing and point: "Brand new
   construction" 32x, "Is the sticker wrong or is the builder wrong?" 25x at
   2.3M views. #18 Cold Open Demo. The payoff is visual and in the first frame.
4. **Money-fear question with a date on it.** "Is the housing market going to
   crash or stay stuck?" 11.4x at 796K, "Why home prices aren't falling off a
   cliff" 74x, "Should you buy in 2023 or wait?" 9.5x, "Beware 1st time
   buyers!" 8.9x.
5. **Favourites lists that invite correction.** "My 3 favorite restaurants in
   San Diego. What did I miss?" 42x on a 788-subscriber account.
6. **Famous-house trivia** (Twilight house 48x, Friends apartments 5.7x). Views
   from people who will never buy in the market. Noise for lead gen.

## Top outliers (max three per account)

| x median | views | median | account | title (their words) |
|---|---|---|---|---|
| 702.7x | 156,000 | 222 | @ViviendoEnFlorida | Esto es lo que nadie te dice sobre Boca Ratón |
| 220.7x | 49,000 | 222 | @ViviendoEnFlorida | La verdad sobre vivir en Boca Raton que no te dicen |
| 137.9x | 28,000 | 203 | @ViviendoEnOrlando | Doing what I love, with the best people |
| 103.6x | 23,000 | 222 | @ViviendoEnFlorida | Oportunidades en Pre-Venta en Miami: ¡Inversiones de lujo desde cero! |
| 74.4x | 93,000 | 1,250 | @JenniferBeeston | Why home prices aren't falling off a cliff |
| 48.3x | 23,000 | 476 | @JasonCassity | The Cullen House from Twilight |
| 42.0x | 20,000 | 476 | @JasonCassity | My 3 Favorite Restaurants in San Diego. What did I miss? |
| 32.0x | 128,000 | 4,000 | @InspectorAJ | Brand new construction |
| 25.3x | 2,300,000 | 91,000 | @cyfyhomeinspections | Is the sticker wrong or is the builder wrong? |
| 24.0x | 169,000 | 7,050 | @KenPozek | Windermere or Winter Park Florida? Which one do you prefer? |
| 20.0x | 1,100 | 55 | @LivingInPhiladelphia | 4 Philly Suburbs With Homes Under $250K |
| 18.7x | 118,000 | 6,300 | @ShaheedahHill | What Happens at a Foreclosure Auction? |
| 18.6x | 7,900 | 425 | @LivingInDC | Exposing Maryland's Speed Cameras! - Bethesda MD - Greater DC Living |
| 14.3x | 372,000 | 26,000 | @EnesYilmazer | You Found the Dream Home. Now What? |
| 14.1x | 6,000 | 425 | @LivingInDC | WHY are there NO highrise buildings in DC? - Living in DC Explained |
| 13.5x | 54,000 | 4,000 | @InspectorAJ | Whoa. Nice caulk. |
| 13.3x | 14,000 | 1,050 | @AndrewFinney | Should You Sell Your House in 2023? |
| 12.9x | 711 | 55 | @LivingInPhiladelphia | Real Estate Battleground: Lennar vs. Keystone Custom Homes (Part 2) |
| 12.6x | 328,000 | 26,000 | @EnesYilmazer | You Can Own Your Dream Home |
| 11.8x | 5,200 | 440 | @CodyTuma | 5 states with the highest taxes. |
| 11.8x | 47,000 | 4,000 | @InspectorAJ | Lets inspect the exterior of a new build, shall we? |
| 11.7x | 644 | 55 | @LivingInPhiladelphia | The Rocks That Literally Ring Like Bells! |
| 11.4x | 796,000 | 70,000 | @fmsmith319 | Is The Housing Market Going To Crash Or Stay Stuck? |
| 10.8x | 2,200 | 203 | @ViviendoEnOrlando | This is your sign to buy in Winter Park |
| 10.8x | 2,200 | 203 | @ViviendoEnOrlando | Thrifting, but make it an experience |
| 10.8x | 4,600 | 425 | @LivingInDC | Life in Arlington VA - The Healthiest City in the Country | Living in Washington DC Metro  |
| 10.1x | 922,000 | 91,000 | @cyfyhomeinspections | Arizona finally got rain and countless new build homes failed |
| 9.9x | 1,700 | 172 | @ChristopheChoo | Inside a Rare Brentwood Park Estate in Los Angeles | $22.95M Fresh Prince of Bel Air |
| 9.5x | 10,000 | 1,050 | @AndrewFinney | Should You Buy a House in 2023 or Wait? |
| 9.4x | 4,500 | 476 | @JasonCassity | Stay tuned for more real estate tips like this. |
| 9.3x | 1,500 | 162 | @PreguntaleAlLender | ¡Consolida Deudas y Ahorra Dinero Ya! |
| 8.9x | 56,000 | 6,300 | @ShaheedahHill | Beware 1st Time Buyers! |
| 8.8x | 26,000 | 2,950 | @WinTheHouseYouLove | 2023 FHA Loan Requirements Highlights |
| 8.8x | 154,000 | 17,500 | @RyanSerhant | The starter home is dead |
| 8.7x | 61,000 | 7,050 | @KenPozek | Job openings in Orlando? Not what you'd think |
| 8.1x | 1,400 | 172 | @ChristopheChoo | Is This the Best View in the Hollywood Hills? |
| 8.1x | 24,000 | 2,950 | @WinTheHouseYouLove | Biden's $15k Tax Credit BILL |
| 8.0x | 1,300 | 162 | @PreguntaleAlLender | Puntaje bajo? Tu historial de pagos puede salvarte |
| 7.5x | 3,300 | 440 | @CodyTuma | 3 Steps to Get Rich in Your 30s |
| 7.4x | 1,200 | 162 | @PreguntaleAlLender | Rentar vs. Comprar: El Ahorro Real Revelado |
| 7.0x | 1,200 | 172 | @ChristopheChoo | A Private Tour of this Sunset Strip Oasis |
| 7.0x | 16,000 | 2,300 | @NicoleNark | BEST First Time Home Buyer Loans 2023 (Pt.1) |
| 6.9x | 2,100 | 305 | @LivingInBmore | Baltimore is ready when you are! |
| 6.9x | 179,000 | 26,000 | @EnesYilmazer | Cody Ko's Malibu Home Tour |
| 6.6x | 116,000 | 17,500 | @RyanSerhant | DAY IN THE LIFE OF A CEO | 4:30 AM - 10:00 PM |
