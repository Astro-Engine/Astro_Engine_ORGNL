"""
Vedic Astrology Calculations Module
Contains all chart calculation and Shrapit Dosha analysis logic
"""

import swisseph as swe
from datetime import datetime
import os

# Zodiac signs
ZODIAC_SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# Planet IDs
PLANETS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mars': swe.MARS,
    'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS,
    'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE,
    'Ketu': swe.MEAN_NODE,
    'Ascendant': None
}

# Planet lordships
PLANET_LORDS = {
    'Aries': 'Mars',
    'Taurus': 'Venus',
    'Gemini': 'Mercury',
    'Cancer': 'Moon',
    'Leo': 'Sun',
    'Virgo': 'Mercury',
    'Libra': 'Venus',
    'Scorpio': 'Mars',
    'Sagittarius': 'Jupiter',
    'Capricorn': 'Saturn',
    'Aquarius': 'Saturn',
    'Pisces': 'Jupiter'
}

# Exaltation signs
EXALTATION_SIGNS = {
    'Sun': 'Aries',
    'Moon': 'Taurus',
    'Mars': 'Capricorn',
    'Mercury': 'Virgo',
    'Jupiter': 'Cancer',
    'Venus': 'Pisces',
    'Saturn': 'Libra',
    'Rahu': 'Taurus',
    'Ketu': 'Scorpio'
}

# Own signs
OWN_SIGNS = {
    'Sun': ['Leo'],
    'Moon': ['Cancer'],
    'Mars': ['Aries', 'Scorpio'],
    'Mercury': ['Gemini', 'Virgo'],
    'Jupiter': ['Sagittarius', 'Pisces'],
    'Venus': ['Taurus', 'Libra'],
    'Saturn': ['Capricorn', 'Aquarius'],
    'Rahu': [],
    'Ketu': []
}


class VedicChart:
    def __init__(self, birth_date, birth_time, latitude, longitude, timezone_offset):
        self.birth_date = birth_date
        self.birth_time = birth_time
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.timezone_offset = float(timezone_offset)
        self.planets = {}
        self.houses = {}
        self.ascendant_degree = 0
        self.ascendant_sign_index = 0
        
    def calculate_julian_day(self):
        """Convert datetime to Julian Day in UTC"""
        dt_str = f"{self.birth_date} {self.birth_time}"
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        
        # Adjust for timezone to get UTC
        utc_hour = dt.hour + dt.minute / 60.0 + dt.second / 3600.0 - self.timezone_offset
        
        jd = swe.julday(dt.year, dt.month, dt.day, utc_hour)
        return jd
    
    def calculate_ayanamsa(self, jd):
        """Calculate Lahiri Ayanamsa"""
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        ayanamsa = swe.get_ayanamsa_ut(jd)
        return ayanamsa
    
    def calculate_ascendant(self, jd, ayanamsa):
        """Calculate Vedic Ascendant (Lagna)"""
        # Calculate tropical ascendant using Placidus
        cusps, ascmc = swe.houses(jd, self.latitude, self.longitude, b'P')
        tropical_asc = ascmc[0]
        
        # Convert to sidereal (Vedic)
        sidereal_asc = (tropical_asc - ayanamsa) % 360
        
        # Store ascendant degree and sign index
        self.ascendant_degree = sidereal_asc
        self.ascendant_sign_index = int(sidereal_asc / 30)
        
        return sidereal_asc
    
    def get_sign_index_from_longitude(self, longitude):
        """Get sign index (0-11) from longitude"""
        # Normalize longitude to 0-360 range
        normalized_long = longitude % 360
        # Calculate sign index (each sign is 30 degrees)
        sign_index = int(normalized_long / 30)
        return sign_index
    
    def get_sign_name_from_index(self, sign_index):
        """Get sign name from sign index"""
        return ZODIAC_SIGNS[sign_index]
    
    def calculate_whole_sign_house(self, planet_longitude):
        """
        Calculate house using Whole Sign House System
        
        Logic:
        - In Whole Sign system, each zodiac sign = one house
        - The sign containing the Ascendant = 1st house
        - Next sign = 2nd house, and so on
        
        Formula: house = ((planet_sign_index - ascendant_sign_index) % 12) + 1
        
        Example:
        - Ascendant in Aries (index 0) → Aries = House 1, Taurus = House 2, etc.
        - Planet in Cancer (index 3) → House = ((3 - 0) % 12) + 1 = 4
        """
        # Get planet's sign index
        planet_sign_index = self.get_sign_index_from_longitude(planet_longitude)
        
        # Calculate house number
        # The modulo operation handles wrap-around (e.g., from Pisces to Aries)
        house_number = ((planet_sign_index - self.ascendant_sign_index) % 12) + 1
        
        return house_number
    
    def get_planetary_positions(self):
        """Calculate positions of all planets in Sidereal zodiac"""
        jd = self.calculate_julian_day()
        ayanamsa = self.calculate_ayanamsa(jd)
        
        # Calculate Ascendant FIRST (needed for house calculations)
        ascendant_long = self.calculate_ascendant(jd, ayanamsa)
        
        # Store Ascendant data
        self.planets['Ascendant'] = {
            'longitude': ascendant_long,
            'sign': self.ascendant_sign_index,
            'sign_name': ZODIAC_SIGNS[self.ascendant_sign_index],
            'degree_in_sign': ascendant_long % 30,
            'house': 1  # Ascendant is always 1st house
        }
        
        # Calculate all other planets
        for planet_name, planet_id in PLANETS.items():
            if planet_name == 'Ascendant':
                continue
                
            if planet_name == 'Ketu':
                # Ketu is 180° opposite to Rahu
                rahu_long = self.planets['Rahu']['longitude']
                vedic_position = (rahu_long + 180) % 360
            else:
                # Calculate tropical position
                position, ret = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH)
                tropical_long = position[0]
                
                # Convert to sidereal (Vedic)
                vedic_position = (tropical_long - ayanamsa) % 360
            
            # Get sign information
            sign_index = self.get_sign_index_from_longitude(vedic_position)
            sign_name = self.get_sign_name_from_index(sign_index)
            degree_in_sign = vedic_position % 30
            
            # Calculate house using Whole Sign system
            house_number = self.calculate_whole_sign_house(vedic_position)
            
            # Store planet data
            self.planets[planet_name] = {
                'longitude': vedic_position,
                'sign': sign_index,
                'sign_name': sign_name,
                'degree_in_sign': degree_in_sign,
                'house': house_number
            }
        
        return self.planets
    
    def get_planet_house(self, planet_name):
        """Get house number for a planet"""
        if planet_name in self.planets:
            return self.planets[planet_name]['house']
        return None
    
    def get_planet_sign_name(self, planet_name):
        """Get sign name for a planet"""
        if planet_name in self.planets:
            return self.planets[planet_name]['sign_name']
        return None
    
    def is_planet_exalted(self, planet_name):
        """Check if planet is exalted"""
        if planet_name not in EXALTATION_SIGNS:
            return False
        planet_sign = self.get_planet_sign_name(planet_name)
        return planet_sign == EXALTATION_SIGNS[planet_name]
    
    def is_planet_in_own_sign(self, planet_name):
        """Check if planet is in its own sign"""
        if planet_name not in OWN_SIGNS:
            return False
        planet_sign = self.get_planet_sign_name(planet_name)
        return planet_sign in OWN_SIGNS[planet_name]
    
    def is_planet_strong(self, planet_name):
        """Check if planet is strong (exalted or in own sign)"""
        return self.is_planet_exalted(planet_name) or self.is_planet_in_own_sign(planet_name)
    
    def get_ascendant_lord(self):
        """Get the lord of ascendant sign"""
        ascendant_sign = self.planets['Ascendant']['sign_name']
        return PLANET_LORDS.get(ascendant_sign)
    
    def check_planet_aspects(self, planet_name, target_house):
        """
        Check if a planet aspects a particular house
        
        Aspect Rules:
        - Jupiter: aspects 5th, 7th, 9th houses from its position
        - Saturn: aspects 3rd, 7th, 10th houses from its position
        - Mars: aspects 4th, 7th, 8th houses from its position
        - All others: aspect 7th house only
        """
        planet_house = self.get_planet_house(planet_name)
        
        if planet_house is None:
            return False
        
        if planet_name == 'Jupiter':
            # Jupiter aspects 5th, 7th, 9th from its position
            aspect_houses = [
                ((planet_house + 4 - 1) % 12) + 1,  # 5th house
                ((planet_house + 6 - 1) % 12) + 1,  # 7th house
                ((planet_house + 8 - 1) % 12) + 1   # 9th house
            ]
        elif planet_name == 'Saturn':
            # Saturn aspects 3rd, 7th, 10th from its position
            aspect_houses = [
                ((planet_house + 2 - 1) % 12) + 1,  # 3rd house
                ((planet_house + 6 - 1) % 12) + 1,  # 7th house
                ((planet_house + 9 - 1) % 12) + 1   # 10th house
            ]
        elif planet_name == 'Mars':
            # Mars aspects 4th, 7th, 8th from its position
            aspect_houses = [
                ((planet_house + 3 - 1) % 12) + 1,  # 4th house
                ((planet_house + 6 - 1) % 12) + 1,  # 7th house
                ((planet_house + 7 - 1) % 12) + 1   # 8th house
            ]
        elif planet_name in ['Rahu', 'Ketu']:
            # Rahu and Ketu aspect 7th house only
            aspect_houses = [
                ((planet_house + 6 - 1) % 12) + 1   # 7th house
            ]
        else:
            # All other planets aspect 7th house only
            aspect_houses = [
                ((planet_house + 6 - 1) % 12) + 1   # 7th house
            ]
        
        return target_house in aspect_houses


class ShrapitDoshaAnalyzer:
    def __init__(self, chart):
        self.chart = chart
    
    def analyze(self):
        """Complete Shrapit Dosha analysis with all rules"""
        result = {
            'present': False,
            'type': None,
            'severity': 'NONE',
            'severity_score': 0.0,
            'saturn_house': None,
            'rahu_house': None,
            'conjunction_house': None,
            'conjunction_sign': None,
            'degree_difference': None,
            'house_severity_info': None,
            'cancellations': [],
            'aggravations': [],
            'detailed_analysis': {},
            'recommendations': []
        }
        
        saturn_house = self.chart.get_planet_house('Saturn')
        rahu_house = self.chart.get_planet_house('Rahu')
        
        result['saturn_house'] = saturn_house
        result['rahu_house'] = rahu_house
        
        # Check for primary conjunction
        if saturn_house == rahu_house:
            result['present'] = True
            result['type'] = 'Conjunction (Primary)'
            result['conjunction_house'] = saturn_house
            result['conjunction_sign'] = self.chart.get_planet_sign_name('Saturn')
            
            # Calculate degree difference
            saturn_deg = self.chart.planets['Saturn']['longitude']
            rahu_deg = self.chart.planets['Rahu']['longitude']
            degree_diff = abs(saturn_deg - rahu_deg)
            if degree_diff > 180:
                degree_diff = 360 - degree_diff
            result['degree_difference'] = round(degree_diff, 2)
            
            # Calculate comprehensive severity
            severity_info = self.calculate_severity(saturn_house, degree_diff, result['conjunction_sign'])
            result.update(severity_info)
            
        # Check for aspect (secondary condition)
        elif self.check_saturn_aspects_rahu():
            result['present'] = True
            result['type'] = 'Aspect (Secondary - Less Severe)'
            result['severity'] = 'LOW'
            result['severity_score'] = 2.0
            result['detailed_analysis']['aspect_info'] = 'Saturn aspects Rahu but they are not conjunct'
            result['recommendations'].append('Effects are milder due to aspect only, not direct conjunction')
        
        return result
    
    def calculate_severity(self, house, degree_diff, sign_name):
        """Calculate severity with all factors"""
        severity_info = {}
        
        # Step 1: Base score from degree difference
        if degree_diff <= 5:
            base_score = 10.0
            severity_info['degree_analysis'] = f'Very tight conjunction ({degree_diff}°) - Maximum intensity'
        elif degree_diff <= 10:
            base_score = 7.0
            severity_info['degree_analysis'] = f'Tight conjunction ({degree_diff}°) - High intensity'
        else:
            base_score = 5.0
            severity_info['degree_analysis'] = f'Loose conjunction ({degree_diff}°) - Moderate intensity'
        
        severity_score = base_score
        
        # Step 2: House-based severity
        house_multipliers = {
            1: {'multiplier': 2.0, 'severity': 'VERY HIGH', 'effects': 'Physical/mental trauma, identity crisis, health issues'},
            2: {'multiplier': 1.5, 'severity': 'HIGH', 'effects': 'Family disputes, financial problems, speech issues'},
            3: {'multiplier': 0.7, 'severity': 'LOW', 'effects': 'Sibling issues (Upachaya house - can overcome with effort)'},
            4: {'multiplier': 2.0, 'severity': 'VERY HIGH', 'effects': 'Mother\'s health, property issues, no peace/happiness'},
            5: {'multiplier': 1.5, 'severity': 'HIGH', 'effects': 'Child problems, education obstacles, love failures'},
            6: {'multiplier': 0.6, 'severity': 'LOW', 'effects': 'Enemies, diseases (Upachaya - dosha fights dosha)'},
            7: {'multiplier': 2.0, 'severity': 'VERY HIGH', 'effects': 'Marriage delays/divorce, partnership failures'},
            8: {'multiplier': 2.0, 'severity': 'VERY HIGH', 'effects': 'Sudden losses, chronic diseases, surgeries'},
            9: {'multiplier': 1.2, 'severity': 'MEDIUM', 'effects': 'Father\'s health, luck blocked, spiritual obstacles'},
            10: {'multiplier': 1.2, 'severity': 'MEDIUM', 'effects': 'Career instability, professional setbacks'},
            11: {'multiplier': 0.7, 'severity': 'LOW', 'effects': 'Income problems (Upachaya - can achieve with effort)'},
            12: {'multiplier': 2.0, 'severity': 'VERY HIGH', 'effects': 'Extreme losses, debts, confinement, isolation'}
        }
        
        house_info = house_multipliers.get(house, {'multiplier': 1.0, 'severity': 'MEDIUM', 'effects': 'General obstacles'})
        severity_score *= house_info['multiplier']
        
        severity_info['house_severity_info'] = {
            'house': house,
            'base_severity': house_info['severity'],
            'primary_effects': house_info['effects'],
            'multiplier_applied': house_info['multiplier']
        }
        
        # Step 3: Sign-based modification
        sign_effects = {
            'Capricorn': {'multiplier': 1.3, 'reason': 'Saturn\'s own sign - increases intensity'},
            'Aquarius': {'multiplier': 1.3, 'reason': 'Saturn\'s own sign - increases intensity'},
            'Libra': {'multiplier': 1.2, 'reason': 'Saturn exalted - increases intensity'},
            'Pisces': {'multiplier': 0.5, 'reason': 'Watery sign, Jupiter\'s sign - greatly reduces'},
            'Sagittarius': {'multiplier': 0.7, 'reason': 'Jupiter\'s sign - reduces intensity'},
            'Cancer': {'multiplier': 0.8, 'reason': 'Jupiter exalted here - reduces intensity'},
            'Aries': {'multiplier': 0.9, 'reason': 'Saturn debilitated - slightly reduces'}
        }
        
        sign_info = sign_effects.get(sign_name, {'multiplier': 1.0, 'reason': 'Neutral sign'})
        severity_score *= sign_info['multiplier']
        
        severity_info['sign_analysis'] = {
            'sign': sign_name,
            'effect': sign_info['reason'],
            'multiplier_applied': sign_info['multiplier']
        }
        
        # Step 4: Check cancellations
        cancellations = []
        
        # Jupiter aspect (most powerful cancellation)
        if self.chart.check_planet_aspects('Jupiter', house):
            original_score = severity_score
            severity_score *= 0.3  # 70% reduction
            cancellations.append({
                'type': 'Jupiter Aspect',
                'effect': 'Greatly reduces dosha by 70%',
                'reduction': f'{original_score:.2f} → {severity_score:.2f}',
                'jupiter_house': self.chart.get_planet_house('Jupiter'),
                'strength': 'VERY STRONG'
            })
        
        # Benefic planets in Kendra/Trikona
        kendra_trikona_result = self.check_benefics_in_kendra_trikona()
        if kendra_trikona_result['present']:
            original_score = severity_score
            severity_score *= 0.8  # 20% reduction
            cancellations.append({
                'type': 'Benefic Planets in Kendra/Trikona',
                'planets': kendra_trikona_result['planets'],
                'effect': 'Reduces dosha by 20%',
                'reduction': f'{original_score:.2f} → {severity_score:.2f}',
                'strength': 'MEDIUM'
            })
        
        # Strong ascendant lord
        ascendant_lord_info = self.check_ascendant_lord_strength()
        if ascendant_lord_info['is_strong']:
            original_score = severity_score
            severity_score *= 0.85  # 15% reduction
            cancellations.append({
                'type': 'Strong Ascendant Lord',
                'lord': ascendant_lord_info['lord'],
                'reason': ascendant_lord_info['reason'],
                'effect': 'Provides resilience - 15% reduction',
                'reduction': f'{original_score:.2f} → {severity_score:.2f}',
                'strength': 'MEDIUM'
            })
        
        # Benefic yogas
        yogas = self.check_benefic_yogas()
        if yogas:
            original_score = severity_score
            severity_score *= 0.9  # 10% reduction per yoga
            cancellations.append({
                'type': 'Benefic Yogas Present',
                'yogas': yogas,
                'effect': '10% reduction',
                'reduction': f'{original_score:.2f} → {severity_score:.2f}',
                'strength': 'LOW-MEDIUM'
            })
        
        severity_info['cancellations'] = cancellations
        
        # Step 5: Check aggravations
        aggravations = []
        
        # Check for other malefic aspects
        if self.check_malefic_aspects(house):
            original_score = severity_score
            severity_score *= 1.2  # 20% increase
            aggravations.append({
                'type': 'Additional Malefic Aspects',
                'effect': 'Increases effects by 20%',
                'increase': f'{original_score:.2f} → {severity_score:.2f}'
            })
        
        severity_info['aggravations'] = aggravations
        
        # Final severity classification
        if severity_score <= 2:
            final_severity = 'VERY LOW (Nearly Cancelled)'
        elif severity_score <= 5:
            final_severity = 'LOW'
        elif severity_score <= 8:
            final_severity = 'MEDIUM'
        elif severity_score <= 12:
            final_severity = 'HIGH'
        else:
            final_severity = 'VERY HIGH'
        
        severity_info['severity'] = final_severity
        severity_info['severity_score'] = round(severity_score, 2)
        
        # Add recommendations
        recommendations = self.generate_recommendations(final_severity, cancellations, house)
        severity_info['recommendations'] = recommendations
        
        # Detailed analysis summary
        severity_info['detailed_analysis'] = {
            'base_calculation': f'Base score: {base_score} (from {degree_diff}° separation)',
            'house_impact': f'House {house} multiplier: {house_info["multiplier"]}x',
            'sign_impact': f'Sign {sign_name} multiplier: {sign_info["multiplier"]}x',
            'cancellation_count': len(cancellations),
            'aggravation_count': len(aggravations),
            'final_assessment': f'Final severity: {final_severity} (Score: {severity_score:.2f}/20)'
        }
        
        return severity_info
    
    def check_saturn_aspects_rahu(self):
        """Check if Saturn aspects Rahu (3rd, 7th, 10th)"""
        rahu_house = self.chart.get_planet_house('Rahu')
        return self.chart.check_planet_aspects('Saturn', rahu_house)
    
    def check_benefics_in_kendra_trikona(self):
        """Check for strong benefic planets in Kendra (1,4,7,10) or Trikona (1,5,9)"""
        kendra = [1, 4, 7, 10]
        trikona = [1, 5, 9]
        important_houses = set(kendra + trikona)
        
        benefics = ['Jupiter', 'Venus', 'Mercury', 'Moon']
        strong_benefics = []
        
        for planet in benefics:
            planet_house = self.chart.get_planet_house(planet)
            if planet_house in important_houses:
                if self.chart.is_planet_strong(planet):
                    strong_benefics.append({
                        'planet': planet,
                        'house': planet_house,
                        'sign': self.chart.get_planet_sign_name(planet),
                        'strength': 'Exalted' if self.chart.is_planet_exalted(planet) else 'Own Sign'
                    })
        
        return {
            'present': len(strong_benefics) > 0,
            'planets': strong_benefics
        }
    
    def check_ascendant_lord_strength(self):
        """Check if ascendant lord is strong"""
        lord = self.chart.get_ascendant_lord()
        
        if not lord:
            return {'is_strong': False, 'lord': None}
        
        is_strong = self.chart.is_planet_strong(lord)
        reason = ''
        
        if self.chart.is_planet_exalted(lord):
            reason = f'{lord} is exalted in {self.chart.get_planet_sign_name(lord)}'
        elif self.chart.is_planet_in_own_sign(lord):
            reason = f'{lord} is in own sign {self.chart.get_planet_sign_name(lord)}'
        
        return {
            'is_strong': is_strong,
            'lord': lord,
            'reason': reason
        }
    
    def check_benefic_yogas(self):
        """Check for major benefic yogas"""
        yogas = []
        
        # Gaja Kesari Yoga (Jupiter-Moon in Kendra from each other)
        jupiter_house = self.chart.get_planet_house('Jupiter')
        moon_house = self.chart.get_planet_house('Moon')
        
        house_diff = abs(jupiter_house - moon_house)
        if house_diff in [0, 3, 6, 9]:  # Kendra relationship (1, 4, 7, 10 houses apart)
            yogas.append({
                'name': 'Gaja Kesari Yoga',
                'description': 'Jupiter and Moon in Kendra - brings wisdom and prosperity'
            })
        
        # Hamsa Yoga (Jupiter in Kendra in own/exaltation)
        if jupiter_house in [1, 4, 7, 10]:
            if self.chart.is_planet_strong('Jupiter'):
                yogas.append({
                    'name': 'Hamsa Yoga (Pancha Mahapurusha)',
                    'description': 'Jupiter strong in Kendra - brings righteousness and success'
                })
        
        # Malavya Yoga (Venus in Kendra in own/exaltation)
        venus_house = self.chart.get_planet_house('Venus')
        if venus_house in [1, 4, 7, 10]:
            if self.chart.is_planet_strong('Venus'):
                yogas.append({
                    'name': 'Malavya Yoga (Pancha Mahapurusha)',
                    'description': 'Venus strong in Kendra - brings luxury and comforts'
                })
        
        return yogas
    
    def check_malefic_aspects(self, target_house):
        """Check if malefic planets (Mars, Rahu, Ketu) aspect the target house"""
        malefics = ['Mars', 'Rahu', 'Ketu']
        
        for malefic in malefics:
            if self.chart.check_planet_aspects(malefic, target_house):
                return True
        
        return False
    
    def generate_recommendations(self, severity, cancellations, house):
        """Generate personalized recommendations"""
        recommendations = []
        
        if severity in ['VERY HIGH', 'HIGH']:
            recommendations.append('🔴 CRITICAL: Perform Shrapit Dosha Nivaran Puja as soon as possible')
            recommendations.append('Chant "Om Sham Shanaishcharaya Namah" (Saturn) 108 times daily')
            recommendations.append('Chant "Om Bhram Bhreem Bhroum Sah Rahave Namah" (Rahu) 108 times daily')
            recommendations.append('Visit Shani temple every Saturday and offer mustard oil lamp')
            recommendations.append('Perform Pitra Tarpan on Amavasya (new moon day)')
            recommendations.append('Consider Pind Daan at Gaya, Haridwar, or Varanasi')
        elif severity == 'MEDIUM':
            recommendations.append('🟡 MODERATE: Regular remedies recommended')
            recommendations.append('Chant Saturn and Rahu mantras 108 times daily')
            recommendations.append('Worship Lord Hanuman on Saturdays')
            recommendations.append('Feed crows regularly (represent ancestors)')
        else:
            recommendations.append('🟢 MILD: Basic remedies sufficient')
            recommendations.append('Maintain regular spiritual practices')
            recommendations.append('Worship on Saturdays when possible')
        
        # Add cancellation-specific recommendations
        if any(c['type'] == 'Jupiter Aspect' for c in cancellations):
            recommendations.append('✅ Jupiter\'s grace is protecting you - strengthen Jupiter through yellow clothes on Thursdays')
        
        # House-specific recommendations
        house_remedies = {
            1: 'Focus on health and self-care. Meditation and yoga highly beneficial',
            4: 'Serve your mother. Donate for temples. Maintain peace at home',
            5: 'Worship Lord Ganesha for children. Education requires extra effort',
            7: 'Be patient with marriage. Worship Goddess Parvati for relationship harmony',
            8: 'Extra caution with health. Regular health checkups advised',
            12: 'Control expenses. Practice charity. Spiritual practices essential'
        }
        
        if house in house_remedies:
            recommendations.append(f'📍 House {house} specific: {house_remedies[house]}')
        
        # General recommendations
        recommendations.extend([
            'Donate black sesame seeds, black gram (urad dal), iron items on Saturdays',
            'Avoid alcohol and non-vegetarian food on Saturdays',
            'Serve elderly and physically challenged people regularly',
            'Plant and water Peepal tree on Saturdays'
        ])
        
        return recommendations


def set_ephemeris_path(ephe_path):
    """Set Swiss Ephemeris path"""
    swe.set_ephe_path(ephe_path)