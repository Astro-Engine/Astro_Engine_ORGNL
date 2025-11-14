





# import swisseph as swe
# from datetime import datetime

# # Chaldean numerology chart
# chaldean_chart = {
#     'a': 1, 'i': 1, 'j': 1, 'q': 1, 'y': 1,
#     'b': 2, 'k': 2, 'r': 2,
#     'c': 3, 'g': 3, 'l': 3, 's': 3,
#     'd': 4, 'm': 4, 't': 4,
#     'e': 5, 'h': 5, 'n': 5, 'x': 5,
#     'u': 6, 'v': 6, 'w': 6,
#     'o': 7, 'z': 7,
#     'f': 8, 'p': 8
# }

# # Personal-focused interpretations for root numbers
# personal_interpretations = {
#     1: "You are a natural leader, independent, and ambitious. Your path is one of innovation and self-reliance.",
#     2: "You are cooperative, diplomatic, and sensitive. Partnerships and relationships are key to your success.",
#     3: "You are creative, expressive, and social. Communication and self-expression are your strengths.",
#     4: "You are practical, disciplined, and hardworking. Stability and structure are essential for your growth.",
#     5: "You are adventurous, adaptable, and freedom-loving. Change and variety fuel your journey.",
#     6: "You are responsible, nurturing, and harmonious. Service to others and community are central to your life.",
#     7: "You are analytical, introspective, and wise. Knowledge and spirituality guide your path.",
#     8: "You are ambitious, powerful, and material-focused. Success and achievement drive your actions.",
#     9: "You are humanitarian, compassionate, and idealistic. Completion and global vision define your purpose.",
#     11: "You are intuitive, inspirational, and visionary. Enlightenment and higher consciousness are your calling.",
#     22: "You are a master builder, practical idealist, and achiever. Large-scale projects and impact are your destiny.",
#     33: "You are a master teacher, compassionate healer, and guide. Education and healing are your life's work."
# }

# # Enhanced business-focused interpretations with astrological insights
# business_interpretations = {
#     1: "A venture driven by leadership and innovation, ruled by the Sun. Ideal for pioneering startups or bold initiatives. Expect strong visibility and influence.",
#     2: "A business rooted in partnership and cooperation, guided by the Moon. Perfect for collaborative efforts or customer-focused services. Emotional resonance is your strength.",
#     3: "A creative enterprise blessed by Jupiter’s expansive energy. Suited for artistic, educational, or communicative ventures. Growth comes through optimism and expression.",
#     4: "A stable, structured business under Rahu/Uranus’s unconventional influence. Best for disciplined industries or tech innovations. Patience yields breakthroughs.",
#     5: "A dynamic, adaptable venture ruled by Mercury. Ideal for fast-paced, versatile industries like marketing or travel. Communication drives success.",
#     6: "A harmonious, service-oriented business influenced by Venus. Perfect for caregiving, beauty, or luxury markets. Relationships and aesthetics are key.",
#     7: "A knowledge-based enterprise under Ketu/Neptune’s spiritual guidance. Suitable for research, healing, or introspective fields. Wisdom is your asset.",
#     8: "A powerful, wealth-focused business ruled by Saturn. Ideal for finance, real estate, or long-term investments. Discipline ensures prosperity.",
#     9: "A humanitarian venture guided by Mars’s passionate energy. Best for social causes or competitive fields. Courage fuels your global impact.",
#     11: "A visionary business with Moon/Uranus’s intuitive spark. Perfect for spiritual or innovative enterprises. Inspiration leads to enlightenment.",
#     22: "A master builder’s dream under Jupiter/Pluto’s transformative power. Suited for ambitious, large-scale projects. Practical idealism creates lasting legacies.",
#     33: "A compassionate, teaching-focused business ruled by Jupiter/Neptune. Ideal for education or healing ventures. Your influence uplifts and heals."
# }

# # Ruling planets for each number
# ruling_planets = {
#     1: "Sun",
#     2: "Moon",
#     3: "Jupiter",
#     4: "Rahu/Uranus",
#     5: "Mercury",
#     6: "Venus",
#     7: "Ketu/Neptune",
#     8: "Saturn",
#     9: "Mars",
#     11: "Moon (or Uranus)",
#     22: "Jupiter (or Pluto)",
#     33: "Jupiter (or Neptune)"
# }

# # Elemental associations for root numbers
# elemental_associations = {
#     1: "Fire", 2: "Water", 3: "Air", 4: "Earth", 5: "Fire", 6: "Water", 7: "Air", 8: "Earth", 9: "Fire",
#     11: "Air", 22: "Earth", 33: "Water"
# }

# # Enhanced astrological insights for business contexts
# planet_insights = {
#     "Sun": {
#         "positive": "Radiates leadership, innovation, and a commanding brand presence. Your business shines brightly, inspiring loyalty and recognition.",
#         "challenge": "Avoid ego-driven choices or over-centralization. Balance authority with teamwork.",
#         "business_tip": "Launch initiatives on Sundays to harness solar energy."
#     },
#     "Moon": {
#         "positive": "Excels in emotional intelligence and adaptability. A customer-centric approach builds deep trust and connection.",
#         "challenge": "Guard against inconsistent strategies or emotional decisions. Maintain steady focus.",
#         "business_tip": "Plan key meetings on Mondays for intuitive clarity."
#     },
#     "Jupiter": {
#         "positive": "Brings growth, wisdom, and expansive opportunities. Perfect for scaling into education, publishing, or global markets.",
#         "challenge": "Avoid overexpansion or risky optimism. Anchor growth with practicality.",
#         "business_tip": "Sign deals on Thursdays to align with Jupiter’s abundance."
#     },
#     "Rahu/Uranus": {
#         "positive": "Sparks innovation and disruptive breakthroughs. Ideal for tech startups or unconventional niches.",
#         "challenge": "Risk of instability or chaos. Build a strong operational base.",
#         "business_tip": "Start projects on Saturdays to tap into transformative energy."
#     },
#     "Mercury": {
#         "positive": "Thrives on communication, adaptability, and intellect. Great for trading, media, or networking ventures.",
#         "challenge": "Scattered focus can dilute impact. Prioritize strategic depth.",
#         "business_tip": "Schedule brainstorming on Wednesdays for Mercury’s agility."
#     },
#     "Venus": {
#         "positive": "Fosters harmony, beauty, and strong relationships. Perfect for art, design, or luxury branding.",
#         "challenge": "Avoid indulgence or financial laxity. Keep budgets disciplined.",
#         "business_tip": "Launch products on Fridays to channel Venus’s charm."
#     },
#     "Ketu/Neptune": {
#         "positive": "Guides with spirituality, intuition, and detachment. Suited for healing, meditation, or non-profits.",
#         "challenge": "Escapism or impracticality can hinder progress. Stay grounded.",
#         "business_tip": "Reflect on Tuesdays to align with Ketu’s insight."
#     },
#     "Saturn": {
#         "positive": "Builds enduring success through discipline and structure. Ideal for long-term ventures like finance or construction.",
#         "challenge": "Rigidity or fear of risk can stall growth. Embrace calculated change.",
#         "business_tip": "Finalize contracts on Saturdays for Saturn’s stability."
#     },
#     "Mars": {
#         "positive": "Ignites energy, courage, and competitiveness. Great for sports, fitness, or high-stakes industries.",
#         "challenge": "Impulsiveness or conflict can disrupt. Direct energy purposefully.",
#         "business_tip": "Kick off campaigns on Tuesdays to leverage Mars’s drive."
#     },
#     "Moon (or Uranus)": {
#         "positive": "Blends intuition with innovation. A unique edge for visionary or tech-driven businesses.",
#         "challenge": "Emotional swings or erratic moves need balance. Seek consistency.",
#         "business_tip": "Plan on Mondays or Saturdays for dual planetary support."
#     },
#     "Jupiter (or Pluto)": {
#         "positive": "Combines expansion with deep transformation. Ideal for impactful, scalable enterprises.",
#         "challenge": "Overreach or power struggles can arise. Use influence wisely.",
#         "business_tip": "Act on Thursdays or Tuesdays for growth and change."
#     },
#     "Jupiter (or Neptune)": {
#         "positive": "Merges wisdom with compassion. Perfect for teaching, healing, or spiritual businesses.",
#         "challenge": "Idealism without action falters. Ground your vision.",
#         "business_tip": "Teach or launch on Thursdays or Tuesdays for alignment."
#     }
# }

# # Sun sign insights for founding dates
# sun_sign_insights = {
#     "Aries": "Bold, pioneering spirit. Excellent for startups or competitive industries. Your business thrives on action and initiative.",
#     "Taurus": "Stability and persistence. Good for long-term, steady growth businesses. Focus on building solid foundations.",
#     "Gemini": "Adaptability and communication. Ideal for networking, media, or multi-faceted ventures. Stay focused amidst variety.",
#     "Cancer": "Nurturing and intuitive. Great for family-oriented or caregiving businesses. Balance emotion with practicality.",
#     "Leo": "Creativity and leadership. Perfect for entertainment, branding, or luxury markets. Avoid the spotlight overshadowing teamwork.",
#     "Virgo": "Detail-oriented and analytical. Suitable for health, service, or precision-based industries. Don’t let perfectionism hinder progress.",
#     "Libra": "Harmony and partnership. Ideal for law, diplomacy, or design. Seek balance in decision-making.",
#     "Scorpio": "Intensity and transformation. Good for research, psychology, or transformative services. Manage power dynamics carefully.",
#     "Sagittarius": "Expansion and exploration. Excellent for travel, education, or global businesses. Avoid overextension.",
#     "Capricorn": "Discipline and ambition. Perfect for corporate, financial, or structural enterprises. Balance work with renewal.",
#     "Aquarius": "Innovation and humanitarianism. Ideal for technology, social causes, or unconventional ventures. Stay grounded.",
#     "Pisces": "Compassion and imagination. Great for arts, healing, or spiritual businesses. Maintain boundaries and practicality."
# }

# # Practical recommendations
# number_colors = {
#     1: ["Gold", "Orange", "Red"],
#     2: ["Silver", "White", "Green"],
#     3: ["Yellow", "Purple", "Mauve"],
#     4: ["Electric Blue", "Grey", "Slate"],
#     5: ["Turquoise", "Light Green", "White"],
#     6: ["Rose", "Blue", "Indigo"],
#     7: ["Violet", "Purple", "White"],
#     8: ["Black", "Dark Blue", "Brown"],
#     9: ["Red", "Crimson", "Pink"],
#     11: ["Silver", "Pearl", "White"],
#     22: ["Gold", "Brown", "Green"],
#     33: ["Violet", "Rose", "Pink"]
# }

# number_gemstones = {
#     1: "Ruby",
#     2: "Pearl",
#     3: "Topaz",
#     4: "Sapphire",
#     5: "Emerald",
#     6: "Diamond",
#     7: "Amethyst",
#     8: "Onyx",
#     9: "Coral",
#     11: "Moonstone",
#     22: "Jade",
#     33: "Rose Quartz"
# }

# planet_days = {
#     "Sun": "Sunday",
#     "Moon": "Monday",
#     "Jupiter": "Thursday",
#     "Rahu/Uranus": "Saturday",
#     "Mercury": "Wednesday",
#     "Venus": "Friday",
#     "Ketu/Neptune": "Tuesday",
#     "Saturn": "Saturday",
#     "Mars": "Tuesday",
#     "Moon (or Uranus)": "Monday or Saturday",
#     "Jupiter (or Pluto)": "Thursday or Tuesday",
#     "Jupiter (or Neptune)": "Thursday or Tuesday"
# }

# def calculate_chaldean_numbers(name):
#     """
#     Calculate the compound and root numbers for a name using Chaldean numerology.
#     Only alphabetic characters are processed.
    
#     Args:
#         name (str): The business name or tagline.
    
#     Returns:
#         dict: Contains 'compound_number' and 'root_number'.
#     """
#     name_lower = name.lower()
#     total = 0
#     for char in name_lower:
#         if char in chaldean_chart:
#             total += chaldean_chart[char]
#     compound_number = total
#     if total in [11, 22, 33]:
#         root_number = total
#     else:
#         while total > 9:
#             total = sum(int(digit) for digit in str(total))
#         root_number = total
#     return {"compound_number": compound_number, "root_number": root_number}

# def calculate_date_numerology(date_str):
#     """
#     Calculate the numerological value of a date in 'YYYY-MM-DD' format.
    
#     Args:
#         date_str (str): The date string.
    
#     Returns:
#         int or None: The numerological value, or None if invalid.
#     """
#     try:
#         datetime.strptime(date_str, '%Y-%m-%d')
#         digits = [int(char) for char in date_str if char.isdigit()]
#         total = sum(digits)
#         while total > 9 and total not in [11, 22, 33]:
#             total = sum(int(digit) for digit in str(total))
#         return total
#     except ValueError:
#         return None

# def get_sun_sign(date_str):
#     """
#     Calculate the Sun's zodiac sign for a given date using pyswisseph.
#     Assumes 12:00 UT for simplicity.
    
#     Args:
#         date_str (str): Date in 'YYYY-MM-DD' format.
    
#     Returns:
#         str or None: The Sun's sign, or None if calculation fails.
#     """
#     try:
#         year, month, day = map(int, date_str.split('-'))
#         jd = swe.julday(year, month, day, 12.0)
#         sun_pos, _ = swe.calc_ut(jd, swe.SUN)
#         longitude = sun_pos[0]
#         sign_index = int(longitude / 30)
#         signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
#                  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
#         return signs[sign_index]
#     except Exception:
#         return None

# def get_element_from_number(number):
#     """
#     Get the elemental association for a numerological root number.
    
#     Args:
#         number (int): The root number.
    
#     Returns:
#         str: The element associated with the number.
#     """
#     return elemental_associations.get(number, "Unknown")

# def get_sun_sign_element(sign):
#     """
#     Get the elemental association for a zodiac sign.
    
#     Args:
#         sign (str): The zodiac sign.
    
#     Returns:
#         str: The element associated with the sign.
#     """
#     fire = ["Aries", "Leo", "Sagittarius"]
#     earth = ["Taurus", "Virgo", "Capricorn"]
#     air = ["Gemini", "Libra", "Aquarius"]
#     water = ["Cancer", "Scorpio", "Pisces"]
#     if sign in fire:
#         return "Fire"
#     elif sign in earth:
#         return "Earth"
#     elif sign in air:
#         return "Air"
#     elif sign in water:
#         return "Water"
#     else:
#         return "Unknown"

# def get_elemental_compatibility(element1, element2):
#     """
#     Determine the compatibility between two elements with astrological nuance.
    
#     Args:
#         element1 (str): First element.
#         element2 (str): Second element.
    
#     Returns:
#         str: Compatibility message.
#     """
#     if element1 == element2:
#         return f"Harmonious alignment: both share {element1}’s core energy, amplifying strength."
#     elif (element1 == "Fire" and element2 == "Air") or (element1 == "Air" and element2 == "Fire"):
#         return "Dynamic synergy: Air fuels Fire’s passion, igniting growth and inspiration."
#     elif (element1 == "Water" and element2 == "Earth") or (element1 == "Earth" and element2 == "Water"):
#         return "Nurturing bond: Water feeds Earth’s stability, fostering resilience and depth."
#     elif (element1 == "Fire" and element2 == "Water") or (element1 == "Water" and element2 == "Fire"):
#         return "Opposing forces: Fire’s intensity clashes with Water’s calm—balance is key."
#     elif (element1 == "Air" and element2 == "Earth") or (element1 == "Earth" and element2 == "Air"):
#         return "Neutral tension: Air’s fluidity meets Earth’s solidity—adaptation is needed."
#     else:
#         return "Neutral flow: no strong astrological interplay, offering flexibility."







"""
Chaldean Numerology Calculations Module
All numerology calculation functions with corrected master number logic
"""

import swisseph as swe
from datetime import datetime

# Set the Swiss Ephemeris path
swe.set_ephe_path('astro_api/ephe')

# ============================================================================
# CONSTANTS
# ============================================================================

# Chaldean numerology chart
chaldean_chart = {
    'a': 1, 'i': 1, 'j': 1, 'q': 1, 'y': 1,
    'b': 2, 'k': 2, 'r': 2,
    'c': 3, 'g': 3, 'l': 3, 's': 3,
    'd': 4, 'm': 4, 't': 4,
    'e': 5, 'h': 5, 'n': 5, 'x': 5,
    'u': 6, 'v': 6, 'w': 6,
    'o': 7, 'z': 7,
    'f': 8, 'p': 8
}

# Personal-focused interpretations for root numbers
personal_interpretations = {
    1: "You are a natural leader, independent, and ambitious. Your path is one of innovation and self-reliance.",
    2: "You are cooperative, diplomatic, and sensitive. Partnerships and relationships are key to your success.",
    3: "You are creative, expressive, and social. Communication and self-expression are your strengths.",
    4: "You are practical, disciplined, and hardworking. Stability and structure are essential for your growth.",
    5: "You are adventurous, adaptable, and freedom-loving. Change and variety fuel your journey.",
    6: "You are responsible, nurturing, and harmonious. Service to others and community are central to your life.",
    7: "You are analytical, introspective, and wise. Knowledge and spirituality guide your path.",
    8: "You are ambitious, powerful, and material-focused. Success and achievement drive your actions.",
    9: "You are humanitarian, compassionate, and idealistic. Completion and global vision define your purpose.",
    11: "You are intuitive, inspirational, and visionary. Enlightenment and higher consciousness are your calling.",
    22: "You are a master builder, practical idealist, and achiever. Large-scale projects and impact are your destiny.",
    33: "You are a master teacher, compassionate healer, and guide. Education and healing are your life's work."
}

# Enhanced business-focused interpretations with astrological insights
business_interpretations = {
    1: "A venture driven by leadership and innovation, ruled by the Sun. Ideal for pioneering startups or bold initiatives. Expect strong visibility and influence.",
    2: "A business rooted in partnership and cooperation, guided by the Moon. Perfect for collaborative efforts or customer-focused services. Emotional resonance is your strength.",
    3: "A creative enterprise blessed by Jupiter's expansive energy. Suited for artistic, educational, or communicative ventures. Growth comes through optimism and expression.",
    4: "A stable, structured business under Rahu/Uranus's unconventional influence. Best for disciplined industries or tech innovations. Patience yields breakthroughs.",
    5: "A dynamic, adaptable venture ruled by Mercury. Ideal for fast-paced, versatile industries like marketing or travel. Communication drives success.",
    6: "A harmonious, service-oriented business influenced by Venus. Perfect for caregiving, beauty, or luxury markets. Relationships and aesthetics are key.",
    7: "A knowledge-based enterprise under Ketu/Neptune's spiritual guidance. Suitable for research, healing, or introspective fields. Wisdom is your asset.",
    8: "A powerful, wealth-focused business ruled by Saturn. Ideal for finance, real estate, or long-term investments. Discipline ensures prosperity.",
    9: "A humanitarian venture guided by Mars's passionate energy. Best for social causes or competitive fields. Courage fuels your global impact.",
    11: "A visionary business with Moon/Uranus's intuitive spark. Perfect for spiritual or innovative enterprises. Inspiration leads to enlightenment.",
    22: "A master builder's dream under Jupiter/Pluto's transformative power. Suited for ambitious, large-scale projects. Practical idealism creates lasting legacies.",
    33: "A compassionate, teaching-focused business ruled by Jupiter/Neptune. Ideal for education or healing ventures. Your influence uplifts and heals."
}

# Ruling planets for each number
ruling_planets = {
    1: "Sun",
    2: "Moon",
    3: "Jupiter",
    4: "Rahu/Uranus",
    5: "Mercury",
    6: "Venus",
    7: "Ketu/Neptune",
    8: "Saturn",
    9: "Mars",
    11: "Moon (or Uranus)",
    22: "Jupiter (or Pluto)",
    33: "Jupiter (or Neptune)"
}

# Elemental associations for root numbers
elemental_associations = {
    1: "Fire", 2: "Water", 3: "Air", 4: "Earth", 5: "Fire", 6: "Water", 7: "Air", 8: "Earth", 9: "Fire",
    11: "Air", 22: "Earth", 33: "Water"
}

# Enhanced astrological insights for business contexts
planet_insights = {
    "Sun": {
        "positive": "Radiates leadership, innovation, and a commanding brand presence. Your business shines brightly, inspiring loyalty and recognition.",
        "challenge": "Avoid ego-driven choices or over-centralization. Balance authority with teamwork.",
        "business_tip": "Launch initiatives on Sundays to harness solar energy."
    },
    "Moon": {
        "positive": "Excels in emotional intelligence and adaptability. A customer-centric approach builds deep trust and connection.",
        "challenge": "Guard against inconsistent strategies or emotional decisions. Maintain steady focus.",
        "business_tip": "Plan key meetings on Mondays for intuitive clarity."
    },
    "Jupiter": {
        "positive": "Brings growth, wisdom, and expansive opportunities. Perfect for scaling into education, publishing, or global markets.",
        "challenge": "Avoid overexpansion or risky optimism. Anchor growth with practicality.",
        "business_tip": "Sign deals on Thursdays to align with Jupiter's abundance."
    },
    "Rahu/Uranus": {
        "positive": "Sparks innovation and disruptive breakthroughs. Ideal for tech startups or unconventional niches.",
        "challenge": "Risk of instability or chaos. Build a strong operational base.",
        "business_tip": "Start projects on Saturdays to tap into transformative energy."
    },
    "Mercury": {
        "positive": "Thrives on communication, adaptability, and intellect. Great for trading, media, or networking ventures.",
        "challenge": "Scattered focus can dilute impact. Prioritize strategic depth.",
        "business_tip": "Schedule brainstorming on Wednesdays for Mercury's agility."
    },
    "Venus": {
        "positive": "Fosters harmony, beauty, and strong relationships. Perfect for art, design, or luxury branding.",
        "challenge": "Avoid indulgence or financial laxity. Keep budgets disciplined.",
        "business_tip": "Launch products on Fridays to channel Venus's charm."
    },
    "Ketu/Neptune": {
        "positive": "Guides with spirituality, intuition, and detachment. Suited for healing, meditation, or non-profits.",
        "challenge": "Escapism or impracticality can hinder progress. Stay grounded.",
        "business_tip": "Reflect on Tuesdays to align with Ketu's insight."
    },
    "Saturn": {
        "positive": "Builds enduring success through discipline and structure. Ideal for long-term ventures like finance or construction.",
        "challenge": "Rigidity or fear of risk can stall growth. Embrace calculated change.",
        "business_tip": "Finalize contracts on Saturdays for Saturn's stability."
    },
    "Mars": {
        "positive": "Ignites energy, courage, and competitiveness. Great for sports, fitness, or high-stakes industries.",
        "challenge": "Impulsiveness or conflict can disrupt. Direct energy purposefully.",
        "business_tip": "Kick off campaigns on Tuesdays to leverage Mars's drive."
    },
    "Moon (or Uranus)": {
        "positive": "Blends intuition with innovation. A unique edge for visionary or tech-driven businesses.",
        "challenge": "Emotional swings or erratic moves need balance. Seek consistency.",
        "business_tip": "Plan on Mondays or Saturdays for dual planetary support."
    },
    "Jupiter (or Pluto)": {
        "positive": "Combines expansion with deep transformation. Ideal for impactful, scalable enterprises.",
        "challenge": "Overreach or power struggles can arise. Use influence wisely.",
        "business_tip": "Act on Thursdays or Tuesdays for growth and change."
    },
    "Jupiter (or Neptune)": {
        "positive": "Merges wisdom with compassion. Perfect for teaching, healing, or spiritual businesses.",
        "challenge": "Idealism without action falters. Ground your vision.",
        "business_tip": "Teach or launch on Thursdays or Tuesdays for alignment."
    }
}

# Sun sign insights for founding dates
sun_sign_insights = {
    "Aries": "Bold, pioneering spirit. Excellent for startups or competitive industries. Your business thrives on action and initiative.",
    "Taurus": "Stability and persistence. Good for long-term, steady growth businesses. Focus on building solid foundations.",
    "Gemini": "Adaptability and communication. Ideal for networking, media, or multi-faceted ventures. Stay focused amidst variety.",
    "Cancer": "Nurturing and intuitive. Great for family-oriented or caregiving businesses. Balance emotion with practicality.",
    "Leo": "Creativity and leadership. Perfect for entertainment, branding, or luxury markets. Avoid the spotlight overshadowing teamwork.",
    "Virgo": "Detail-oriented and analytical. Suitable for health, service, or precision-based industries. Don't let perfectionism hinder progress.",
    "Libra": "Harmony and partnership. Ideal for law, diplomacy, or design. Seek balance in decision-making.",
    "Scorpio": "Intensity and transformation. Good for research, psychology, or transformative services. Manage power dynamics carefully.",
    "Sagittarius": "Expansion and exploration. Excellent for travel, education, or global businesses. Avoid overextension.",
    "Capricorn": "Discipline and ambition. Perfect for corporate, financial, or structural enterprises. Balance work with renewal.",
    "Aquarius": "Innovation and humanitarianism. Ideal for technology, social causes, or unconventional ventures. Stay grounded.",
    "Pisces": "Compassion and imagination. Great for arts, healing, or spiritual businesses. Maintain boundaries and practicality."
}

# Practical recommendations
number_colors = {
    1: ["Gold", "Orange", "Red"],
    2: ["Silver", "White", "Green"],
    3: ["Yellow", "Purple", "Mauve"],
    4: ["Electric Blue", "Grey", "Slate"],
    5: ["Turquoise", "Light Green", "White"],
    6: ["Rose", "Blue", "Indigo"],
    7: ["Violet", "Purple", "White"],
    8: ["Black", "Dark Blue", "Brown"],
    9: ["Red", "Crimson", "Pink"],
    11: ["Silver", "Pearl", "White"],
    22: ["Gold", "Brown", "Green"],
    33: ["Violet", "Rose", "Pink"]
}

number_gemstones = {
    1: "Ruby",
    2: "Pearl",
    3: "Topaz",
    4: "Sapphire",
    5: "Emerald",
    6: "Diamond",
    7: "Amethyst",
    8: "Onyx",
    9: "Coral",
    11: "Moonstone",
    22: "Jade",
    33: "Rose Quartz"
}

planet_days = {
    "Sun": "Sunday",
    "Moon": "Monday",
    "Jupiter": "Thursday",
    "Rahu/Uranus": "Saturday",
    "Mercury": "Wednesday",
    "Venus": "Friday",
    "Ketu/Neptune": "Tuesday",
    "Saturn": "Saturday",
    "Mars": "Tuesday",
    "Moon (or Uranus)": "Monday or Saturday",
    "Jupiter (or Pluto)": "Thursday or Tuesday",
    "Jupiter (or Neptune)": "Thursday or Tuesday"
}


# ============================================================================
# CALCULATION FUNCTIONS
# ============================================================================

def calculate_chaldean_numbers(name):
    """
    ✅ CORRECTED VERSION
    Calculate the compound and root numbers for a name using Chaldean numerology.
    Only alphabetic characters are processed.
    Master numbers (11, 22, 33) are preserved during reduction.
    
    Args:
        name (str): The business name or tagline.
    
    Returns:
        dict: Contains 'compound_number' and 'root_number'.
    """
    name_lower = name.lower()
    total = 0
    
    # Sum all letter values
    for char in name_lower:
        if char in chaldean_chart:
            total += chaldean_chart[char]
    
    compound_number = total
    
    # Reduce to root number, but PRESERVE master numbers (11, 22, 33)
    # Check for master numbers AFTER each reduction step
    while total > 9:
        if total in [11, 22, 33]:  # ✅ CRITICAL: Check INSIDE the loop!
            break
        total = sum(int(digit) for digit in str(total))
    
    root_number = total
    
    return {"compound_number": compound_number, "root_number": root_number}


def calculate_date_numerology(date_str):
    """
    ✅ CORRECTED VERSION
    Calculate the numerological value of a date in 'YYYY-MM-DD' format.
    Master numbers (11, 22, 33) are preserved during reduction.
    
    Args:
        date_str (str): The date string.
    
    Returns:
        int or None: The numerological value, or None if invalid.
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        
        # Extract all digits from the date
        digits = [int(char) for char in date_str if char.isdigit()]
        total = sum(digits)
        
        # Reduce to single digit, but PRESERVE master numbers (11, 22, 33)
        # Check for master numbers AFTER each reduction step
        while total > 9:
            if total in [11, 22, 33]:  # ✅ CRITICAL: Check INSIDE the loop!
                break
            total = sum(int(digit) for digit in str(total))
        
        return total
    except ValueError:
        return None


def get_sun_sign(date_str):
    """
    Calculate the Sun's zodiac sign for a given date using pyswisseph.
    Assumes 12:00 UT for simplicity.
    
    Args:
        date_str (str): Date in 'YYYY-MM-DD' format.
    
    Returns:
        str or None: The Sun's sign, or None if calculation fails.
    """
    try:
        year, month, day = map(int, date_str.split('-'))
        jd = swe.julday(year, month, day, 12.0)
        sun_pos, _ = swe.calc_ut(jd, swe.SUN)
        longitude = sun_pos[0]
        sign_index = int(longitude / 30)
        signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                 "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        return signs[sign_index]
    except Exception:
        return None


def get_element_from_number(number):
    """
    Get the elemental association for a numerological root number.
    
    Args:
        number (int): The root number.
    
    Returns:
        str: The element associated with the number.
    """
    return elemental_associations.get(number, "Unknown")


def get_sun_sign_element(sign):
    """
    Get the elemental association for a zodiac sign.
    
    Args:
        sign (str): The zodiac sign.
    
    Returns:
        str: The element associated with the sign.
    """
    fire = ["Aries", "Leo", "Sagittarius"]
    earth = ["Taurus", "Virgo", "Capricorn"]
    air = ["Gemini", "Libra", "Aquarius"]
    water = ["Cancer", "Scorpio", "Pisces"]
    if sign in fire:
        return "Fire"
    elif sign in earth:
        return "Earth"
    elif sign in air:
        return "Air"
    elif sign in water:
        return "Water"
    else:
        return "Unknown"


def get_elemental_compatibility(element1, element2):
    """
    Determine the compatibility between two elements with astrological nuance.
    
    Args:
        element1 (str): First element.
        element2 (str): Second element.
    
    Returns:
        str: Compatibility message.
    """
    if element1 == element2:
        return f"Harmonious alignment: both share {element1}'s core energy, amplifying strength."
    elif (element1 == "Fire" and element2 == "Air") or (element1 == "Air" and element2 == "Fire"):
        return "Dynamic synergy: Air fuels Fire's passion, igniting growth and inspiration."
    elif (element1 == "Water" and element2 == "Earth") or (element1 == "Earth" and element2 == "Water"):
        return "Nurturing bond: Water feeds Earth's stability, fostering resilience and depth."
    elif (element1 == "Fire" and element2 == "Water") or (element1 == "Water" and element2 == "Fire"):
        return "Opposing forces: Fire's intensity clashes with Water's calm—balance is key."
    elif (element1 == "Air" and element2 == "Earth") or (element1 == "Earth" and element2 == "Air"):
        return "Neutral tension: Air's fluidity meets Earth's solidity—adaptation is needed."
    else:
        return "Neutral flow: no strong astrological interplay, offering flexibility."


