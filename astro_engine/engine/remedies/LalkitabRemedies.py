import swisseph as swe
from datetime import datetime
import os

# Set Swiss Ephemeris path
EPHE_PATH = os.path.join(os.path.dirname(__file__), 'ephe')
swe.set_ephe_path(EPHE_PATH)

# Planet constants
PLANETS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mars': swe.MARS,
    'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS,
    'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE,
    'Ketu': -1  # Will calculate as opposite of Rahu
}

# Complete Lal Kitab Remedies Database (108 combinations)
LAL_KITAB_REMEDIES = {
    "Sun": {
        "planet_info": {
            "day": "Sunday",
            "time": "Sunrise",
            "color": ["Red", "Saffron"],
            "metal": "Copper",
            "items": ["Wheat", "Jaggery"],
            "respect": "Father/elders"
        },
        "remedy_cycle": "43 days",
        1: {
            "domain": "Self, body, vitality",
            "benefic": "Leadership, confidence",
            "malefic": "Low vitality, eye issues, ego clashes",
            "remedies": [
                "Offer water to Sun at sunrise",
                "Pour copper water to tree",
                "Donate wheat/jaggery",
                "Respect father"
            ],
            "why": "Exchanges honor to Sun's realm, relieving self-karmic friction",
            "practical": "Morning sunlight 10-15 min; Surya chants",
            "donations": ["Wheat", "Jaggery", "Red cloth", "Copper"],
            "cautions": ["Avoid ego displays", "Avoid authority arguments"]
        },
        2: {
            "domain": "Family, speech, wealth",
            "benefic": "Dignified speech, family honor",
            "malefic": "Financial disputes, harsh words",
            "remedies": [
                "Donate food (wheat/sugar)",
                "Keep copper coin in money box",
                "Use respectful speech",
                "Give gift to father"
            ],
            "why": "Offers honor back to Sun in family/possessions",
            "practical": "Soften language; transparent finances",
            "donations": ["Wheat", "Jaggery", "Red cloth", "Food packets"],
            "cautions": ["Avoid sarcasm", "Avoid disputes"]
        },
        3: {
            "domain": "Siblings, communication, effort",
            "benefic": "Brave communicator",
            "malefic": "Sibling disputes, accidents",
            "remedies": [
                "Feed birds/crows",
                "Donate red cloth",
                "Help sibling",
                "Wear copper ring"
            ],
            "why": "Giving to 'below' balances ego clashes",
            "practical": "Mindful hand safety; measured arguments",
            "donations": ["Red cloth", "Red thread", "Food/money to younger ones"],
            "cautions": ["Avoid recklessness", "Avoid boasting"]
        },
        4: {
            "domain": "Home, mother, property",
            "benefic": "Solid family status",
            "malefic": "Domestic stress, property disputes",
            "remedies": [
                "Plant/care Tulsi with copper water",
                "Donate home items",
                "Respect mother",
                "Keep tidy pooja area"
            ],
            "why": "Builds/stabilizes home, returning Sun's desires",
            "practical": "Calm property dealings; reconcile disputes",
            "donations": ["Floor mat", "Bed linen", "Bricks"],
            "cautions": ["Avoid prideful claims"]
        },
        5: {
            "domain": "Children, intelligence, romance",
            "benefic": "Creative leader",
            "malefic": "Progeny delays, romantic pride",
            "remedies": [
                "Feed jaggery sweets to children",
                "Donate books",
                "Respect teachers"
            ],
            "why": "Giving to children/teachers stabilizes creative authority",
            "practical": "Mentorship over dominance",
            "donations": ["Educational items", "Sweets"],
            "cautions": ["Avoid arrogance in romance"]
        },
        6: {
            "domain": "Health, debts, service",
            "benefic": "Overcomes enemies via discipline",
            "malefic": "Heart issues, co-worker friction",
            "remedies": [
                "Feed needy/hospital patients",
                "Give red cloth to service workers",
                "Practice disciplined hygiene"
            ],
            "why": "Humility/service balances pride causing issues",
            "practical": "Follow medical advice",
            "donations": ["Food packets", "Red cloth"],
            "cautions": ["Avoid workplace aggression"]
        },
        7: {
            "domain": "Marriage, contracts",
            "benefic": "Dignified partnerships",
            "malefic": "Ego clashes in marriage",
            "remedies": [
                "Make offerings to partner's parents",
                "Donate red cloth at couple temple",
                "Practice public humility"
            ],
            "why": "Acknowledging partner heals imbalance",
            "practical": "Make balanced decisions",
            "donations": ["Red/saffron cloth"],
            "cautions": ["Avoid one-sided choices"]
        },
        8: {
            "domain": "Secrets, longevity",
            "benefic": "Regenerative capacity",
            "malefic": "Sudden losses, health mysteries",
            "remedies": [
                "Donate to transformative charities",
                "Offer oil lamp",
                "Respect privacy"
            ],
            "why": "Transforms control into service for transitions",
            "practical": "Be conservative in speculation",
            "donations": ["Oil", "To hospice/orphanage"],
            "cautions": ["Avoid prying", "Avoid occult shortcuts"]
        },
        9: {
            "domain": "Father, higher learning",
            "benefic": "Clear dharma, luck",
            "malefic": "Father troubles, faith loss",
            "remedies": [
                "Donate books/oil to priests",
                "Visit elder for blessings",
                "Support pilgrimages"
            ],
            "why": "Giving to dharma realm returns honor",
            "practical": "Honor education commitments",
            "donations": ["Books", "Food to teachers"],
            "cautions": ["Avoid prideful dismissal of elders"]
        },
        10: {
            "domain": "Profession, authority",
            "benefic": "Prominent career",
            "malefic": "Setbacks, boss conflicts",
            "remedies": [
                "Donate to public institutions",
                "Offer token to government temple",
                "Acknowledge mentors"
            ],
            "why": "Giving honor to public role maintains balance",
            "practical": "Maintain humble visibility",
            "donations": ["To schools/public service"],
            "cautions": ["Avoid ego politics"]
        },
        11: {
            "domain": "Gains, aspirations",
            "benefic": "Influence circle",
            "malefic": "Blocked aspirations, sibling disputes",
            "remedies": [
                "Donate to community kitchens",
                "Host meal",
                "Share recognition"
            ],
            "why": "Outward giving reclaims inward gains",
            "practical": "Engage in humble networking",
            "donations": ["To elders/mentors"],
            "cautions": ["Avoid self-centered pursuits"]
        },
        12: {
            "domain": "Expenditure, isolation",
            "benefic": "Soulful seclusion",
            "malefic": "Loneliness, spending leaks",
            "remedies": [
                "Donate to hospitals/old-age homes",
                "Light lamp for isolated",
                "Practice humble service"
            ],
            "why": "Sacrificial service heals ego losses",
            "practical": "Use solitude for discipline",
            "donations": ["To foreign pilgrims"],
            "cautions": ["Avoid impulsive spending"]
        }
    },
    "Moon": {
        "planet_info": {
            "day": "Monday",
            "time": "Daylight",
            "color": "White",
            "metal": "Silver",
            "items": ["Milk", "Rice"],
            "respect": "Mother/women"
        },
        "remedy_cycle": "43 days",
        1: {
            "domain": "Personality, emotions",
            "benefic": "Intuitive, caring",
            "malefic": "Mood swings, insomnia",
            "remedies": [
                "Offer milk to Shivling",
                "Keep silver utensils",
                "Serve mother",
                "Avoid alcohol"
            ],
            "why": "Soothes emotional imbalance via mother-karma",
            "practical": "Maintain clean surroundings",
            "donations": ["Milk", "Silver"],
            "cautions": ["Avoid night wandering"]
        },
        2: {
            "domain": "Family, finances",
            "benefic": "Sweet voice, support",
            "malefic": "Deceptive speech, over-indulgence",
            "remedies": [
                "Donate milk/rice",
                "Avoid late eating",
                "Feed white animals",
                "Keep silver coin in purse"
            ],
            "why": "Stabilizes emotional wealth",
            "practical": "Practice mindful eating",
            "donations": ["Milk", "Rice"],
            "cautions": ["Avoid harsh words"]
        },
        3: {
            "domain": "Communication, skills",
            "benefic": "Creative communicator",
            "malefic": "Weak courage, disputes",
            "remedies": [
                "Feed wheat-jaggery to cows",
                "Wear silver ring",
                "Help siblings",
                "Avoid boasts"
            ],
            "why": "Service strengthens emotional courage",
            "practical": "Practice honest communication",
            "donations": ["Wheat dough"],
            "cautions": ["Avoid false promises"]
        },
        4: {
            "domain": "Home, property",
            "benefic": "Peaceful domestic life",
            "malefic": "Disturbed home, mother's health issues",
            "remedies": [
                "Keep silver pot with water",
                "Donate white sweets",
                "Feed cows",
                "Avoid quarrels with mother"
            ],
            "why": "Harmony through mother-service",
            "practical": "Maintain pure water routines",
            "donations": ["Milk", "Rice"],
            "cautions": ["Avoid domestic arguments"]
        },
        5: {
            "domain": "Children, speculation",
            "benefic": "Artistic imagination",
            "malefic": "Child issues, unstable love",
            "remedies": [
                "Feed kheer to children",
                "Gift white clothes to girls",
                "Respect teachers",
                "Avoid gambling"
            ],
            "why": "Blessings from children/teachers enhance flow",
            "practical": "Make stable judgments",
            "donations": ["White clothes"],
            "cautions": ["Avoid false pride"]
        },
        6: {
            "domain": "Health, debts",
            "benefic": "Disciplined health",
            "malefic": "Stomach issues, stress",
            "remedies": [
                "Donate milk to workers",
                "Feed stray dogs",
                "Clean water vessel",
                "Avoid night milk"
            ],
            "why": "Humble service balances stress",
            "practical": "Maintain routine hygiene",
            "donations": ["Milk", "Rice"],
            "cautions": ["Avoid emotional manipulation"]
        },
        7: {
            "domain": "Spouse, contracts",
            "benefic": "Harmonious partnerships",
            "malefic": "Mistrust, quarrels",
            "remedies": [
                "Gift white items to spouse",
                "Donate milk",
                "Respect women",
                "Avoid extra-marital affairs"
            ],
            "why": "Calms emotions in shared life",
            "practical": "Practice open communication",
            "donations": ["Milk", "Rice"],
            "cautions": ["Avoid mood swings"]
        },
        8: {
            "domain": "Hidden matters",
            "benefic": "Strong intuition",
            "malefic": "Restlessness, losses",
            "remedies": [
                "Float rice in water",
                "Donate milk",
                "Respect women",
                "Keep silver"
            ],
            "why": "Stabilizes turbulent debts",
            "practical": "Respect privacy",
            "donations": ["Milk to orphanage"],
            "cautions": ["Avoid hurting women"]
        },
        9: {
            "domain": "Luck, father",
            "benefic": "Philosophical faith",
            "malefic": "Wavering faith, father issues",
            "remedies": [
                "Donate milk to religious places",
                "Serve father",
                "Offer white sweets",
                "Avoid disrespect to elders"
            ],
            "why": "Honors guru/father blessings",
            "practical": "Maintain devotional routines",
            "donations": ["Milk", "Rice"],
            "cautions": ["Avoid elder disrespect"]
        },
        10: {
            "domain": "Profession, status",
            "benefic": "Emotional intelligence at work",
            "malefic": "Instability, boss conflicts",
            "remedies": [
                "Donate white clothes to women",
                "Keep silver glass at work",
                "Respect boss",
                "Avoid dishonesty"
            ],
            "why": "Stabilizes reputation",
            "practical": "Maintain honest dealings",
            "donations": ["Milk", "White clothes"],
            "cautions": ["Avoid backbiting"]
        },
        11: {
            "domain": "Ambitions, siblings",
            "benefic": "Social support",
            "malefic": "Ups/downs in gains",
            "remedies": [
                "Feed kheer to children",
                "Keep silver pot with water",
                "Respect elders",
                "Avoid selfishness"
            ],
            "why": "Donations stabilize group gains",
            "practical": "Make credible promises",
            "donations": ["Milk rice to poor"],
            "cautions": ["Avoid emotional dependence"]
        },
        12: {
            "domain": "Losses, foreign",
            "benefic": "Spiritual compassion",
            "malefic": "Depression, overspending",
            "remedies": [
                "Donate to shelters",
                "Float silver",
                "Light ghee lamp",
                "Practice silent charity"
            ],
            "why": "Transforms leaks into karma",
            "practical": "Keep mind uncluttered",
            "donations": ["Milk, rice to hospitals"],
            "cautions": ["Avoid pride in charity"]
        }
    },
    "Mars": {
        "planet_info": {
            "day": "Tuesday",
            "time": "Daylight",
            "color": "Red",
            "metal": "Copper",
            "items": ["Masoor dal", "Honey"],
            "respect": "Brothers/mother"
        },
        "remedy_cycle": "43 days",
        1: {
            "domain": "Personality, body",
            "benefic": "Brave physique",
            "malefic": "Aggression, accidents",
            "remedies": [
                "Take honey drop daily",
                "Respect brothers",
                "Donate masoor dal",
                "Avoid violence"
            ],
            "why": "Sweetens aggression, clears brother-karma",
            "practical": "Practice anger control",
            "donations": ["Red lentils"],
            "cautions": ["Avoid alcohol"]
        },
        2: {
            "domain": "Wealth, food",
            "benefic": "Bold protector",
            "malefic": "Harsh tongue, quarrels",
            "remedies": [
                "Keep silver",
                "Donate masoor/sindoor",
                "Feed cows sweet roti",
                "Control speech"
            ],
            "why": "Cools fiery family karma",
            "practical": "Use mindful words",
            "donations": ["Masoor dal"],
            "cautions": ["Avoid wasteful expenses"]
        },
        3: {
            "domain": "Brothers, journeys",
            "benefic": "Adventurous",
            "malefic": "Sibling fights, risks",
            "remedies": [
                "Serve brothers",
                "Donate red clothes",
                "Feed monkeys jaggery",
                "Avoid lying"
            ],
            "why": "Balances disputes in Mars's field",
            "practical": "Practice safe travel",
            "donations": ["Red clothes"],
            "cautions": ["Avoid boasting"]
        },
        4: {
            "domain": "Property, vehicles",
            "benefic": "Land gains",
            "malefic": "Mother health, home accidents",
            "remedies": [
                "Keep honey pot at home",
                "Respect mother",
                "Feed cows fodder",
                "Avoid anger at home"
            ],
            "why": "Pacifies domestic fire",
            "practical": "Maintain clutter-free home",
            "donations": ["Green fodder"],
            "cautions": ["Avoid alcohol at home"]
        },
        5: {
            "domain": "Education, romance",
            "benefic": "Disciplined creativity",
            "malefic": "Child issues, impulsivity",
            "remedies": [
                "Drink copper water daily",
                "Donate to Hanuman temple",
                "Feed sweets to children",
                "Avoid gambling"
            ],
            "why": "Balances blood/heat in progeny",
            "practical": "Practice patient guidance",
            "donations": ["Masoor dal"],
            "cautions": ["Avoid speculation"]
        },
        6: {
            "domain": "Debts, service",
            "benefic": "Enemy victor",
            "malefic": "Blood diseases, quarrels",
            "remedies": [
                "Donate masoor/sindoor",
                "Feed crows/dogs",
                "Respect servants",
                "Avoid red donations"
            ],
            "why": "Channels energy to service",
            "practical": "Maintain disciplined health",
            "donations": ["Red masoor"],
            "cautions": ["Avoid exploitation"]
        },
        7: {
            "domain": "Spouse, partnerships",
            "benefic": "Passionate bonds",
            "malefic": "Quarrels, Manglik effects",
            "remedies": [
                "Keep honey at home",
                "Gift red to spouse",
                "Feed monkeys/cows",
                "Respect spouse family"
            ],
            "why": "Pacifies marital fire",
            "practical": "Maintain balanced passion",
            "donations": ["Red clothes"],
            "cautions": ["Avoid infidelity"]
        },
        8: {
            "domain": "Inheritance, sudden events",
            "benefic": "Occult courage",
            "malefic": "Accidents, losses",
            "remedies": [
                "Float coconut",
                "Feed birds",
                "Avoid meat/liquor",
                "Respect in-laws"
            ],
            "why": "Surrenders hidden debts",
            "practical": "Be conservative with risks",
            "donations": ["Coconut"],
            "cautions": ["Avoid occult misuse"]
        },
        9: {
            "domain": "Luck, journeys",
            "benefic": "Dharmic leadership",
            "malefic": "Father quarrels, bad luck",
            "remedies": [
                "Donate masoor/copper",
                "Respect father",
                "Offer Sun water",
                "Avoid arrogance"
            ],
            "why": "Balances fiery dharma",
            "practical": "Practice sincere devotion",
            "donations": ["Red masoor"],
            "cautions": ["Avoid religious pride"]
        },
        10: {
            "domain": "Status, authority",
            "benefic": "Technical leadership",
            "malefic": "Job fights, changes",
            "remedies": [
                "Keep honey jar",
                "Donate masoor",
                "Respect bosses",
                "Avoid false statements"
            ],
            "why": "Softens work harshness",
            "practical": "Maintain ethical conduct",
            "donations": ["Sindoor"],
            "cautions": ["Avoid office quarrels"]
        },
        11: {
            "domain": "Elder siblings, aspirations",
            "benefic": "Courageous gains",
            "malefic": "Sibling disputes, unstable income",
            "remedies": [
                "Feed monkeys chana",
                "Donate masoor",
                "Gift red to elders",
                "Avoid misuse"
            ],
            "why": "Clears gain blockages",
            "practical": "Maintain loyal networks",
            "donations": ["Copper items"],
            "cautions": ["Avoid selfish groups"]
        },
        12: {
            "domain": "Expenditure, foreign",
            "benefic": "Spiritual discipline",
            "malefic": "Overspending, abroad accidents",
            "remedies": [
                "Float masoor",
                "Donate red clothes",
                "Keep honey",
                "Avoid debts"
            ],
            "why": "Dissolves loss-karma",
            "practical": "Maintain budget control",
            "donations": ["Red clothes"],
            "cautions": ["Avoid unnecessary loans"]
        }
    },
    "Mercury": {
        "planet_info": {
            "day": "Wednesday",
            "time": "Daylight",
            "color": "Green",
            "metal": "Silver",
            "items": ["Moong dal"],
            "respect": "Maternal uncles/teachers"
        },
        "remedy_cycle": "43 days",
        1: {
            "domain": "Personality",
            "benefic": "Witty, youthful",
            "malefic": "Nervous, cunning",
            "remedies": [
                "Feed green fodder to cows",
                "Keep green handkerchief",
                "Serve maternal uncles",
                "Avoid lies"
            ],
            "why": "Calms nervous self-image",
            "practical": "Take decisive actions",
            "donations": ["Green gram"],
            "cautions": ["Avoid manipulation"]
        },
        2: {
            "domain": "Speech, finances",
            "benefic": "Sweet trade skills",
            "malefic": "Lying speech, instability",
            "remedies": [
                "Donate moong dal",
                "Keep silver",
                "Feed parrots",
                "Avoid false family speech"
            ],
            "why": "Balances money-family vibrations",
            "practical": "Maintain honest records",
            "donations": ["Green gram"],
            "cautions": ["Avoid harsh words"]
        },
        3: {
            "domain": "Courage, journeys",
            "benefic": "Skilled writer",
            "malefic": "Sibling quarrels, accidents",
            "remedies": [
                "Keep green cloth/bangle",
                "Serve siblings",
                "Donate moong",
                "Chant Vishnu mantras"
            ],
            "why": "Gifts clear disputes",
            "practical": "Practice safe short trips",
            "donations": ["Green vegetables"],
            "cautions": ["Avoid misuse of words"]
        },
        4: {
            "domain": "Property, heart",
            "benefic": "Learning home",
            "malefic": "Mother health, disputes",
            "remedies": [
                "Keep silver ball in locker",
                "Donate green clothes to women",
                "Respect mother",
                "Feed cows"
            ],
            "why": "Stabilizes nervous property",
            "practical": "Keep home tidy",
            "donations": ["Green clothes"],
            "cautions": ["Avoid harsh home words"]
        },
        5: {
            "domain": "Creativity, speculation",
            "benefic": "Sharp memory",
            "malefic": "Education breaks, losses",
            "remedies": [
                "Donate stationery",
                "Give green fruits to children",
                "Chant Budh mantra",
                "Avoid lying in romance"
            ],
            "why": "Heals karmic education",
            "practical": "Maintain focused learning",
            "donations": ["Books", "Pens"],
            "cautions": ["Avoid gambling"]
        },
        6: {
            "domain": "Health, debts",
            "benefic": "Clever debater",
            "malefic": "Skin/nerve issues",
            "remedies": [
                "Donate moong to workers",
                "Keep green cloth in pocket",
                "Feed cows/parrots",
                "Avoid arguments"
            ],
            "why": "Reduces stress in service",
            "practical": "Maintain clean routines",
            "donations": ["Moong dal"],
            "cautions": ["Avoid manipulative talks"]
        },
        7: {
            "domain": "Partnerships",
            "benefic": "Communicative spouse",
            "malefic": "Lies in marriage",
            "remedies": [
                "Gift green to spouse",
                "Donate moong",
                "Keep silver",
                "Avoid relationship lies"
            ],
            "why": "Harmony via gifts",
            "practical": "Maintain transparent contracts",
            "donations": ["Green fruits"],
            "cautions": ["Avoid cunning spouse issues"]
        },
        8: {
            "domain": "Transformation",
            "benefic": "Research skills",
            "malefic": "Losses, breakdowns",
            "remedies": [
                "Float moong/coconut",
                "Feed cows",
                "Donate stationery",
                "Avoid speculation"
            ],
            "why": "Reduces sudden debts",
            "practical": "Maintain privacy",
            "donations": ["Stationery to students"],
            "cautions": ["Avoid gambling"]
        },
        9: {
            "domain": "Higher learning",
            "benefic": "Philosophical trade luck",
            "malefic": "Study breaks, elder disrespect",
            "remedies": [
                "Donate green to priests",
                "Serve father",
                "Water Tulsi",
                "Avoid knowledge arrogance"
            ],
            "why": "Stabilizes dharmic imbalance",
            "practical": "Show guru respect",
            "donations": ["Green clothes"],
            "cautions": ["Avoid arrogance"]
        },
        10: {
            "domain": "Status",
            "benefic": "Business success",
            "malefic": "Unstable profession",
            "remedies": [
                "Keep silver pen at work",
                "Donate stationery",
                "Feed cows",
                "Avoid gossip"
            ],
            "why": "Enhances credibility",
            "practical": "Maintain professional honesty",
            "donations": ["Stationery to schools"],
            "cautions": ["Avoid dishonesty"]
        },
        11: {
            "domain": "Networks",
            "benefic": "Intellectual gains",
            "malefic": "False friends",
            "remedies": [
                "Donate moong to children",
                "Keep silver coin in wallet",
                "Feed parrots",
                "Avoid cheating friends"
            ],
            "why": "Strengthens via messengers",
            "practical": "Maintain loyal circles",
            "donations": ["Green vegetables"],
            "cautions": ["Avoid unstable income"]
        },
        12: {
            "domain": "Expenditure, foreign",
            "benefic": "Occult interest",
            "malefic": "Addictions, breakdowns",
            "remedies": [
                "Donate green to ashrams",
                "Feed cows/birds",
                "Keep silver near bed",
                "Avoid addictions"
            ],
            "why": "Redirects loss-energy",
            "practical": "Practice meditation",
            "donations": ["Moong dal"],
            "cautions": ["Avoid overspending"]
        }
    },
    "Jupiter": {
        "planet_info": {
            "day": "Thursday",
            "time": "Daylight",
            "color": "Yellow",
            "metal": "Gold",
            "items": ["Chana dal"],
            "respect": "Gurus/elders"
        },
        "remedy_cycle": "43 days",
        1: {
            "domain": "Personality",
            "benefic": "Wise, lucky",
            "malefic": "Arrogance, delays",
            "remedies": [
                "Donate turmeric/yellow",
                "Wear yellow",
                "Respect teachers",
                "Avoid knowledge pride"
            ],
            "why": "Restores dharma-karma",
            "practical": "Practice humble learning",
            "donations": ["Chana dal", "Yellow clothes"],
            "cautions": ["Avoid idealism excess"]
        },
        2: {
            "domain": "Speech, savings",
            "benefic": "Prosperous speech",
            "malefic": "Wealth waste, quarrels",
            "remedies": [
                "Keep gold in locker",
                "Donate chana/turmeric",
                "Respect elders",
                "Feed cows gram"
            ],
            "why": "Stabilizes expansion",
            "practical": "Practice savings discipline",
            "donations": ["Yellow sweets"],
            "cautions": ["Avoid harsh speech"]
        },
        3: {
            "domain": "Courage",
            "benefic": "Skilled siblings",
            "malefic": "Quarrels, weak effort",
            "remedies": [
                "Help siblings",
                "Donate books",
                "Feed yellow sweets to children",
                "Avoid gossip"
            ],
            "why": "Knowledge donation balances",
            "practical": "Practice patient efforts",
            "donations": ["Stationery"],
            "cautions": ["Avoid false promises"]
        },
        4: {
            "domain": "Property",
            "benefic": "Prosperous home",
            "malefic": "Mother illness",
            "remedies": [
                "Keep gold/yellow in pooja",
                "Donate yellow to women",
                "Respect mother",
                "Feed cows gram"
            ],
            "why": "Serves home harmony",
            "practical": "Provide mother care",
            "donations": ["Yellow fruits"],
            "cautions": ["Avoid domestic quarrels"]
        },
        5: {
            "domain": "Creativity",
            "benefic": "Intelligent progeny",
            "malefic": "Child problems",
            "remedies": [
                "Donate books/yellow fruits",
                "Feed children sweets",
                "Respect teachers",
                "Keep gold near study area"
            ],
            "why": "Balances education karma",
            "practical": "Maintain ethical studies",
            "donations": ["Pens", "Books"],
            "cautions": ["Avoid love arrogance"]
        },
        6: {
            "domain": "Illness",
            "benefic": "Service wisdom",
            "malefic": "Obesity, debts",
            "remedies": [
                "Donate yellow to workers",
                "Feed cows gram",
                "Respect servants",
                "Avoid arguments"
            ],
            "why": "Transforms enmity",
            "practical": "Practice humble service",
            "donations": ["Turmeric", "Yellow dal"],
            "cautions": ["Avoid arrogance"]
        },
        7: {
            "domain": "Partnerships",
            "benefic": "Prosperous spouse",
            "malefic": "Delayed marriage",
            "remedies": [
                "Donate turmeric/saffron",
                "Gift yellow to spouse",
                "Respect family",
                "Keep gold in locker"
            ],
            "why": "Stabilizes harmony",
            "practical": "Maintain balanced expectations",
            "donations": ["Yellow sweets"],
            "cautions": ["Avoid over-expectations"]
        },
        8: {
            "domain": "Secrets",
            "benefic": "Occult depth",
            "malefic": "Losses, disputes",
            "remedies": [
                "Donate yellow/bananas",
                "Float chana",
                "Respect in-laws",
                "Avoid occult arrogance"
            ],
            "why": "Reduces sudden tension",
            "practical": "Practice dispute mediation",
            "donations": ["Yellow cloth"],
            "cautions": ["Avoid secretive practices"]
        },
        9: {
            "domain": "Luck",
            "benefic": "Spiritual blessings",
            "malefic": "Guru disrespect",
            "remedies": [
                "Donate books/saffron",
                "Serve father",
                "Offer yellow sweets to priests",
                "Avoid hypocrisy"
            ],
            "why": "Strengthens dharma",
            "practical": "Maintain sincere faith",
            "donations": ["Yellow fruits"],
            "cautions": ["Avoid religious disrespect"]
        },
        10: {
            "domain": "Authority",
            "benefic": "Respected profession",
            "malefic": "Ego clashes",
            "remedies": [
                "Donate turmeric/bananas",
                "Keep gold/yellow at work",
                "Respect authority",
                "Avoid unethical acts"
            ],
            "why": "Ethical donations for stability",
            "practical": "Focus on competence",
            "donations": ["Yellow sweets"],
            "cautions": ["Avoid misuse of power"]
        },
        11: {
            "domain": "Networks",
            "benefic": "Prosperity",
            "malefic": "Sibling disputes",
            "remedies": [
                "Donate yellow to elders",
                "Wear gold ornament",
                "Respect siblings",
                "Feed cows gram"
            ],
            "why": "Stabilizes networks",
            "practical": "Keep group promises",
            "donations": ["Yellow dal", "Yellow clothes"],
            "cautions": ["Avoid arrogance in groups"]
        },
        12: {
            "domain": "Expenditure",
            "benefic": "Charitable foreign gains",
            "malefic": "Overspending",
            "remedies": [
                "Donate to ashrams",
                "Light ghee lamp",
                "Practice silent service",
                "Avoid waste"
            ],
            "why": "Redirects loss to karma",
            "practical": "Practice humble charity",
            "donations": ["Turmeric", "Chana dal"],
            "cautions": ["Avoid addictions"]
        }
    },
    "Venus": {
        "planet_info": {
            "day": "Friday",
            "time": "Daylight",
            "color": "White",
            "metal": "Silver",
            "items": ["White sweets", "Rice/ghee"],
            "respect": "Women/spouse"
        },
        "remedy_cycle": "43 days",
        1: {
            "domain": "Appearance",
            "benefic": "Charming artist",
            "malefic": "Vanity, eye issues",
            "remedies": [
                "Donate white sweets",
                "Keep silver",
                "Respect women",
                "Feed cows jaggery-rice"
            ],
            "why": "Stabilizes beauty karma",
            "practical": "Maintain balanced indulgences",
            "donations": ["White clothes"],
            "cautions": ["Avoid misconduct"]
        },
        2: {
            "domain": "Speech, possessions",
            "benefic": "Musical wealth",
            "malefic": "Wasteful quarrels",
            "remedies": [
                "Keep ghee in silver pot",
                "Donate white sweets",
                "Respect family women",
                "Feed ants sugar"
            ],
            "why": "Balances family pleasures",
            "practical": "Practice mindful spending",
            "donations": ["Milk"],
            "cautions": ["Avoid harsh words"]
        },
        3: {
            "domain": "Courage",
            "benefic": "Artistic hobbies",
            "malefic": "Sibling misuse",
            "remedies": [
                "Donate white/curd",
                "Feed cows ghee-rice",
                "Gift to siblings",
                "Avoid false love promises"
            ],
            "why": "Resolves relationship disputes",
            "practical": "Practice honest courage",
            "donations": ["White clothes"],
            "cautions": ["Avoid false romance"]
        },
        4: {
            "domain": "Comforts",
            "benefic": "Loving vehicles",
            "malefic": "Home instability",
            "remedies": [
                "Offer white flowers in temple",
                "Donate milk",
                "Gift to mother",
                "Avoid alcohol at home"
            ],
            "why": "Calms domestic vibrations",
            "practical": "Give mother gifts",
            "donations": ["White sweets"],
            "cautions": ["Avoid misconduct at home"]
        },
        5: {
            "domain": "Romance",
            "benefic": "Romantic creativity",
            "malefic": "Broken affairs",
            "remedies": [
                "Donate white to children",
                "Feed cows rice-sugar",
                "Gift flowers to partner",
                "Avoid gambling"
            ],
            "why": "Aligns harmony in love",
            "practical": "Practice patient romance",
            "donations": ["White sweets"],
            "cautions": ["Avoid speculative losses"]
        },
        6: {
            "domain": "Service",
            "benefic": "Charming work",
            "malefic": "Kidney/eye issues",
            "remedies": [
                "Donate curd/rice to poor",
                "Feed sweets to girls",
                "Respect female workers",
                "Avoid excess pleasures"
            ],
            "why": "Serves women/health debts",
            "practical": "Practice pleasure moderation",
            "donations": ["White clothes"],
            "cautions": ["Avoid quarrels with women"]
        },
        7: {
            "domain": "Spouse",
            "benefic": "Loving business",
            "malefic": "Infidelity",
            "remedies": [
                "Gift ornaments to spouse",
                "Donate curd/milk",
                "Avoid cheating",
                "Feed cows ghee-rice"
            ],
            "why": "Stabilizes marital balance",
            "practical": "Maintain faithful partnerships",
            "donations": ["White sweets"],
            "cautions": ["Avoid instability"]
        },
        8: {
            "domain": "Secrets",
            "benefic": "Sensual inheritance",
            "malefic": "Affairs, disputes",
            "remedies": [
                "Float rice/flowers",
                "Donate ghee/sugar",
                "Respect in-laws",
                "Avoid pleasure misuse"
            ],
            "why": "Reduces hidden karma",
            "practical": "Practice ethical sensuality",
            "donations": ["Curd"],
            "cautions": ["Avoid sexual health risks"]
        },
        9: {
            "domain": "Fortune",
            "benefic": "Artistic faith",
            "malefic": "Pleasure misuse in dharma",
            "remedies": [
                "Donate ghee to priests",
                "Respect father",
                "Offer white flowers in temple",
                "Avoid arrogance"
            ],
            "why": "Aligns karmic dharma",
            "practical": "Practice devotional arts",
            "donations": ["White clothes"],
            "cautions": ["Avoid religious hypocrisy"]
        },
        10: {
            "domain": "Status",
            "benefic": "Artistic profession",
            "malefic": "Scandals",
            "remedies": [
                "Keep silver in locker",
                "Donate white sweets",
                "Avoid unethical acts",
                "Gift flowers at work"
            ],
            "why": "Keeps career stable",
            "practical": "Use charm ethically",
            "donations": ["Ghee", "Sugar"],
            "cautions": ["Avoid workplace misuse"]
        },
        11: {
            "domain": "Networks",
            "benefic": "Beauty gains",
            "malefic": "Luxury waste",
            "remedies": [
                "Donate white to children",
                "Feed cows jaggery-rice",
                "Gift to sisters",
                "Avoid overspending"
            ],
            "why": "Restores social harmony",
            "practical": "Maintain balanced luxuries",
            "donations": ["White clothes"],
            "cautions": ["Avoid sibling disputes"]
        },
        12: {
            "domain": "Expenditure",
            "benefic": "Devotional foreign",
            "malefic": "Addictions",
            "remedies": [
                "Donate to ashrams",
                "Float white flowers",
                "Respect women",
                "Keep silver near bed"
            ],
            "why": "Converts expenditure to blessings",
            "practical": "Practice compassionate spending",
            "donations": ["Sugar", "Rice"],
            "cautions": ["Avoid secret affairs"]
        }
    },
    "Saturn": {
        "planet_info": {
            "day": "Saturday",
            "time": "Daylight",
            "color": "Black",
            "metal": "Iron",
            "items": ["Black til", "Mustard oil"],
            "respect": "Servants/poor"
        },
        "remedy_cycle": "43 days",
        1: {
            "domain": "Body",
            "benefic": "Disciplined longevity",
            "malefic": "Depression, loneliness",
            "remedies": [
                "Feed black dogs roti",
                "Donate til/oil/iron",
                "Respect poor",
                "Avoid bad company"
            ],
            "why": "Repays karmic debts",
            "practical": "Practice patience routines",
            "donations": ["Black sesame"],
            "cautions": ["Avoid alcohol"]
        },
        2: {
            "domain": "Speech",
            "benefic": "Steady growth",
            "malefic": "Poverty, harshness",
            "remedies": [
                "Donate oil/til",
                "Keep iron",
                "Feed crows",
                "Avoid greed"
            ],
            "why": "Releases family blockages",
            "practical": "Practice gentle speech",
            "donations": ["Mustard oil"],
            "cautions": ["Avoid lies"]
        },
        3: {
            "domain": "Courage",
            "benefic": "Patient bravery",
            "malefic": "Wasted efforts",
            "remedies": [
                "Respect siblings",
                "Donate til/urad",
                "Feed monkeys/dogs",
                "Avoid arrogance"
            ],
            "why": "Channels heavy energy",
            "practical": "Maintain focused efforts",
            "donations": ["Black til"],
            "cautions": ["Avoid quarrels"]
        },
        4: {
            "domain": "Property",
            "benefic": "Late gains",
            "malefic": "Unhappy home",
            "remedies": [
                "Donate iron/oil/black clothes",
                "Feed crows/cows",
                "Respect mother",
                "Keep home clean"
            ],
            "why": "Stabilizes restrictions",
            "practical": "Remove clutter",
            "donations": ["Iron utensils"],
            "cautions": ["Avoid mother neglect"]
        },
        5: {
            "domain": "Creativity",
            "benefic": "Responsible learning",
            "malefic": "Delayed education",
            "remedies": [
                "Donate til/oil/blankets",
                "Serve students",
                "Feed crows/dogs",
                "Avoid gambling"
            ],
            "why": "Strengthens delays",
            "practical": "Practice persistent studies",
            "donations": ["Blankets to poor"],
            "cautions": ["Avoid speculation"]
        },
        6: {
            "domain": "Service",
            "benefic": "Disciplined victory",
            "malefic": "Chronic illness",
            "remedies": [
                "Feed ants flour-sugar",
                "Donate oil/urad",
                "Respect workers",
                "Avoid cruelty"
            ],
            "why": "Dissolves debts",
            "practical": "Show servant kindness",
            "donations": ["Urad dal"],
            "cautions": ["Avoid exploitation"]
        },
        7: {
            "domain": "Partnerships",
            "benefic": "Loyal bonds",
            "malefic": "Delayed quarrels",
            "remedies": [
                "Donate to couples",
                "Feed crows/dogs",
                "Gift dark to spouse",
                "Avoid harshness"
            ],
            "why": "Pacifies marriage debts",
            "practical": "Practice honest loyalty",
            "donations": ["Black clothes"],
            "cautions": ["Avoid coldness"]
        },
        8: {
            "domain": "Inheritance",
            "benefic": "Spiritual longevity",
            "malefic": "Sudden illness",
            "remedies": [
                "Donate oil/urad/til",
                "Light oil lamp at Peepal",
                "Respect in-laws",
                "Avoid liquor"
            ],
            "why": "Lights hidden burdens",
            "practical": "Practice secret restraint",
            "donations": ["Mustard oil"],
            "cautions": ["Avoid misconduct"]
        },
        9: {
            "domain": "Fortune",
            "benefic": "Karmic justice",
            "malefic": "Father health",
            "remedies": [
                "Serve father",
                "Donate til/oil/shoes to priests",
                "Feed crows",
                "Avoid disrespect"
            ],
            "why": "Resolves dharma tests",
            "practical": "Practice elder service",
            "donations": ["Shoes"],
            "cautions": ["Avoid hypocrisy"]
        },
        10: {
            "domain": "Status",
            "benefic": "Steady rise",
            "malefic": "Humiliation",
            "remedies": [
                "Keep iron at work",
                "Donate til/oil/shoes",
                "Feed crows",
                "Respect bosses"
            ],
            "why": "Releases career blocks",
            "practical": "Avoid politics",
            "donations": ["Black til"],
            "cautions": ["Avoid laziness"]
        },
        11: {
            "domain": "Networks",
            "benefic": "Hard-earned support",
            "malefic": "Delayed income",
            "remedies": [
                "Donate til/urad/shoes",
                "Gift black to siblings",
                "Feed crows",
                "Avoid selfishness"
            ],
            "why": "Speeds blessings",
            "practical": "Maintain friend loyalty",
            "donations": ["Urad dal"],
            "cautions": ["Avoid false friends"]
        },
        12: {
            "domain": "Isolation",
            "benefic": "Foreign service",
            "malefic": "Imprisonment",
            "remedies": [
                "Donate to jails/ashrams",
                "Feed dogs/crows",
                "Light oil lamp",
                "Avoid addictions"
            ],
            "why": "Converts loss to merit",
            "practical": "Maintain clean habits",
            "donations": ["Black clothes"],
            "cautions": ["Avoid bad company"]
        }
    },
    "Rahu": {
        "planet_info": {
            "day": "Saturday",
            "time": "Daylight",
            "color": "Black/Blue",
            "metal": "Silver",
            "items": ["Black til", "Blankets"],
            "respect": "Elders (avoid cheats/addictions)"
        },
        "remedy_cycle": "43 days",
        1: {
            "domain": "Identity",
            "benefic": "Magnetic rise",
            "malefic": "Confusion, addictions",
            "remedies": [
                "Keep silver ball in pocket",
                "Wear blue clothes",
                "Donate til/oil/blankets",
                "Respect elders"
            ],
            "why": "Calms self-illusion",
            "practical": "Maintain honest identity",
            "donations": ["Black til"],
            "cautions": ["Avoid cheating"]
        },
        2: {
            "domain": "Speech",
            "benefic": "Foreign wealth",
            "malefic": "Lying, unstable finances",
            "remedies": [
                "Keep silver coin in wallet",
                "Donate food/til",
                "Feed dogs bread-milk",
                "Avoid foul speech"
            ],
            "why": "Balances family shadows",
            "practical": "Take care of throat",
            "donations": ["Mustard oil"],
            "cautions": ["Avoid alcohol"]
        },
        3: {
            "domain": "Effort",
            "benefic": "Media boldness",
            "malefic": "Risky ventures",
            "remedies": [
                "Feed birds grains",
                "Wear silver chain",
                "Donate blankets",
                "Avoid boasting"
            ],
            "why": "Airy karma via birds",
            "practical": "Maintain sibling harmony",
            "donations": ["Black sesame"],
            "cautions": ["Avoid false courage"]
        },
        4: {
            "domain": "Property",
            "benefic": "Foreign home",
            "malefic": "Unrest",
            "remedies": [
                "Keep silver vessel with water",
                "Donate blankets/til",
                "Respect mother",
                "Avoid intoxicants"
            ],
            "why": "Calms domestic unrest",
            "practical": "Practice mother respect",
            "donations": ["Black blankets"],
            "cautions": ["Avoid hurting home"]
        },
        5: {
            "domain": "Education",
            "benefic": "Clever politics",
            "malefic": "Gambling addiction",
            "remedies": [
                "Donate to students",
                "Keep silver elephant",
                "Feed dogs/crows",
                "Avoid speculation"
            ],
            "why": "Balances child wisdom",
            "practical": "Maintain focused creativity",
            "donations": ["Mustard oil"],
            "cautions": ["Avoid child health neglect"]
        },
        6: {
            "domain": "Service",
            "benefic": "Strategist",
            "malefic": "Hidden illness",
            "remedies": [
                "Donate urad/til/shoes",
                "Feed dogs/cows",
                "Keep silver coin",
                "Avoid dishonesty"
            ],
            "why": "Dissolves debts",
            "practical": "Practice ethical service",
            "donations": ["Black urad"],
            "cautions": ["Avoid cheating"]
        },
        7: {
            "domain": "Partnerships",
            "benefic": "Diplomatic foreign",
            "malefic": "Fraud, disputes",
            "remedies": [
                "Donate to couples",
                "Gift silver to spouse",
                "Feed dogs",
                "Avoid relationship cheating"
            ],
            "why": "Stabilizes illusions",
            "practical": "Practice faithful diplomacy",
            "donations": ["Black clothes"],
            "cautions": ["Avoid sexual misconduct"]
        },
        8: {
            "domain": "Inheritance",
            "benefic": "Occult foreign",
            "malefic": "Accidents",
            "remedies": [
                "Float coconut/til",
                "Donate blankets/oil",
                "Wear silver chain",
                "Avoid occult misuse"
            ],
            "why": "Dissolves sudden karma",
            "practical": "Practice longevity care",
            "donations": ["Urad dal"],
            "cautions": ["Avoid intoxicants"]
        },
        9: {
            "domain": "Fortune",
            "benefic": "Unconventional luck",
            "malefic": "Fake faith",
            "remedies": [
                "Donate to temples",
                "Serve father",
                "Keep silver Ganesh",
                "Avoid hypocrisy"
            ],
            "why": "Removes illusion blocks",
            "practical": "Practice sincere pilgrimages",
            "donations": ["Black til"],
            "cautions": ["Avoid guru conflicts"]
        },
        10: {
            "domain": "Status",
            "benefic": "Sudden govt rise",
            "malefic": "Scandals",
            "remedies": [
                "Donate to workers",
                "Feed dogs",
                "Keep silver at work",
                "Avoid dishonesty"
            ],
            "why": "Stabilizes career shadows",
            "practical": "Practice ethical prestige",
            "donations": ["Black clothes"],
            "cautions": ["Avoid false prestige"]
        },
        11: {
            "domain": "Networks",
            "benefic": "Influential mass",
            "malefic": "Addiction losses",
            "remedies": [
                "Donate blankets/urad",
                "Feed dogs/birds",
                "Keep silver in wallet",
                "Avoid bad company"
            ],
            "why": "Releases mass karma",
            "practical": "Maintain loyal networks",
            "donations": ["Til"],
            "cautions": ["Avoid intoxication"]
        },
        12: {
            "domain": "Foreign",
            "benefic": "Spiritual moksha",
            "malefic": "Jail, insomnia",
            "remedies": [
                "Donate to jails/ashrams",
                "Feed dogs",
                "Float coconut",
                "Avoid affairs"
            ],
            "why": "Redirects loss to blessings",
            "practical": "Practice meditation",
            "donations": ["Mustard oil"],
            "cautions": ["Avoid secret enemies"]
        }
    },
    "Ketu": {
        "planet_info": {
            "day": "Tuesday/Saturday",
            "time": "Daylight",
            "color": "Grey",
            "metal": "Silver",
            "items": ["Sesame", "Blankets"],
            "respect": "Elders/teachers (embrace detachment)"
        },
        "remedy_cycle": "43 days",
        1: {
            "domain": "Identity",
            "benefic": "Intuitive detachment",
            "malefic": "Aimless confusion",
            "remedies": [
                "Feed stray dogs",
                "Donate blankets/sesame",
                "Keep silver coin",
                "Avoid addictions"
            ],
            "why": "Pacifies shadow influences",
            "practical": "Maintain grounded routines",
            "donations": ["Grey clothes"],
            "cautions": ["Avoid lying"]
        },
        2: {
            "domain": "Speech",
            "benefic": "Detached wealth",
            "malefic": "Abusive quarrels",
            "remedies": [
                "Donate sesame/blankets",
                "Feed dogs bread-milk",
                "Respect women",
                "Keep silver in kitchen"
            ],
            "why": "Calms speech disruptions",
            "practical": "Use gentle family words",
            "donations": ["Grey clothes"],
            "cautions": ["Avoid poverty neglect"]
        },
        3: {
            "domain": "Communication",
            "benefic": "Occult courage",
            "malefic": "Travel accidents",
            "remedies": [
                "Donate blankets/sesame",
                "Feed dogs/birds",
                "Respect siblings",
                "Avoid dishonesty"
            ],
            "why": "Releases blockages",
            "practical": "Practice honest efforts",
            "donations": ["Black blankets"],
            "cautions": ["Avoid sibling quarrels"]
        },
        4: {
            "domain": "Property",
            "benefic": "Spiritual home",
            "malefic": "Disturbed peace",
            "remedies": [
                "Feed dogs",
                "Donate blankets",
                "Respect mother",
                "Keep silver vessel"
            ],
            "why": "Harmonizes vibrations",
            "practical": "Provide mother care",
            "donations": ["Grey/black blankets"],
            "cautions": ["Avoid harshness"]
        },
        5: {
            "domain": "Creativity",
            "benefic": "Intuitive intelligence",
            "malefic": "Education losses",
            "remedies": [
                "Donate to students",
                "Feed dogs chapati-milk",
                "Respect teachers",
                "Keep silver near study"
            ],
            "why": "Dissolves debts",
            "practical": "Practice detached learning",
            "donations": ["Sesame"],
            "cautions": ["Avoid arrogance"]
        },
        6: {
            "domain": "Service",
            "benefic": "Hidden victory",
            "malefic": "Chronic debts",
            "remedies": [
                "Donate urad/sesame/blankets",
                "Feed dogs",
                "Respect poor",
                "Avoid cruelty"
            ],
            "why": "Heals service tests",
            "practical": "Practice humble work",
            "donations": ["Black urad"],
            "cautions": ["Avoid quarrels"]
        },
        7: {
            "domain": "Partnerships",
            "benefic": "Unconventional bonds",
            "malefic": "Detachment disputes",
            "remedies": [
                "Gift silver to spouse",
                "Feed dogs/cows",
                "Donate to couples",
                "Avoid dishonesty"
            ],
            "why": "Pacifies marital karma",
            "practical": "Practice faithful detachment",
            "donations": ["Blankets"],
            "cautions": ["Avoid affairs"]
        },
        8: {
            "domain": "Inheritance",
            "benefic": "Mystical longevity",
            "malefic": "Accidents",
            "remedies": [
                "Float coconut",
                "Donate urad/sesame",
                "Feed dogs",
                "Respect in-laws"
            ],
            "why": "Surrenders hidden load",
            "practical": "Practice ethical secrets",
            "donations": ["Blankets"],
            "cautions": ["Avoid illness neglect"]
        },
        9: {
            "domain": "Fortune",
            "benefic": "Unconventional wisdom",
            "malefic": "Luck loss",
            "remedies": [
                "Donate sesame/shoes to temples",
                "Serve father",
                "Keep silver Ganesh",
                "Avoid disrespect"
            ],
            "why": "Stabilizes fortune",
            "practical": "Practice sincere faith",
            "donations": ["Blankets"],
            "cautions": ["Avoid false religiosity"]
        },
        10: {
            "domain": "Status",
            "benefic": "Spiritual profession",
            "malefic": "Scandals",
            "remedies": [
                "Keep silver at work",
                "Donate urad to workers",
                "Feed dogs",
                "Avoid fraud"
            ],
            "why": "Heals work debts",
            "practical": "Practice detached ethics",
            "donations": ["Sesame"],
            "cautions": ["Avoid dishonest prestige"]
        },
        11: {
            "domain": "Networks",
            "benefic": "Mystical gains",
            "malefic": "Delayed income",
            "remedies": [
                "Donate urad/sesame",
                "Feed dogs/birds",
                "Keep silver in wallet",
                "Avoid bad company"
            ],
            "why": "Converts losses to blessings",
            "practical": "Maintain loyal groups",
            "donations": ["Black urad"],
            "cautions": ["Avoid false friends"]
        },
        12: {
            "domain": "Isolation",
            "benefic": "Moksha focus",
            "malefic": "Depression, jail",
            "remedies": [
                "Donate to ashrams/jails",
                "Feed dogs bread-milk",
                "Keep silver under pillow",
                "Avoid affairs"
            ],
            "why": "Redirects loss to merit",
            "practical": "Embrace meditation",
            "donations": ["Blankets"],
            "cautions": ["Avoid addictions"]
        }
    }
}

# General planet info for 43-day cycles
PLANET_INFO = {
    'Sun': {'day': 'Sunday', 'time': 'Sunrise', 'color': 'Red/Saffron', 'metal': 'Copper', 'items': ['Wheat', 'Jaggery']},
    'Moon': {'day': 'Monday', 'time': 'Morning', 'color': 'White', 'metal': 'Silver', 'items': ['Milk', 'Rice']},
    'Mars': {'day': 'Tuesday', 'time': 'Morning', 'color': 'Red', 'metal': 'Copper', 'items': ['Masoor dal', 'Honey']},
    'Mercury': {'day': 'Wednesday', 'time': 'Morning', 'color': 'Green', 'metal': 'Silver', 'items': ['Moong dal']},
    'Jupiter': {'day': 'Thursday', 'time': 'Morning', 'color': 'Yellow', 'metal': 'Gold', 'items': ['Chana dal', 'Turmeric']},
    'Venus': {'day': 'Friday', 'time': 'Morning', 'color': 'White', 'metal': 'Silver', 'items': ['White sweets', 'Rice', 'Ghee']},
    'Saturn': {'day': 'Saturday', 'time': 'Evening', 'color': 'Black', 'metal': 'Iron', 'items': ['Black til', 'Mustard oil']},
    'Rahu': {'day': 'Saturday', 'time': 'Evening', 'color': 'Blue/Black', 'metal': 'Silver', 'items': ['Black til', 'Blankets']},
    'Ketu': {'day': 'Tuesday/Saturday', 'time': 'Morning/Evening', 'color': 'Grey', 'metal': 'Silver', 'items': ['Sesame', 'Blankets']}
}


def lal_kitab_calculate_julian_day(date_str, time_str, timezone_offset=5.5):
    """Calculate Julian Day for given date, time and timezone"""
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    
    # Convert to UTC
    utc_dt = dt.timestamp() - (timezone_offset * 3600)
    utc_dt = datetime.utcfromtimestamp(utc_dt)
    
    year = utc_dt.year
    month = utc_dt.month
    day = utc_dt.day
    hour = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    
    jd = swe.julday(year, month, day, hour)
    return jd


def lal_kitab_calculate_ayanamsa(jd):
    """Calculate Lahiri Ayanamsa"""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    return ayanamsa


def lal_kitab_get_planet_position(planet_id, jd, ayanamsa):
    """Get sidereal position of planet"""
    if planet_id == -1:  # Ketu
        # Calculate Rahu first
        rahu_pos, _ = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SWIEPH)
        # Ketu is 180 degrees opposite
        ketu_long = (rahu_pos[0] + 180) % 360
        ketu_long_sid = (ketu_long - ayanamsa) % 360
        return ketu_long_sid
    
    pos, _ = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH)
    tropical_long = pos[0]
    sidereal_long = (tropical_long - ayanamsa) % 360
    return sidereal_long


def lal_kitab_calculate_ascendant(jd, lat, lon, ayanamsa):
    """Calculate Ascendant (Lagna) using whole sign system"""
    houses, ascmc = swe.houses(jd, lat, lon, b'P')  # Placidus for ASC calculation
    tropical_asc = ascmc[0]
    sidereal_asc = (tropical_asc - ayanamsa) % 360
    return sidereal_asc


def lal_kitab_get_house_from_degree(degree):
    """Get house number from degree (Whole Sign System)"""
    # In whole sign system, each house is exactly 30 degrees
    house = int(degree / 30) + 1
    return house if house <= 12 else 1


def lal_kitab_calculate_chart(birth_date, birth_time, latitude, longitude, timezone_offset):
    """Calculate complete birth chart with all planets"""
    try:
        jd = lal_kitab_calculate_julian_day(birth_date, birth_time, timezone_offset)
        ayanamsa = lal_kitab_calculate_ayanamsa(jd)
        ascendant_degree = lal_kitab_calculate_ascendant(jd, latitude, longitude, ayanamsa)
        ascendant_sign = lal_kitab_get_house_from_degree(ascendant_degree)
        
        chart_data = {
            'birth_info': {
                'date': birth_date,
                'time': birth_time,
                'latitude': latitude,
                'longitude': longitude,
                'timezone_offset': timezone_offset
            },
            'ayanamsa': round(ayanamsa, 6),
            'ascendant': {
                'degree': round(ascendant_degree, 6),
                'sign': ascendant_sign
            },
            'planets': {}
        }
        
        for planet_name, planet_id in PLANETS.items():
            planet_degree = lal_kitab_get_planet_position(planet_id, jd, ayanamsa)
            
            # Calculate house based on whole sign system from Ascendant
            # Distance from ascendant in whole signs
            sign_position = int(planet_degree / 30) + 1
            asc_sign = ascendant_sign
            
            # Calculate house: distance from ascendant sign
            house = ((sign_position - asc_sign) % 12) + 1
            if house <= 0:
                house += 12
            
            chart_data['planets'][planet_name] = {
                'degree': round(planet_degree, 6),
                'sign': sign_position,
                'house': house
            }
        
        return chart_data
    
    except Exception as e:
        raise Exception(f"Chart calculation error: {str(e)}")


def lal_kitab_get_remedies_for_planet_house(planet, house):
    """Get Lal Kitab remedies for specific planet-house combination"""
    if planet not in LAL_KITAB_REMEDIES:
        raise ValueError(f'Invalid planet: {planet}')
    
    if house < 1 or house > 12:
        raise ValueError('House must be between 1 and 12')
    
    remedies = LAL_KITAB_REMEDIES[planet][house]
    planet_info = PLANET_INFO[planet]
    
    return {
        'planet': planet,
        'house': house,
        'planet_info': planet_info,
        'remedy_cycle': '43 days',
        'best_day': planet_info['day'],
        'best_time': planet_info['time'],
        'details': remedies
    }


def lal_kitab_get_all_chart_remedies(chart_data):
    """Get all Lal Kitab remedies for all planets in the chart"""
    all_remedies = []
    
    for planet_name, planet_data in chart_data['planets'].items():
        house = planet_data['house']
        remedies = LAL_KITAB_REMEDIES[planet_name][house]
        planet_info = PLANET_INFO[planet_name]
        
        all_remedies.append({
            'planet': planet_name,
            'house': house,
            'degree': planet_data['degree'],
            'sign': planet_data['sign'],
            'planet_info': planet_info,
            'remedy_cycle': '43 days',
            'best_day': planet_info['day'],
            'best_time': planet_info['time'],
            'remedies': remedies
        })
    
    return all_remedies


def lal_kitab_get_planet_info():
    """Get general information about all planets"""
    return {
        'planets': PLANET_INFO,
        'general_guidelines': {
            'remedy_duration': '43 days',
            'timing': 'Perform during daylight hours on planet\'s specific day',
            'philosophy': 'Karmic exchanges through donations, behavioral adjustments, and simple rituals',
            'focus': 'Intention over complexity',
            'note': 'Always combine with professional advice for health/legal issues'
        }
    }


def lal_kitab_get_all_remedies_for_planet(planet):
    """Get all 12 house remedies for a specific planet"""
    if planet not in LAL_KITAB_REMEDIES:
        raise ValueError(f'Invalid planet: {planet}')
    
    planet_remedies = LAL_KITAB_REMEDIES[planet]
    planet_info = PLANET_INFO[planet]
    
    return {
        'planet': planet,
        'planet_info': planet_info,
        'remedies_by_house': planet_remedies
    }