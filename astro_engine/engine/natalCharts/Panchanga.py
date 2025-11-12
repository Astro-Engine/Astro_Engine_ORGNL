# """
# PANCHANGA CALCULATION MODULE
# =============================
# All astronomical and Vedic calculations (NO MUHURAT TIMINGS)

# Features:
# - Complete Panchanga (Tithi, Nakshatra, Yoga, Karana, Vara)
# - Sunrise/Sunset/Moonrise/Moonset (Exact with Skyfield)
# - 30 Murthas with Deity and Nature
# - Choghadiya (Day and Night periods)
# - Hora (24 Planetary Hours)
# - Lagna (Ascendant with 12 House Cusps)
# """

# import swisseph as swe
# import datetime
# import pytz
# from typing import Dict, Optional, List, Tuple
# from datetime import timedelta
# import os

# # Try to import Skyfield
# try:
#     from skyfield import api, almanac
#     SKYFIELD_AVAILABLE = True
#     print("✓ Skyfield available - EXACT calculations enabled")
# except ImportError:
#     SKYFIELD_AVAILABLE = False
#     print("⚠️ Skyfield not available - install with: pip install skyfield")

# # Configuration
# SWISS_EPHE_PATH = "astro_api/ephe"
# LAHIRI_AYANAMSA = swe.SIDM_LAHIRI

# # Initialize Skyfield (if available)
# ts_global = None
# eph_global = None

# if SKYFIELD_AVAILABLE:
#     try:
#         ts_global = api.load.timescale()
#         eph_global = api.load('de421.bsp')
#         print("✓ Skyfield ephemeris loaded (JPL DE421)")
#     except Exception as e:
#         print(f"⚠️ Skyfield load error: {e}")
#         SKYFIELD_AVAILABLE = False

# # ============================================================================
# # MURTHA DATABASE - Complete 30 Murthas with Deities and Nature
# # ============================================================================

# MURTHA_DATABASE = {
#     1: {"name": "Rudra", "deity": "Shiva", "nature": "Ashubha", "quality": "Inauspicious"},
#     2: {"name": "Mahendra", "deity": "Indra", "nature": "Shubha", "quality": "Auspicious"},
#     3: {"name": "Dhata", "deity": "Brahma", "nature": "Shubha", "quality": "Auspicious"},
#     4: {"name": "Raudra", "deity": "Rudra", "nature": "Ashubha", "quality": "Inauspicious"},
#     5: {"name": "Kala", "deity": "Yama", "nature": "Ashubha", "quality": "Inauspicious"},
#     6: {"name": "Vaivasvata", "deity": "Yama", "nature": "Ashubha", "quality": "Inauspicious"},
#     7: {"name": "Ghora", "deity": "Yama", "nature": "Ashubha", "quality": "Inauspicious"},
#     8: {"name": "Sarpa", "deity": "Serpents", "nature": "Ashubha", "quality": "Inauspicious"},
#     9: {"name": "Amrita", "deity": "Vishnu", "nature": "Shubha", "quality": "Most Auspicious"},
#     10: {"name": "Maitra", "deity": "Mitra", "nature": "Shubha", "quality": "Auspicious"},
#     11: {"name": "Pitri", "deity": "Ancestors", "nature": "Ashubha", "quality": "Inauspicious"},
#     12: {"name": "Kala", "deity": "Kali", "nature": "Ashubha", "quality": "Inauspicious"},
#     13: {"name": "Sarva", "deity": "Shiva", "nature": "Ashubha", "quality": "Inauspicious"},
#     14: {"name": "Bhaga", "deity": "Bhaga Deva", "nature": "Shubha", "quality": "Auspicious"},
#     15: {"name": "Aryaman", "deity": "Aryaman", "nature": "Shubha", "quality": "Auspicious"},
#     16: {"name": "Girisha", "deity": "Shiva", "nature": "Ashubha", "quality": "Inauspicious"},
#     17: {"name": "Ajapada", "deity": "Ajapada", "nature": "Ashubha", "quality": "Inauspicious"},
#     18: {"name": "Ahirbudhnya", "deity": "Ahirbudhnya", "nature": "Ashubha", "quality": "Inauspicious"},
#     19: {"name": "Pushya", "deity": "Brihaspati", "nature": "Shubha", "quality": "Most Auspicious"},
#     20: {"name": "Ashvini", "deity": "Ashvini Kumaras", "nature": "Shubha", "quality": "Auspicious"},
#     21: {"name": "Yama", "deity": "Yama", "nature": "Ashubha", "quality": "Inauspicious"},
#     22: {"name": "Agni", "deity": "Agni", "nature": "Ashubha", "quality": "Inauspicious"},
#     23: {"name": "Vidhatr", "deity": "Brahma", "nature": "Shubha", "quality": "Auspicious"},
#     24: {"name": "Kanda", "deity": "Kanda", "nature": "Ashubha", "quality": "Inauspicious"},
#     25: {"name": "Aditi", "deity": "Aditi", "nature": "Shubha", "quality": "Auspicious"},
#     26: {"name": "Jiva", "deity": "Brihaspati", "nature": "Shubha", "quality": "Auspicious"},
#     27: {"name": "Vishnu", "deity": "Vishnu", "nature": "Shubha", "quality": "Most Auspicious"},
#     28: {"name": "Dyumani", "deity": "Yama", "nature": "Ashubha", "quality": "Inauspicious"},
#     29: {"name": "Dhatri", "deity": "Brahma", "nature": "Shubha", "quality": "Auspicious"},
#     30: {"name": "Tvastr", "deity": "Tvashta", "nature": "Ashubha", "quality": "Inauspicious"}
# }

# # ============================================================================
# # CHOGHADIYA DATABASE
# # ============================================================================

# CHOGHADIYA_TYPES = {
#     "Amrit": {
#         "nature": "Shubha",
#         "quality": "Most Auspicious",
#         "description": "Nectar - Excellent for all activities",
#         "best_for": "All important activities, ceremonies, weddings, new beginnings",
#         "deity": "Vishnu",
#         "color": "green"
#     },
#     "Shubh": {
#         "nature": "Shubha",
#         "quality": "Auspicious",
#         "description": "Auspicious - Good for most activities",
#         "best_for": "Business deals, meetings, general activities",
#         "deity": "Lakshmi",
#         "color": "green"
#     },
#     "Labh": {
#         "nature": "Shubha",
#         "quality": "Auspicious",
#         "description": "Profit - Excellent for financial matters",
#         "best_for": "Business transactions, shopping, investments, financial decisions",
#         "deity": "Kubera",
#         "color": "green"
#     },
#     "Char": {
#         "nature": "Mishra",
#         "quality": "Neutral/Mixed",
#         "description": "Movable - Good for travel and movement",
#         "best_for": "Travel, transportation, temporary activities",
#         "avoid": "Starting permanent ventures",
#         "deity": "Vayu",
#         "color": "yellow"
#     },
#     "Rog": {
#         "nature": "Ashubha",
#         "quality": "Inauspicious",
#         "description": "Disease - Avoid important activities",
#         "avoid": "All important activities, medical procedures, new beginnings",
#         "deity": "Yama",
#         "color": "red"
#     },
#     "Kaal": {
#         "nature": "Ashubha",
#         "quality": "Most Inauspicious",
#         "description": "Death - Most inauspicious period",
#         "avoid": "Everything except destruction work",
#         "deity": "Kala Bhairava",
#         "color": "red"
#     },
#     "Udveg": {
#         "nature": "Ashubha",
#         "quality": "Inauspicious",
#         "description": "Anxiety - Causes stress and confusion",
#         "avoid": "Important decisions, new ventures, emotional discussions",
#         "deity": "Rahu",
#         "color": "red"
#     }
# }

# DAY_CHOGHADIYA_SEQUENCE = {
#     0: ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg"],
#     1: ["Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit"],
#     2: ["Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"],
#     3: ["Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh"],
#     4: ["Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh"],
#     5: ["Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char"],
#     6: ["Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal"]
# }

# NIGHT_CHOGHADIYA_SEQUENCE = {
#     0: ["Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh"],
#     1: ["Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char"],
#     2: ["Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal"],
#     3: ["Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg"],
#     4: ["Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit"],
#     5: ["Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog"],
#     6: ["Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh"]
# }

# # ============================================================================
# # HORA DATABASE AND CALCULATIONS
# # ============================================================================

# HORA_LORDS = {
#     "Sun": {
#         "sanskrit_name": "Surya",
#         "nature": "Royal, Authoritative, Powerful",
#         "quality": "Neutral",
#         "best_for": "Government work, meeting authorities, leadership activities, applying for jobs, medical treatments, buying gold",
#         "avoid": "Starting quarrels, ego-driven decisions",
#         "color": "orange",
#         "rank": 4
#     },
#     "Moon": {
#         "sanskrit_name": "Chandra",
#         "nature": "Emotional, Nurturing, Peaceful",
#         "quality": "Good",
#         "best_for": "Public dealings, travel (water), buying pearls/silver, meeting mother, household work, agriculture, liquid medicines",
#         "avoid": "Important permanent decisions (Moon is changeable)",
#         "color": "lightblue",
#         "rank": 4
#     },
#     "Mars": {
#         "sanskrit_name": "Mangal",
#         "nature": "Aggressive, Energetic, Courageous",
#         "quality": "Specific Purpose",
#         "best_for": "Sports/competitions, surgery, buying property/land, military/police work, dealing with enemies, physical activities, buying weapons/tools",
#         "avoid": "Peaceful negotiations, marriage proposals",
#         "color": "red",
#         "rank": 5
#     },
#     "Mercury": {
#         "sanskrit_name": "Budh",
#         "nature": "Intellectual, Communicative, Business-minded",
#         "quality": "Excellent",
#         "best_for": "Business transactions, signing contracts, education, writing/publishing, communication, trading/commerce, accounts/banking, short travels",
#         "avoid": "Almost nothing (very versatile)",
#         "color": "green",
#         "rank": 1
#     },
#     "Jupiter": {
#         "sanskrit_name": "Guru/Brihaspati",
#         "nature": "Auspicious, Spiritual, Wisdom",
#         "quality": "Most Excellent",
#         "best_for": "Marriage ceremonies, religious ceremonies, education, meeting teachers/gurus, legal matters, financial investments, charitable activities, children-related matters",
#         "avoid": "Unethical activities",
#         "color": "yellow",
#         "rank": 1
#     },
#     "Venus": {
#         "sanskrit_name": "Shukra",
#         "nature": "Luxury, Beauty, Pleasure, Artistic",
#         "quality": "Excellent",
#         "best_for": "Marriage/romantic activities, buying jewelry/clothes, arts/entertainment, music/dance, luxury purchases, beauty treatments, social gatherings, romantic proposals",
#         "avoid": "Harsh/serious activities",
#         "color": "pink",
#         "rank": 2
#     },
#     "Saturn": {
#         "sanskrit_name": "Shani",
#         "nature": "Serious, Disciplined, Karmic, Slow",
#         "quality": "Generally Inauspicious",
#         "best_for": "Buying property (real estate), construction work, dealing with servants/laborers, chronic disease treatment, mining/oil work, spiritual practices (serious), legal proceedings, resolving old issues",
#         "avoid": "Auspicious ceremonies, new ventures, joyful activities",
#         "color": "darkgray",
#         "rank": 6
#     }
# }

# CHALDEAN_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

# DAY_LORDS = {
#     0: "Sun",       # Sunday (Ravi-var)
#     1: "Moon",      # Monday (Som-var)
#     2: "Mars",      # Tuesday (Mangal-var)
#     3: "Mercury",   # Wednesday (Budh-var)
#     4: "Jupiter",   # Thursday (Guru-var/Brihaspati-var)
#     5: "Venus",     # Friday (Shukra-var)
#     6: "Saturn"     # Saturday (Shani-var)
# }

# # ============================================================================
# # LAGNA (ASCENDANT) DATABASE AND CALCULATIONS
# # ============================================================================

# RASHI_DATABASE = {
#     1: {
#         "name": "Aries",
#         "sanskrit_name": "Mesha",
#         "lord": "Mars",
#         "element": "Fire",
#         "quality": "Movable (Chara)",
#         "nature": "Dynamic, Energetic, Pioneering",
#         "body_parts": "Head, Face, Brain",
#         "characteristics": "Courageous, Impulsive, Leadership, Athletic",
#         "best_for": "Quick actions, leadership roles, sports, military",
#         "avoid_for": "Activities requiring patience and diplomacy"
#     },
#     2: {
#         "name": "Taurus",
#         "sanskrit_name": "Vrishabha",
#         "lord": "Venus",
#         "element": "Earth",
#         "quality": "Fixed (Sthira)",
#         "nature": "Stable, Sensual, Practical",
#         "body_parts": "Neck, Throat, Voice",
#         "characteristics": "Patient, Determined, Pleasure-loving, Beautiful",
#         "best_for": "Marriage, property purchase, financial matters, luxury",
#         "avoid_for": "Quick changes, urgent matters"
#     },
#     3: {
#         "name": "Gemini",
#         "sanskrit_name": "Mithuna",
#         "lord": "Mercury",
#         "element": "Air",
#         "quality": "Dual (Dwiswabhava)",
#         "nature": "Communicative, Versatile, Curious",
#         "body_parts": "Arms, Shoulders, Hands",
#         "characteristics": "Intelligent, Social, Restless, Expressive",
#         "best_for": "Communication, business, writing, learning, trade",
#         "avoid_for": "Serious spiritual practices"
#     },
#     4: {
#         "name": "Cancer",
#         "sanskrit_name": "Karka",
#         "lord": "Moon",
#         "element": "Water",
#         "quality": "Movable (Chara)",
#         "nature": "Emotional, Nurturing, Sensitive",
#         "body_parts": "Chest, Breasts, Stomach",
#         "characteristics": "Caring, Moody, Intuitive, Protective",
#         "best_for": "Family matters, home purchase, nurturing activities",
#         "avoid_for": "Harsh negotiations, litigation"
#     },
#     5: {
#         "name": "Leo",
#         "sanskrit_name": "Simha",
#         "lord": "Sun",
#         "element": "Fire",
#         "quality": "Fixed (Sthira)",
#         "nature": "Royal, Dignified, Authoritative",
#         "body_parts": "Heart, Upper Back, Spine",
#         "characteristics": "Confident, Generous, Dramatic, Leadership",
#         "best_for": "Authority matters, government work, leadership, ceremonies",
#         "avoid_for": "Humble service activities"
#     },
#     6: {
#         "name": "Virgo",
#         "sanskrit_name": "Kanya",
#         "lord": "Mercury",
#         "element": "Earth",
#         "quality": "Dual (Dwiswabhava)",
#         "nature": "Analytical, Perfectionist, Practical",
#         "body_parts": "Intestines, Digestive System",
#         "characteristics": "Intelligent, Critical, Service-oriented, Detail-focused",
#         "best_for": "Analysis, health matters, service, accounting, editing",
#         "avoid_for": "Creative/artistic activities requiring spontaneity"
#     },
#     7: {
#         "name": "Libra",
#         "sanskrit_name": "Tula",
#         "lord": "Venus",
#         "element": "Air",
#         "quality": "Movable (Chara)",
#         "nature": "Balanced, Diplomatic, Artistic",
#         "body_parts": "Kidneys, Lower Back",
#         "characteristics": "Harmonious, Indecisive, Charming, Fair",
#         "best_for": "Marriage, partnerships, legal matters, arts, diplomacy",
#         "avoid_for": "Solo ventures, quick decisions"
#     },
#     8: {
#         "name": "Scorpio",
#         "sanskrit_name": "Vrishchika",
#         "lord": "Mars",
#         "element": "Water",
#         "quality": "Fixed (Sthira)",
#         "nature": "Intense, Mysterious, Transformative",
#         "body_parts": "Reproductive Organs",
#         "characteristics": "Deep, Secretive, Powerful, Investigative",
#         "best_for": "Research, occult, surgery, transformation, investigation",
#         "avoid_for": "Marriage, joyful ceremonies (generally inauspicious)"
#     },
#     9: {
#         "name": "Sagittarius",
#         "sanskrit_name": "Dhanu",
#         "lord": "Jupiter",
#         "element": "Fire",
#         "quality": "Dual (Dwiswabhava)",
#         "nature": "Philosophical, Optimistic, Adventurous",
#         "body_parts": "Thighs, Hips",
#         "characteristics": "Wise, Honest, Freedom-loving, Religious",
#         "best_for": "Education, religious ceremonies, travel, philosophy, teaching",
#         "avoid_for": "Detailed analytical work"
#     },
#     10: {
#         "name": "Capricorn",
#         "sanskrit_name": "Makara",
#         "lord": "Saturn",
#         "element": "Earth",
#         "quality": "Movable (Chara)",
#         "nature": "Ambitious, Disciplined, Practical",
#         "body_parts": "Knees, Bones, Joints",
#         "characteristics": "Serious, Responsible, Patient, Career-focused",
#         "best_for": "Career matters, long-term planning, construction, discipline",
#         "avoid_for": "Entertainment, joyful celebrations"
#     },
#     11: {
#         "name": "Aquarius",
#         "sanskrit_name": "Kumbha",
#         "lord": "Saturn",
#         "element": "Air",
#         "quality": "Fixed (Sthira)",
#         "nature": "Humanitarian, Innovative, Eccentric",
#         "body_parts": "Ankles, Calves",
#         "characteristics": "Independent, Intellectual, Unconventional, Social",
#         "best_for": "Social causes, innovation, technology, group activities",
#         "avoid_for": "Traditional ceremonies"
#     },
#     12: {
#         "name": "Pisces",
#         "sanskrit_name": "Meena",
#         "lord": "Jupiter",
#         "element": "Water",
#         "quality": "Dual (Dwiswabhava)",
#         "nature": "Spiritual, Compassionate, Dreamy",
#         "body_parts": "Feet, Lymphatic System",
#         "characteristics": "Intuitive, Escapist, Artistic, Mystical",
#         "best_for": "Spiritual practices, arts, charity, healing, meditation",
#         "avoid_for": "Business dealings requiring practicality"
#     }
# }

# NAKSHATRAS = [
#     "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
#     "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
#     "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
#     "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
#     "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
#     "Uttara Bhadrapada", "Revati"
# ]

# HOUSE_SIGNIFICATIONS = {
#     1: "Self, Body, Personality, Health, Appearance",
#     2: "Wealth, Family, Speech, Food, Values",
#     3: "Siblings, Courage, Skills, Short Journeys, Communication",
#     4: "Mother, Home, Property, Vehicles, Education, Peace",
#     5: "Children, Intelligence, Creativity, Romance, Speculation",
#     6: "Enemies, Diseases, Debts, Service, Obstacles",
#     7: "Spouse, Partnerships, Marriage, Business Partners",
#     8: "Longevity, Death, Transformation, Occult, Inheritance",
#     9: "Father, Luck, Religion, Higher Education, Long Journeys",
#     10: "Career, Status, Reputation, Authority, Profession",
#     11: "Gains, Income, Friends, Elder Siblings, Aspirations",
#     12: "Losses, Expenses, Foreign Lands, Spirituality, Liberation"
# }

# # ============================================================================
# # HELPER FUNCTIONS
# # ============================================================================

# def get_murtha_details(murtha_number: int) -> Dict:
#     """Get deity, nature, and quality for given Murtha number (1-30)"""
#     return MURTHA_DATABASE.get(murtha_number, {
#         "name": "Unknown", "deity": "Unknown", "nature": "Unknown", "quality": "Unknown"
#     })

# def format_time(dt: datetime.datetime) -> str:
#     """Format datetime to HH:MM:SS string"""
#     return dt.strftime("%H:%M:%S")

# # ============================================================================
# # PANCHANGA CALCULATION
# # ============================================================================

# def calculate_panchanga_elements(date_str, time_str, timezone_str):
#     """Calculate Panchanga elements using Swiss Ephemeris"""
    
#     if not os.path.exists(SWISS_EPHE_PATH):
#         os.makedirs(SWISS_EPHE_PATH, exist_ok=True)
#     swe.set_ephe_path(SWISS_EPHE_PATH)
#     swe.set_sid_mode(LAHIRI_AYANAMSA)
    
#     tz = pytz.timezone(timezone_str)
#     dt_str = f"{date_str} {time_str}"
#     dt_naive = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
#     dt_local = tz.localize(dt_naive)
#     dt_utc = dt_local.astimezone(pytz.UTC)
    
#     jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
#                     dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)
    
#     flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
#     sun_result = swe.calc_ut(jd, swe.SUN, flags)
#     moon_result = swe.calc_ut(jd, swe.MOON, flags)
    
#     sun_lon = sun_result[0][0] % 360.0
#     moon_lon = moon_result[0][0] % 360.0
#     phase_angle = (moon_lon - sun_lon) % 360.0
    
#     tithi_num = int(phase_angle / 12) + 1
#     tithi_progress = (phase_angle % 12) / 12 * 100
#     paksha = "Shukla Paksha" if tithi_num <= 15 else "Krishna Paksha"
    
#     nak_num = int(moon_lon / 13.333333) + 1
#     nak_progress = (moon_lon % 13.333333) / 13.333333
#     pada = int(nak_progress * 4) + 1
    
#     yoga_sum = (sun_lon + moon_lon) % 360.0
#     yoga_num = int(yoga_sum / 13.333333) + 1
    
#     karana_num = int(phase_angle / 6) + 1
#     weekday = dt_local.weekday()
#     vara_num = (weekday + 1) % 7 + 1
    
#     TITHIS = ["Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami",
#               "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
#               "Ekadashi", "Dvadashi", "Trayodashi", "Chaturdashi", "Purnima",
#               "Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami",
#               "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
#               "Ekadashi", "Dvadashi", "Trayodashi", "Chaturdashi", "Amavasya"]
    
#     YOGAS = ["Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma",
#              "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
#              "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva", "Siddha", "Sadhya",
#              "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"]
    
#     KARANAS_MOV = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]
#     KARANAS_FIX = ["Shakuni", "Chatushpada", "Naga", "Kimstughna"]
#     VARAS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
#     half_tithi_idx = int(phase_angle / 6)
#     if half_tithi_idx == 0:
#         karana_name = "Kimstughna"
#         karana_type = "fixed"
#     elif half_tithi_idx >= 57:
#         karana_name = KARANAS_FIX[min(2, half_tithi_idx - 57)]
#         karana_type = "fixed"
#     else:
#         karana_name = KARANAS_MOV[(half_tithi_idx - 1) % 7]
#         karana_type = "movable"
    
#     return {
#         "tithi": {"number": tithi_num, "name": TITHIS[tithi_num - 1], "paksha": paksha, 
#                   "progress_percent": round(tithi_progress, 2)},
#         "nakshatra": {"number": nak_num, "name": NAKSHATRAS[nak_num - 1] if nak_num <= 27 else "Revati",
#                       "pada": pada, "progress_percent": round(nak_progress * 100, 2)},
#         "yoga": {"number": yoga_num, "name": YOGAS[yoga_num - 1] if yoga_num <= 27 else "Vaidhriti",
#                  "progress_percent": round((yoga_sum % 13.333333) / 13.333333 * 100, 2)},
#         "karana": {"number": karana_num, "name": karana_name, "type": karana_type,
#                    "progress_percent": round((phase_angle % 6) / 6 * 100, 2)},
#         "vara": {"number": vara_num, "name": VARAS[vara_num - 1]},
#         "weekday": weekday,
#         "julian_day": jd
#     }

# # ============================================================================
# # SUN AND MOON TIMES
# # ============================================================================

# def calculate_exact_sun_times(date_str, time_str, latitude, longitude, timezone_str):
#     """Calculate EXACT sun rise/set using Skyfield"""
#     if not SKYFIELD_AVAILABLE:
#         return None
    
#     try:
#         tz = pytz.timezone(timezone_str)
#         dt_str = f"{date_str} {time_str}"
#         dt_local = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
#         dt_local = tz.localize(dt_local)
        
#         location = api.wgs84.latlon(latitude, longitude)
#         dt_start = dt_local.replace(hour=0, minute=0, second=0)
#         dt_end = dt_start + timedelta(days=1)
        
#         t0 = ts_global.from_datetime(dt_start)
#         t1 = ts_global.from_datetime(dt_end)
        
#         sun = eph_global['sun']
#         f = almanac.risings_and_settings(eph_global, sun, location)
#         times, events = almanac.find_discrete(t0, t1, f)
        
#         sunrise = None
#         sunset = None
#         sunrise_dt = None
#         sunset_dt = None
        
#         for time, event in zip(times, events):
#             time_utc = time.utc_datetime()
#             time_local = time_utc.replace(tzinfo=pytz.UTC).astimezone(tz)
            
#             if event == 1:
#                 sunrise = format_time(time_local)
#                 sunrise_dt = time_local
#             elif event == 0:
#                 sunset = format_time(time_local)
#                 sunset_dt = time_local
        
#         if sunrise and sunset:
#             return {
#                 "sunrise": sunrise, "sunset": sunset,
#                 "sunrise_dt": sunrise_dt, "sunset_dt": sunset_dt,
#                 "method": "skyfield_exact"
#             }
#         return None
#     except Exception as e:
#         print(f"Sun calculation error: {e}")
#         return None

# def calculate_exact_moon_times(date_str, time_str, latitude, longitude, timezone_str):
#     """Calculate EXACT moon rise/set using Skyfield"""
#     if not SKYFIELD_AVAILABLE:
#         return None
    
#     try:
#         tz = pytz.timezone(timezone_str)
#         dt_str = f"{date_str} {time_str}"
#         dt_local = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
#         dt_local = tz.localize(dt_local)
        
#         location = api.wgs84.latlon(latitude, longitude)
#         dt_start = dt_local.replace(hour=0, minute=0, second=0)
#         dt_end = dt_start + timedelta(days=2)
        
#         t0 = ts_global.from_datetime(dt_start)
#         t1 = ts_global.from_datetime(dt_end)
        
#         moon = eph_global['moon']
#         f = almanac.risings_and_settings(eph_global, moon, location)
#         times, events = almanac.find_discrete(t0, t1, f)
        
#         moonrise = None
#         moonset = None
#         target_date = dt_local.date()
        
#         for time, event in zip(times, events):
#             time_utc = time.utc_datetime()
#             time_local = time_utc.replace(tzinfo=pytz.UTC).astimezone(tz)
            
#             if time_local.date() == target_date:
#                 if event == 1 and moonrise is None:
#                     moonrise = time_local
#                 elif event == 0 and moonset is None:
#                     moonset = time_local
#             elif time_local.date() == target_date + timedelta(days=1) and time_local.hour < 12:
#                 if event == 0 and moonset is None:
#                     moonset = time_local
        
#         if moonrise and moonset:
#             return {"moonrise": format_time(moonrise), "moonset": format_time(moonset), "method": "skyfield_exact"}
#         return None
#     except Exception as e:
#         print(f"Moon calculation error: {e}")
#         return None

# # ============================================================================
# # MURTHA CALCULATION
# # ============================================================================

# def calculate_exact_murtha_corrected(date_str: str, time_str: str, latitude: float, 
#                                     longitude: float, timezone_str: str,
#                                     sunset_dt: Optional[datetime.datetime] = None) -> Optional[Dict]:
#     """Calculate current Murtha with CORRECTED day length display"""
    
#     if not SKYFIELD_AVAILABLE:
#         return None
    
#     try:
#         tz = pytz.timezone(timezone_str)
#         dt_str = f"{date_str} {time_str}"
#         dt_local = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
#         dt_local = tz.localize(dt_local)
        
#         location = api.wgs84.latlon(latitude, longitude)
#         dt_start = (dt_local - timedelta(days=1)).replace(hour=0, minute=0, second=0)
#         dt_end = (dt_local + timedelta(days=1)).replace(hour=23, minute=59, second=59)
        
#         t0 = ts_global.from_datetime(dt_start)
#         t1 = ts_global.from_datetime(dt_end)
        
#         sun = eph_global['sun']
#         f = almanac.risings_and_settings(eph_global, sun, location)
#         times, events = almanac.find_discrete(t0, t1, f)
        
#         sunrise_times = []
#         for time, event in zip(times, events):
#             if event == 1:
#                 time_utc = time.utc_datetime()
#                 time_local = time_utc.replace(tzinfo=pytz.UTC).astimezone(tz)
#                 sunrise_times.append(time_local)
        
#         if len(sunrise_times) < 2:
#             return None
        
#         sunrise_times.sort()
#         current_sunrise = None
#         next_sunrise = None
        
#         for i in range(len(sunrise_times) - 1):
#             if sunrise_times[i] <= dt_local < sunrise_times[i + 1]:
#                 current_sunrise = sunrise_times[i]
#                 next_sunrise = sunrise_times[i + 1]
#                 break
        
#         if not current_sunrise and dt_local < sunrise_times[0]:
#             current_sunrise, next_sunrise = sunrise_times[0], sunrise_times[1]
#         if not current_sunrise and dt_local >= sunrise_times[-1]:
#             current_sunrise, next_sunrise = sunrise_times[-2], sunrise_times[-1]
        
#         if not current_sunrise or not next_sunrise:
#             return None
        
#         murtha_cycle_seconds = (next_sunrise - current_sunrise).total_seconds()
#         murtha_cycle_hours = murtha_cycle_seconds / 3600.0
        
#         daylight_hours = None
#         if sunset_dt:
#             daylight_seconds = (sunset_dt - current_sunrise).total_seconds()
#             daylight_hours = daylight_seconds / 3600.0
        
#         murtha_duration_seconds = murtha_cycle_seconds / 30.0
#         elapsed_seconds = (dt_local - current_sunrise).total_seconds()
        
#         if elapsed_seconds < 0:
#             murtha_number = 30
#         else:
#             murtha_number = min(int(elapsed_seconds / murtha_duration_seconds) + 1, 30)
        
#         murtha_data = get_murtha_details(murtha_number)
#         murtha_start = current_sunrise + timedelta(seconds=(murtha_number - 1) * murtha_duration_seconds)
#         murtha_end = current_sunrise + timedelta(seconds=murtha_number * murtha_duration_seconds)
        
#         remaining_seconds = (murtha_end - dt_local).total_seconds()
#         elapsed_in_murtha = (dt_local - murtha_start).total_seconds()
        
#         return {
#             "murtha_number": murtha_number, "murtha_name": murtha_data["name"],
#             "deity": murtha_data["deity"], "nature": murtha_data["nature"],
#             "quality": murtha_data["quality"],
#             "start_time": format_time(murtha_start), "end_time": format_time(murtha_end),
#             "duration_minutes": round(murtha_duration_seconds / 60.0, 2),
#             "elapsed_minutes": round(elapsed_in_murtha / 60.0, 2),
#             "remaining_minutes": round(remaining_seconds / 60.0, 2),
#             "progress_percent": round((elapsed_in_murtha / murtha_duration_seconds) * 100, 2),
#             "day_info": {
#                 "sunrise": format_time(current_sunrise),
#                 "next_sunrise": format_time(next_sunrise),
#                 "murtha_cycle_hours": round(murtha_cycle_hours, 2),
#                 "daylight_hours": round(daylight_hours, 2) if daylight_hours else None,
#                 "explanation": "Murtha uses sunrise-to-sunrise cycle; daylight shows actual sun hours"
#             },
#             "method": "skyfield_exact"
#         }
#     except Exception as e:
#         print(f"Murtha calculation error: {e}")
#         return None

# # ============================================================================
# # CHOGHADIYA CALCULATIONS
# # ============================================================================

# def calculate_choghadiya(sunrise_dt: datetime.datetime, sunset_dt: datetime.datetime,
#                         next_sunrise_dt: datetime.datetime, weekday: int) -> Dict:
#     """Calculate Day and Night Choghadiya periods"""
    
#     print(f"\n🌙 Choghadiya Calculation for weekday {weekday}")
    
#     day_duration_seconds = (sunset_dt - sunrise_dt).total_seconds()
#     night_duration_seconds = (next_sunrise_dt - sunset_dt).total_seconds()
#     day_chog_duration = day_duration_seconds / 8.0
#     night_chog_duration = night_duration_seconds / 8.0
    
#     day_sequence = DAY_CHOGHADIYA_SEQUENCE[weekday]
#     night_sequence = NIGHT_CHOGHADIYA_SEQUENCE[weekday]
    
#     day_choghadiyas = []
#     for i, chog_type in enumerate(day_sequence):
#         chog_start = sunrise_dt + timedelta(seconds=i * day_chog_duration)
#         chog_end = sunrise_dt + timedelta(seconds=(i + 1) * day_chog_duration)
#         chog_details = CHOGHADIYA_TYPES[chog_type]
        
#         day_choghadiyas.append({
#             "number": i + 1, "type": chog_type,
#             "start": format_time(chog_start), "end": format_time(chog_end),
#             "duration_minutes": round(day_chog_duration / 60, 2),
#             "nature": chog_details["nature"], "quality": chog_details["quality"],
#             "description": chog_details["description"],
#             "best_for": chog_details.get("best_for", ""),
#             "avoid": chog_details.get("avoid", ""),
#             "deity": chog_details["deity"], "color": chog_details["color"]
#         })
    
#     night_choghadiyas = []
#     for i, chog_type in enumerate(night_sequence):
#         chog_start = sunset_dt + timedelta(seconds=i * night_chog_duration)
#         chog_end = sunset_dt + timedelta(seconds=(i + 1) * night_chog_duration)
#         chog_details = CHOGHADIYA_TYPES[chog_type]
        
#         night_choghadiyas.append({
#             "number": i + 1, "type": chog_type,
#             "start": format_time(chog_start), "end": format_time(chog_end),
#             "duration_minutes": round(night_chog_duration / 60, 2),
#             "nature": chog_details["nature"], "quality": chog_details["quality"],
#             "description": chog_details["description"],
#             "best_for": chog_details.get("best_for", ""),
#             "avoid": chog_details.get("avoid", ""),
#             "deity": chog_details["deity"], "color": chog_details["color"]
#         })
    
#     return {
#         "day_choghadiya": day_choghadiyas,
#         "night_choghadiya": night_choghadiyas,
#         "summary": {
#             "day_duration_hours": round(day_duration_seconds / 3600, 2),
#             "night_duration_hours": round(night_duration_seconds / 3600, 2),
#             "day_choghadiya_minutes": round(day_chog_duration / 60, 2),
#             "night_choghadiya_minutes": round(night_chog_duration / 60, 2),
#             "calculation_method": "classical_gujarati_panchanga"
#         }
#     }

# def get_current_choghadiya(current_dt: datetime.datetime, sunrise_dt: datetime.datetime,
#                            sunset_dt: datetime.datetime, next_sunrise_dt: datetime.datetime,
#                            weekday: int) -> Dict:
#     """Get the CURRENT active Choghadiya"""
    
#     if sunrise_dt <= current_dt < sunset_dt:
#         is_day = True
#         period_start = sunrise_dt
#         period_end = sunset_dt
#         duration = (sunset_dt - sunrise_dt).total_seconds()
#         sequence = DAY_CHOGHADIYA_SEQUENCE[weekday]
#     else:
#         is_day = False
#         period_start = sunset_dt
#         period_end = next_sunrise_dt
#         duration = (next_sunrise_dt - sunset_dt).total_seconds()
#         sequence = NIGHT_CHOGHADIYA_SEQUENCE[weekday]
    
#     chog_duration = duration / 8.0
#     elapsed_seconds = (current_dt - period_start).total_seconds()
    
#     if elapsed_seconds < 0:
#         current_chog_num = 0
#     else:
#         current_chog_num = min(int(elapsed_seconds / chog_duration), 7)
    
#     chog_type = sequence[current_chog_num]
#     chog_details = CHOGHADIYA_TYPES[chog_type]
#     chog_start = period_start + timedelta(seconds=current_chog_num * chog_duration)
#     chog_end = period_start + timedelta(seconds=(current_chog_num + 1) * chog_duration)
    
#     remaining_seconds = (chog_end - current_dt).total_seconds()
#     elapsed_in_chog = (current_dt - chog_start).total_seconds()
#     progress_percent = (elapsed_in_chog / chog_duration) * 100
    
#     return {
#         "current_choghadiya": {
#             "period": "Day" if is_day else "Night",
#             "number": current_chog_num + 1, "type": chog_type,
#             "start": format_time(chog_start), "end": format_time(chog_end),
#             "duration_minutes": round(chog_duration / 60, 2),
#             "elapsed_minutes": round(elapsed_in_chog / 60, 2),
#             "remaining_minutes": round(remaining_seconds / 60, 2),
#             "progress_percent": round(progress_percent, 2),
#             "nature": chog_details["nature"], "quality": chog_details["quality"],
#             "description": chog_details["description"],
#             "best_for": chog_details.get("best_for", ""),
#             "avoid": chog_details.get("avoid", ""),
#             "deity": chog_details["deity"], "color": chog_details["color"]
#         }
#     }

# # ============================================================================
# # HORA CALCULATIONS
# # ============================================================================

# def calculate_hora(sunrise_dt: datetime.datetime, 
#                   sunset_dt: datetime.datetime,
#                   next_sunrise_dt: datetime.datetime,
#                   weekday: int) -> Dict:
#     """Calculate all 24 Hora periods for the day and night"""
    
#     print(f"\n⏰ Hora Calculation:")
#     print(f"   Weekday: {weekday} (0=Sun, 1=Mon, ..., 6=Sat)")
#     print(f"   Day Lord: {DAY_LORDS[weekday]}")
    
#     day_duration_seconds = (sunset_dt - sunrise_dt).total_seconds()
#     night_duration_seconds = (next_sunrise_dt - sunset_dt).total_seconds()
    
#     day_hora_duration = day_duration_seconds / 12.0
#     night_hora_duration = night_duration_seconds / 12.0
    
#     print(f"   Day Hora: {day_hora_duration / 60:.2f} minutes each")
#     print(f"   Night Hora: {night_hora_duration / 60:.2f} minutes each")
    
#     day_lord = DAY_LORDS[weekday]
#     start_index = CHALDEAN_ORDER.index(day_lord)
    
#     day_horas = []
#     for i in range(12):
#         hora_start = sunrise_dt + timedelta(seconds=i * day_hora_duration)
#         hora_end = sunrise_dt + timedelta(seconds=(i + 1) * day_hora_duration)
        
#         planet_index = (start_index + i) % 7
#         hora_lord = CHALDEAN_ORDER[planet_index]
#         hora_details = HORA_LORDS[hora_lord]
        
#         day_horas.append({
#             "hora_number": i + 1,
#             "absolute_hora": i + 1,
#             "hora_lord": hora_lord,
#             "sanskrit_name": hora_details["sanskrit_name"],
#             "start": format_time(hora_start),
#             "end": format_time(hora_end),
#             "duration_minutes": round(day_hora_duration / 60, 2),
#             "nature": hora_details["nature"],
#             "quality": hora_details["quality"],
#             "best_for": hora_details["best_for"],
#             "avoid": hora_details["avoid"],
#             "color": hora_details["color"],
#             "rank": hora_details["rank"],
#             "period": "Day"
#         })
    
#     night_start_index = (start_index + 12) % 7
#     night_horas = []
    
#     for i in range(12):
#         hora_start = sunset_dt + timedelta(seconds=i * night_hora_duration)
#         hora_end = sunset_dt + timedelta(seconds=(i + 1) * night_hora_duration)
        
#         planet_index = (night_start_index + i) % 7
#         hora_lord = CHALDEAN_ORDER[planet_index]
#         hora_details = HORA_LORDS[hora_lord]
        
#         night_horas.append({
#             "hora_number": i + 1,
#             "absolute_hora": i + 13,
#             "hora_lord": hora_lord,
#             "sanskrit_name": hora_details["sanskrit_name"],
#             "start": format_time(hora_start),
#             "end": format_time(hora_end),
#             "duration_minutes": round(night_hora_duration / 60, 2),
#             "nature": hora_details["nature"],
#             "quality": hora_details["quality"],
#             "best_for": hora_details["best_for"],
#             "avoid": hora_details["avoid"],
#             "color": hora_details["color"],
#             "rank": hora_details["rank"],
#             "period": "Night"
#         })
    
#     print(f"   ✓ Calculated 24 Horas (12 day + 12 night)")
    
#     return {
#         "day_hora": day_horas,
#         "night_hora": night_horas,
#         "summary": {
#             "day_lord": day_lord,
#             "day_duration_hours": round(day_duration_seconds / 3600, 2),
#             "night_duration_hours": round(night_duration_seconds / 3600, 2),
#             "day_hora_minutes": round(day_hora_duration / 60, 2),
#             "night_hora_minutes": round(night_hora_duration / 60, 2),
#             "chaldean_order": CHALDEAN_ORDER,
#             "calculation_method": "classical_vedic_hora"
#         }
#     }

# def get_current_hora(current_dt: datetime.datetime,
#                     sunrise_dt: datetime.datetime,
#                     sunset_dt: datetime.datetime,
#                     next_sunrise_dt: datetime.datetime,
#                     weekday: int) -> Dict:
#     """Get the CURRENT active Hora for a given time"""
    
#     if sunrise_dt <= current_dt < sunset_dt:
#         is_day = True
#         period_start = sunrise_dt
#         period_end = sunset_dt
#         duration = (sunset_dt - sunrise_dt).total_seconds()
#         base_hora = 0
#     else:
#         is_day = False
#         period_start = sunset_dt
#         period_end = next_sunrise_dt
#         duration = (next_sunrise_dt - sunset_dt).total_seconds()
#         base_hora = 12
    
#     hora_duration = duration / 12.0
#     elapsed_seconds = (current_dt - period_start).total_seconds()
    
#     if elapsed_seconds < 0:
#         hora_number_in_period = 0
#     else:
#         hora_number_in_period = min(int(elapsed_seconds / hora_duration), 11)
    
#     absolute_hora = base_hora + hora_number_in_period + 1
    
#     day_lord = DAY_LORDS[weekday]
#     start_index = CHALDEAN_ORDER.index(day_lord)
    
#     planet_index = (start_index + (absolute_hora - 1)) % 7
#     hora_lord = CHALDEAN_ORDER[planet_index]
#     hora_details = HORA_LORDS[hora_lord]
    
#     hora_start = period_start + timedelta(seconds=hora_number_in_period * hora_duration)
#     hora_end = period_start + timedelta(seconds=(hora_number_in_period + 1) * hora_duration)
    
#     remaining_seconds = (hora_end - current_dt).total_seconds()
#     elapsed_in_hora = (current_dt - hora_start).total_seconds()
#     progress_percent = (elapsed_in_hora / hora_duration) * 100
    
#     if hora_details["rank"] <= 2:
#         recommendation = "Excellent time for " + hora_details["best_for"].split(',')[0]
#     elif hora_details["rank"] <= 4:
#         recommendation = "Good for specific activities - check suitability"
#     else:
#         recommendation = "Generally avoid important activities - " + hora_details["avoid"].split(',')[0]
    
#     return {
#         "current_hora": {
#             "hora_number": hora_number_in_period + 1,
#             "absolute_hora": absolute_hora,
#             "period": "Day" if is_day else "Night",
#             "hora_lord": hora_lord,
#             "sanskrit_name": hora_details["sanskrit_name"],
#             "start": format_time(hora_start),
#             "end": format_time(hora_end),
#             "duration_minutes": round(hora_duration / 60, 2),
#             "elapsed_minutes": round(elapsed_in_hora / 60, 2),
#             "remaining_minutes": round(remaining_seconds / 60, 2),
#             "progress_percent": round(progress_percent, 2),
#             "nature": hora_details["nature"],
#             "quality": hora_details["quality"],
#             "best_for": hora_details["best_for"],
#             "avoid": hora_details["avoid"],
#             "color": hora_details["color"],
#             "rank": hora_details["rank"],
#             "recommendation": recommendation
#         }
#     }

# # ============================================================================
# # LAGNA (ASCENDANT) CALCULATIONS
# # ============================================================================

# def calculate_lagna(date_str: str, time_str: str, latitude: float, 
#                    longitude: float, timezone_str: str) -> Dict:
#     """Calculate Lagna (Ascendant) and all 12 house cusps"""
    
#     if not os.path.exists(SWISS_EPHE_PATH):
#         os.makedirs(SWISS_EPHE_PATH, exist_ok=True)
    
#     swe.set_ephe_path(SWISS_EPHE_PATH)
#     swe.set_sid_mode(LAHIRI_AYANAMSA)
    
#     print(f"\n🎯 Lagna Calculation:")
#     print(f"   Date: {date_str}, Time: {time_str}")
#     print(f"   Location: {latitude}°N, {longitude}°E")
    
#     tz = pytz.timezone(timezone_str)
#     dt_str = f"{date_str} {time_str}"
#     dt_local = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
#     dt_local = tz.localize(dt_local)
#     dt_utc = dt_local.astimezone(pytz.UTC)
    
#     print(f"   UTC: {dt_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    
#     jd = swe.julday(
#         dt_utc.year, dt_utc.month, dt_utc.day,
#         dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
#     )
    
#     print(f"   Julian Day: {jd:.6f}")
    
#     try:
#         cusps, ascmc = swe.houses(jd, latitude, longitude, b'P')
        
#         print(f"   ✓ House calculation successful")
#         print(f"   Cusps: {len(cusps)} elements, ASCMC: {len(ascmc)} elements")
        
#         if len(cusps) < 13:
#             print(f"   ⚠️ Warning: Expected 13 cusps, got {len(cusps)}")
#             cusps = list(cusps)
        
#         if len(ascmc) < 2:
#             raise ValueError(f"ASCMC has insufficient elements: {len(ascmc)}")
            
#     except Exception as e:
#         print(f"   ⚠️ Placidus calculation issue: {e}")
#         print(f"   Trying Whole Sign houses as fallback...")
        
#         try:
#             cusps, ascmc = swe.houses(jd, latitude, longitude, b'W')
#             print(f"   ✓ Whole Sign calculation successful")
#         except Exception as e2:
#             print(f"   ❌ Whole Sign also failed: {e2}")
#             raise ValueError(f"All house calculation methods failed. Original error: {e}, Fallback error: {e2}")
    
#     try:
#         tropical_asc = ascmc[0]
#     except (IndexError, TypeError) as e:
#         raise ValueError(f"Cannot access Ascendant from ASCMC: {e}. ASCMC content: {ascmc}")
    
#     ayanamsa = swe.get_ayanamsa_ut(jd)
    
#     print(f"   Tropical Ascendant: {tropical_asc:.6f}°")
#     print(f"   Ayanamsa (Lahiri): {ayanamsa:.6f}°")
    
#     sidereal_asc = (tropical_asc - ayanamsa) % 360
    
#     print(f"   Sidereal Ascendant: {sidereal_asc:.6f}°")
    
#     rashi_num = int(sidereal_asc / 30) + 1
#     degree_in_rashi = sidereal_asc % 30
    
#     rashi_details = RASHI_DATABASE[rashi_num]
    
#     print(f"   Lagna Rashi: {rashi_details['name']} ({rashi_details['sanskrit_name']})")
#     print(f"   Degree in Rashi: {degree_in_rashi:.4f}°")
    
#     degrees = int(degree_in_rashi)
#     minutes = int((degree_in_rashi - degrees) * 60)
#     seconds = int(((degree_in_rashi - degrees) * 60 - minutes) * 60)
    
#     nak_num = int(sidereal_asc / 13.333333) + 1
#     if nak_num > 27:
#         nak_num = 27
    
#     nak_pada = int((sidereal_asc % 13.333333) / 3.333333) + 1
    
#     lagna_nakshatra = NAKSHATRAS[nak_num - 1]
    
#     print(f"   Lagna Nakshatra: {lagna_nakshatra} Pada {nak_pada}")
    
#     house_cusps_sidereal = {}
    
#     print(f"   Calculating {len(cusps)-1} house cusps...")
    
#     for i in range(1, 13):
#         try:
#             if i < len(cusps):
#                 tropical_cusp = cusps[i]
#             else:
#                 print(f"   ⚠️ Cusp {i} not available, using Equal House method")
#                 tropical_cusp = (tropical_asc + (i-1) * 30) % 360
            
#             sidereal_cusp = (tropical_cusp - ayanamsa) % 360
#             cusp_rashi = int(sidereal_cusp / 30) + 1
#             cusp_degree = sidereal_cusp % 30
            
#             house_cusps_sidereal[f"house_{i}"] = {
#                 "cusp_degree": round(sidereal_cusp, 4),
#                 "rashi_number": cusp_rashi,
#                 "rashi_name": RASHI_DATABASE[cusp_rashi]["name"],
#                 "degree_in_rashi": round(cusp_degree, 4),
#                 "signification": HOUSE_SIGNIFICATIONS[i]
#             }
            
#             if i <= 3:
#                 print(f"   House {i}: {RASHI_DATABASE[cusp_rashi]['name']} {cusp_degree:.2f}°")
                
#         except (IndexError, KeyError, TypeError) as e:
#             print(f"   ⚠️ Error accessing cusp {i}: {e}")
#             tropical_cusp = (tropical_asc + (i-1) * 30) % 360
#             sidereal_cusp = (tropical_cusp - ayanamsa) % 360
#             cusp_rashi = int(sidereal_cusp / 30) + 1
#             cusp_degree = sidereal_cusp % 30
            
#             house_cusps_sidereal[f"house_{i}"] = {
#                 "cusp_degree": round(sidereal_cusp, 4),
#                 "rashi_number": cusp_rashi,
#                 "rashi_name": RASHI_DATABASE[cusp_rashi]["name"],
#                 "degree_in_rashi": round(cusp_degree, 4),
#                 "signification": HOUSE_SIGNIFICATIONS[i],
#                 "note": "Calculated using Equal House fallback"
#             }
    
#     try:
#         mc_tropical = ascmc[1] if len(ascmc) > 1 else (tropical_asc + 270) % 360
#     except:
#         mc_tropical = (tropical_asc + 270) % 360
        
#     mc_sidereal = (mc_tropical - ayanamsa) % 360
#     mc_rashi = int(mc_sidereal / 30) + 1
    
#     descendant_sidereal = (sidereal_asc + 180) % 360
#     desc_rashi = int(descendant_sidereal / 30) + 1
    
#     ic_sidereal = (mc_sidereal + 180) % 360
#     ic_rashi = int(ic_sidereal / 30) + 1
    
#     print(f"   ✓ Lagna calculation complete")
    
#     return {
#         "lagna": {
#             "rashi_number": rashi_num,
#             "rashi_name": rashi_details["name"],
#             "sanskrit_name": rashi_details["sanskrit_name"],
#             "lord": rashi_details["lord"],
#             "element": rashi_details["element"],
#             "quality": rashi_details["quality"],
#             "absolute_degree": round(sidereal_asc, 6),
#             "degree_in_rashi": round(degree_in_rashi, 6),
#             "dms": f"{degrees}° {minutes}' {seconds}\"",
#             "nakshatra": lagna_nakshatra,
#             "nakshatra_number": nak_num,
#             "nakshatra_pada": nak_pada,
#             "nature": rashi_details["nature"],
#             "body_parts": rashi_details["body_parts"],
#             "characteristics": rashi_details["characteristics"],
#             "best_for": rashi_details["best_for"],
#             "avoid_for": rashi_details["avoid_for"]
#         },
#         "house_cusps": house_cusps_sidereal,
#         "special_points": {
#             "ascendant": {
#                 "degree": round(sidereal_asc, 4),
#                 "rashi": rashi_details["name"],
#                 "description": "1st House - Self, Personality, Physical Body"
#             },
#             "midheaven": {
#                 "degree": round(mc_sidereal, 4),
#                 "rashi": RASHI_DATABASE[mc_rashi]["name"],
#                 "description": "10th House - Career, Status, Public Life"
#             },
#             "descendant": {
#                 "degree": round(descendant_sidereal, 4),
#                 "rashi": RASHI_DATABASE[desc_rashi]["name"],
#                 "description": "7th House - Spouse, Partnerships, Marriage"
#             },
#             "imum_coeli": {
#                 "degree": round(ic_sidereal, 4),
#                 "rashi": RASHI_DATABASE[ic_rashi]["name"],
#                 "description": "4th House - Home, Mother, Inner Peace"
#             }
#         },
#         "technical_data": {
#             "tropical_ascendant": round(tropical_asc, 6),
#             "ayanamsa_lahiri": round(ayanamsa, 6),
#             "julian_day": round(jd, 6),
#             "house_system": "Placidus",
#             "ayanamsa_system": "Lahiri",
#             "calculation_method": "swiss_ephemeris_sidereal"
#         }
#     }

# def calculate_sunrise_sunset(date_str: str, latitude: float, longitude: float, 
#                             timezone_str: str) -> Dict:
#     """Calculate exact sunrise and sunset times using Skyfield"""
    
#     if not SKYFIELD_AVAILABLE:
#         print("   ⚠️  Skyfield not available, using approximate sunrise")
#         tz = pytz.timezone(timezone_str)
#         date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
#         date_obj = tz.localize(date_obj)
        
#         sunrise_approx = date_obj.replace(hour=6, minute=40, second=0)
#         sunset_approx = date_obj.replace(hour=18, minute=0, second=0)
        
#         return {
#             "sunrise": sunrise_approx,
#             "sunset": sunset_approx,
#             "method": "approximate"
#         }
    
#     from skyfield import api as sky_api
#     from skyfield import almanac
    
#     ts = sky_api.load.timescale()
#     eph = sky_api.load('de421.bsp')
    
#     location = sky_api.wgs84.latlon(latitude, longitude)
    
#     tz = pytz.timezone(timezone_str)
#     date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
#     date_obj = tz.localize(date_obj)
    
#     t0 = ts.from_datetime(date_obj.replace(hour=0, minute=0, second=0))
#     t1 = ts.from_datetime(date_obj.replace(hour=23, minute=59, second=59))
    
#     f = almanac.sunrise_sunset(eph, location)
#     times, events = almanac.find_discrete(t0, t1, f)
    
#     sunrise_time = None
#     sunset_time = None
    
#     for time, event in zip(times, events):
#         dt = time.utc_datetime().replace(tzinfo=pytz.UTC).astimezone(tz)
#         if event == 1:
#             sunrise_time = dt
#         elif event == 0:
#             sunset_time = dt
    
#     return {
#         "sunrise": sunrise_time,
#         "sunset": sunset_time,
#         "method": "skyfield_accurate"
#     }

# def calculate_lagna_timings_vedic(date_str: str, latitude: float, longitude: float, 
#                                   timezone_str: str) -> Dict:
#     """Calculate EXACT Lagna timings from SUNRISE to SUNRISE (Vedic day)"""
    
#     if not os.path.exists(SWISS_EPHE_PATH):
#         os.makedirs(SWISS_EPHE_PATH, exist_ok=True)
    
#     swe.set_ephe_path(SWISS_EPHE_PATH)
#     swe.set_sid_mode(LAHIRI_AYANAMSA)
    
#     print(f"\n🌅 Calculating Lagna Timings (Vedic Day: Sunrise to Sunrise):")
#     print(f"   Date: {date_str}")
#     print(f"   Location: {latitude}°N, {longitude}°E")
#     print(f"   Timezone: {timezone_str}")
    
#     tz = pytz.timezone(timezone_str)
    
#     print(f"   Calculating sunrise times...")
    
#     today_sun = calculate_sunrise_sunset(date_str, latitude, longitude, timezone_str)
#     sunrise_today = today_sun["sunrise"]
    
#     date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
#     next_date = date_obj + timedelta(days=1)
#     next_date_str = next_date.strftime('%Y-%m-%d')
    
#     tomorrow_sun = calculate_sunrise_sunset(next_date_str, latitude, longitude, timezone_str)
#     sunrise_tomorrow = tomorrow_sun["sunrise"]
    
#     print(f"   Sunrise today: {sunrise_today.strftime('%Y-%m-%d %H:%M:%S')}")
#     print(f"   Sunrise tomorrow: {sunrise_tomorrow.strftime('%Y-%m-%d %H:%M:%S')}")
#     print(f"   Vedic day duration: {(sunrise_tomorrow - sunrise_today).total_seconds() / 3600:.2f} hours")
    
#     scan_start = sunrise_today - timedelta(hours=1)
#     scan_end = sunrise_tomorrow + timedelta(hours=1)
    
#     print(f"   Scan range: {scan_start.strftime('%H:%M')} to {scan_end.strftime('%Y-%m-%d %H:%M')}")
    
#     all_transitions = []
    
#     current_dt = scan_start
#     increment = timedelta(minutes=3)
    
#     prev_lagna = None
#     prev_dt = None
    
#     print(f"   Scanning for Lagna changes...")
    
#     scan_count = 0
#     while current_dt <= scan_end:
#         try:
#             dt_utc = current_dt.astimezone(pytz.UTC)
#             jd = swe.julday(
#                 dt_utc.year, dt_utc.month, dt_utc.day,
#                 dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
#             )
            
#             cusps, ascmc = swe.houses(jd, latitude, longitude, b'P')
#             tropical_asc = ascmc[0]
#             ayanamsa = swe.get_ayanamsa_ut(jd)
#             sidereal_asc = (tropical_asc - ayanamsa) % 360
            
#             lagna_num = int(sidereal_asc / 30) + 1
            
#             if prev_lagna is None:
#                 prev_lagna = lagna_num
#                 prev_dt = current_dt
#             elif lagna_num != prev_lagna:
#                 if scan_count < 5:
#                     print(f"   Transition: {RASHI_DATABASE[prev_lagna]['name']} → {RASHI_DATABASE[lagna_num]['name']}")
                
#                 search_start = current_dt - increment
#                 search_end = current_dt
                
#                 transition_count = 0
#                 while (search_end - search_start).total_seconds() > 1 and transition_count < 20:
#                     mid_dt = search_start + (search_end - search_start) / 2
                    
#                     mid_utc = mid_dt.astimezone(pytz.UTC)
#                     mid_jd = swe.julday(
#                         mid_utc.year, mid_utc.month, mid_utc.day,
#                         mid_utc.hour + mid_utc.minute/60.0 + mid_utc.second/3600.0
#                     )
                    
#                     mid_cusps, mid_ascmc = swe.houses(mid_jd, latitude, longitude, b'P')
#                     mid_tropical = mid_ascmc[0]
#                     mid_ayanamsa = swe.get_ayanamsa_ut(mid_jd)
#                     mid_sidereal = (mid_tropical - mid_ayanamsa) % 360
#                     mid_lagna = int(mid_sidereal / 30) + 1
                    
#                     if mid_lagna == prev_lagna:
#                         search_start = mid_dt
#                     else:
#                         search_end = mid_dt
                    
#                     transition_count += 1
                
#                 transition_time = search_end
                
#                 all_transitions.append({
#                     "lagna_number": prev_lagna,
#                     "lagna_name": RASHI_DATABASE[prev_lagna]["name"],
#                     "start_datetime": prev_dt,
#                     "end_datetime": transition_time
#                 })
                
#                 prev_lagna = lagna_num
#                 prev_dt = transition_time
#                 scan_count += 1
            
#         except Exception as e:
#             print(f"   Warning at {current_dt.strftime('%H:%M:%S')}: {e}")
        
#         current_dt += increment
    
#     if prev_lagna is not None:
#         all_transitions.append({
#             "lagna_number": prev_lagna,
#             "lagna_name": RASHI_DATABASE[prev_lagna]["name"],
#             "start_datetime": prev_dt,
#             "end_datetime": scan_end
#         })
    
#     print(f"   Found {len(all_transitions)} Lagna periods in extended scan")
    
#     filtered_lagnas = []
    
#     for lagna_period in all_transitions:
#         start_dt = lagna_period["start_datetime"]
#         end_dt = lagna_period["end_datetime"]
        
#         if end_dt > sunrise_today and start_dt < sunrise_tomorrow:
#             display_start = start_dt if start_dt >= sunrise_today else sunrise_today
#             display_end = end_dt if end_dt <= sunrise_tomorrow else sunrise_tomorrow
            
#             duration_seconds = (display_end - display_start).total_seconds()
#             duration_minutes = duration_seconds / 60.0
            
#             def format_vedic_time(dt, reference_date):
#                 time_str = dt.strftime('%H:%M:%S')
                
#                 if dt.date() > reference_date:
#                     hours_from_midnight = dt.hour
#                     total_hours = 24 + hours_from_midnight
#                     vedic_time = f"{total_hours:02d}:{dt.strftime('%M:%S')}"
#                     return vedic_time, time_str
#                 else:
#                     return time_str, time_str
            
#             reference_date = sunrise_today.date()
#             start_vedic, start_standard = format_vedic_time(display_start, reference_date)
#             end_vedic, end_standard = format_vedic_time(display_end, reference_date)
            
#             lagna_details = RASHI_DATABASE[lagna_period["lagna_number"]]
            
#             lagna_info = {
#                 "lagna_number": lagna_period["lagna_number"],
#                 "lagna_name": lagna_period["lagna_name"],
#                 "sanskrit_name": lagna_details["sanskrit_name"],
#                 "lord": lagna_details["lord"],
#                 "element": lagna_details["element"],
#                 "quality": lagna_details["quality"],
#                 "start_time": start_standard,
#                 "end_time": end_standard,
#                 "start_time_vedic": start_vedic,
#                 "end_time_vedic": end_vedic,
#                 "duration_minutes": round(duration_minutes, 2),
#                 "duration_hours": round(duration_minutes / 60, 2),
#                 "best_for": lagna_details["best_for"],
#                 "avoid_for": lagna_details["avoid_for"],
#                 "characteristics": lagna_details["characteristics"]
#             }
            
#             if display_start.date() > reference_date:
#                 lagna_info["note"] = "Next calendar day (same Vedic day)"
#             if start_dt < sunrise_today:
#                 lagna_info["note"] = f"Started before sunrise at {start_dt.strftime('%H:%M:%S')}"
#             if end_dt > sunrise_tomorrow:
#                 lagna_info["note"] = f"Continues past next sunrise"
            
#             filtered_lagnas.append(lagna_info)
    
#     print(f"   Filtered to {len(filtered_lagnas)} Lagnas for Vedic day")
    
#     total_duration = sum([lagna["duration_minutes"] for lagna in filtered_lagnas])
#     expected_duration = (sunrise_tomorrow - sunrise_today).total_seconds() / 60.0
    
#     print(f"   Total duration: {total_duration:.2f} minutes ({total_duration/60:.2f} hours)")
#     print(f"   Expected: {expected_duration:.2f} minutes ({expected_duration/60:.2f} hours)")
    
#     if abs(total_duration - expected_duration) > 1:
#         print(f"   ⚠️  WARNING: Duration mismatch by {abs(total_duration - expected_duration):.2f} minutes")
#     else:
#         print(f"   ✓ Duration validation passed")
    
#     avg_duration = total_duration / len(filtered_lagnas) if filtered_lagnas else 0
#     min_duration = min([ls["duration_minutes"] for ls in filtered_lagnas]) if filtered_lagnas else 0
#     max_duration = max([ls["duration_minutes"] for ls in filtered_lagnas]) if filtered_lagnas else 0
    
#     return {
#         "lagna_schedule": filtered_lagnas,
#         "vedic_day": {
#             "date": date_str,
#             "sunrise_today": sunrise_today.strftime('%Y-%m-%d %H:%M:%S'),
#             "sunrise_tomorrow": sunrise_tomorrow.strftime('%Y-%m-%d %H:%M:%S'),
#             "day_type": "Vedic Day (Sunrise to Sunrise)",
#             "duration_hours": round(expected_duration / 60, 2)
#         },
#         "summary": {
#             "total_lagnas": len(filtered_lagnas),
#             "total_duration_minutes": round(total_duration, 2),
#             "total_duration_hours": round(total_duration / 60, 2),
#             "average_duration_minutes": round(avg_duration, 2),
#             "minimum_duration_minutes": round(min_duration, 2),
#             "maximum_duration_minutes": round(max_duration, 2),
#             "latitude": latitude,
#             "longitude": longitude,
#             "calculation_method": "Vedic (Sunrise to Sunrise)"
#         }
#     }

# def get_current_lagna_timing(date_str: str, time_str: str, latitude: float,
#                              longitude: float, timezone_str: str) -> Dict:
#     """Get current Lagna with its timing within Vedic day (sunrise to sunrise)"""
    
#     full_schedule = calculate_lagna_timings_vedic(date_str, latitude, longitude, timezone_str)
    
#     tz = pytz.timezone(timezone_str)
#     dt_str = f"{date_str} {time_str}"
#     current_dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
#     current_dt = tz.localize(current_dt)
    
#     current_lagna_info = None
#     next_lagna_info = None
    
#     for i, lagna in enumerate(full_schedule["lagna_schedule"]):
#         start_time_str = lagna["start_time"]
#         end_time_str = lagna["end_time"]
        
#         start_time_parts = start_time_str.split(':')
#         end_time_parts = end_time_str.split(':')
        
#         start_dt = current_dt.replace(
#             hour=int(start_time_parts[0]),
#             minute=int(start_time_parts[1]),
#             second=int(start_time_parts[2])
#         )
        
#         end_dt = current_dt.replace(
#             hour=int(end_time_parts[0]),
#             minute=int(end_time_parts[1]),
#             second=int(end_time_parts[2])
#         )
        
#         if end_dt <= start_dt:
#             end_dt += timedelta(days=1)
        
#         if start_dt <= current_dt < end_dt:
#             current_lagna_info = lagna.copy()
            
#             elapsed_seconds = (current_dt - start_dt).total_seconds()
#             remaining_seconds = (end_dt - current_dt).total_seconds()
#             total_seconds = (end_dt - start_dt).total_seconds()
            
#             progress_percent = (elapsed_seconds / total_seconds * 100) if total_seconds > 0 else 0
            
#             current_lagna_info["elapsed_minutes"] = round(elapsed_seconds / 60, 2)
#             current_lagna_info["remaining_minutes"] = round(remaining_seconds / 60, 2)
#             current_lagna_info["progress_percent"] = round(progress_percent, 2)
            
#             if i < len(full_schedule["lagna_schedule"]) - 1:
#                 next_lagna_info = full_schedule["lagna_schedule"][i + 1]
            
#             break
    
#     if not current_lagna_info:
#         return {
#             "error": "Could not determine current Lagna",
#             "full_schedule": full_schedule
#         }
    
#     return {
#         "current_lagna": current_lagna_info,
#         "next_lagna": next_lagna_info if next_lagna_info else {
#             "note": "No more Lagna changes in this Vedic day"
#         },
#         "vedic_day_info": full_schedule["vedic_day"],
#         "full_day_schedule": full_schedule["lagna_schedule"]
#     }





"""
PANCHANGA CALCULATION MODULE
=============================
All astronomical and Vedic calculations (NO MUHURAT TIMINGS)

Features:
- Complete Panchanga (Tithi, Nakshatra, Yoga, Karana, Vara)
- Sunrise/Sunset/Moonrise/Moonset (Exact with Skyfield)
- 30 Murthas with Deity and Nature
- Choghadiya (Day and Night periods)
- Hora (24 Planetary Hours)
- Lagna (Ascendant with 12 House Cusps)
"""

import swisseph as swe
import datetime
import pytz
from typing import Dict, Optional, List, Tuple
from datetime import timedelta
import os

# Try to import Skyfield
try:
    from skyfield import api, almanac
    SKYFIELD_AVAILABLE = True
    print("✓ Skyfield available - EXACT calculations enabled")
except ImportError:
    SKYFIELD_AVAILABLE = False
    print("⚠️ Skyfield not available - install with: pip install skyfield")

# Configuration
SWISS_EPHE_PATH = "astro_api/ephe"
LAHIRI_AYANAMSA = swe.SIDM_LAHIRI

# Initialize Skyfield (if available)
ts_global = None
eph_global = None

if SKYFIELD_AVAILABLE:
    try:
        ts_global = api.load.timescale()
        eph_global = api.load('de421.bsp')
        print("✓ Skyfield ephemeris loaded (JPL DE421)")
    except Exception as e:
        print(f"⚠️ Skyfield load error: {e}")
        SKYFIELD_AVAILABLE = False

# ============================================================================
# MURTHA DATABASE - Complete 30 Murthas with Deities and Nature
# ============================================================================

MURTHA_DATABASE = {
    1: {"name": "Rudra", "deity": "Shiva", "nature": "Ashubha", "quality": "Inauspicious"},
    2: {"name": "Mahendra", "deity": "Indra", "nature": "Shubha", "quality": "Auspicious"},
    3: {"name": "Dhata", "deity": "Brahma", "nature": "Shubha", "quality": "Auspicious"},
    4: {"name": "Raudra", "deity": "Rudra", "nature": "Ashubha", "quality": "Inauspicious"},
    5: {"name": "Kala", "deity": "Yama", "nature": "Ashubha", "quality": "Inauspicious"},
    6: {"name": "Vaivasvata", "deity": "Yama", "nature": "Ashubha", "quality": "Inauspicious"},
    7: {"name": "Ghora", "deity": "Yama", "nature": "Ashubha", "quality": "Inauspicious"},
    8: {"name": "Sarpa", "deity": "Serpents", "nature": "Ashubha", "quality": "Inauspicious"},
    9: {"name": "Amrita", "deity": "Vishnu", "nature": "Shubha", "quality": "Most Auspicious"},
    10: {"name": "Maitra", "deity": "Mitra", "nature": "Shubha", "quality": "Auspicious"},
    11: {"name": "Pitri", "deity": "Ancestors", "nature": "Ashubha", "quality": "Inauspicious"},
    12: {"name": "Kala", "deity": "Kali", "nature": "Ashubha", "quality": "Inauspicious"},
    13: {"name": "Sarva", "deity": "Shiva", "nature": "Ashubha", "quality": "Inauspicious"},
    14: {"name": "Bhaga", "deity": "Bhaga Deva", "nature": "Shubha", "quality": "Auspicious"},
    15: {"name": "Aryaman", "deity": "Aryaman", "nature": "Shubha", "quality": "Auspicious"},
    16: {"name": "Girisha", "deity": "Shiva", "nature": "Ashubha", "quality": "Inauspicious"},
    17: {"name": "Ajapada", "deity": "Ajapada", "nature": "Ashubha", "quality": "Inauspicious"},
    18: {"name": "Ahirbudhnya", "deity": "Ahirbudhnya", "nature": "Ashubha", "quality": "Inauspicious"},
    19: {"name": "Pushya", "deity": "Brihaspati", "nature": "Shubha", "quality": "Most Auspicious"},
    20: {"name": "Ashvini", "deity": "Ashvini Kumaras", "nature": "Shubha", "quality": "Auspicious"},
    21: {"name": "Yama", "deity": "Yama", "nature": "Ashubha", "quality": "Inauspicious"},
    22: {"name": "Agni", "deity": "Agni", "nature": "Ashubha", "quality": "Inauspicious"},
    23: {"name": "Vidhatr", "deity": "Brahma", "nature": "Shubha", "quality": "Auspicious"},
    24: {"name": "Kanda", "deity": "Kanda", "nature": "Ashubha", "quality": "Inauspicious"},
    25: {"name": "Aditi", "deity": "Aditi", "nature": "Shubha", "quality": "Auspicious"},
    26: {"name": "Jiva", "deity": "Brihaspati", "nature": "Shubha", "quality": "Auspicious"},
    27: {"name": "Vishnu", "deity": "Vishnu", "nature": "Shubha", "quality": "Most Auspicious"},
    28: {"name": "Dyumani", "deity": "Yama", "nature": "Ashubha", "quality": "Inauspicious"},
    29: {"name": "Dhatri", "deity": "Brahma", "nature": "Shubha", "quality": "Auspicious"},
    30: {"name": "Tvastr", "deity": "Tvashta", "nature": "Ashubha", "quality": "Inauspicious"}
}

# ============================================================================
# CHOGHADIYA DATABASE
# ============================================================================

CHOGHADIYA_TYPES = {
    "Amrit": {
        "nature": "Shubha",
        "quality": "Most Auspicious",
        "description": "Nectar - Excellent for all activities",
        "best_for": "All important activities, ceremonies, weddings, new beginnings",
        "deity": "Vishnu",
        "color": "green"
    },
    "Shubh": {
        "nature": "Shubha",
        "quality": "Auspicious",
        "description": "Auspicious - Good for most activities",
        "best_for": "Business deals, meetings, general activities",
        "deity": "Lakshmi",
        "color": "green"
    },
    "Labh": {
        "nature": "Shubha",
        "quality": "Auspicious",
        "description": "Profit - Excellent for financial matters",
        "best_for": "Business transactions, shopping, investments, financial decisions",
        "deity": "Kubera",
        "color": "green"
    },
    "Char": {
        "nature": "Mishra",
        "quality": "Neutral/Mixed",
        "description": "Movable - Good for travel and movement",
        "best_for": "Travel, transportation, temporary activities",
        "avoid": "Starting permanent ventures",
        "deity": "Vayu",
        "color": "yellow"
    },
    "Rog": {
        "nature": "Ashubha",
        "quality": "Inauspicious",
        "description": "Disease - Avoid important activities",
        "avoid": "All important activities, medical procedures, new beginnings",
        "deity": "Yama",
        "color": "red"
    },
    "Kaal": {
        "nature": "Ashubha",
        "quality": "Most Inauspicious",
        "description": "Death - Most inauspicious period",
        "avoid": "Everything except destruction work",
        "deity": "Kala Bhairava",
        "color": "red"
    },
    "Udveg": {
        "nature": "Ashubha",
        "quality": "Inauspicious",
        "description": "Anxiety - Causes stress and confusion",
        "avoid": "Important decisions, new ventures, emotional discussions",
        "deity": "Rahu",
        "color": "red"
    }
}

DAY_CHOGHADIYA_SEQUENCE = {
    0: ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg"],
    1: ["Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit"],
    2: ["Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"],
    3: ["Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh"],
    4: ["Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh"],
    5: ["Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char"],
    6: ["Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal"]
}

NIGHT_CHOGHADIYA_SEQUENCE = {
    0: ["Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh"],
    1: ["Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char"],
    2: ["Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal"],
    3: ["Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg"],
    4: ["Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit"],
    5: ["Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog"],
    6: ["Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh"]
}

# ============================================================================
# HORA DATABASE AND CALCULATIONS
# ============================================================================

HORA_LORDS = {
    "Sun": {
        "sanskrit_name": "Surya",
        "nature": "Royal, Authoritative, Powerful",
        "quality": "Neutral",
        "best_for": "Government work, meeting authorities, leadership activities, applying for jobs, medical treatments, buying gold",
        "avoid": "Starting quarrels, ego-driven decisions",
        "color": "orange",
        "rank": 4
    },
    "Moon": {
        "sanskrit_name": "Chandra",
        "nature": "Emotional, Nurturing, Peaceful",
        "quality": "Good",
        "best_for": "Public dealings, travel (water), buying pearls/silver, meeting mother, household work, agriculture, liquid medicines",
        "avoid": "Important permanent decisions (Moon is changeable)",
        "color": "lightblue",
        "rank": 4
    },
    "Mars": {
        "sanskrit_name": "Mangal",
        "nature": "Aggressive, Energetic, Courageous",
        "quality": "Specific Purpose",
        "best_for": "Sports/competitions, surgery, buying property/land, military/police work, dealing with enemies, physical activities, buying weapons/tools",
        "avoid": "Peaceful negotiations, marriage proposals",
        "color": "red",
        "rank": 5
    },
    "Mercury": {
        "sanskrit_name": "Budh",
        "nature": "Intellectual, Communicative, Business-minded",
        "quality": "Excellent",
        "best_for": "Business transactions, signing contracts, education, writing/publishing, communication, trading/commerce, accounts/banking, short travels",
        "avoid": "Almost nothing (very versatile)",
        "color": "green",
        "rank": 1
    },
    "Jupiter": {
        "sanskrit_name": "Guru/Brihaspati",
        "nature": "Auspicious, Spiritual, Wisdom",
        "quality": "Most Excellent",
        "best_for": "Marriage ceremonies, religious ceremonies, education, meeting teachers/gurus, legal matters, financial investments, charitable activities, children-related matters",
        "avoid": "Unethical activities",
        "color": "yellow",
        "rank": 1
    },
    "Venus": {
        "sanskrit_name": "Shukra",
        "nature": "Luxury, Beauty, Pleasure, Artistic",
        "quality": "Excellent",
        "best_for": "Marriage/romantic activities, buying jewelry/clothes, arts/entertainment, music/dance, luxury purchases, beauty treatments, social gatherings, romantic proposals",
        "avoid": "Harsh/serious activities",
        "color": "pink",
        "rank": 2
    },
    "Saturn": {
        "sanskrit_name": "Shani",
        "nature": "Serious, Disciplined, Karmic, Slow",
        "quality": "Generally Inauspicious",
        "best_for": "Buying property (real estate), construction work, dealing with servants/laborers, chronic disease treatment, mining/oil work, spiritual practices (serious), legal proceedings, resolving old issues",
        "avoid": "Auspicious ceremonies, new ventures, joyful activities",
        "color": "darkgray",
        "rank": 6
    }
}

CHALDEAN_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

DAY_LORDS = {
    0: "Sun",       # Sunday (Ravi-var)
    1: "Moon",      # Monday (Som-var)
    2: "Mars",      # Tuesday (Mangal-var)
    3: "Mercury",   # Wednesday (Budh-var)
    4: "Jupiter",   # Thursday (Guru-var/Brihaspati-var)
    5: "Venus",     # Friday (Shukra-var)
    6: "Saturn"     # Saturday (Shani-var)
}

# ============================================================================
# LAGNA (ASCENDANT) DATABASE AND CALCULATIONS
# ============================================================================

RASHI_DATABASE = {
    1: {
        "name": "Aries",
        "sanskrit_name": "Mesha",
        "lord": "Mars",
        "element": "Fire",
        "quality": "Movable (Chara)",
        "nature": "Dynamic, Energetic, Pioneering",
        "body_parts": "Head, Face, Brain",
        "characteristics": "Courageous, Impulsive, Leadership, Athletic",
        "best_for": "Quick actions, leadership roles, sports, military",
        "avoid_for": "Activities requiring patience and diplomacy"
    },
    2: {
        "name": "Taurus",
        "sanskrit_name": "Vrishabha",
        "lord": "Venus",
        "element": "Earth",
        "quality": "Fixed (Sthira)",
        "nature": "Stable, Sensual, Practical",
        "body_parts": "Neck, Throat, Voice",
        "characteristics": "Patient, Determined, Pleasure-loving, Beautiful",
        "best_for": "Marriage, property purchase, financial matters, luxury",
        "avoid_for": "Quick changes, urgent matters"
    },
    3: {
        "name": "Gemini",
        "sanskrit_name": "Mithuna",
        "lord": "Mercury",
        "element": "Air",
        "quality": "Dual (Dwiswabhava)",
        "nature": "Communicative, Versatile, Curious",
        "body_parts": "Arms, Shoulders, Hands",
        "characteristics": "Intelligent, Social, Restless, Expressive",
        "best_for": "Communication, business, writing, learning, trade",
        "avoid_for": "Serious spiritual practices"
    },
    4: {
        "name": "Cancer",
        "sanskrit_name": "Karka",
        "lord": "Moon",
        "element": "Water",
        "quality": "Movable (Chara)",
        "nature": "Emotional, Nurturing, Sensitive",
        "body_parts": "Chest, Breasts, Stomach",
        "characteristics": "Caring, Moody, Intuitive, Protective",
        "best_for": "Family matters, home purchase, nurturing activities",
        "avoid_for": "Harsh negotiations, litigation"
    },
    5: {
        "name": "Leo",
        "sanskrit_name": "Simha",
        "lord": "Sun",
        "element": "Fire",
        "quality": "Fixed (Sthira)",
        "nature": "Royal, Dignified, Authoritative",
        "body_parts": "Heart, Upper Back, Spine",
        "characteristics": "Confident, Generous, Dramatic, Leadership",
        "best_for": "Authority matters, government work, leadership, ceremonies",
        "avoid_for": "Humble service activities"
    },
    6: {
        "name": "Virgo",
        "sanskrit_name": "Kanya",
        "lord": "Mercury",
        "element": "Earth",
        "quality": "Dual (Dwiswabhava)",
        "nature": "Analytical, Perfectionist, Practical",
        "body_parts": "Intestines, Digestive System",
        "characteristics": "Intelligent, Critical, Service-oriented, Detail-focused",
        "best_for": "Analysis, health matters, service, accounting, editing",
        "avoid_for": "Creative/artistic activities requiring spontaneity"
    },
    7: {
        "name": "Libra",
        "sanskrit_name": "Tula",
        "lord": "Venus",
        "element": "Air",
        "quality": "Movable (Chara)",
        "nature": "Balanced, Diplomatic, Artistic",
        "body_parts": "Kidneys, Lower Back",
        "characteristics": "Harmonious, Indecisive, Charming, Fair",
        "best_for": "Marriage, partnerships, legal matters, arts, diplomacy",
        "avoid_for": "Solo ventures, quick decisions"
    },
    8: {
        "name": "Scorpio",
        "sanskrit_name": "Vrishchika",
        "lord": "Mars",
        "element": "Water",
        "quality": "Fixed (Sthira)",
        "nature": "Intense, Mysterious, Transformative",
        "body_parts": "Reproductive Organs",
        "characteristics": "Deep, Secretive, Powerful, Investigative",
        "best_for": "Research, occult, surgery, transformation, investigation",
        "avoid_for": "Marriage, joyful ceremonies (generally inauspicious)"
    },
    9: {
        "name": "Sagittarius",
        "sanskrit_name": "Dhanu",
        "lord": "Jupiter",
        "element": "Fire",
        "quality": "Dual (Dwiswabhava)",
        "nature": "Philosophical, Optimistic, Adventurous",
        "body_parts": "Thighs, Hips",
        "characteristics": "Wise, Honest, Freedom-loving, Religious",
        "best_for": "Education, religious ceremonies, travel, philosophy, teaching",
        "avoid_for": "Detailed analytical work"
    },
    10: {
        "name": "Capricorn",
        "sanskrit_name": "Makara",
        "lord": "Saturn",
        "element": "Earth",
        "quality": "Movable (Chara)",
        "nature": "Ambitious, Disciplined, Practical",
        "body_parts": "Knees, Bones, Joints",
        "characteristics": "Serious, Responsible, Patient, Career-focused",
        "best_for": "Career matters, long-term planning, construction, discipline",
        "avoid_for": "Entertainment, joyful celebrations"
    },
    11: {
        "name": "Aquarius",
        "sanskrit_name": "Kumbha",
        "lord": "Saturn",
        "element": "Air",
        "quality": "Fixed (Sthira)",
        "nature": "Humanitarian, Innovative, Eccentric",
        "body_parts": "Ankles, Calves",
        "characteristics": "Independent, Intellectual, Unconventional, Social",
        "best_for": "Social causes, innovation, technology, group activities",
        "avoid_for": "Traditional ceremonies"
    },
    12: {
        "name": "Pisces",
        "sanskrit_name": "Meena",
        "lord": "Jupiter",
        "element": "Water",
        "quality": "Dual (Dwiswabhava)",
        "nature": "Spiritual, Compassionate, Dreamy",
        "body_parts": "Feet, Lymphatic System",
        "characteristics": "Intuitive, Escapist, Artistic, Mystical",
        "best_for": "Spiritual practices, arts, charity, healing, meditation",
        "avoid_for": "Business dealings requiring practicality"
    }
}

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

HOUSE_SIGNIFICATIONS = {
    1: "Self, Body, Personality, Health, Appearance",
    2: "Wealth, Family, Speech, Food, Values",
    3: "Siblings, Courage, Skills, Short Journeys, Communication",
    4: "Mother, Home, Property, Vehicles, Education, Peace",
    5: "Children, Intelligence, Creativity, Romance, Speculation",
    6: "Enemies, Diseases, Debts, Service, Obstacles",
    7: "Spouse, Partnerships, Marriage, Business Partners",
    8: "Longevity, Death, Transformation, Occult, Inheritance",
    9: "Father, Luck, Religion, Higher Education, Long Journeys",
    10: "Career, Status, Reputation, Authority, Profession",
    11: "Gains, Income, Friends, Elder Siblings, Aspirations",
    12: "Losses, Expenses, Foreign Lands, Spirituality, Liberation"
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_murtha_details(murtha_number: int) -> Dict:
    """Get deity, nature, and quality for given Murtha number (1-30)"""
    return MURTHA_DATABASE.get(murtha_number, {
        "name": "Unknown", "deity": "Unknown", "nature": "Unknown", "quality": "Unknown"
    })

def format_time(dt: datetime.datetime) -> str:
    """Format datetime to HH:MM:SS string"""
    return dt.strftime("%H:%M:%S")

# ============================================================================
# PANCHANGA CALCULATION WITH EXACT TIMINGS
# ============================================================================

def calculate_tithi_end_time(jd_start: float, current_tithi_num: int, 
                             current_phase_angle: float, timezone_str: str) -> Optional[Dict]:
    """
    Calculate EXACT time when current Tithi ends
    
    Logic:
    - Each Tithi spans 12° of phase angle (Moon-Sun difference)
    - Tithi 1 (Pratipada): 0° to 12°
    - Tithi 2 (Dvitiya): 12° to 24°
    - ...
    - Tithi 15 (Purnima): 168° to 180°
    - Tithi 16 (Pratipada K): 180° to 192°
    - ...
    - Tithi 30 (Amavasya): 348° to 360° (0°)
    
    Method: Binary search to find exact moment phase angle crosses boundary
    """
    
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    
    # Calculate target phase angle for end of current Tithi
    tithi_end_angle = current_tithi_num * 12.0
    if tithi_end_angle >= 360:
        tithi_end_angle = 0.0  # Amavasya ends at 0° (new moon)
    
    print(f"\n🌙 Searching for Tithi #{current_tithi_num} end time...")
    print(f"   Current phase: {current_phase_angle:.4f}°")
    print(f"   Target phase: {tithi_end_angle:.4f}°")
    
    # Estimate time remaining (Moon moves ~13.176°/day relative to Sun in phase angle)
    degrees_remaining = (tithi_end_angle - current_phase_angle) % 360.0
    moon_speed_per_day = 13.176
    approx_days_remaining = degrees_remaining / moon_speed_per_day
    
    print(f"   Estimated time: {approx_days_remaining * 24:.1f} hours")
    
    # Binary search for exact transition
    search_jd_start = jd_start + (approx_days_remaining * 0.8)  # Start a bit before estimate
    search_jd_end = jd_start + (approx_days_remaining * 1.2) + 0.5  # End a bit after
    
    max_iterations = 30
    iteration = 0
    
    while (search_jd_end - search_jd_start) > (1.0 / 86400.0) and iteration < max_iterations:  # 1 second precision
        mid_jd = (search_jd_start + search_jd_end) / 2.0
        
        sun_result = swe.calc_ut(mid_jd, swe.SUN, flags)
        moon_result = swe.calc_ut(mid_jd, swe.MOON, flags)
        
        sun_lon = sun_result[0][0] % 360.0
        moon_lon = moon_result[0][0] % 360.0
        phase_angle = (moon_lon - sun_lon) % 360.0
        
        # Check if we've crossed the boundary
        if current_tithi_num == 30:  # Amavasya special case
            # We're looking for phase angle to cross from 348-360 to 0-12
            if phase_angle < 180:  # We've crossed into new cycle
                search_jd_end = mid_jd
            else:
                search_jd_start = mid_jd
        else:
            if phase_angle >= tithi_end_angle:
                search_jd_end = mid_jd
            else:
                search_jd_start = mid_jd
        
        iteration += 1
    
    end_jd = search_jd_end
    
    # Convert to local time
    tz = pytz.timezone(timezone_str)
    year, month, day, hour = swe.revjul(end_jd)
    hour_int = int(hour)
    minute = int((hour - hour_int) * 60)
    second = int(((hour - hour_int) * 60 - minute) * 60)
    
    utc_dt = datetime.datetime(year, month, day, hour_int, minute, second, tzinfo=pytz.UTC)
    local_dt = utc_dt.astimezone(tz)
    
    print(f"   ✓ Found at: {local_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return {
        "end_time": local_dt.strftime("%H:%M:%S"),
        "end_datetime": local_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": local_dt.strftime("%Y-%m-%d")
    }

def calculate_nakshatra_end_time(jd_start: float, current_nak_num: int,
                                 current_moon_lon: float, timezone_str: str) -> Optional[Dict]:
    """
    Calculate EXACT time when current Nakshatra ends
    
    Logic:
    - Each Nakshatra spans 13.333333° (13°20')
    - Nakshatra 1 (Ashwini): 0° to 13.333333°
    - Nakshatra 2 (Bharani): 13.333333° to 26.666666°
    - ...
    - Nakshatra 27 (Revati): 346.666666° to 360°
    
    Method: Binary search to find exact moment Moon crosses boundary
    """
    
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    
    # Calculate target longitude for end of current Nakshatra
    nak_end_lon = current_nak_num * 13.333333
    if current_nak_num == 27:
        nak_end_lon = 360.0
    
    print(f"\n⭐ Searching for Nakshatra #{current_nak_num} end time...")
    print(f"   Current Moon: {current_moon_lon:.4f}°")
    print(f"   Target Moon: {nak_end_lon:.4f}°")
    
    # Estimate time remaining (Moon moves ~13.176°/day)
    degrees_remaining = (nak_end_lon - current_moon_lon) % 360.0
    if degrees_remaining > 180:  # Shortest path
        degrees_remaining = 360.0 - degrees_remaining
    
    moon_speed_per_day = 13.176
    approx_days_remaining = degrees_remaining / moon_speed_per_day
    
    print(f"   Estimated time: {approx_days_remaining * 24:.1f} hours")
    
    # Binary search
    search_jd_start = jd_start + (approx_days_remaining * 0.8)
    search_jd_end = jd_start + (approx_days_remaining * 1.2) + 0.5
    
    max_iterations = 30
    iteration = 0
    
    while (search_jd_end - search_jd_start) > (1.0 / 86400.0) and iteration < max_iterations:
        mid_jd = (search_jd_start + search_jd_end) / 2.0
        
        moon_result = swe.calc_ut(mid_jd, swe.MOON, flags)
        moon_lon = moon_result[0][0] % 360.0
        
        if current_nak_num == 27:  # Revati special case
            if moon_lon < 180:  # Crossed into Ashwini
                search_jd_end = mid_jd
            else:
                search_jd_start = mid_jd
        else:
            if moon_lon >= nak_end_lon:
                search_jd_end = mid_jd
            else:
                search_jd_start = mid_jd
        
        iteration += 1
    
    end_jd = search_jd_end
    
    # Convert to local time
    tz = pytz.timezone(timezone_str)
    year, month, day, hour = swe.revjul(end_jd)
    hour_int = int(hour)
    minute = int((hour - hour_int) * 60)
    second = int(((hour - hour_int) * 60 - minute) * 60)
    
    utc_dt = datetime.datetime(year, month, day, hour_int, minute, second, tzinfo=pytz.UTC)
    local_dt = utc_dt.astimezone(tz)
    
    print(f"   ✓ Found at: {local_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return {
        "end_time": local_dt.strftime("%H:%M:%S"),
        "end_datetime": local_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": local_dt.strftime("%Y-%m-%d")
    }

def calculate_yoga_end_time(jd_start: float, current_yoga_num: int,
                            current_yoga_sum: float, timezone_str: str) -> Optional[Dict]:
    """
    Calculate EXACT time when current Yoga ends
    
    Logic:
    - Yoga = (Sun longitude + Moon longitude) % 360
    - Each Yoga spans 13.333333° (13°20')
    - Yoga 1 (Vishkambha): 0° to 13.333333°
    - Yoga 2 (Priti): 13.333333° to 26.666666°
    - ...
    - Yoga 27 (Vaidhriti): 346.666666° to 360°
    
    Method: Binary search to find exact moment sum crosses boundary
    """
    
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    
    # Calculate target yoga sum for end of current Yoga
    yoga_end_sum = current_yoga_num * 13.333333
    if current_yoga_num == 27:
        yoga_end_sum = 360.0
    
    print(f"\n🔗 Searching for Yoga #{current_yoga_num} end time...")
    print(f"   Current sum: {current_yoga_sum:.4f}°")
    print(f"   Target sum: {yoga_end_sum:.4f}°")
    
    # Estimate time remaining (Sun+Moon sum increases ~13.4°/day on average)
    degrees_remaining = (yoga_end_sum - current_yoga_sum) % 360.0
    combined_speed_per_day = 13.4  # Approximate
    approx_days_remaining = degrees_remaining / combined_speed_per_day
    
    print(f"   Estimated time: {approx_days_remaining * 24:.1f} hours")
    
    # Binary search
    search_jd_start = jd_start + (approx_days_remaining * 0.8)
    search_jd_end = jd_start + (approx_days_remaining * 1.2) + 0.5
    
    max_iterations = 30
    iteration = 0
    
    while (search_jd_end - search_jd_start) > (1.0 / 86400.0) and iteration < max_iterations:
        mid_jd = (search_jd_start + search_jd_end) / 2.0
        
        sun_result = swe.calc_ut(mid_jd, swe.SUN, flags)
        moon_result = swe.calc_ut(mid_jd, swe.MOON, flags)
        
        sun_lon = sun_result[0][0] % 360.0
        moon_lon = moon_result[0][0] % 360.0
        yoga_sum = (sun_lon + moon_lon) % 360.0
        
        if current_yoga_num == 27:  # Vaidhriti special case
            if yoga_sum < 180:  # Crossed into Vishkambha
                search_jd_end = mid_jd
            else:
                search_jd_start = mid_jd
        else:
            if yoga_sum >= yoga_end_sum:
                search_jd_end = mid_jd
            else:
                search_jd_start = mid_jd
        
        iteration += 1
    
    end_jd = search_jd_end
    
    # Convert to local time
    tz = pytz.timezone(timezone_str)
    year, month, day, hour = swe.revjul(end_jd)
    hour_int = int(hour)
    minute = int((hour - hour_int) * 60)
    second = int(((hour - hour_int) * 60 - minute) * 60)
    
    utc_dt = datetime.datetime(year, month, day, hour_int, minute, second, tzinfo=pytz.UTC)
    local_dt = utc_dt.astimezone(tz)
    
    print(f"   ✓ Found at: {local_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return {
        "end_time": local_dt.strftime("%H:%M:%S"),
        "end_datetime": local_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": local_dt.strftime("%Y-%m-%d")
    }

def calculate_karana_end_time(jd_start: float, current_karana_half: int,
                              current_phase_angle: float, timezone_str: str) -> Optional[Dict]:
    """
    Calculate EXACT time when current Karana ends
    
    Logic:
    - Each Karana spans 6° of phase angle (half a Tithi)
    - There are 60 half-Tithis in a lunar month (30 Tithis × 2)
    - Karana changes every 6° of phase angle
    
    Method: Binary search to find exact moment phase angle crosses boundary
    """
    
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    
    # Calculate target phase angle for end of current Karana
    karana_end_angle = current_karana_half * 6.0
    if karana_end_angle >= 360:
        karana_end_angle = karana_end_angle % 360.0
    
    print(f"\n⚡ Searching for Karana (half-Tithi #{current_karana_half}) end time...")
    print(f"   Current phase: {current_phase_angle:.4f}°")
    print(f"   Target phase: {karana_end_angle:.4f}°")
    
    # Estimate time remaining
    degrees_remaining = (karana_end_angle - current_phase_angle) % 360.0
    if degrees_remaining > 180:
        degrees_remaining = 360.0 - degrees_remaining
    
    moon_speed_per_day = 13.176
    approx_days_remaining = degrees_remaining / moon_speed_per_day
    
    print(f"   Estimated time: {approx_days_remaining * 24:.1f} hours")
    
    # Binary search
    search_jd_start = jd_start + (approx_days_remaining * 0.8)
    search_jd_end = jd_start + (approx_days_remaining * 1.2) + 0.5
    
    max_iterations = 30
    iteration = 0
    
    while (search_jd_end - search_jd_start) > (1.0 / 86400.0) and iteration < max_iterations:
        mid_jd = (search_jd_start + search_jd_end) / 2.0
        
        sun_result = swe.calc_ut(mid_jd, swe.SUN, flags)
        moon_result = swe.calc_ut(mid_jd, swe.MOON, flags)
        
        sun_lon = sun_result[0][0] % 360.0
        moon_lon = moon_result[0][0] % 360.0
        phase_angle = (moon_lon - sun_lon) % 360.0
        
        # Check which half-Tithi we're in
        half_tithi = int(phase_angle / 6.0)
        
        if half_tithi >= current_karana_half:
            search_jd_end = mid_jd
        else:
            search_jd_start = mid_jd
        
        iteration += 1
    
    end_jd = search_jd_end
    
    # Convert to local time
    tz = pytz.timezone(timezone_str)
    year, month, day, hour = swe.revjul(end_jd)
    hour_int = int(hour)
    minute = int((hour - hour_int) * 60)
    second = int(((hour - hour_int) * 60 - minute) * 60)
    
    utc_dt = datetime.datetime(year, month, day, hour_int, minute, second, tzinfo=pytz.UTC)
    local_dt = utc_dt.astimezone(tz)
    
    print(f"   ✓ Found at: {local_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return {
        "end_time": local_dt.strftime("%H:%M:%S"),
        "end_datetime": local_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": local_dt.strftime("%Y-%m-%d")
    }

def calculate_panchanga_elements(date_str, time_str, timezone_str):
    """
    Calculate Panchanga elements with EXACT END TIMES using Swiss Ephemeris
    
    This function calculates:
    1. Current Tithi, Nakshatra, Yoga, Karana, Vara
    2. Progress percentage for each element
    3. EXACT end time for each element (using binary search)
    
    Classical Reference:
    - Surya Siddhanta (astronomical calculations)
    - Brihat Samhita (Panchanga definitions)
    - Modern ephemeris for precision
    
    All calculations use Swiss Ephemeris with Lahiri Ayanamsa (sidereal zodiac)
    """
    
    if not os.path.exists(SWISS_EPHE_PATH):
        os.makedirs(SWISS_EPHE_PATH, exist_ok=True)
    swe.set_ephe_path(SWISS_EPHE_PATH)
    swe.set_sid_mode(LAHIRI_AYANAMSA)
    
    print(f"\n📅 Panchanga Calculation with Exact Timings:")
    print(f"   Date/Time: {date_str} {time_str}")
    print(f"   Timezone: {timezone_str}")
    
    tz = pytz.timezone(timezone_str)
    dt_str = f"{date_str} {time_str}"
    dt_naive = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    dt_local = tz.localize(dt_naive)
    dt_utc = dt_local.astimezone(pytz.UTC)
    
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                    dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)
    
    print(f"   Julian Day: {jd:.6f}")
    
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun_result = swe.calc_ut(jd, swe.SUN, flags)
    moon_result = swe.calc_ut(jd, swe.MOON, flags)
    
    sun_lon = sun_result[0][0] % 360.0
    moon_lon = moon_result[0][0] % 360.0
    phase_angle = (moon_lon - sun_lon) % 360.0
    
    print(f"   Sun: {sun_lon:.4f}°, Moon: {moon_lon:.4f}°")
    print(f"   Phase angle: {phase_angle:.4f}°")
    
    # Calculate current Tithi
    tithi_num = int(phase_angle / 12) + 1
    tithi_progress = (phase_angle % 12) / 12 * 100
    paksha = "Shukla Paksha" if tithi_num <= 15 else "Krishna Paksha"
    
    # Calculate current Nakshatra
    nak_num = int(moon_lon / 13.333333) + 1
    nak_progress = (moon_lon % 13.333333) / 13.333333
    pada = int(nak_progress * 4) + 1
    
    # Calculate current Yoga
    yoga_sum = (sun_lon + moon_lon) % 360.0
    yoga_num = int(yoga_sum / 13.333333) + 1
    
    # Calculate current Karana
    half_tithi_idx = int(phase_angle / 6)
    karana_num = int(phase_angle / 6) + 1
    
    weekday = dt_local.weekday()
    vara_num = (weekday + 1) % 7 + 1
    
    # Name arrays
    TITHIS = ["Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami",
              "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
              "Ekadashi", "Dvadashi", "Trayodashi", "Chaturdashi", "Purnima",
              "Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami",
              "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
              "Ekadashi", "Dvadashi", "Trayodashi", "Chaturdashi", "Amavasya"]
    
    YOGAS = ["Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma",
             "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
             "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva", "Siddha", "Sadhya",
             "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"]
    
    KARANAS_MOV = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]
    KARANAS_FIX = ["Shakuni", "Chatushpada", "Naga", "Kimstughna"]
    VARAS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    # Determine Karana name
    if half_tithi_idx == 0:
        karana_name = "Kimstughna"
        karana_type = "fixed"
    elif half_tithi_idx >= 57:
        karana_name = KARANAS_FIX[min(2, half_tithi_idx - 57)]
        karana_type = "fixed"
    else:
        karana_name = KARANAS_MOV[(half_tithi_idx - 1) % 7]
        karana_type = "movable"
    
    print(f"   Current: Tithi {tithi_num}, Nak {nak_num}, Yoga {yoga_num}, Karana {karana_num}")
    
    # Calculate EXACT end times for each element
    tithi_end = calculate_tithi_end_time(jd, tithi_num, phase_angle, timezone_str)
    nak_end = calculate_nakshatra_end_time(jd, nak_num, moon_lon, timezone_str)
    yoga_end = calculate_yoga_end_time(jd, yoga_num, yoga_sum, timezone_str)
    karana_end = calculate_karana_end_time(jd, half_tithi_idx + 1, phase_angle, timezone_str)
    
    print(f"   ✓ All end times calculated")
    
    return {
        "tithi": {
            "number": tithi_num,
            "name": TITHIS[tithi_num - 1],
            "paksha": paksha,
            "progress_percent": round(tithi_progress, 2),
            "end_time": tithi_end["end_time"] if tithi_end else None,
            "end_datetime": tithi_end["end_datetime"] if tithi_end else None,
            "end_date": tithi_end["end_date"] if tithi_end else None
        },
        "nakshatra": {
            "number": nak_num,
            "name": NAKSHATRAS[nak_num - 1] if nak_num <= 27 else "Revati",
            "pada": pada,
            "progress_percent": round(nak_progress * 100, 2),
            "end_time": nak_end["end_time"] if nak_end else None,
            "end_datetime": nak_end["end_datetime"] if nak_end else None,
            "end_date": nak_end["end_date"] if nak_end else None
        },
        "yoga": {
            "number": yoga_num,
            "name": YOGAS[yoga_num - 1] if yoga_num <= 27 else "Vaidhriti",
            "progress_percent": round((yoga_sum % 13.333333) / 13.333333 * 100, 2),
            "end_time": yoga_end["end_time"] if yoga_end else None,
            "end_datetime": yoga_end["end_datetime"] if yoga_end else None,
            "end_date": yoga_end["end_date"] if yoga_end else None
        },
        "karana": {
            "number": karana_num,
            "name": karana_name,
            "type": karana_type,
            "progress_percent": round((phase_angle % 6) / 6 * 100, 2),
            "end_time": karana_end["end_time"] if karana_end else None,
            "end_datetime": karana_end["end_datetime"] if karana_end else None,
            "end_date": karana_end["end_date"] if karana_end else None
        },
        "vara": {
            "number": vara_num,
            "name": VARAS[vara_num - 1]
        },
        "weekday": weekday,
        "julian_day": jd
    }

# ============================================================================
# SUN AND MOON TIMES
# ============================================================================

def calculate_exact_sun_times(date_str, time_str, latitude, longitude, timezone_str):
    """Calculate EXACT sun rise/set using Skyfield"""
    if not SKYFIELD_AVAILABLE:
        return None
    
    try:
        tz = pytz.timezone(timezone_str)
        dt_str = f"{date_str} {time_str}"
        dt_local = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        dt_local = tz.localize(dt_local)
        
        location = api.wgs84.latlon(latitude, longitude)
        dt_start = dt_local.replace(hour=0, minute=0, second=0)
        dt_end = dt_start + timedelta(days=1)
        
        t0 = ts_global.from_datetime(dt_start)
        t1 = ts_global.from_datetime(dt_end)
        
        sun = eph_global['sun']
        f = almanac.risings_and_settings(eph_global, sun, location)
        times, events = almanac.find_discrete(t0, t1, f)
        
        sunrise = None
        sunset = None
        sunrise_dt = None
        sunset_dt = None
        
        for time, event in zip(times, events):
            time_utc = time.utc_datetime()
            time_local = time_utc.replace(tzinfo=pytz.UTC).astimezone(tz)
            
            if event == 1:
                sunrise = format_time(time_local)
                sunrise_dt = time_local
            elif event == 0:
                sunset = format_time(time_local)
                sunset_dt = time_local
        
        if sunrise and sunset:
            return {
                "sunrise": sunrise, "sunset": sunset,
                "sunrise_dt": sunrise_dt, "sunset_dt": sunset_dt,
                "method": "skyfield_exact"
            }
        return None
    except Exception as e:
        print(f"Sun calculation error: {e}")
        return None

def calculate_exact_moon_times(date_str, time_str, latitude, longitude, timezone_str):
    """Calculate EXACT moon rise/set using Skyfield"""
    if not SKYFIELD_AVAILABLE:
        return None
    
    try:
        tz = pytz.timezone(timezone_str)
        dt_str = f"{date_str} {time_str}"
        dt_local = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        dt_local = tz.localize(dt_local)
        
        location = api.wgs84.latlon(latitude, longitude)
        dt_start = dt_local.replace(hour=0, minute=0, second=0)
        dt_end = dt_start + timedelta(days=2)
        
        t0 = ts_global.from_datetime(dt_start)
        t1 = ts_global.from_datetime(dt_end)
        
        moon = eph_global['moon']
        f = almanac.risings_and_settings(eph_global, moon, location)
        times, events = almanac.find_discrete(t0, t1, f)
        
        moonrise = None
        moonset = None
        target_date = dt_local.date()
        
        for time, event in zip(times, events):
            time_utc = time.utc_datetime()
            time_local = time_utc.replace(tzinfo=pytz.UTC).astimezone(tz)
            
            if time_local.date() == target_date:
                if event == 1 and moonrise is None:
                    moonrise = time_local
                elif event == 0 and moonset is None:
                    moonset = time_local
            elif time_local.date() == target_date + timedelta(days=1) and time_local.hour < 12:
                if event == 0 and moonset is None:
                    moonset = time_local
        
        if moonrise and moonset:
            return {"moonrise": format_time(moonrise), "moonset": format_time(moonset), "method": "skyfield_exact"}
        return None
    except Exception as e:
        print(f"Moon calculation error: {e}")
        return None

# ============================================================================
# MURTHA CALCULATION
# ============================================================================

def calculate_exact_murtha_corrected(date_str: str, time_str: str, latitude: float, 
                                    longitude: float, timezone_str: str,
                                    sunset_dt: Optional[datetime.datetime] = None) -> Optional[Dict]:
    """Calculate current Murtha with CORRECTED day length display"""
    
    if not SKYFIELD_AVAILABLE:
        return None
    
    try:
        tz = pytz.timezone(timezone_str)
        dt_str = f"{date_str} {time_str}"
        dt_local = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        dt_local = tz.localize(dt_local)
        
        location = api.wgs84.latlon(latitude, longitude)
        dt_start = (dt_local - timedelta(days=1)).replace(hour=0, minute=0, second=0)
        dt_end = (dt_local + timedelta(days=1)).replace(hour=23, minute=59, second=59)
        
        t0 = ts_global.from_datetime(dt_start)
        t1 = ts_global.from_datetime(dt_end)
        
        sun = eph_global['sun']
        f = almanac.risings_and_settings(eph_global, sun, location)
        times, events = almanac.find_discrete(t0, t1, f)
        
        sunrise_times = []
        for time, event in zip(times, events):
            if event == 1:
                time_utc = time.utc_datetime()
                time_local = time_utc.replace(tzinfo=pytz.UTC).astimezone(tz)
                sunrise_times.append(time_local)
        
        if len(sunrise_times) < 2:
            return None
        
        sunrise_times.sort()
        current_sunrise = None
        next_sunrise = None
        
        for i in range(len(sunrise_times) - 1):
            if sunrise_times[i] <= dt_local < sunrise_times[i + 1]:
                current_sunrise = sunrise_times[i]
                next_sunrise = sunrise_times[i + 1]
                break
        
        if not current_sunrise and dt_local < sunrise_times[0]:
            current_sunrise, next_sunrise = sunrise_times[0], sunrise_times[1]
        if not current_sunrise and dt_local >= sunrise_times[-1]:
            current_sunrise, next_sunrise = sunrise_times[-2], sunrise_times[-1]
        
        if not current_sunrise or not next_sunrise:
            return None
        
        murtha_cycle_seconds = (next_sunrise - current_sunrise).total_seconds()
        murtha_cycle_hours = murtha_cycle_seconds / 3600.0
        
        daylight_hours = None
        if sunset_dt:
            daylight_seconds = (sunset_dt - current_sunrise).total_seconds()
            daylight_hours = daylight_seconds / 3600.0
        
        murtha_duration_seconds = murtha_cycle_seconds / 30.0
        elapsed_seconds = (dt_local - current_sunrise).total_seconds()
        
        if elapsed_seconds < 0:
            murtha_number = 30
        else:
            murtha_number = min(int(elapsed_seconds / murtha_duration_seconds) + 1, 30)
        
        murtha_data = get_murtha_details(murtha_number)
        murtha_start = current_sunrise + timedelta(seconds=(murtha_number - 1) * murtha_duration_seconds)
        murtha_end = current_sunrise + timedelta(seconds=murtha_number * murtha_duration_seconds)
        
        remaining_seconds = (murtha_end - dt_local).total_seconds()
        elapsed_in_murtha = (dt_local - murtha_start).total_seconds()
        
        return {
            "murtha_number": murtha_number, "murtha_name": murtha_data["name"],
            "deity": murtha_data["deity"], "nature": murtha_data["nature"],
            "quality": murtha_data["quality"],
            "start_time": format_time(murtha_start), "end_time": format_time(murtha_end),
            "duration_minutes": round(murtha_duration_seconds / 60.0, 2),
            "elapsed_minutes": round(elapsed_in_murtha / 60.0, 2),
            "remaining_minutes": round(remaining_seconds / 60.0, 2),
            "progress_percent": round((elapsed_in_murtha / murtha_duration_seconds) * 100, 2),
            "day_info": {
                "sunrise": format_time(current_sunrise),
                "next_sunrise": format_time(next_sunrise),
                "murtha_cycle_hours": round(murtha_cycle_hours, 2),
                "daylight_hours": round(daylight_hours, 2) if daylight_hours else None,
                "explanation": "Murtha uses sunrise-to-sunrise cycle; daylight shows actual sun hours"
            },
            "method": "skyfield_exact"
        }
    except Exception as e:
        print(f"Murtha calculation error: {e}")
        return None

# ============================================================================
# CHOGHADIYA CALCULATIONS
# ============================================================================

def calculate_choghadiya(sunrise_dt: datetime.datetime, sunset_dt: datetime.datetime,
                        next_sunrise_dt: datetime.datetime, weekday: int) -> Dict:
    """Calculate Day and Night Choghadiya periods"""
    
    print(f"\n🌙 Choghadiya Calculation for weekday {weekday}")
    
    day_duration_seconds = (sunset_dt - sunrise_dt).total_seconds()
    night_duration_seconds = (next_sunrise_dt - sunset_dt).total_seconds()
    day_chog_duration = day_duration_seconds / 8.0
    night_chog_duration = night_duration_seconds / 8.0
    
    day_sequence = DAY_CHOGHADIYA_SEQUENCE[weekday]
    night_sequence = NIGHT_CHOGHADIYA_SEQUENCE[weekday]
    
    day_choghadiyas = []
    for i, chog_type in enumerate(day_sequence):
        chog_start = sunrise_dt + timedelta(seconds=i * day_chog_duration)
        chog_end = sunrise_dt + timedelta(seconds=(i + 1) * day_chog_duration)
        chog_details = CHOGHADIYA_TYPES[chog_type]
        
        day_choghadiyas.append({
            "number": i + 1, "type": chog_type,
            "start": format_time(chog_start), "end": format_time(chog_end),
            "duration_minutes": round(day_chog_duration / 60, 2),
            "nature": chog_details["nature"], "quality": chog_details["quality"],
            "description": chog_details["description"],
            "best_for": chog_details.get("best_for", ""),
            "avoid": chog_details.get("avoid", ""),
            "deity": chog_details["deity"], "color": chog_details["color"]
        })
    
    night_choghadiyas = []
    for i, chog_type in enumerate(night_sequence):
        chog_start = sunset_dt + timedelta(seconds=i * night_chog_duration)
        chog_end = sunset_dt + timedelta(seconds=(i + 1) * night_chog_duration)
        chog_details = CHOGHADIYA_TYPES[chog_type]
        
        night_choghadiyas.append({
            "number": i + 1, "type": chog_type,
            "start": format_time(chog_start), "end": format_time(chog_end),
            "duration_minutes": round(night_chog_duration / 60, 2),
            "nature": chog_details["nature"], "quality": chog_details["quality"],
            "description": chog_details["description"],
            "best_for": chog_details.get("best_for", ""),
            "avoid": chog_details.get("avoid", ""),
            "deity": chog_details["deity"], "color": chog_details["color"]
        })
    
    return {
        "day_choghadiya": day_choghadiyas,
        "night_choghadiya": night_choghadiyas,
        "summary": {
            "day_duration_hours": round(day_duration_seconds / 3600, 2),
            "night_duration_hours": round(night_duration_seconds / 3600, 2),
            "day_choghadiya_minutes": round(day_chog_duration / 60, 2),
            "night_choghadiya_minutes": round(night_chog_duration / 60, 2),
            "calculation_method": "classical_gujarati_panchanga"
        }
    }

def get_current_choghadiya(current_dt: datetime.datetime, sunrise_dt: datetime.datetime,
                           sunset_dt: datetime.datetime, next_sunrise_dt: datetime.datetime,
                           weekday: int) -> Dict:
    """Get the CURRENT active Choghadiya"""
    
    if sunrise_dt <= current_dt < sunset_dt:
        is_day = True
        period_start = sunrise_dt
        period_end = sunset_dt
        duration = (sunset_dt - sunrise_dt).total_seconds()
        sequence = DAY_CHOGHADIYA_SEQUENCE[weekday]
    else:
        is_day = False
        period_start = sunset_dt
        period_end = next_sunrise_dt
        duration = (next_sunrise_dt - sunset_dt).total_seconds()
        sequence = NIGHT_CHOGHADIYA_SEQUENCE[weekday]
    
    chog_duration = duration / 8.0
    elapsed_seconds = (current_dt - period_start).total_seconds()
    
    if elapsed_seconds < 0:
        current_chog_num = 0
    else:
        current_chog_num = min(int(elapsed_seconds / chog_duration), 7)
    
    chog_type = sequence[current_chog_num]
    chog_details = CHOGHADIYA_TYPES[chog_type]
    chog_start = period_start + timedelta(seconds=current_chog_num * chog_duration)
    chog_end = period_start + timedelta(seconds=(current_chog_num + 1) * chog_duration)
    
    remaining_seconds = (chog_end - current_dt).total_seconds()
    elapsed_in_chog = (current_dt - chog_start).total_seconds()
    progress_percent = (elapsed_in_chog / chog_duration) * 100
    
    return {
        "current_choghadiya": {
            "period": "Day" if is_day else "Night",
            "number": current_chog_num + 1, "type": chog_type,
            "start": format_time(chog_start), "end": format_time(chog_end),
            "duration_minutes": round(chog_duration / 60, 2),
            "elapsed_minutes": round(elapsed_in_chog / 60, 2),
            "remaining_minutes": round(remaining_seconds / 60, 2),
            "progress_percent": round(progress_percent, 2),
            "nature": chog_details["nature"], "quality": chog_details["quality"],
            "description": chog_details["description"],
            "best_for": chog_details.get("best_for", ""),
            "avoid": chog_details.get("avoid", ""),
            "deity": chog_details["deity"], "color": chog_details["color"]
        }
    }

# ============================================================================
# HORA CALCULATIONS
# ============================================================================

def calculate_hora(sunrise_dt: datetime.datetime, 
                  sunset_dt: datetime.datetime,
                  next_sunrise_dt: datetime.datetime,
                  weekday: int) -> Dict:
    """Calculate all 24 Hora periods for the day and night"""
    
    print(f"\n⏰ Hora Calculation:")
    print(f"   Weekday: {weekday} (0=Sun, 1=Mon, ..., 6=Sat)")
    print(f"   Day Lord: {DAY_LORDS[weekday]}")
    
    day_duration_seconds = (sunset_dt - sunrise_dt).total_seconds()
    night_duration_seconds = (next_sunrise_dt - sunset_dt).total_seconds()
    
    day_hora_duration = day_duration_seconds / 12.0
    night_hora_duration = night_duration_seconds / 12.0
    
    print(f"   Day Hora: {day_hora_duration / 60:.2f} minutes each")
    print(f"   Night Hora: {night_hora_duration / 60:.2f} minutes each")
    
    day_lord = DAY_LORDS[weekday]
    start_index = CHALDEAN_ORDER.index(day_lord)
    
    day_horas = []
    for i in range(12):
        hora_start = sunrise_dt + timedelta(seconds=i * day_hora_duration)
        hora_end = sunrise_dt + timedelta(seconds=(i + 1) * day_hora_duration)
        
        planet_index = (start_index + i) % 7
        hora_lord = CHALDEAN_ORDER[planet_index]
        hora_details = HORA_LORDS[hora_lord]
        
        day_horas.append({
            "hora_number": i + 1,
            "absolute_hora": i + 1,
            "hora_lord": hora_lord,
            "sanskrit_name": hora_details["sanskrit_name"],
            "start": format_time(hora_start),
            "end": format_time(hora_end),
            "duration_minutes": round(day_hora_duration / 60, 2),
            "nature": hora_details["nature"],
            "quality": hora_details["quality"],
            "best_for": hora_details["best_for"],
            "avoid": hora_details["avoid"],
            "color": hora_details["color"],
            "rank": hora_details["rank"],
            "period": "Day"
        })
    
    night_start_index = (start_index + 12) % 7
    night_horas = []
    
    for i in range(12):
        hora_start = sunset_dt + timedelta(seconds=i * night_hora_duration)
        hora_end = sunset_dt + timedelta(seconds=(i + 1) * night_hora_duration)
        
        planet_index = (night_start_index + i) % 7
        hora_lord = CHALDEAN_ORDER[planet_index]
        hora_details = HORA_LORDS[hora_lord]
        
        night_horas.append({
            "hora_number": i + 1,
            "absolute_hora": i + 13,
            "hora_lord": hora_lord,
            "sanskrit_name": hora_details["sanskrit_name"],
            "start": format_time(hora_start),
            "end": format_time(hora_end),
            "duration_minutes": round(night_hora_duration / 60, 2),
            "nature": hora_details["nature"],
            "quality": hora_details["quality"],
            "best_for": hora_details["best_for"],
            "avoid": hora_details["avoid"],
            "color": hora_details["color"],
            "rank": hora_details["rank"],
            "period": "Night"
        })
    
    print(f"   ✓ Calculated 24 Horas (12 day + 12 night)")
    
    return {
        "day_hora": day_horas,
        "night_hora": night_horas,
        "summary": {
            "day_lord": day_lord,
            "day_duration_hours": round(day_duration_seconds / 3600, 2),
            "night_duration_hours": round(night_duration_seconds / 3600, 2),
            "day_hora_minutes": round(day_hora_duration / 60, 2),
            "night_hora_minutes": round(night_hora_duration / 60, 2),
            "chaldean_order": CHALDEAN_ORDER,
            "calculation_method": "classical_vedic_hora"
        }
    }

def get_current_hora(current_dt: datetime.datetime,
                    sunrise_dt: datetime.datetime,
                    sunset_dt: datetime.datetime,
                    next_sunrise_dt: datetime.datetime,
                    weekday: int) -> Dict:
    """Get the CURRENT active Hora for a given time"""
    
    if sunrise_dt <= current_dt < sunset_dt:
        is_day = True
        period_start = sunrise_dt
        period_end = sunset_dt
        duration = (sunset_dt - sunrise_dt).total_seconds()
        base_hora = 0
    else:
        is_day = False
        period_start = sunset_dt
        period_end = next_sunrise_dt
        duration = (next_sunrise_dt - sunset_dt).total_seconds()
        base_hora = 12
    
    hora_duration = duration / 12.0
    elapsed_seconds = (current_dt - period_start).total_seconds()
    
    if elapsed_seconds < 0:
        hora_number_in_period = 0
    else:
        hora_number_in_period = min(int(elapsed_seconds / hora_duration), 11)
    
    absolute_hora = base_hora + hora_number_in_period + 1
    
    day_lord = DAY_LORDS[weekday]
    start_index = CHALDEAN_ORDER.index(day_lord)
    
    planet_index = (start_index + (absolute_hora - 1)) % 7
    hora_lord = CHALDEAN_ORDER[planet_index]
    hora_details = HORA_LORDS[hora_lord]
    
    hora_start = period_start + timedelta(seconds=hora_number_in_period * hora_duration)
    hora_end = period_start + timedelta(seconds=(hora_number_in_period + 1) * hora_duration)
    
    remaining_seconds = (hora_end - current_dt).total_seconds()
    elapsed_in_hora = (current_dt - hora_start).total_seconds()
    progress_percent = (elapsed_in_hora / hora_duration) * 100
    
    if hora_details["rank"] <= 2:
        recommendation = "Excellent time for " + hora_details["best_for"].split(',')[0]
    elif hora_details["rank"] <= 4:
        recommendation = "Good for specific activities - check suitability"
    else:
        recommendation = "Generally avoid important activities - " + hora_details["avoid"].split(',')[0]
    
    return {
        "current_hora": {
            "hora_number": hora_number_in_period + 1,
            "absolute_hora": absolute_hora,
            "period": "Day" if is_day else "Night",
            "hora_lord": hora_lord,
            "sanskrit_name": hora_details["sanskrit_name"],
            "start": format_time(hora_start),
            "end": format_time(hora_end),
            "duration_minutes": round(hora_duration / 60, 2),
            "elapsed_minutes": round(elapsed_in_hora / 60, 2),
            "remaining_minutes": round(remaining_seconds / 60, 2),
            "progress_percent": round(progress_percent, 2),
            "nature": hora_details["nature"],
            "quality": hora_details["quality"],
            "best_for": hora_details["best_for"],
            "avoid": hora_details["avoid"],
            "color": hora_details["color"],
            "rank": hora_details["rank"],
            "recommendation": recommendation
        }
    }

# ============================================================================
# LAGNA (ASCENDANT) CALCULATIONS
# ============================================================================

def calculate_lagna(date_str: str, time_str: str, latitude: float, 
                   longitude: float, timezone_str: str) -> Dict:
    """Calculate Lagna (Ascendant) and all 12 house cusps"""
    
    if not os.path.exists(SWISS_EPHE_PATH):
        os.makedirs(SWISS_EPHE_PATH, exist_ok=True)
    
    swe.set_ephe_path(SWISS_EPHE_PATH)
    swe.set_sid_mode(LAHIRI_AYANAMSA)
    
    print(f"\n🎯 Lagna Calculation:")
    print(f"   Date: {date_str}, Time: {time_str}")
    print(f"   Location: {latitude}°N, {longitude}°E")
    
    tz = pytz.timezone(timezone_str)
    dt_str = f"{date_str} {time_str}"
    dt_local = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    dt_local = tz.localize(dt_local)
    dt_utc = dt_local.astimezone(pytz.UTC)
    
    print(f"   UTC: {dt_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    
    jd = swe.julday(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
    )
    
    print(f"   Julian Day: {jd:.6f}")
    
    try:
        cusps, ascmc = swe.houses(jd, latitude, longitude, b'P')
        
        print(f"   ✓ House calculation successful")
        print(f"   Cusps: {len(cusps)} elements, ASCMC: {len(ascmc)} elements")
        
        if len(cusps) < 13:
            print(f"   ⚠️ Warning: Expected 13 cusps, got {len(cusps)}")
            cusps = list(cusps)
        
        if len(ascmc) < 2:
            raise ValueError(f"ASCMC has insufficient elements: {len(ascmc)}")
            
    except Exception as e:
        print(f"   ⚠️ Placidus calculation issue: {e}")
        print(f"   Trying Whole Sign houses as fallback...")
        
        try:
            cusps, ascmc = swe.houses(jd, latitude, longitude, b'W')
            print(f"   ✓ Whole Sign calculation successful")
        except Exception as e2:
            print(f"   ❌ Whole Sign also failed: {e2}")
            raise ValueError(f"All house calculation methods failed. Original error: {e}, Fallback error: {e2}")
    
    try:
        tropical_asc = ascmc[0]
    except (IndexError, TypeError) as e:
        raise ValueError(f"Cannot access Ascendant from ASCMC: {e}. ASCMC content: {ascmc}")
    
    ayanamsa = swe.get_ayanamsa_ut(jd)
    
    print(f"   Tropical Ascendant: {tropical_asc:.6f}°")
    print(f"   Ayanamsa (Lahiri): {ayanamsa:.6f}°")
    
    sidereal_asc = (tropical_asc - ayanamsa) % 360
    
    print(f"   Sidereal Ascendant: {sidereal_asc:.6f}°")
    
    rashi_num = int(sidereal_asc / 30) + 1
    degree_in_rashi = sidereal_asc % 30
    
    rashi_details = RASHI_DATABASE[rashi_num]
    
    print(f"   Lagna Rashi: {rashi_details['name']} ({rashi_details['sanskrit_name']})")
    print(f"   Degree in Rashi: {degree_in_rashi:.4f}°")
    
    degrees = int(degree_in_rashi)
    minutes = int((degree_in_rashi - degrees) * 60)
    seconds = int(((degree_in_rashi - degrees) * 60 - minutes) * 60)
    
    nak_num = int(sidereal_asc / 13.333333) + 1
    if nak_num > 27:
        nak_num = 27
    
    nak_pada = int((sidereal_asc % 13.333333) / 3.333333) + 1
    
    lagna_nakshatra = NAKSHATRAS[nak_num - 1]
    
    print(f"   Lagna Nakshatra: {lagna_nakshatra} Pada {nak_pada}")
    
    house_cusps_sidereal = {}
    
    print(f"   Calculating {len(cusps)-1} house cusps...")
    
    for i in range(1, 13):
        try:
            if i < len(cusps):
                tropical_cusp = cusps[i]
            else:
                print(f"   ⚠️ Cusp {i} not available, using Equal House method")
                tropical_cusp = (tropical_asc + (i-1) * 30) % 360
            
            sidereal_cusp = (tropical_cusp - ayanamsa) % 360
            cusp_rashi = int(sidereal_cusp / 30) + 1
            cusp_degree = sidereal_cusp % 30
            
            house_cusps_sidereal[f"house_{i}"] = {
                "cusp_degree": round(sidereal_cusp, 4),
                "rashi_number": cusp_rashi,
                "rashi_name": RASHI_DATABASE[cusp_rashi]["name"],
                "degree_in_rashi": round(cusp_degree, 4),
                "signification": HOUSE_SIGNIFICATIONS[i]
            }
            
            if i <= 3:
                print(f"   House {i}: {RASHI_DATABASE[cusp_rashi]['name']} {cusp_degree:.2f}°")
                
        except (IndexError, KeyError, TypeError) as e:
            print(f"   ⚠️ Error accessing cusp {i}: {e}")
            tropical_cusp = (tropical_asc + (i-1) * 30) % 360
            sidereal_cusp = (tropical_cusp - ayanamsa) % 360
            cusp_rashi = int(sidereal_cusp / 30) + 1
            cusp_degree = sidereal_cusp % 30
            
            house_cusps_sidereal[f"house_{i}"] = {
                "cusp_degree": round(sidereal_cusp, 4),
                "rashi_number": cusp_rashi,
                "rashi_name": RASHI_DATABASE[cusp_rashi]["name"],
                "degree_in_rashi": round(cusp_degree, 4),
                "signification": HOUSE_SIGNIFICATIONS[i],
                "note": "Calculated using Equal House fallback"
            }
    
    try:
        mc_tropical = ascmc[1] if len(ascmc) > 1 else (tropical_asc + 270) % 360
    except:
        mc_tropical = (tropical_asc + 270) % 360
        
    mc_sidereal = (mc_tropical - ayanamsa) % 360
    mc_rashi = int(mc_sidereal / 30) + 1
    
    descendant_sidereal = (sidereal_asc + 180) % 360
    desc_rashi = int(descendant_sidereal / 30) + 1
    
    ic_sidereal = (mc_sidereal + 180) % 360
    ic_rashi = int(ic_sidereal / 30) + 1
    
    print(f"   ✓ Lagna calculation complete")
    
    return {
        "lagna": {
            "rashi_number": rashi_num,
            "rashi_name": rashi_details["name"],
            "sanskrit_name": rashi_details["sanskrit_name"],
            "lord": rashi_details["lord"],
            "element": rashi_details["element"],
            "quality": rashi_details["quality"],
            "absolute_degree": round(sidereal_asc, 6),
            "degree_in_rashi": round(degree_in_rashi, 6),
            "dms": f"{degrees}° {minutes}' {seconds}\"",
            "nakshatra": lagna_nakshatra,
            "nakshatra_number": nak_num,
            "nakshatra_pada": nak_pada,
            "nature": rashi_details["nature"],
            "body_parts": rashi_details["body_parts"],
            "characteristics": rashi_details["characteristics"],
            "best_for": rashi_details["best_for"],
            "avoid_for": rashi_details["avoid_for"]
        },
        "house_cusps": house_cusps_sidereal,
        "special_points": {
            "ascendant": {
                "degree": round(sidereal_asc, 4),
                "rashi": rashi_details["name"],
                "description": "1st House - Self, Personality, Physical Body"
            },
            "midheaven": {
                "degree": round(mc_sidereal, 4),
                "rashi": RASHI_DATABASE[mc_rashi]["name"],
                "description": "10th House - Career, Status, Public Life"
            },
            "descendant": {
                "degree": round(descendant_sidereal, 4),
                "rashi": RASHI_DATABASE[desc_rashi]["name"],
                "description": "7th House - Spouse, Partnerships, Marriage"
            },
            "imum_coeli": {
                "degree": round(ic_sidereal, 4),
                "rashi": RASHI_DATABASE[ic_rashi]["name"],
                "description": "4th House - Home, Mother, Inner Peace"
            }
        },
        "technical_data": {
            "tropical_ascendant": round(tropical_asc, 6),
            "ayanamsa_lahiri": round(ayanamsa, 6),
            "julian_day": round(jd, 6),
            "house_system": "Placidus",
            "ayanamsa_system": "Lahiri",
            "calculation_method": "swiss_ephemeris_sidereal"
        }
    }

def calculate_sunrise_sunset(date_str: str, latitude: float, longitude: float, 
                            timezone_str: str) -> Dict:
    """Calculate exact sunrise and sunset times using Skyfield"""
    
    if not SKYFIELD_AVAILABLE:
        print("   ⚠️  Skyfield not available, using approximate sunrise")
        tz = pytz.timezone(timezone_str)
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        date_obj = tz.localize(date_obj)
        
        sunrise_approx = date_obj.replace(hour=6, minute=40, second=0)
        sunset_approx = date_obj.replace(hour=18, minute=0, second=0)
        
        return {
            "sunrise": sunrise_approx,
            "sunset": sunset_approx,
            "method": "approximate"
        }
    
    from skyfield import api as sky_api
    from skyfield import almanac
    
    ts = sky_api.load.timescale()
    eph = sky_api.load('de421.bsp')
    
    location = sky_api.wgs84.latlon(latitude, longitude)
    
    tz = pytz.timezone(timezone_str)
    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    date_obj = tz.localize(date_obj)
    
    t0 = ts.from_datetime(date_obj.replace(hour=0, minute=0, second=0))
    t1 = ts.from_datetime(date_obj.replace(hour=23, minute=59, second=59))
    
    f = almanac.sunrise_sunset(eph, location)
    times, events = almanac.find_discrete(t0, t1, f)
    
    sunrise_time = None
    sunset_time = None
    
    for time, event in zip(times, events):
        dt = time.utc_datetime().replace(tzinfo=pytz.UTC).astimezone(tz)
        if event == 1:
            sunrise_time = dt
        elif event == 0:
            sunset_time = dt
    
    return {
        "sunrise": sunrise_time,
        "sunset": sunset_time,
        "method": "skyfield_accurate"
    }

def calculate_lagna_timings_vedic(date_str: str, latitude: float, longitude: float, 
                                  timezone_str: str) -> Dict:
    """Calculate EXACT Lagna timings from SUNRISE to SUNRISE (Vedic day)"""
    
    if not os.path.exists(SWISS_EPHE_PATH):
        os.makedirs(SWISS_EPHE_PATH, exist_ok=True)
    
    swe.set_ephe_path(SWISS_EPHE_PATH)
    swe.set_sid_mode(LAHIRI_AYANAMSA)
    
    print(f"\n🌅 Calculating Lagna Timings (Vedic Day: Sunrise to Sunrise):")
    print(f"   Date: {date_str}")
    print(f"   Location: {latitude}°N, {longitude}°E")
    print(f"   Timezone: {timezone_str}")
    
    tz = pytz.timezone(timezone_str)
    
    print(f"   Calculating sunrise times...")
    
    today_sun = calculate_sunrise_sunset(date_str, latitude, longitude, timezone_str)
    sunrise_today = today_sun["sunrise"]
    
    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    next_date = date_obj + timedelta(days=1)
    next_date_str = next_date.strftime('%Y-%m-%d')
    
    tomorrow_sun = calculate_sunrise_sunset(next_date_str, latitude, longitude, timezone_str)
    sunrise_tomorrow = tomorrow_sun["sunrise"]
    
    print(f"   Sunrise today: {sunrise_today.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Sunrise tomorrow: {sunrise_tomorrow.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Vedic day duration: {(sunrise_tomorrow - sunrise_today).total_seconds() / 3600:.2f} hours")
    
    scan_start = sunrise_today - timedelta(hours=1)
    scan_end = sunrise_tomorrow + timedelta(hours=1)
    
    print(f"   Scan range: {scan_start.strftime('%H:%M')} to {scan_end.strftime('%Y-%m-%d %H:%M')}")
    
    all_transitions = []
    
    current_dt = scan_start
    increment = timedelta(minutes=3)
    
    prev_lagna = None
    prev_dt = None
    
    print(f"   Scanning for Lagna changes...")
    
    scan_count = 0
    while current_dt <= scan_end:
        try:
            dt_utc = current_dt.astimezone(pytz.UTC)
            jd = swe.julday(
                dt_utc.year, dt_utc.month, dt_utc.day,
                dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
            )
            
            cusps, ascmc = swe.houses(jd, latitude, longitude, b'P')
            tropical_asc = ascmc[0]
            ayanamsa = swe.get_ayanamsa_ut(jd)
            sidereal_asc = (tropical_asc - ayanamsa) % 360
            
            lagna_num = int(sidereal_asc / 30) + 1
            
            if prev_lagna is None:
                prev_lagna = lagna_num
                prev_dt = current_dt
            elif lagna_num != prev_lagna:
                if scan_count < 5:
                    print(f"   Transition: {RASHI_DATABASE[prev_lagna]['name']} → {RASHI_DATABASE[lagna_num]['name']}")
                
                search_start = current_dt - increment
                search_end = current_dt
                
                transition_count = 0
                while (search_end - search_start).total_seconds() > 1 and transition_count < 20:
                    mid_dt = search_start + (search_end - search_start) / 2
                    
                    mid_utc = mid_dt.astimezone(pytz.UTC)
                    mid_jd = swe.julday(
                        mid_utc.year, mid_utc.month, mid_utc.day,
                        mid_utc.hour + mid_utc.minute/60.0 + mid_utc.second/3600.0
                    )
                    
                    mid_cusps, mid_ascmc = swe.houses(mid_jd, latitude, longitude, b'P')
                    mid_tropical = mid_ascmc[0]
                    mid_ayanamsa = swe.get_ayanamsa_ut(mid_jd)
                    mid_sidereal = (mid_tropical - mid_ayanamsa) % 360
                    mid_lagna = int(mid_sidereal / 30) + 1
                    
                    if mid_lagna == prev_lagna:
                        search_start = mid_dt
                    else:
                        search_end = mid_dt
                    
                    transition_count += 1
                
                transition_time = search_end
                
                all_transitions.append({
                    "lagna_number": prev_lagna,
                    "lagna_name": RASHI_DATABASE[prev_lagna]["name"],
                    "start_datetime": prev_dt,
                    "end_datetime": transition_time
                })
                
                prev_lagna = lagna_num
                prev_dt = transition_time
                scan_count += 1
            
        except Exception as e:
            print(f"   Warning at {current_dt.strftime('%H:%M:%S')}: {e}")
        
        current_dt += increment
    
    if prev_lagna is not None:
        all_transitions.append({
            "lagna_number": prev_lagna,
            "lagna_name": RASHI_DATABASE[prev_lagna]["name"],
            "start_datetime": prev_dt,
            "end_datetime": scan_end
        })
    
    print(f"   Found {len(all_transitions)} Lagna periods in extended scan")
    
    filtered_lagnas = []
    
    for lagna_period in all_transitions:
        start_dt = lagna_period["start_datetime"]
        end_dt = lagna_period["end_datetime"]
        
        if end_dt > sunrise_today and start_dt < sunrise_tomorrow:
            display_start = start_dt if start_dt >= sunrise_today else sunrise_today
            display_end = end_dt if end_dt <= sunrise_tomorrow else sunrise_tomorrow
            
            duration_seconds = (display_end - display_start).total_seconds()
            duration_minutes = duration_seconds / 60.0
            
            def format_vedic_time(dt, reference_date):
                time_str = dt.strftime('%H:%M:%S')
                
                if dt.date() > reference_date:
                    hours_from_midnight = dt.hour
                    total_hours = 24 + hours_from_midnight
                    vedic_time = f"{total_hours:02d}:{dt.strftime('%M:%S')}"
                    return vedic_time, time_str
                else:
                    return time_str, time_str
            
            reference_date = sunrise_today.date()
            start_vedic, start_standard = format_vedic_time(display_start, reference_date)
            end_vedic, end_standard = format_vedic_time(display_end, reference_date)
            
            lagna_details = RASHI_DATABASE[lagna_period["lagna_number"]]
            
            lagna_info = {
                "lagna_number": lagna_period["lagna_number"],
                "lagna_name": lagna_period["lagna_name"],
                "sanskrit_name": lagna_details["sanskrit_name"],
                "lord": lagna_details["lord"],
                "element": lagna_details["element"],
                "quality": lagna_details["quality"],
                "start_time": start_standard,
                "end_time": end_standard,
                "start_time_vedic": start_vedic,
                "end_time_vedic": end_vedic,
                "duration_minutes": round(duration_minutes, 2),
                "duration_hours": round(duration_minutes / 60, 2),
                "best_for": lagna_details["best_for"],
                "avoid_for": lagna_details["avoid_for"],
                "characteristics": lagna_details["characteristics"]
            }
            
            if display_start.date() > reference_date:
                lagna_info["note"] = "Next calendar day (same Vedic day)"
            if start_dt < sunrise_today:
                lagna_info["note"] = f"Started before sunrise at {start_dt.strftime('%H:%M:%S')}"
            if end_dt > sunrise_tomorrow:
                lagna_info["note"] = f"Continues past next sunrise"
            
            filtered_lagnas.append(lagna_info)
    
    print(f"   Filtered to {len(filtered_lagnas)} Lagnas for Vedic day")
    
    total_duration = sum([lagna["duration_minutes"] for lagna in filtered_lagnas])
    expected_duration = (sunrise_tomorrow - sunrise_today).total_seconds() / 60.0
    
    print(f"   Total duration: {total_duration:.2f} minutes ({total_duration/60:.2f} hours)")
    print(f"   Expected: {expected_duration:.2f} minutes ({expected_duration/60:.2f} hours)")
    
    if abs(total_duration - expected_duration) > 1:
        print(f"   ⚠️  WARNING: Duration mismatch by {abs(total_duration - expected_duration):.2f} minutes")
    else:
        print(f"   ✓ Duration validation passed")
    
    avg_duration = total_duration / len(filtered_lagnas) if filtered_lagnas else 0
    min_duration = min([ls["duration_minutes"] for ls in filtered_lagnas]) if filtered_lagnas else 0
    max_duration = max([ls["duration_minutes"] for ls in filtered_lagnas]) if filtered_lagnas else 0
    
    return {
        "lagna_schedule": filtered_lagnas,
        "vedic_day": {
            "date": date_str,
            "sunrise_today": sunrise_today.strftime('%Y-%m-%d %H:%M:%S'),
            "sunrise_tomorrow": sunrise_tomorrow.strftime('%Y-%m-%d %H:%M:%S'),
            "day_type": "Vedic Day (Sunrise to Sunrise)",
            "duration_hours": round(expected_duration / 60, 2)
        },
        "summary": {
            "total_lagnas": len(filtered_lagnas),
            "total_duration_minutes": round(total_duration, 2),
            "total_duration_hours": round(total_duration / 60, 2),
            "average_duration_minutes": round(avg_duration, 2),
            "minimum_duration_minutes": round(min_duration, 2),
            "maximum_duration_minutes": round(max_duration, 2),
            "latitude": latitude,
            "longitude": longitude,
            "calculation_method": "Vedic (Sunrise to Sunrise)"
        }
    }

def get_current_lagna_timing(date_str: str, time_str: str, latitude: float,
                             longitude: float, timezone_str: str) -> Dict:
    """Get current Lagna with its timing within Vedic day (sunrise to sunrise)"""
    
    full_schedule = calculate_lagna_timings_vedic(date_str, latitude, longitude, timezone_str)
    
    tz = pytz.timezone(timezone_str)
    dt_str = f"{date_str} {time_str}"
    current_dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    current_dt = tz.localize(current_dt)
    
    current_lagna_info = None
    next_lagna_info = None
    
    for i, lagna in enumerate(full_schedule["lagna_schedule"]):
        start_time_str = lagna["start_time"]
        end_time_str = lagna["end_time"]
        
        start_time_parts = start_time_str.split(':')
        end_time_parts = end_time_str.split(':')
        
        start_dt = current_dt.replace(
            hour=int(start_time_parts[0]),
            minute=int(start_time_parts[1]),
            second=int(start_time_parts[2])
        )
        
        end_dt = current_dt.replace(
            hour=int(end_time_parts[0]),
            minute=int(end_time_parts[1]),
            second=int(end_time_parts[2])
        )
        
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)
        
        if start_dt <= current_dt < end_dt:
            current_lagna_info = lagna.copy()
            
            elapsed_seconds = (current_dt - start_dt).total_seconds()
            remaining_seconds = (end_dt - current_dt).total_seconds()
            total_seconds = (end_dt - start_dt).total_seconds()
            
            progress_percent = (elapsed_seconds / total_seconds * 100) if total_seconds > 0 else 0
            
            current_lagna_info["elapsed_minutes"] = round(elapsed_seconds / 60, 2)
            current_lagna_info["remaining_minutes"] = round(remaining_seconds / 60, 2)
            current_lagna_info["progress_percent"] = round(progress_percent, 2)
            
            if i < len(full_schedule["lagna_schedule"]) - 1:
                next_lagna_info = full_schedule["lagna_schedule"][i + 1]
            
            break
    
    if not current_lagna_info:
        return {
            "error": "Could not determine current Lagna",
            "full_schedule": full_schedule
        }
    
    return {
        "current_lagna": current_lagna_info,
        "next_lagna": next_lagna_info if next_lagna_info else {
            "note": "No more Lagna changes in this Vedic day"
        },
        "vedic_day_info": full_schedule["vedic_day"],
        "full_day_schedule": full_schedule["lagna_schedule"]
    }

