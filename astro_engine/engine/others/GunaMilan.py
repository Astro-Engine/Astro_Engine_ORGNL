"""
Guna Milan (Ashtakoot) Calculations Module
All astronomical and astrological calculations for Vedic compatibility
"""

from datetime import datetime, timedelta
import swisseph as swe
import os

# Set Swiss Ephemeris path
EPHE_PATH = os.path.join(os.path.dirname(__file__), 'ephe')
swe.set_ephe_path(EPHE_PATH)

# Constants
LAHIRI_AYANAMSA = swe.SIDM_LAHIRI

# Nakshatra names (1-27)
NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Rashi names (1-12)
RASHI_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# ==================== NAKSHATRA PROPERTIES ====================

# Varna classification (Nakshatra: 1-27)
VARNA_MAP = {
    1: "Brahmin", 5: "Brahmin", 7: "Brahmin", 8: "Brahmin", 13: "Brahmin",
    15: "Brahmin", 17: "Brahmin", 22: "Brahmin", 27: "Brahmin",
    2: "Kshatriya", 4: "Kshatriya", 9: "Kshatriya", 10: "Kshatriya",
    11: "Kshatriya", 16: "Kshatriya", 20: "Kshatriya", 23: "Kshatriya", 25: "Kshatriya",
    3: "Vaishya", 6: "Vaishya", 12: "Vaishya", 14: "Vaishya",
    18: "Vaishya", 21: "Vaishya", 24: "Vaishya", 26: "Vaishya",
    19: "Shudra"
}

VARNA_ORDER = {"Brahmin": 4, "Kshatriya": 3, "Vaishya": 2, "Shudra": 1}

# Vashya classification by Rashi (1-12)
VASHYA_MAP = {
    1: "Quadruped",    # Aries
    2: "Quadruped",    # Taurus
    3: "Human",        # Gemini
    4: "Aquatic",      # Cancer
    5: "Quadruped",    # Leo (special case)
    6: "Human",        # Virgo
    7: "Human",        # Libra
    8: "Insect",       # Scorpio
    9: "Human",        # Sagittarius (first half), but treated as Human generally
    10: "Aquatic",     # Capricorn
    11: "Human",       # Aquarius
    12: "Aquatic"      # Pisces
}

# Gana classification (Nakshatra: 1-27)
GANA_MAP = {
    1: "Deva", 5: "Deva", 7: "Deva", 8: "Deva", 13: "Deva",
    15: "Deva", 17: "Deva", 22: "Deva", 27: "Deva",
    2: "Manushya", 4: "Manushya", 6: "Manushya", 11: "Manushya",
    12: "Manushya", 20: "Manushya", 21: "Manushya", 25: "Manushya", 26: "Manushya",
    3: "Rakshasa", 9: "Rakshasa", 10: "Rakshasa", 14: "Rakshasa",
    16: "Rakshasa", 18: "Rakshasa", 19: "Rakshasa", 23: "Rakshasa", 24: "Rakshasa"
}

# Nadi classification (Nakshatra: 1-27)
NADI_MAP = {
    1: "Aadi", 6: "Aadi", 7: "Aadi", 12: "Aadi", 13: "Aadi",
    18: "Aadi", 19: "Aadi", 24: "Aadi", 26: "Aadi",
    2: "Madhya", 5: "Madhya", 8: "Madhya", 11: "Madhya", 14: "Madhya",
    17: "Madhya", 20: "Madhya", 23: "Madhya", 25: "Madhya",
    3: "Antya", 4: "Antya", 9: "Antya", 10: "Antya", 15: "Antya",
    16: "Antya", 21: "Antya", 22: "Antya", 27: "Antya"
}

# Yoni classification (Nakshatra: 1-27) - [Animal, Gender]
YONI_MAP = {
    1: ["Horse", "M"], 2: ["Elephant", "M"], 3: ["Sheep", "F"], 4: ["Serpent", "M"],
    5: ["Serpent", "F"], 6: ["Dog", "F"], 7: ["Cat", "F"], 8: ["Sheep", "M"],
    9: ["Cat", "M"], 10: ["Rat", "M"], 11: ["Rat", "F"], 12: ["Cow", "M"],
    13: ["Buffalo", "F"], 14: ["Tiger", "F"], 15: ["Buffalo", "M"], 16: ["Tiger", "M"],
    17: ["Deer", "F"], 18: ["Deer", "M"], 19: ["Dog", "M"], 20: ["Monkey", "M"],
    21: ["Mongoose", "M"], 22: ["Monkey", "F"], 23: ["Lion", "F"], 24: ["Horse", "F"],
    25: ["Lion", "M"], 26: ["Cow", "F"], 27: ["Elephant", "F"]
}

# Yoni enmity - 0 points for these combinations
YONI_ENEMIES = {
    ("Cat", "Rat"), ("Rat", "Cat"),
    ("Dog", "Deer"), ("Deer", "Dog"),
    ("Serpent", "Mongoose"), ("Mongoose", "Serpent"),
    ("Horse", "Buffalo"), ("Buffalo", "Horse"),
    ("Cow", "Tiger"), ("Tiger", "Cow"),
    ("Lion", "Elephant"), ("Elephant", "Lion"),
    ("Monkey", "Sheep"), ("Sheep", "Monkey")
}

# Rashi lords (1-12)
RASHI_LORDS = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
}

# Planetary natural relationships
PLANETARY_RELATIONS = {
    "Sun": {"friends": ["Moon", "Mars", "Jupiter"], "enemies": ["Venus", "Saturn"], "neutral": ["Mercury"]},
    "Moon": {"friends": ["Sun", "Mercury"], "enemies": [], "neutral": ["Mars", "Jupiter", "Venus", "Saturn"]},
    "Mars": {"friends": ["Sun", "Moon", "Jupiter"], "enemies": ["Mercury"], "neutral": ["Venus", "Saturn"]},
    "Mercury": {"friends": ["Sun", "Venus"], "enemies": ["Moon"], "neutral": ["Mars", "Jupiter", "Saturn"]},
    "Jupiter": {"friends": ["Sun", "Moon", "Mars"], "enemies": ["Mercury", "Venus"], "neutral": ["Saturn"]},
    "Venus": {"friends": ["Mercury", "Saturn"], "enemies": ["Sun", "Moon"], "neutral": ["Mars", "Jupiter"]},
    "Saturn": {"friends": ["Mercury", "Venus"], "enemies": ["Sun", "Moon", "Mars"], "neutral": ["Jupiter"]}
}


# ==================== ASTRONOMICAL CALCULATIONS ====================

def calculate_julian_day_ut(date_str, time_str, timezone_offset):
    """
    Calculate Julian Day in Universal Time (UT)
    
    Args:
        date_str: Date in format "YYYY-MM-DD"
        time_str: Time in format "HH:MM:SS"
        timezone_offset: Timezone offset in hours (e.g., 5.5 for IST)
    
    Returns:
        Julian Day Number in UT
    """
    # Parse local date and time
    dt_local = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    
    # Convert to UTC by subtracting timezone offset
    dt_utc = dt_local - timedelta(hours=timezone_offset)
    
    # Extract components
    year = dt_utc.year
    month = dt_utc.month
    day = dt_utc.day
    hour = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    
    # Calculate Julian Day
    jd = swe.julday(year, month, day, hour)
    
    return jd


def calculate_ascendant(jd, latitude, longitude):
    """
    Calculate Ascendant (Lagna) using Swiss Ephemeris
    
    Args:
        jd: Julian Day in UT
        latitude: Birth latitude in degrees
        longitude: Birth longitude in degrees
    
    Returns:
        Sidereal Ascendant longitude in degrees (0-360)
    """
    # Set ayanamsa
    swe.set_sid_mode(LAHIRI_AYANAMSA)
    
    # Calculate houses using Whole Sign house system
    # For Vedic, we use sidereal mode
    cusps, ascmc = swe.houses_ex(jd, float(latitude), float(longitude), b'W', swe.FLG_SIDEREAL)
    
    # ascmc[0] contains the Ascendant
    ascendant = ascmc[0]
    
    # Normalize to 0-360
    ascendant = ascendant % 360
    
    return ascendant


def get_planet_position_sidereal(jd, planet_id):
    """
    Get sidereal position of a planet
    
    Args:
        jd: Julian Day in UT
        planet_id: Swiss Ephemeris planet constant (e.g., swe.MOON, swe.SUN)
    
    Returns:
        Sidereal longitude in degrees (0-360)
    """
    # Set ayanamsa to Lahiri
    swe.set_sid_mode(LAHIRI_AYANAMSA)
    
    # Calculate planet position in sidereal zodiac
    result = swe.calc_ut(jd, planet_id, swe.FLG_SIDEREAL)
    
    # result[0][0] contains the longitude
    longitude = result[0][0]
    
    # Normalize to 0-360
    longitude = longitude % 360
    
    return longitude


def get_nakshatra_and_pada(longitude):
    """
    Calculate Nakshatra number (1-27) and Pada (1-4) from longitude
    
    Logic:
    - 360 degrees divided into 27 nakshatras
    - Each nakshatra spans 13°20' (13.333... degrees)
    - Each nakshatra has 4 padas of 3°20' (3.333... degrees) each
    
    Args:
        longitude: Sidereal longitude in degrees (0-360)
    
    Returns:
        Tuple of (nakshatra_number, pada_number)
    """
    # Each nakshatra spans 360/27 degrees
    nakshatra_span = 360.0 / 27.0  # 13.333...
    
    # Calculate nakshatra number (1-27)
    nakshatra_num = int(longitude / nakshatra_span) + 1
    
    # Handle edge case at 360 degrees
    if nakshatra_num > 27:
        nakshatra_num = 27
    
    # Calculate position within the nakshatra
    position_in_nakshatra = longitude % nakshatra_span
    
    # Each pada spans nakshatra_span/4 degrees
    pada_span = nakshatra_span / 4.0  # 3.333...
    
    # Calculate pada number (1-4)
    pada = int(position_in_nakshatra / pada_span) + 1
    
    # Handle edge case
    if pada > 4:
        pada = 4
    
    return nakshatra_num, pada


def get_rashi(longitude):
    """
    Calculate Rashi (sign) number from longitude
    
    Logic:
    - 360 degrees divided into 12 rashis
    - Each rashi spans 30 degrees
    
    Args:
        longitude: Sidereal longitude in degrees (0-360)
    
    Returns:
        Rashi number (1-12)
    """
    # Each rashi spans 30 degrees
    rashi_num = int(longitude / 30.0) + 1
    
    # Handle edge case at 360 degrees
    if rashi_num > 12:
        rashi_num = 12
    
    return rashi_num


def calculate_birth_details(birth_data):
    """
    Calculate complete birth details including Ascendant, Moon nakshatra, pada, and rashi
    
    Args:
        birth_data: Dictionary containing:
            - birth_date: "YYYY-MM-DD"
            - birth_time: "HH:MM:SS"
            - latitude: decimal degrees
            - longitude: decimal degrees
            - timezone_offset: hours (e.g., 5.5 for IST)
    
    Returns:
        Dictionary with calculated astrological details
    """
    # Calculate Julian Day in UT
    jd = calculate_julian_day_ut(
        birth_data['birth_date'],
        birth_data['birth_time'],
        birth_data['timezone_offset']
    )
    
    # Calculate Ascendant (Lagna)
    ascendant_long = calculate_ascendant(
        jd,
        birth_data['latitude'],
        birth_data['longitude']
    )
    ascendant_rashi = get_rashi(ascendant_long)
    ascendant_nakshatra, ascendant_pada = get_nakshatra_and_pada(ascendant_long)
    
    # Calculate Moon position
    moon_long = get_planet_position_sidereal(jd, swe.MOON)
    moon_nakshatra, moon_pada = get_nakshatra_and_pada(moon_long)
    moon_rashi = get_rashi(moon_long)
    
    return {
        'ascendant': {
            'longitude': round(ascendant_long, 6),
            'rashi': ascendant_rashi,
            'rashi_name': RASHI_NAMES[ascendant_rashi - 1],
            'nakshatra': ascendant_nakshatra,
            'nakshatra_name': NAKSHATRA_NAMES[ascendant_nakshatra - 1],
            'pada': ascendant_pada
        },
        'moon': {
            'longitude': round(moon_long, 6),
            'nakshatra': moon_nakshatra,
            'nakshatra_name': NAKSHATRA_NAMES[moon_nakshatra - 1],
            'pada': moon_pada,
            'rashi': moon_rashi,
            'rashi_name': RASHI_NAMES[moon_rashi - 1]
        }
    }


# ==================== GUNA MILAN CALCULATIONS ====================

class GunaMilanCalculator:
    """
    Calculate Guna Milan (Ashtakoot) compatibility
    
    All calculations use MOON's nakshatra and rashi (not Ascendant)
    """
    
    def __init__(self, male_moon_details, female_moon_details):
        """
        Initialize with Moon details from both charts
        
        Args:
            male_moon_details: Dict with 'nakshatra', 'pada', 'rashi'
            female_moon_details: Dict with 'nakshatra', 'pada', 'rashi'
        """
        self.male = male_moon_details
        self.female = female_moon_details
    
    def calculate_varna(self):
        """
        VARNA KUTA - 1 point
        
        Logic:
        - Compares spiritual/ego levels based on nakshatra
        - Male's varna should be equal or higher than female's
        - Brahmin (4) > Kshatriya (3) > Vaishya (2) > Shudra (1)
        
        Scoring:
        - Male varna >= Female varna: 1 point
        - Otherwise: 0 points
        """
        male_varna = VARNA_MAP.get(self.male['nakshatra'], "Shudra")
        female_varna = VARNA_MAP.get(self.female['nakshatra'], "Shudra")
        
        male_order = VARNA_ORDER[male_varna]
        female_order = VARNA_ORDER[female_varna]
        
        points = 1 if male_order >= female_order else 0
        
        return {
            'name': 'Varna Kuta',
            'male_varna': male_varna,
            'female_varna': female_varna,
            'points_obtained': points,
            'max_points': 1,
            'description': 'Spiritual compatibility based on ego levels'
        }
    
    def calculate_vashya(self):
        """
        VASHYA KUTA - 2 points
        
        Logic:
        - Based on Moon's rashi (not nakshatra)
        - Checks mutual attraction and control between rashis
        
        Scoring:
        - Same rashi: 2 points
        - Same vashya group: 2 points
        - Compatible groups (Human-Aquatic): 1 point
        - Leo-Aquarius special case: 2 points
        - Otherwise: 0 points
        """
        male_vashya = VASHYA_MAP[self.male['rashi']]
        female_vashya = VASHYA_MAP[self.female['rashi']]
        
        # Same rashi
        if self.male['rashi'] == self.female['rashi']:
            points = 2
        # Same vashya group
        elif male_vashya == female_vashya:
            points = 2
        # Human and Aquatic are compatible
        elif (male_vashya == "Human" and female_vashya == "Aquatic") or \
             (male_vashya == "Aquatic" and female_vashya == "Human"):
            points = 1
        # Leo (5) and Aquarius (11) special case
        elif (self.male['rashi'] == 5 and self.female['rashi'] == 11) or \
             (self.male['rashi'] == 11 and self.female['rashi'] == 5):
            points = 2
        else:
            points = 0
        
        return {
            'name': 'Vashya Kuta',
            'male_vashya': male_vashya,
            'female_vashya': female_vashya,
            'points_obtained': points,
            'max_points': 2,
            'description': 'Mutual attraction and control'
        }
    
    def calculate_tara(self):
        """
        TARA KUTA - 3 points
        
        Logic:
        - Count nakshatras from male to female and vice versa
        - Divide count by 9 and check remainder for Tara type
        - Both directions must be checked
        
        Favorable Taras (remainders): 2, 4, 6, 8, 9
        Unfavorable Taras: 1, 3, 5, 7
        
        Scoring:
        - Both favorable: 3 points
        - One favorable: 1.5 points
        - Both unfavorable: 0 points
        """
        def get_tara_type(count):
            remainder = count % 9
            if remainder == 0:
                remainder = 9
            
            tara_names = {
                1: "Janma", 2: "Sampat", 3: "Vipat", 4: "Kshema",
                5: "Pratyak", 6: "Sadhana", 7: "Vadha", 8: "Mitra", 9: "Ati-Mitra"
            }
            return tara_names[remainder], remainder
        
        # Male to Female count
        count_m_to_f = (self.female['nakshatra'] - self.male['nakshatra']) % 27
        if count_m_to_f == 0:
            count_m_to_f = 27
        tara_m_to_f, rem_m_to_f = get_tara_type(count_m_to_f)
        
        # Female to Male count
        count_f_to_m = (self.male['nakshatra'] - self.female['nakshatra']) % 27
        if count_f_to_m == 0:
            count_f_to_m = 27
        tara_f_to_m, rem_f_to_m = get_tara_type(count_f_to_m)
        
        # Check if favorable (2, 4, 6, 8, 9)
        favorable = [2, 4, 6, 8, 9]
        m_to_f_favorable = rem_m_to_f in favorable
        f_to_m_favorable = rem_f_to_m in favorable
        
        # Calculate points
        if m_to_f_favorable and f_to_m_favorable:
            points = 3
        elif m_to_f_favorable or f_to_m_favorable:
            points = 1.5
        else:
            points = 0
        
        return {
            'name': 'Tara Kuta',
            'male_to_female_tara': tara_m_to_f,
            'female_to_male_tara': tara_f_to_m,
            'male_to_female_count': count_m_to_f,
            'female_to_male_count': count_f_to_m,
            'points_obtained': points,
            'max_points': 3,
            'description': 'Birth star compatibility and destiny'
        }
    
    def calculate_yoni(self):
        """
        YONI KUTA - 4 points
        
        Logic:
        - Each nakshatra has an animal symbol and gender
        - Checks compatibility between animals
        
        Scoring:
        - Same animal, opposite gender: 4 points (best)
        - Natural enemies: 0 points
        - Same animal, same gender: 2 points
        - Different animals (neutral): 2 points
        """
        male_yoni = YONI_MAP[self.male['nakshatra']]
        female_yoni = YONI_MAP[self.female['nakshatra']]
        
        male_animal, male_gender = male_yoni
        female_animal, female_gender = female_yoni
        
        # Same animal, opposite gender (perfect match)
        if male_animal == female_animal and male_gender != female_gender:
            points = 4
        # Natural enemies
        elif (male_animal, female_animal) in YONI_ENEMIES:
            points = 0
        # Same animal, same gender
        elif male_animal == female_animal:
            points = 2
        # Different animals (neutral)
        else:
            points = 2
        
        return {
            'name': 'Yoni Kuta',
            'male_yoni': f"{male_animal} ({male_gender})",
            'female_yoni': f"{female_animal} ({female_gender})",
            'points_obtained': points,
            'max_points': 4,
            'description': 'Physical and sexual compatibility'
        }
    
    def calculate_graha_maitri(self):
        """
        GRAHA MAITRI KUTA - 5 points
        
        Logic:
        - Based on friendship between Moon rashi lords
        - Checks natural planetary relationships
        
        Scoring:
        - Same lord: 5 points
        - Both friends: 5 points
        - One friend, one neutral: 4 points
        - Both neutral: 3 points
        - One friend/neutral, one enemy: 1 point
        - Both enemies: 0 points
        """
        male_lord = RASHI_LORDS[self.male['rashi']]
        female_lord = RASHI_LORDS[self.female['rashi']]
        
        # Same lord
        if male_lord == female_lord:
            points = 5
        else:
            # Get relationships
            male_to_female = self._get_relationship(male_lord, female_lord)
            female_to_male = self._get_relationship(female_lord, male_lord)
            
            # Calculate points based on mutual relationship
            if male_to_female == "friend" and female_to_male == "friend":
                points = 5
            elif male_to_female == "friend" or female_to_male == "friend":
                if male_to_female == "neutral" or female_to_male == "neutral":
                    points = 4
                else:  # one friend, one enemy
                    points = 1
            elif male_to_female == "neutral" and female_to_male == "neutral":
                points = 3
            elif male_to_female == "neutral" or female_to_male == "neutral":
                points = 1
            else:  # both enemies
                points = 0
        
        return {
            'name': 'Graha Maitri Kuta',
            'male_rashi_lord': male_lord,
            'female_rashi_lord': female_lord,
            'points_obtained': points,
            'max_points': 5,
            'description': 'Mental and psychological compatibility'
        }
    
    def _get_relationship(self, planet1, planet2):
        """Helper: Get relationship between two planets"""
        if planet2 in PLANETARY_RELATIONS[planet1]['friends']:
            return "friend"
        elif planet2 in PLANETARY_RELATIONS[planet1]['enemies']:
            return "enemy"
        else:
            return "neutral"
    
    def calculate_gana(self):
        """
        GANA KUTA - 6 points
        
        Logic:
        - Based on nakshatra's Gana (temperament)
        - Deva (divine), Manushya (human), Rakshasa (demonic)
        
        Scoring:
        - Same gana: 6 points
        - Deva-Manushya: 6 points
        - Manushya male - Rakshasa female: 6 points
        - Deva-Rakshasa: 0 points
        - Rakshasa male - Manushya female: 0 points
        """
        male_gana = GANA_MAP[self.male['nakshatra']]
        female_gana = GANA_MAP[self.female['nakshatra']]
        
        # Same gana
        if male_gana == female_gana:
            points = 6
        # Deva and Manushya compatible
        elif (male_gana == "Deva" and female_gana == "Manushya") or \
             (male_gana == "Manushya" and female_gana == "Deva"):
            points = 6
        # Manushya male and Rakshasa female acceptable
        elif male_gana == "Manushya" and female_gana == "Rakshasa":
            points = 6
        # All other combinations are incompatible
        else:
            points = 0
        
        return {
            'name': 'Gana Kuta',
            'male_gana': male_gana,
            'female_gana': female_gana,
            'points_obtained': points,
            'max_points': 6,
            'description': 'Temperament and behavior compatibility'
        }
    
    def calculate_bhakoot(self):
        """
        BHAKOOT/RASHI KUTA - 7 points
        
        Logic:
        - Based on position of female's rashi from male's rashi
        - Certain positions create doshas (afflictions)
        
        Inauspicious positions:
        - 2-12: Financial problems
        - 5-9: Loss of children (with exceptions)
        - 6-8: Health issues, enmity
        
        Exceptions apply if:
        - Same rashi
        - 7th from each other (opposition) - DEBATABLE
        - Same rashi lord
        - Friend rashi lords
        
        Scoring:
        - Favorable: 7 points
        - Unfavorable with exception: 7 points
        - Unfavorable without exception: 0 points
        """
        male_rashi = self.male['rashi']
        female_rashi = self.female['rashi']
        
        # Same rashi
        if male_rashi == female_rashi:
            return {
                'name': 'Bhakoot Kuta',
                'male_rashi': RASHI_NAMES[male_rashi - 1],
                'female_rashi': RASHI_NAMES[female_rashi - 1],
                'position': 'Same',
                'dosha': 'None',
                'points_obtained': 7,
                'max_points': 7,
                'description': 'Love, affection and prosperity'
            }
        
        # Calculate position (1-12)
        position = (female_rashi - male_rashi) % 12
        if position == 0:
            position = 12
        
        # Check for inauspicious positions
        inauspicious = False
        dosha_type = None
        
        # 2-12 relationship
        if position == 2 or position == 12:
            inauspicious = True
            dosha_type = "2-12 (Dwiradwadasha)"
        # 5-9 relationship
        elif position == 5 or position == 9:
            inauspicious = True
            dosha_type = "5-9 (Panchanava)"
        # 6-8 relationship (MOST SERIOUS)
        elif position == 6 or position == 8:
            inauspicious = True
            dosha_type = "6-8 (Shadashtaka)"
        
        # Check for exceptions ONLY if inauspicious
        if inauspicious:
            if self._check_bhakoot_exception(male_rashi, female_rashi):
                # Exception applies - give points
                points = 7
                dosha_type = f"{dosha_type} - Exception applies"
                inauspicious = False
            else:
                # No exception - dosha stands
                points = 0
        else:
            points = 7
            dosha_type = "None"
        
        return {
            'name': 'Bhakoot Kuta',
            'male_rashi': RASHI_NAMES[male_rashi - 1],
            'female_rashi': RASHI_NAMES[female_rashi - 1],
            'position': position,
            'dosha': dosha_type,
            'points_obtained': points,
            'max_points': 7,
            'description': 'Love, affection and prosperity'
        }
    
    def _check_bhakoot_exception(self, rashi1, rashi2):
        """
        Check for Bhakoot dosha exceptions
        
        Exceptions:
        1. Same rashi lord
        2. Friend rashi lords
        3. 7th from each other (STRICT: only if lords are friends)
        """
        lord1 = RASHI_LORDS[rashi1]
        lord2 = RASHI_LORDS[rashi2]
        
        # Same lord
        if lord1 == lord2:
            return True
        
        # Friend lords
        if self._get_relationship(lord1, lord2) == "friend" and \
           self._get_relationship(lord2, lord1) == "friend":
            return True
        
        # 7th house (opposition) - only if lords are friends
        # Using STRICT interpretation
        if abs(rashi1 - rashi2) == 6:
            if self._get_relationship(lord1, lord2) == "friend" or \
               self._get_relationship(lord2, lord1) == "friend":
                return True
        
        return False
    
    def calculate_nadi(self):
        """
        NADI KUTA - 8 points (MOST IMPORTANT)
        
        Logic:
        - Based on nakshatra's Nadi (pulse/energy)
        - Aadi (Vata), Madhya (Pitta), Antya (Kapha)
        - Same Nadi = Nadi Dosha (highly inauspicious)
        
        Exceptions:
        1. Same nakshatra, different pada
        2. Same rashi, different nakshatra
        3. Rashi lords are friends
        
        Scoring:
        - Different Nadi: 8 points
        - Same Nadi with exception: 8 points
        - Same Nadi without exception: 0 points (DOSHA)
        """
        male_nadi = NADI_MAP[self.male['nakshatra']]
        female_nadi = NADI_MAP[self.female['nakshatra']]
        
        # Different Nadi - no dosha
        if male_nadi != female_nadi:
            return {
                'name': 'Nadi Kuta',
                'male_nadi': male_nadi,
                'female_nadi': female_nadi,
                'nadi_dosha': False,
                'points_obtained': 8,
                'max_points': 8,
                'description': 'Health, genetics and progeny'
            }
        
        # Same Nadi - check for exceptions
        exception = self._check_nadi_exception()
        
        if exception:
            points = 8
            dosha = False
        else:
            points = 0
            dosha = True
        
        return {
            'name': 'Nadi Kuta',
            'male_nadi': male_nadi,
            'female_nadi': female_nadi,
            'nadi_dosha': dosha,
            'exception_applied': exception,
            'points_obtained': points,
            'max_points': 8,
            'description': 'Health, genetics and progeny'
        }
    
    def _check_nadi_exception(self):
        """Check for Nadi dosha exceptions"""
        # Exception 1: Same nakshatra but different pada
        if self.male['nakshatra'] == self.female['nakshatra'] and \
           self.male['pada'] != self.female['pada']:
            return True
        
        # Exception 2: Same rashi but different nakshatra
        if self.male['rashi'] == self.female['rashi'] and \
           self.male['nakshatra'] != self.female['nakshatra']:
            return True
        
        # Exception 3: Rashi lords are friends
        male_lord = RASHI_LORDS[self.male['rashi']]
        female_lord = RASHI_LORDS[self.female['rashi']]
        if self._get_relationship(male_lord, female_lord) == "friend" and \
           self._get_relationship(female_lord, male_lord) == "friend":
            return True
        
        return False
    
    def calculate_all_kutas(self):
        """Calculate all 8 kutas and return complete analysis"""
        kutas = {
            'varna': self.calculate_varna(),
            'vashya': self.calculate_vashya(),
            'tara': self.calculate_tara(),
            'yoni': self.calculate_yoni(),
            'graha_maitri': self.calculate_graha_maitri(),
            'gana': self.calculate_gana(),
            'bhakoot': self.calculate_bhakoot(),
            'nadi': self.calculate_nadi()
        }
        
        total_score = sum(k['points_obtained'] for k in kutas.values())
        max_score = 36
        percentage = round((total_score / max_score) * 100, 2)
        
        # Compatibility assessment
        if total_score >= 32:
            level = "Excellent"
            recommendation = "Highly compatible - Very good match"
        elif total_score >= 24:
            level = "Good"
            recommendation = "Good compatibility - Recommended"
        elif total_score >= 18:
            level = "Average"
            recommendation = "Average compatibility - Acceptable with remedies"
        else:
            level = "Poor"
            recommendation = "Poor compatibility - Not recommended"
        
        # Identify critical doshas
        critical_doshas = []
        if kutas['nadi']['nadi_dosha']:
            critical_doshas.append("Nadi Dosha (Most serious - genetic incompatibility)")
        if kutas['bhakoot']['points_obtained'] == 0:
            critical_doshas.append(f"Bhakoot Dosha - {kutas['bhakoot']['dosha']}")
        if kutas['gana']['points_obtained'] == 0:
            critical_doshas.append("Gana Dosha (temperament mismatch)")
        
        return {
            'kutas': kutas,
            'total_score': total_score,
            'max_score': max_score,
            'percentage': percentage,
            'compatibility_level': level,
            'recommendation': recommendation,
            'critical_doshas': critical_doshas if critical_doshas else None
        }