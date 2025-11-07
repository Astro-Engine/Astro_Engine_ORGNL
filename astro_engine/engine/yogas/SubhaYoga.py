# subha_yogas_calc.py
from datetime import datetime, timedelta
import swisseph as swe
import math

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_api/ephe')

# Zodiac signs
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

class CompleteShubhYogaCalculator:
    def __init__(self):
        # Natural classifications
        self.natural_benefics = ['Jupiter', 'Venus', 'Moon', 'Mercury']
        self.natural_malefics = ['Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu']
        
        # House classifications
        self.kendra_houses = [1, 4, 7, 10]  # Angular houses
        self.trikona_houses = [1, 5, 9]     # Trinal houses
        self.wealth_houses = [2, 5, 9, 11]  # Wealth houses
        self.dusthana_houses = [6, 8, 12]   # Difficult houses
        self.upachaya_houses = [3, 6, 10, 11]  # Growth houses
        
        # Own signs for planets (sign indices 0-11) - VERIFIED
        self.own_signs = {
            'Sun': [4],           # Leo
            'Moon': [3],          # Cancer
            'Mars': [0, 7],       # Aries, Scorpio
            'Mercury': [2, 5],    # Gemini, Virgo
            'Jupiter': [8, 11],   # Sagittarius, Pisces
            'Venus': [1, 6],      # Taurus, Libra
            'Saturn': [9, 10]     # Capricorn, Aquarius
        }
        
        # Exaltation positions (sign index, degree) - VERIFIED
        self.exaltation_positions = {
            'Sun': (0, 10),       # 10° Aries
            'Moon': (1, 3),       # 3° Taurus
            'Mars': (9, 28),      # 28° Capricorn
            'Mercury': (5, 15),   # 15° Virgo
            'Jupiter': (3, 5),    # 5° Cancer
            'Venus': (11, 27),    # 27° Pisces
            'Saturn': (6, 20)     # 20° Libra
        }
        
        # Debilitation positions (sign index, degree) - VERIFIED
        self.debilitation_positions = {
            'Sun': (6, 10),       # 10° Libra
            'Moon': (7, 3),       # 3° Scorpio
            'Mars': (3, 28),      # 28° Cancer
            'Mercury': (11, 15),  # 15° Pisces
            'Jupiter': (9, 5),    # 5° Capricorn
            'Venus': (5, 27),     # 27° Virgo
            'Saturn': (0, 20)     # 20° Aries
        }
        
        # Moolatrikona positions (sign index, start degree, end degree)
        self.moolatrikona_positions = {
            'Sun': (4, 0, 20),    # Leo 0-20°
            'Moon': (1, 4, 30),   # Taurus 4-30°
            'Mars': (0, 0, 12),   # Aries 0-12°
            'Mercury': (5, 16, 20), # Virgo 16-20°
            'Jupiter': (8, 0, 10), # Sagittarius 0-10°
            'Venus': (6, 0, 15),  # Libra 0-15°
            'Saturn': (10, 0, 20) # Aquarius 0-20°
        }

        # Sign lords for advanced calculations
        self.sign_lords = [
            'Mars', 'Venus', 'Mercury', 'Moon', 'Sun', 'Mercury',
            'Venus', 'Mars', 'Jupiter', 'Saturn', 'Saturn', 'Jupiter'
        ]

        # Strength cache for absolute consistency
        self._strength_cache = {}

    def get_sign_index(self, longitude):
        """Get sign index from longitude"""
        return int(longitude // 30) % 12

    def get_degree_in_sign(self, longitude):
        """Get degree within sign"""
        return longitude % 30

    def calculate_angular_distance(self, lon1, lon2):
        """Calculate angular distance between two longitudes"""
        diff = abs(lon1 - lon2)
        return min(diff, 360 - diff)

    def is_mutual_kendra(self, house1, house2):
        """Check if two houses are in mutual kendra relationship"""
        diff = abs(house1 - house2)
        return diff in [0, 3, 6, 9] or (12 - diff) in [0, 3, 6, 9]

    def calculate_planetary_strength_MASTER(self, planet_name, longitude, planet_houses=None, planet_positions=None):
        """THE SINGLE SOURCE OF TRUTH FOR ALL PLANETARY STRENGTH CALCULATIONS"""
        
        # Create unique cache key
        cache_key = f"{planet_name}_{longitude}_{id(planet_houses)}_{id(planet_positions)}"
        if cache_key in self._strength_cache:
            return self._strength_cache[cache_key]
        
        if planet_name in ['Rahu', 'Ketu']:
            strength = 50.0
            self._strength_cache[cache_key] = strength
            return strength
            
        sign_index = self.get_sign_index(longitude)
        degree_in_sign = self.get_degree_in_sign(longitude)
        base_strength = 50.0
        
        # STEP 1: Check exaltation (HIGHEST PRIORITY)
        if planet_name in self.exaltation_positions:
            exalt_sign, exalt_degree = self.exaltation_positions[planet_name]
            if sign_index == exalt_sign:
                degree_diff = abs(degree_in_sign - exalt_degree)
                if degree_diff <= 1:
                    base_strength = 100.0
                elif degree_diff <= 3:
                    base_strength = 95.0
                elif degree_diff <= 5:
                    base_strength = 90.0
                elif degree_diff <= 10:
                    base_strength = 85.0
                elif degree_diff <= 15:
                    base_strength = 80.0
                else:
                    base_strength = 75.0
            else:
                base_strength = self._check_other_dignities(planet_name, sign_index, degree_in_sign)
        else:
            base_strength = self._check_other_dignities(planet_name, sign_index, degree_in_sign)
        
        # STEP 2: Apply conjunction influences
        if planet_houses and planet_positions:
            base_strength = self._apply_conjunction_influences(
                planet_name, base_strength, planet_houses, planet_positions
            )
        
        final_strength = min(base_strength, 100.0)
        self._strength_cache[cache_key] = final_strength
        return final_strength

    def _check_other_dignities(self, planet_name, sign_index, degree_in_sign):
        """Check debilitation, own sign, moolatrikona"""
        
        # Check debilitation (SECOND PRIORITY)
        if planet_name in self.debilitation_positions:
            debil_sign, debil_degree = self.debilitation_positions[planet_name]
            if sign_index == debil_sign:
                degree_diff = abs(degree_in_sign - debil_degree)
                if degree_diff <= 1:
                    return 5.0
                elif degree_diff <= 3:
                    return 10.0
                elif degree_diff <= 5:
                    return 15.0
                elif degree_diff <= 10:
                    return 20.0
                else:
                    return 25.0
        
        # Check Moolatrikona (THIRD PRIORITY)
        if planet_name in self.moolatrikona_positions:
            moola_sign, start_deg, end_deg = self.moolatrikona_positions[planet_name]
            if sign_index == moola_sign and start_deg <= degree_in_sign <= end_deg:
                return 85.0
        
        # Check own sign (FOURTH PRIORITY) - CRITICAL FIX
        if planet_name in self.own_signs and sign_index in self.own_signs[planet_name]:
            return 75.0  # STRONG for own sign
        
        # Default neutral
        return 50.0

    def _apply_conjunction_influences(self, planet_name, base_strength, planet_houses, planet_positions):
        """Apply conjunction influences uniformly"""
        planet_house = planet_houses.get(planet_name)
        if not planet_house:
            return base_strength
        
        conjunct_planets = [p for p, h in planet_houses.items() 
                           if h == planet_house and p != planet_name]
        
        strength_modifier = 0.0
        
        for conjunct_planet in conjunct_planets:
            planet_lon = planet_positions[planet_name][0]
            conjunct_lon = planet_positions[conjunct_planet][0]
            angular_distance = self.calculate_angular_distance(planet_lon, conjunct_lon)
            
            if angular_distance <= 15:
                influence_strength = (15 - angular_distance) / 15
                
                if (conjunct_planet in self.natural_benefics and 
                    planet_name in self.natural_benefics):
                    strength_modifier += 5.0 * influence_strength
                elif (conjunct_planet in self.natural_malefics and 
                      planet_name in self.natural_malefics):
                    strength_modifier -= 2.0 * influence_strength
                elif (conjunct_planet in self.natural_benefics and 
                      planet_name in self.natural_malefics):
                    strength_modifier += 3.0 * influence_strength
                elif (conjunct_planet in self.natural_malefics and 
                      planet_name in self.natural_benefics):
                    strength_modifier -= 1.0 * influence_strength
        
        return min(base_strength + strength_modifier, 100.0)

    def get_strength_category(self, strength_percentage):
        """Convert strength percentage to category"""
        if strength_percentage >= 85:
            return 'Very Strong'
        elif strength_percentage >= 70:
            return 'Strong'
        elif strength_percentage >= 55:
            return 'Moderate'
        elif strength_percentage >= 40:
            return 'Weak'
        else:
            return 'Very Weak'

    # ---- YOGAS (kept identical to your script) ----
    # All the calculate_* methods and helpers below are unchanged in logic.

    def calculate_exaltation_yogas(self, planet_houses, planet_positions):
        exaltation_yogas = []
        for planet_name, (longitude, _, _) in planet_positions.items():
            if planet_name in self.exaltation_positions:
                sign_index = self.get_sign_index(longitude)
                degree_in_sign = self.get_degree_in_sign(longitude)
                house = planet_houses.get(planet_name)
                exalt_sign, exalt_degree = self.exaltation_positions[planet_name]
                if sign_index == exalt_sign and house in (self.kendra_houses + self.trikona_houses):
                    strength = self.calculate_planetary_strength_MASTER(planet_name, longitude, planet_houses, planet_positions)
                    degree_diff = abs(degree_in_sign - exalt_degree)
                    exaltation_yogas.append({
                        'name': f'{planet_name} Exaltation Yoga',
                        'type': 'Exaltation Combination',
                        'description': f'{planet_name} exalted in {SIGNS[sign_index]} in {house}th house creates powerful yoga',
                        'strength': self.get_strength_category(strength),
                        'strength_percentage': round(strength, 2),
                        'details': {
                            'planet': planet_name,
                            'house': house,
                            'sign': SIGNS[sign_index],
                            'degree': round(degree_in_sign, 2),
                            'exaltation_degree': exalt_degree,
                            'degree_from_exact': round(degree_diff, 2),
                            'planet_strength': round(strength, 2)
                        },
                        'effects': self.get_exaltation_effects(planet_name)
                    })
        return exaltation_yogas

    def calculate_own_sign_yogas(self, planet_houses, planet_positions):
        own_sign_yogas = []
        for planet_name, (longitude, _, _) in planet_positions.items():
            if planet_name in self.own_signs:
                sign_index = self.get_sign_index(longitude)
                house = planet_houses.get(planet_name)
                if sign_index in self.own_signs[planet_name]:
                    strength = self.calculate_planetary_strength_MASTER(planet_name, longitude, planet_houses, planet_positions)
                    if (planet_name in self.natural_benefics and 
                        (house in self.wealth_houses or house in self.kendra_houses)):
                        own_sign_yogas.append({
                            'name': f'{planet_name} Own Sign Yoga',
                            'type': 'Own Sign Combination',
                            'description': f'{planet_name} in own sign {SIGNS[sign_index]} in {house}th house',
                            'strength': self.get_strength_category(strength),
                            'strength_percentage': round(strength, 2),
                            'details': {
                                'planet': planet_name,
                                'house': house,
                                'sign': SIGNS[sign_index],
                                'house_significance': self.get_house_significance_detailed(house),
                                'planet_strength': round(strength, 2)
                            },
                            'effects': self.get_own_sign_effects(planet_name, house)
                        })
        return own_sign_yogas

    def calculate_panch_mahapurusha_yogas(self, planet_houses, planet_positions):
        mahapurusha_yogas = []
        yoga_definitions = {
            'Mars': ('Ruchaka Yoga', 'Warrior personality with courage and leadership'),
            'Mercury': ('Bhadra Yoga', 'Intellectual excellence and communication skills'),
            'Jupiter': ('Hamsa Yoga', 'Wisdom, spirituality, and teaching abilities'),
            'Venus': ('Malavya Yoga', 'Artistic talents, luxury, and beauty'),
            'Saturn': ('Sasha Yoga', 'Disciplined leadership and organizational skills')
        }
        for planet, (yoga_name, description) in yoga_definitions.items():
            house = planet_houses.get(planet)
            if house and house in self.kendra_houses:
                longitude = planet_positions[planet][0]
                sign_index = self.get_sign_index(longitude)
                degree_in_sign = self.get_degree_in_sign(longitude)
                is_own_sign = sign_index in self.own_signs.get(planet, [])
                is_exalted = planet in self.exaltation_positions and sign_index == self.exaltation_positions[planet][0]
                is_moolatrikona = False
                if planet in self.moolatrikona_positions:
                    moola_sign, start_deg, end_deg = self.moolatrikona_positions[planet]
                    is_moolatrikona = sign_index == moola_sign and start_deg <= degree_in_sign <= end_deg
                if is_own_sign or is_exalted or is_moolatrikona:
                    strength = self.calculate_planetary_strength_MASTER(planet, longitude, planet_houses, planet_positions)
                    if is_exalted:
                        strength = min(strength + 15, 100)
                    elif is_own_sign or is_moolatrikona:
                        strength = min(strength + 10, 100)
                    mahapurusha_yogas.append({
                        'name': yoga_name,
                        'type': 'Mahapurusha Yoga',
                        'description': f'{planet} in kendra house creating {yoga_name} - {description}',
                        'strength': self.get_strength_category(strength),
                        'strength_percentage': round(strength, 2),
                        'details': {
                            'planet': planet,
                            'house': house,
                            'sign': SIGNS[sign_index],
                            'degree': round(degree_in_sign, 2),
                            'is_own_sign': is_own_sign,
                            'is_exalted': is_exalted,
                            'is_moolatrikona': is_moolatrikona,
                            'planet_strength': round(strength, 2)
                        },
                        'effects': self.get_mahapurusha_effects(planet)
                    })
        return mahapurusha_yogas

    def calculate_gaj_kesari_yoga(self, planet_houses, planet_positions):
        jupiter_house = planet_houses.get('Jupiter')
        moon_house = planet_houses.get('Moon')
        if jupiter_house and moon_house:
            if self.is_mutual_kendra(jupiter_house, moon_house):
                jupiter_strength = self.calculate_planetary_strength_MASTER('Jupiter', planet_positions['Jupiter'][0], planet_houses, planet_positions)
                moon_strength = self.calculate_planetary_strength_MASTER('Moon', planet_positions['Moon'][0], planet_houses, planet_positions)
                avg_strength = (jupiter_strength + moon_strength) / 2
                if jupiter_house in self.kendra_houses:
                    avg_strength += 10
                if moon_house in self.kendra_houses:
                    avg_strength += 5
                jupiter_in_dusthana = jupiter_house in self.dusthana_houses
                moon_in_dusthana = moon_house in self.dusthana_houses
                if jupiter_in_dusthana or moon_in_dusthana:
                    avg_strength *= 0.8
                avg_strength = min(avg_strength, 100)
                return {
                    'name': 'Gaj Kesari Yoga',
                    'type': 'Major Benefic Combination',
                    'description': 'Jupiter and Moon in mutual kendras - brings wisdom, prosperity, and respect',
                    'strength': self.get_strength_category(avg_strength),
                    'strength_percentage': round(avg_strength, 2),
                    'details': {
                        'jupiter_house': jupiter_house,
                        'moon_house': moon_house,
                        'jupiter_strength': round(jupiter_strength, 2),
                        'moon_strength': round(moon_strength, 2),
                        'mutual_kendra': True,
                        'afflicted': jupiter_in_dusthana or moon_in_dusthana
                    },
                    'effects': ['Wisdom and intelligence', 'Good reputation', 'Financial prosperity', 'Respect in society', 'Success in education']
                }
        return None

    def calculate_parivartana_yoga(self, planet_houses, planet_positions):
        parivartana_yogas = []
        planet_signs = {}
        for planet, (longitude, _, _) in planet_positions.items():
            if planet not in ['Rahu', 'Ketu']:
                planet_signs[planet] = self.get_sign_index(longitude)
        checked_pairs = set()
        for p1, p1_sign in planet_signs.items():
            for p2, p2_sign in planet_signs.items():
                if p1 != p2 and (p1, p2) not in checked_pairs and (p2, p1) not in checked_pairs:
                    p1_owns_p2_sign = p1 in self.own_signs and p2_sign in self.own_signs[p1]
                    p2_owns_p1_sign = p2 in self.own_signs and p1_sign in self.own_signs[p2]
                    if p1_owns_p2_sign and p2_owns_p1_sign:
                        p1_strength = self.calculate_planetary_strength_MASTER(p1, planet_positions[p1][0], planet_houses, planet_positions)
                        p2_strength = self.calculate_planetary_strength_MASTER(p2, planet_positions[p2][0], planet_houses, planet_positions)
                        avg_strength = (p1_strength + p2_strength) / 2
                        p1_house = planet_houses[p1]
                        p2_house = planet_houses[p2]
                        if (p1_house in self.kendra_houses + self.trikona_houses and 
                            p2_house in self.kendra_houses + self.trikona_houses):
                            exchange_type = "Maha Parivartana"
                            avg_strength += 15
                        elif (p1_house in self.kendra_houses + self.trikona_houses or 
                              p2_house in self.kendra_houses + self.trikona_houses):
                            exchange_type = "Kahala Parivartana"
                            avg_strength += 10
                        else:
                            exchange_type = "Simple Parivartana"
                            avg_strength += 5
                        avg_strength = min(avg_strength, 100)
                        parivartana_yogas.append({
                            'name': f'{exchange_type} Yoga',
                            'type': 'Exchange Combination',
                            'description': f'{p1} and {p2} in mutual sign exchange creating {exchange_type}',
                            'strength': self.get_strength_category(avg_strength),
                            'strength_percentage': round(avg_strength, 2),
                            'details': {
                                'planet_1': p1,
                                'planet_2': p2,
                                'planet_1_house': p1_house,
                                'planet_2_house': p2_house,
                                'planet_1_sign': SIGNS[p1_sign],
                                'planet_2_sign': SIGNS[p2_sign],
                                'exchange_type': exchange_type,
                                'combined_strength': round(avg_strength, 2)
                            },
                            'effects': self.get_parivartana_effects(exchange_type)
                        })
                        checked_pairs.add((p1, p2))
        return parivartana_yogas

    def calculate_neecha_bhanga_raj_yoga(self, planet_houses, planet_positions):
        neecha_bhanga_yogas = []
        for planet_name, (longitude, _, _) in planet_positions.items():
            if planet_name in self.debilitation_positions:
                sign_index = self.get_sign_index(longitude)
                degree_in_sign = self.get_degree_in_sign(longitude)
                debil_sign, debil_degree = self.debilitation_positions[planet_name]
                if sign_index == debil_sign:
                    house = planet_houses[planet_name]
                    cancellation_factors = []
                    strength_bonus = 0
                    if house in self.kendra_houses:
                        cancellation_factors.append('Kendra position from Ascendant')
                        strength_bonus += 30
                    debil_sign_lord = self.sign_lords[debil_sign]
                    debil_lord_house = planet_houses.get(debil_sign_lord)
                    if debil_lord_house and debil_lord_house in self.kendra_houses:
                        cancellation_factors.append('Debilitation sign lord in kendra')
                        strength_bonus += 25
                    if planet_name in self.exaltation_positions:
                        exalt_sign = self.exaltation_positions[planet_name][0]
                        exalt_lord = self.sign_lords[exalt_sign]
                        exalt_lord_house = planet_houses.get(exalt_lord)
                        if exalt_lord_house and exalt_lord_house in self.kendra_houses:
                            cancellation_factors.append('Exaltation lord in kendra')
                            strength_bonus += 25
                    conjunct_planets = [p for p, h in planet_houses.items() if h == house and p != planet_name]
                    for conj_planet in conjunct_planets:
                        conj_sign = self.get_sign_index(planet_positions[conj_planet][0])
                        if (conj_planet in self.exaltation_positions and 
                            conj_sign == self.exaltation_positions[conj_planet][0]):
                            cancellation_factors.append(f'Conjunct exalted {conj_planet}')
                            strength_bonus += 20
                            break
                    dispositor = self.sign_lords[sign_index]
                    if dispositor in conjunct_planets:
                        cancellation_factors.append(f'Conjunct dispositor {dispositor}')
                        strength_bonus += 15
                    if cancellation_factors:
                        base_strength = self.calculate_planetary_strength_MASTER(planet_name, longitude, planet_houses, planet_positions)
                        final_strength = min(base_strength + strength_bonus, 95)
                        neecha_bhanga_yogas.append({
                            'name': 'Neecha Bhanga Raj Yoga',
                            'type': 'Cancellation Yoga',
                            'description': f'{planet_name} debilitation cancelled - turns weakness into strength',
                            'strength': self.get_strength_category(final_strength),
                            'strength_percentage': round(final_strength, 2),
                            'details': {
                                'planet': planet_name,
                                'debilitated_in': SIGNS[sign_index],
                                'house': house,
                                'cancellation_factors': cancellation_factors,
                                'degree_from_exact': round(abs(degree_in_sign - debil_degree), 2),
                                'original_strength': round(base_strength, 2),
                                'final_strength': round(final_strength, 2)
                            },
                            'effects': ['Exceptional success after struggles', 'Turning adversity into advantage', 'Unique achievements', 'Late but significant success']
                        })
        return neecha_bhanga_yogas

    def calculate_chandra_mangal_yoga(self, planet_houses, planet_positions):
        moon_house = planet_houses.get('Moon')
        mars_house = planet_houses.get('Mars')
        if moon_house and mars_house:
            if moon_house == mars_house or self.is_mutual_kendra(moon_house, mars_house):
                moon_longitude = planet_positions['Moon'][0]
                mars_longitude = planet_positions['Mars'][0]
                angular_distance = self.calculate_angular_distance(moon_longitude, mars_longitude)
                moon_strength = self.calculate_planetary_strength_MASTER('Moon', moon_longitude, planet_houses, planet_positions)
                mars_strength = self.calculate_planetary_strength_MASTER('Mars', mars_longitude, planet_houses, planet_positions)
                avg_strength = (moon_strength + mars_strength) / 2
                if angular_distance <= 5:
                    avg_strength += 15
                elif angular_distance <= 10:
                    avg_strength += 10
                elif angular_distance <= 30:
                    avg_strength += 5
                if moon_house in [2, 4, 11] or mars_house in [2, 4, 11]:
                    avg_strength += 10
                avg_strength = min(avg_strength, 100)
                return {
                    'name': 'Chandra-Mangal Yoga',
                    'type': 'Wealth Combination',
                    'description': 'Moon and Mars combination creating wealth through property and investments',
                    'strength': self.get_strength_category(avg_strength),
                    'strength_percentage': round(avg_strength, 2),
                    'details': {
                        'moon_house': moon_house,
                        'mars_house': mars_house,
                        'angular_distance': round(angular_distance, 2) if moon_house == mars_house else 'Different houses',
                        'moon_strength': round(moon_strength, 2),
                        'mars_strength': round(mars_strength, 2),
                        'property_wealth': moon_house in [2, 4, 11] or mars_house in [2, 4, 11]
                    },
                    'effects': ['Wealth through real estate', 'Property ownership', 'Land investments', 'Material prosperity', 'Construction business']
                }
        return None

    def calculate_enhanced_kartari_yogas(self, planet_houses, planet_positions):
        kartari_yogas = []
        important_houses = [1, 4, 5, 7, 9, 10, 11]
        for target_house in important_houses:
            prev_house = 12 if target_house == 1 else target_house - 1
            next_house = 1 if target_house == 12 else target_house + 1
            prev_planets = [p for p, h in planet_houses.items() if h == prev_house]
            next_planets = [p for p, h in planet_houses.items() if h == next_house]
            prev_benefics = [p for p in prev_planets if p in self.natural_benefics]
            next_benefics = [p for p in next_planets if p in self.natural_benefics]
            if prev_benefics and next_benefics:
                prev_strength = sum([self.calculate_planetary_strength_MASTER(p, planet_positions[p][0], planet_houses, planet_positions) for p in prev_benefics]) / len(prev_benefics)
                next_strength = sum([self.calculate_planetary_strength_MASTER(p, planet_positions[p][0], planet_houses, planet_positions) for p in next_benefics]) / len(next_benefics)
                avg_strength = (prev_strength + next_strength) / 2
                target_planets = [p for p, h in planet_houses.items() if h == target_house]
                has_malefics = any(p in self.natural_malefics for p in target_planets)
                if has_malefics:
                    avg_strength *= 0.8
                else:
                    avg_strength *= 1.1
                if target_house in [1, 10]:
                    avg_strength += 10
                avg_strength = min(avg_strength, 100)
                kartari_yogas.append({
                    'name': 'Shubh Kartari Yoga',
                    'type': 'Protective Combination',
                    'description': f'House {target_house} protected by benefic planets on both sides',
                    'strength': self.get_strength_category(avg_strength),
                    'strength_percentage': round(avg_strength, 2),
                    'details': {
                        'target_house': target_house,
                        'target_house_significance': self.get_house_significance_detailed(target_house),
                        'previous_house_benefics': prev_benefics,
                        'next_house_benefics': next_benefics,
                        'target_planets': target_planets,
                        'has_malefics_in_target': has_malefics,
                        'protection_strength': round(avg_strength, 2)
                    },
                    'effects': self.get_kartari_effects(target_house, 'shubh')
                })
            prev_malefics = [p for p in prev_planets if p in self.natural_malefics]
            next_malefics = [p for p in next_planets if p in self.natural_malefics]
            if prev_malefics and next_malefics:
                prev_strength = sum([self.calculate_planetary_strength_MASTER(p, planet_positions[p][0], planet_houses, planet_positions) for p in prev_malefics]) / len(prev_malefics)
                next_strength = sum([self.calculate_planetary_strength_MASTER(p, planet_positions[p][0], planet_houses, planet_positions) for p in next_malefics]) / len(next_malefics)
                avg_strength = (prev_strength + next_strength) / 2 * 0.6
                kartari_yogas.append({
                    'name': 'Paap Kartari Yoga',
                    'type': 'Challenging Combination',
                    'description': f'House {target_house} hemmed by malefic planets causing challenges',
                    'strength': self.get_strength_category(avg_strength),
                    'strength_percentage': round(avg_strength, 2),
                    'details': {
                        'target_house': target_house,
                        'target_house_significance': self.get_house_significance_detailed(target_house),
                        'previous_house_malefics': prev_malefics,
                        'next_house_malefics': next_malefics,
                        'challenge_intensity': round(avg_strength, 2)
                    },
                    'effects': ['Obstacles and delays', 'Extra effort required', 'Challenges in house matters', 'Need for patience']
                })
        return kartari_yogas

    def calculate_lakshmi_yoga(self, planet_houses, planet_positions):
        lakshmi_yogas = []
        venus_house = planet_houses.get('Venus')
        if venus_house:
            venus_longitude = planet_positions['Venus'][0]
            venus_sign = self.get_sign_index(venus_longitude)
            venus_strength = self.calculate_planetary_strength_MASTER('Venus', venus_longitude, planet_houses, planet_positions)
            if (venus_house in self.kendra_houses and 
                (venus_sign in self.own_signs.get('Venus', []) or 
                 venus_sign == self.exaltation_positions.get('Venus', [None])[0])):
                benefic_support = 0
                supporting_planets = []
                for benefic in ['Jupiter', 'Moon', 'Mercury']:
                    benefic_house = planet_houses.get(benefic)
                    if benefic_house and benefic_house in self.kendra_houses + self.trikona_houses:
                        benefic_support += 1
                        supporting_planets.append(benefic)
                final_strength = venus_strength + (benefic_support * 5)
                final_strength = min(final_strength, 100)
                lakshmi_yogas.append({
                    'name': 'Lakshmi Yoga',
                    'type': 'Prosperity Combination',
                    'description': 'Venus in kendra in own sign/exaltation creating wealth and luxury',
                    'strength': self.get_strength_category(final_strength),
                    'strength_percentage': round(final_strength, 2),
                    'details': {
                        'venus_house': venus_house,
                        'venus_sign': SIGNS[venus_sign],
                        'venus_strength': round(venus_strength, 2),
                        'benefic_support_count': benefic_support,
                        'supporting_planets': supporting_planets,
                        'total_strength': round(final_strength, 2)
                    },
                    'effects': ['Wealth and luxury', 'Beautiful surroundings', 'Artistic success', 'Material comforts', 'Social status']
                })
        return lakshmi_yogas

    def calculate_saraswati_yoga(self, planet_houses, planet_positions):
        saraswati_yogas = []
        mercury_house = planet_houses.get('Mercury')
        jupiter_house = planet_houses.get('Jupiter')
        venus_house = planet_houses.get('Venus')
        if mercury_house and jupiter_house and venus_house:
            relevant_houses = self.kendra_houses + [2, 5]
            if (mercury_house in relevant_houses and 
                jupiter_house in relevant_houses and 
                venus_house in relevant_houses):
                mercury_strength = self.calculate_planetary_strength_MASTER('Mercury', planet_positions['Mercury'][0], planet_houses, planet_positions)
                jupiter_strength = self.calculate_planetary_strength_MASTER('Jupiter', planet_positions['Jupiter'][0], planet_houses, planet_positions)
                venus_strength = self.calculate_planetary_strength_MASTER('Venus', planet_positions['Venus'][0], planet_houses, planet_positions)
                avg_strength = (mercury_strength + jupiter_strength + venus_strength) / 3
                bonus_count = 0
                for planet in ['Mercury', 'Jupiter', 'Venus']:
                    planet_sign = self.get_sign_index(planet_positions[planet][0])
                    if (planet_sign in self.own_signs.get(planet, []) or 
                        planet_sign == self.exaltation_positions.get(planet, [None])[0]):
                        bonus_count += 1
                avg_strength += (bonus_count * 5)
                avg_strength = min(avg_strength, 100)
                saraswati_yogas.append({
                    'name': 'Saraswati Yoga',
                    'type': 'Knowledge Combination',
                    'description': 'Mercury, Jupiter, and Venus in kendras/2nd/5th creating wisdom and learning',
                    'strength': self.get_strength_category(avg_strength),
                    'strength_percentage': round(avg_strength, 2),
                    'details': {
                        'mercury_house': mercury_house,
                        'jupiter_house': jupiter_house,
                        'venus_house': venus_house,
                        'mercury_strength': round(mercury_strength, 2),
                        'jupiter_strength': round(jupiter_strength, 2),
                        'venus_strength': round(venus_strength, 2),
                        'planets_in_dignity': bonus_count,
                        'average_strength': round(avg_strength, 2)
                    },
                    'effects': ['Deep knowledge', 'Scholarly pursuits', 'Artistic talents', 'Teaching abilities', 'Wisdom and learning']
                })
        return saraswati_yogas

    def calculate_amala_yoga(self, planet_houses, planet_positions):
        amala_yogas = []
        tenth_house_planets = [p for p, h in planet_houses.items() if h == 10]
        pure_benefics_10th = [p for p in tenth_house_planets if p in ['Jupiter', 'Venus', 'Mercury']]
        if pure_benefics_10th:
            for planet in pure_benefics_10th:
                planet_strength = self.calculate_planetary_strength_MASTER(planet, planet_positions[planet][0], planet_houses, planet_positions)
                amala_yogas.append({
                    'name': 'Amala Yoga (from Ascendant)',
                    'type': 'Pure Combination',
                    'description': f'{planet} in 10th house creating pure reputation and career success',
                    'strength': self.get_strength_category(planet_strength),
                    'strength_percentage': round(planet_strength, 2),
                    'details': {
                        'planet': planet,
                        'position': '10th from Ascendant',
                        'planet_strength': round(planet_strength, 2)
                    },
                    'effects': ['Spotless reputation', 'Career excellence', 'Pure character', 'Social recognition', 'Professional success']
                })
        moon_house = planet_houses.get('Moon')
        if moon_house:
            tenth_from_moon = ((moon_house - 1 + 9) % 12) + 1
            tenth_from_moon_planets = [p for p, h in planet_houses.items() if h == tenth_from_moon]
            pure_benefics_10th_moon = [p for p in tenth_from_moon_planets if p in ['Jupiter', 'Venus', 'Mercury']]
            if pure_benefics_10th_moon:
                for planet in pure_benefics_10th_moon:
                    planet_strength = self.calculate_planetary_strength_MASTER(planet, planet_positions[planet][0], planet_houses, planet_positions)
                    amala_yogas.append({
                        'name': 'Amala Yoga (from Moon)',
                        'type': 'Pure Combination',
                        'description': f'{planet} in 10th from Moon creating mental purity and wisdom',
                        'strength': self.get_strength_category(planet_strength),
                        'strength_percentage': round(planet_strength, 2),
                        'details': {
                            'planet': planet,
                            'position': f'10th from Moon (house {tenth_from_moon})',
                            'moon_house': moon_house,
                            'planet_strength': round(planet_strength, 2)
                        },
                        'effects': ['Mental purity', 'Spiritual wisdom', 'Ethical conduct', 'Inner peace', 'Moral strength']
                    })
        return amala_yogas

    def calculate_stellium_yogas(self, planet_houses, planet_positions):
        stellium_yogas = []
        house_planets = {}
        for planet, house in planet_houses.items():
            if house not in house_planets:
                house_planets[house] = []
            house_planets[house].append(planet)
        for house, planets in house_planets.items():
            if len(planets) >= 3:
                total_strength = 0
                benefic_count = 0
                malefic_count = 0
                for planet in planets:
                    longitude = planet_positions[planet][0]
                    strength = self.calculate_planetary_strength_MASTER(planet, longitude, planet_houses, planet_positions)
                    total_strength += strength
                    if planet in self.natural_benefics:
                        benefic_count += 1
                    elif planet in self.natural_malefics:
                        malefic_count += 1
                avg_strength = total_strength / len(planets)
                if benefic_count > malefic_count:
                    stellium_type = "Benefic Stellium"
                    description = f"Benefic-dominant stellium in {house}th house with {len(planets)} planets"
                elif malefic_count > benefic_count:
                    stellium_type = "Malefic Stellium"
                    description = f"Malefic-dominant stellium in {house}th house with {len(planets)} planets"
                    avg_strength *= 0.8
                else:
                    stellium_type = "Mixed Stellium"
                    description = f"Mixed stellium in {house}th house with {len(planets)} planets"
                    avg_strength *= 0.9
                if house in self.kendra_houses or house in self.trikona_houses:
                    avg_strength += 10
                avg_strength = min(avg_strength, 100)
                stellium_yogas.append({
                    'name': stellium_type,
                    'type': 'Stellium Combination',
                    'description': description,
                    'strength': self.get_strength_category(avg_strength),
                    'strength_percentage': round(avg_strength, 2),
                    'details': {
                        'house': house,
                        'planets': planets,
                        'planet_count': len(planets),
                        'benefic_count': benefic_count,
                        'malefic_count': malefic_count,
                        'house_significance': self.get_house_significance_detailed(house),
                        'average_strength': round(avg_strength, 2)
                    },
                    'effects': self.get_stellium_effects(house, benefic_count, malefic_count)
                })
        return stellium_yogas

    def calculate_raj_yoga(self, planet_houses, planet_positions):
        raj_yogas = []
        for planet, house in planet_houses.items():
            if house == 1:
                strength = self.calculate_planetary_strength_MASTER(planet, planet_positions[planet][0], planet_houses, planet_positions)
                if planet in self.natural_benefics:
                    strength = min(strength + 15, 100)
                raj_yogas.append({
                    'name': 'Kendra-Trikona Raj Yoga',
                    'type': 'Royal Combination',
                    'description': f'{planet} in 1st house (both Kendra and Trikona) creates powerful Raj Yoga',
                    'strength': self.get_strength_category(strength),
                    'strength_percentage': round(strength, 2),
                    'details': {
                        'planet': planet,
                        'house': house,
                        'planet_strength': round(strength, 2),
                        'is_benefic': planet in self.natural_benefics
                    },
                    'effects': ['Leadership qualities', 'Authority and power', 'Success in career', 'High social status', 'Recognition']
                })
        kendra_planets = [(p, h) for p, h in planet_houses.items() if h in self.kendra_houses and h != 1]
        trikona_planets = [(p, h) for p, h in planet_houses.items() if h in self.trikona_houses and h != 1]
        for k_planet, k_house in kendra_planets:
            for t_planet, t_house in trikona_planets:
                if k_house == t_house and k_planet != t_planet:
                    k_strength = self.calculate_planetary_strength_MASTER(k_planet, planet_positions[k_planet][0], planet_houses, planet_positions)
                    t_strength = self.calculate_planetary_strength_MASTER(t_planet, planet_positions[t_planet][0], planet_houses, planet_positions)
                    avg_strength = (k_strength + t_strength) / 2
                    raj_yogas.append({
                        'name': 'Kendra-Trikona Conjunction Raj Yoga',
                        'type': 'Royal Combination',
                        'description': f'{k_planet} (Kendra) and {t_planet} (Trikona) conjunct in house {k_house}',
                        'strength': self.get_strength_category(avg_strength),
                        'strength_percentage': round(avg_strength, 2),
                        'details': {
                            'kendra_planet': k_planet,
                            'trikona_planet': t_planet,
                            'house': k_house,
                            'kendra_strength': round(k_strength, 2),
                            'trikona_strength': round(t_strength, 2),
                            'combined_strength': round(avg_strength, 2)
                        },
                        'effects': ['Royal status', 'Wealth and prosperity', 'Fame and recognition', 'Leadership abilities']
                    })
        return raj_yogas

    def calculate_dhana_yoga(self, planet_houses, planet_positions):
        dhana_yogas = []
        wealth_planets = []
        for planet, house in planet_houses.items():
            if house in self.wealth_houses:
                strength = self.calculate_planetary_strength_MASTER(planet, planet_positions[planet][0], planet_houses, planet_positions)
                is_benefic = planet in self.natural_benefics
                wealth_planets.append((planet, house, strength, is_benefic))
        benefic_wealth_planets = [(p, h, s) for p, h, s, is_ben in wealth_planets if is_ben]
        if len(benefic_wealth_planets) >= 2:
            total_strength = sum([s for _, _, s in benefic_wealth_planets]) / len(benefic_wealth_planets)
            dhana_yogas.append({
                'name': 'Primary Dhana Yoga',
                'type': 'Wealth Combination',
                'description': f'Multiple benefic planets in wealth houses creating strong prosperity',
                'strength': self.get_strength_category(total_strength),
                'strength_percentage': round(total_strength, 2),
                'details': {
                    'wealth_planets': [(p, h) for p, h, _ in benefic_wealth_planets],
                    'planet_count': len(benefic_wealth_planets),
                    'individual_strengths': [round(s, 2) for _, _, s in benefic_wealth_planets],
                    'average_strength': round(total_strength, 2)
                },
                'effects': ['Multiple income sources', 'Financial stability', 'Wealth accumulation', 'Material prosperity']
            })
        elif len(benefic_wealth_planets) == 1:
            planet, house, strength, = benefic_wealth_planets[0]
            if strength >= 70 or house == 11:
                dhana_yogas.append({
                    'name': 'Secondary Dhana Yoga',
                    'type': 'Wealth Combination',
                    'description': f'{planet} in {house}th house creating wealth potential',
                    'strength': self.get_strength_category(strength * 0.8),
                    'strength_percentage': round(strength * 0.8, 2),
                    'details': {
                        'planet': planet,
                        'house': house,
                        'planet_strength': round(strength, 2),
                        'wealth_house_type': 'gains' if house == 11 else 'fortune' if house in [5, 9] else 'resources'
                    },
                    'effects': ['Financial gains', 'Investment opportunities', 'Economic growth', 'Money through house significations']
                })
        return dhana_yogas

    def calculate_budh_aditya_yoga(self, planet_houses, planet_positions):
        sun_house = planet_houses.get('Sun')
        mercury_house = planet_houses.get('Mercury')
        if sun_house and mercury_house and sun_house == mercury_house:
            sun_longitude = planet_positions['Sun'][0]
            mercury_longitude = planet_positions['Mercury'][0]
            angular_distance = self.calculate_angular_distance(sun_longitude, mercury_longitude)
            is_combust = angular_distance <= 10
            is_deeply_combust = angular_distance <= 6
            is_cazimi = angular_distance <= 0.5
            sun_strength = self.calculate_planetary_strength_MASTER('Sun', sun_longitude, planet_houses, planet_positions)
            mercury_strength = self.calculate_planetary_strength_MASTER('Mercury', mercury_longitude, planet_houses, planet_positions)
            avg_strength = (sun_strength + mercury_strength) / 2
            if is_cazimi:
                avg_strength += 20
            elif is_deeply_combust:
                avg_strength *= 0.5
            elif is_combust:
                avg_strength *= 0.7
            if sun_house in self.kendra_houses or sun_house in self.trikona_houses:
                avg_strength += 10
            avg_strength = min(avg_strength, 100)
            return {
                'name': 'Budh-Aditya Yoga',
                'type': 'Benefic Combination',
                'description': 'Sun and Mercury conjunction enhancing intelligence and communication',
                'strength': self.get_strength_category(avg_strength),
                'strength_percentage': round(avg_strength, 2),
                'details': {
                    'house': sun_house,
                    'angular_distance': round(angular_distance, 2),
                    'is_combust': is_combust,
                    'is_deeply_combust': is_deeply_combust,
                    'is_cazimi': is_cazimi,
                    'sun_strength': round(sun_strength, 2),
                    'mercury_strength': round(mercury_strength, 2)
                },
                'effects': self.get_budh_aditya_effects(is_combust, is_cazimi)
            }
        return None

    def calculate_guru_mangal_yoga(self, planet_houses, planet_positions):
        jupiter_house = planet_houses.get('Jupiter')
        mars_house = planet_houses.get('Mars')
        if jupiter_house and mars_house and jupiter_house == mars_house:
            jupiter_longitude = planet_positions['Jupiter'][0]
            mars_longitude = planet_positions['Mars'][0]
            angular_distance = self.calculate_angular_distance(jupiter_longitude, mars_longitude)
            jupiter_strength = self.calculate_planetary_strength_MASTER('Jupiter', jupiter_longitude, planet_houses, planet_positions)
            mars_strength = self.calculate_planetary_strength_MASTER('Mars', mars_longitude, planet_houses, planet_positions)
            avg_strength = (jupiter_strength + mars_strength) / 2
            if jupiter_house in [3, 6, 10, 11]:
                avg_strength += 15
            if angular_distance <= 10:
                avg_strength += 10
            avg_strength = min(avg_strength, 100)
            return {
                'name': 'Guru-Mangal Yoga',
                'type': 'Technical Combination',
                'description': 'Jupiter and Mars conjunction creating technical expertise and engineering skills',
                'strength': self.get_strength_category(avg_strength),
                'strength_percentage': round(avg_strength, 2),
                'details': {
                    'house': jupiter_house,
                    'angular_distance': round(angular_distance, 2),
                    'jupiter_strength': round(jupiter_strength, 2),
                    'mars_strength': round(mars_strength, 2),
                    'technical_house': jupiter_house in [3, 6, 10, 11]
                },
                'effects': ['Technical expertise', 'Engineering abilities', 'Problem-solving skills', 'Strategic thinking', 'Innovation']
            }
        return None

    def calculate_vosi_veshi_ubhayachari_yogas(self, planet_houses, planet_positions):
        sun_house = planet_houses.get('Sun')
        if not sun_house:
            return []
        solar_yogas = []
        prev_house = 12 if sun_house == 1 else sun_house - 1
        next_house = 1 if sun_house == 12 else sun_house + 1
        exclude_planets = ['Moon', 'Rahu', 'Ketu', 'Sun']
        prev_planets = [p for p, h in planet_houses.items() if h == prev_house and p not in exclude_planets]
        next_planets = [p for p, h in planet_houses.items() if h == next_house and p not in exclude_planets]
        if prev_planets and next_planets:
            prev_strength = sum([self.calculate_planetary_strength_MASTER(p, planet_positions[p][0], planet_houses, planet_positions) for p in prev_planets]) / len(prev_planets)
            next_strength = sum([self.calculate_planetary_strength_MASTER(p, planet_positions[p][0], planet_houses, planet_positions) for p in next_planets]) / len(next_planets)
            avg_strength = (prev_strength + next_strength) / 2
            solar_yogas.append({
                'name': 'Ubhayachari Yoga',
                'type': 'Solar Combination',
                'description': f'Planets on both sides of Sun: {prev_planets} and {next_planets} - excellent leadership',
                'strength': self.get_strength_category(avg_strength),
                'strength_percentage': round(avg_strength, 2),
                'details': {
                    'sun_house': sun_house,
                    'previous_planets': prev_planets,
                    'next_planets': next_planets,
                    'previous_strength': round(prev_strength, 2),
                    'next_strength': round(next_strength, 2),
                    'combined_strength': round(avg_strength, 2)
                },
                'effects': ['Outstanding leadership', 'Fame and recognition', 'Success in all endeavors', 'Royal status']
            })
        elif prev_planets:
            prev_strength = sum([self.calculate_planetary_strength_MASTER(p, planet_positions[p][0], planet_houses, planet_positions) for p in prev_planets]) / len(prev_planets)
            solar_yogas.append({
                'name': 'Veshi Yoga',
                'type': 'Solar Combination',
                'description': f'Planets after Sun: {prev_planets} - successful ventures',
                'strength': self.get_strength_category(prev_strength * 0.8),
                'strength_percentage': round(prev_strength * 0.8, 2),
                'details': {
                    'sun_house': sun_house,
                    'following_planets': prev_planets,
                    'planets_strength': round(prev_strength, 2)
                },
                'effects': ['Business success', 'Steady progress', 'Goal achievement', 'Practical approach']
            })
        elif next_planets:
            next_strength = sum([self.calculate_planetary_strength_MASTER(p, planet_positions[p][0], planet_houses, planet_positions) for p in next_planets]) / len(next_planets)
            solar_yogas.append({
                'name': 'Vosi Yoga',
                'type': 'Solar Combination',
                'description': f'Planets before Sun: {next_planets} - independent nature',
                'strength': self.get_strength_category(next_strength * 0.8),
                'strength_percentage': round(next_strength * 0.8, 2),
                'details': {
                    'sun_house': sun_house,
                    'preceding_planets': next_planets,
                    'planets_strength': round(next_strength, 2)
                },
                'effects': ['Independent thinking', 'Self-reliance', 'Initiative', 'Pioneering spirit']
            })
        return solar_yogas

    # ----- Helper effect & description methods (unchanged) -----

    def get_exaltation_effects(self, planet):
        effects_map = {
            'Sun': ['Powerful leadership', 'Government favor', 'Authority and respect', 'Success in politics', 'Strong willpower'],
            'Moon': ['Emotional stability', 'Public popularity', 'Success with masses', 'Nurturing abilities', 'Intuitive wisdom'],
            'Mars': ['Exceptional courage', 'Military success', 'Physical strength', 'Competitive victories', 'Land ownership'],
            'Mercury': ['Brilliant intellect', 'Communication mastery', 'Business acumen', 'Technical expertise', 'Learning abilities'],
            'Jupiter': ['Supreme wisdom', 'Spiritual leadership', 'Teaching excellence', 'Religious authority', 'Moral character'],
            'Venus': ['Artistic genius', 'Luxury and beauty', 'Romantic success', 'Creative talents', 'Diplomatic skills'],
            'Saturn': ['Disciplined success', 'Long-term achievements', 'Organizational mastery', 'Justice and fairness', 'Patience']
        }
        return effects_map.get(planet, ['Enhanced planetary qualities'])

    def get_own_sign_effects(self, planet, house):
        base_effects = {
            'Sun': ['Strong personality', 'Leadership abilities', 'Recognition'],
            'Moon': ['Emotional strength', 'Nurturing qualities', 'Public connection'],
            'Mars': ['Energy and courage', 'Competitive spirit', 'Action-oriented'],
            'Mercury': ['Intelligence', 'Communication skills', 'Analytical abilities'],
            'Jupiter': ['Wisdom', 'Teaching abilities', 'Spiritual growth'],
            'Venus': ['Artistic talents', 'Luxury', 'Relationship harmony'],
            'Saturn': ['Discipline', 'Hard work', 'Long-term success']
        }
        house_effects = {
            2: ['Financial prosperity', 'Speech abilities', 'Family wealth'],
            5: ['Intelligence', 'Creative abilities', 'Good children'],
            9: ['Fortune and luck', 'Higher learning', 'Spiritual growth'],
            11: ['Gains and profits', 'Friend circle', 'Achievement of desires']
        }
        effects = base_effects.get(planet, ['Planetary strength'])
        if house in house_effects:
            effects.extend(house_effects[house])
        return effects

    def get_mahapurusha_effects(self, planet):
        effects_map = {
            'Mars': ['Courage and bravery', 'Military leadership', 'Physical strength', 'Competitive success', 'Land ownership'],
            'Mercury': ['Intellectual brilliance', 'Communication mastery', 'Business success', 'Analytical skills', 'Writing abilities'],
            'Jupiter': ['Spiritual wisdom', 'Teaching excellence', 'Moral leadership', 'Religious authority', 'Scholarly recognition'],
            'Venus': ['Artistic mastery', 'Luxury and comfort', 'Beauty and charm', 'Creative success', 'Diplomatic skills'],
            'Saturn': ['Disciplined leadership', 'Organizational excellence', 'Long-term success', 'Administrative skills', 'Perseverance']
        }
        return effects_map.get(planet, ['General beneficial effects'])

    def get_parivartana_effects(self, exchange_type):
        effects_map = {
            'Maha Parivartana': ['Exceptional success', 'Royal status', 'Wealth and fame', 'Leadership positions', 'Complete fulfillment'],
            'Kahala Parivartana': ['Good fortune', 'Success in endeavors', 'Recognition', 'Prosperity', 'Achievement of goals'],
            'Simple Parivartana': ['Mutual support', 'Balanced results', 'Cooperation', 'Exchange of benefits', 'Steady progress']
        }
        return effects_map.get(exchange_type, ['Mutual planetary support'])

    def get_stellium_effects(self, house, benefic_count, malefic_count):
        house_effects = {
            1: ['Strong personality', 'Leadership abilities', 'Self-focus'],
            2: ['Financial focus', 'Speech abilities', 'Family matters'],
            3: ['Communication skills', 'Sibling relationships', 'Short travels'],
            4: ['Home and property', 'Mother\'s influence', 'Emotional foundation'],
            5: ['Intelligence concentration', 'Creative abilities', 'Children focus'],
            6: ['Service orientation', 'Health focus', 'Competitive nature'],
            7: ['Relationship focus', 'Partnership abilities', 'Public dealings'],
            8: ['Transformation', 'Research abilities', 'Hidden knowledge'],
            9: ['Higher learning', 'Spiritual focus', 'Fortune and luck'],
            10: ['Career concentration', 'Public recognition', 'Professional success'],
            11: ['Gains and profits', 'Social networks', 'Achievement focus'],
            12: ['Spiritual inclination', 'Foreign connections', 'Charitable nature']
        }
        base_effects = house_effects.get(house, ['Concentrated energy in house matters'])
        if benefic_count > malefic_count:
            base_effects.append('Generally positive outcomes')
        elif malefic_count > benefic_count:
            base_effects.append('Challenges requiring effort')
        else:
            base_effects.append('Mixed results requiring balance')
        return base_effects

    def get_budh_aditya_effects(self, is_combust, is_cazimi):
        if is_cazimi:
            return ['Brilliant intelligence', 'Royal favor', 'Exceptional communication', 'Leadership in learning', 'Divine wisdom']
        elif is_combust:
            return ['Moderate intelligence boost', 'Possible ego in communication', 'Need to balance pride', 'Periodic confusion']
        else:
            return ['Enhanced intelligence', 'Excellent communication', 'Learning abilities', 'Writing talents', 'Intellectual recognition']

    def get_kartari_effects(self, house, kartari_type):
        if kartari_type == 'shubh':
            house_effects = {
                1: ['Protected personality', 'Good health', 'Success in endeavors', 'Positive self-image'],
                4: ['Happy home life', 'Property protection', 'Mother\'s blessings', 'Emotional stability'],
                5: ['Intelligence protection', 'Success in education', 'Good children', 'Creative abilities'],
                7: ['Harmonious relationships', 'Good marriage', 'Business partnerships', 'Diplomatic success'],
                9: ['Fortune and luck', 'Higher learning', 'Spiritual growth', 'Father\'s blessings'],
                10: ['Career success', 'Good reputation', 'Professional growth', 'Recognition'],
                11: ['Financial gains', 'Achievement of goals', 'Supportive friends', 'Profitable ventures']
            }
        else:
            house_effects = {
                1: ['Challenges to personality', 'Health issues', 'Obstacles in endeavors'],
                4: ['Home troubles', 'Property issues', 'Emotional disturbances'],
                5: ['Educational challenges', 'Children problems', 'Creative blocks'],
                7: ['Relationship difficulties', 'Marriage problems', 'Partnership issues'],
                9: ['Fortune obstacles', 'Learning difficulties', 'Spiritual challenges'],
                10: ['Career obstacles', 'Reputation issues', 'Professional struggles'],
                11: ['Financial losses', 'Goal obstacles', 'Friend troubles']
            }
        return house_effects.get(house, ['General protection' if kartari_type == 'shubh' else 'General challenges'])

    def get_house_significance_detailed(self, house):
        house_meanings = {
            1: 'Self, personality, and physical body',
            2: 'Wealth, family, and speech',
            3: 'Communication, siblings, and courage',
            4: 'Home, mother, and emotional foundation',
            5: 'Intelligence, children, and creativity',
            6: 'Service, health, and daily work',
            7: 'Marriage, partnerships, and public relations',
            8: 'Transformation, research, and hidden matters',
            9: 'Fortune, higher learning, and spirituality',
            10: 'Career, reputation, and public recognition',
            11: 'Gains, friends, and achievement of desires',
            12: 'Spirituality, foreign lands, and expenses'
        }
        return house_meanings.get(house, f'House {house} matters')

    def analyze_all_shubh_yogas(self, planet_houses, planet_positions):
        self._strength_cache.clear()
        all_yogas = []
        exaltation_yogas = self.calculate_exaltation_yogas(planet_houses, planet_positions)
        all_yogas.extend(exaltation_yogas)
        own_sign_yogas = self.calculate_own_sign_yogas(planet_houses, planet_positions)
        all_yogas.extend(own_sign_yogas)
        stellium_yogas = self.calculate_stellium_yogas(planet_houses, planet_positions)
        all_yogas.extend(stellium_yogas)
        raj_yogas = self.calculate_raj_yoga(planet_houses, planet_positions)
        all_yogas.extend(raj_yogas)
        mahapurusha_yogas = self.calculate_panch_mahapurusha_yogas(planet_houses, planet_positions)
        all_yogas.extend(mahapurusha_yogas)
        gaj_kesari = self.calculate_gaj_kesari_yoga(planet_houses, planet_positions)
        if gaj_kesari:
            all_yogas.append(gaj_kesari)
        dhana_yogas = self.calculate_dhana_yoga(planet_houses, planet_positions)
        all_yogas.extend(dhana_yogas)
        budh_aditya = self.calculate_budh_aditya_yoga(planet_houses, planet_positions)
        if budh_aditya:
            all_yogas.append(budh_aditya)
        guru_mangal = self.calculate_guru_mangal_yoga(planet_houses, planet_positions)
        if guru_mangal:
            all_yogas.append(guru_mangal)
        chandra_mangal = self.calculate_chandra_mangal_yoga(planet_houses, planet_positions)
        if chandra_mangal:
            all_yogas.append(chandra_mangal)
        parivartana_yogas = self.calculate_parivartana_yoga(planet_houses, planet_positions)
        all_yogas.extend(parivartana_yogas)
        neecha_bhanga_yogas = self.calculate_neecha_bhanga_raj_yoga(planet_houses, planet_positions)
        all_yogas.extend(neecha_bhanga_yogas)
        kartari_yogas = self.calculate_enhanced_kartari_yogas(planet_houses, planet_positions)
        all_yogas.extend(kartari_yogas)
        solar_yogas = self.calculate_vosi_veshi_ubhayachari_yogas(planet_houses, planet_positions)
        all_yogas.extend(solar_yogas)
        lakshmi_yogas = self.calculate_lakshmi_yoga(planet_houses, planet_positions)
        all_yogas.extend(lakshmi_yogas)
        saraswati_yogas = self.calculate_saraswati_yoga(planet_houses, planet_positions)
        all_yogas.extend(saraswati_yogas)
        amala_yogas = self.calculate_amala_yoga(planet_houses, planet_positions)
        all_yogas.extend(amala_yogas)
        return all_yogas


def get_house_whole_sign(lon, asc_sign_index):
    """Calculate house number using Whole Sign system"""
    sign_index = int(lon // 30) % 12
    house_index = (sign_index - asc_sign_index) % 12
    return house_index + 1


def longitude_to_sign(deg):
    """Convert longitude to sign and degree within sign"""
    deg = deg % 360
    sign_index = int(deg // 30)
    sign = SIGNS[sign_index]
    sign_deg = deg % 30
    return sign, sign_deg, sign_index


def add_SubhaYogas(birth_data: dict):
    """
    Entry point that performs the exact same calculations as the original /shubh-yogas route,
    returning a pure Python dict (no jsonify, no Flask).
    """
    # Validate required fields (same messages)
    required = ['user_name', 'birth_date', 'birth_time', 'latitude', 'longitude', 'timezone_offset']
    if not birth_data:
        raise ValueError("No JSON data provided")
    if not all(key in birth_data for key in required):
        raise ValueError("Missing required parameters")

    # Extract and validate coordinates
    latitude = float(birth_data['latitude'])
    longitude = float(birth_data['longitude'])
    timezone_offset = float(birth_data['timezone_offset'])
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        raise ValueError("Invalid latitude or longitude")

    # Parse date and time
    birth_date = datetime.strptime(birth_data['birth_date'], '%Y-%m-%d')
    birth_time = datetime.strptime(birth_data['birth_time'], '%H:%M:%S').time()
    local_datetime = datetime.combine(birth_date, birth_time)
    ut_datetime = local_datetime - timedelta(hours=timezone_offset)

    # Convert to Julian Day
    hour_decimal = ut_datetime.hour + ut_datetime.minute / 60.0 + ut_datetime.second / 3600.0
    jd_ut = swe.julday(ut_datetime.year, ut_datetime.month, ut_datetime.day, hour_decimal)

    # Set Lahiri ayanamsa
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa_value = swe.get_ayanamsa_ut(jd_ut)

    # Calculate planetary positions
    planets = [
        (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MARS, 'Mars'),
        (swe.MERCURY, 'Mercury'), (swe.JUPITER, 'Jupiter'), (swe.VENUS, 'Venus'),
        (swe.SATURN, 'Saturn'), (swe.TRUE_NODE, 'Rahu')
    ]
    flag = swe.FLG_SIDEREAL | swe.FLG_SPEED
    planet_positions = {}
    for planet_id, planet_name in planets:
        pos, ret = swe.calc_ut(jd_ut, planet_id, flag)
        if ret < 0:
            raise RuntimeError(f"Error calculating {planet_name}")
        lon = pos[0] % 360
        speed = pos[3]
        retrograde = 'R' if speed < 0 else ''
        planet_positions[planet_name] = (lon, retrograde, speed)

    # Calculate Ketu as 180° opposite Rahu
    rahu_lon = planet_positions['Rahu'][0]
    ketu_lon = (rahu_lon + 180) % 360
    planet_positions['Ketu'] = (ketu_lon, '', 0)

    # Calculate Ascendant using Whole Sign system
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    ascendant_lon = ascmc[0] % 360
    asc_sign_index = int(ascendant_lon // 30)

    # Calculate house positions for all planets
    planet_houses = {}
    for planet_name, (lon, _, _) in planet_positions.items():
        house = get_house_whole_sign(lon, asc_sign_index)
        planet_houses[planet_name] = house

    # Initialize Complete Shubh Yoga Calculator
    yoga_calculator = CompleteShubhYogaCalculator()

    # Analyze ALL Shubh Yogas
    all_yogas = yoga_calculator.analyze_all_shubh_yogas(planet_houses, planet_positions)

    # Categorize yogas by strength
    very_strong_yogas = [y for y in all_yogas if y.get('strength') == 'Very Strong']
    strong_yogas = [y for y in all_yogas if y.get('strength') == 'Strong']
    moderate_yogas = [y for y in all_yogas if y.get('strength') == 'Moderate']
    weak_yogas = [y for y in all_yogas if y.get('strength') in ['Weak', 'Very Weak']]

    # Calculate overall yoga strength
    if all_yogas:
        total_strength = sum([y.get('strength_percentage', 50) for y in all_yogas]) / len(all_yogas)
        overall_category = yoga_calculator.get_strength_category(total_strength)
    else:
        total_strength = 0
        overall_category = 'No Yogas'

    # Detailed planetary info with unified strength calc
    detailed_planets = {}
    for planet_name, (lon, retro, speed) in planet_positions.items():
        sign, sign_deg, sign_index = longitude_to_sign(lon)
        house = planet_houses[planet_name]
        strength = yoga_calculator.calculate_planetary_strength_MASTER(planet_name, lon, planet_houses, planet_positions)
        detailed_planets[planet_name] = {
            'longitude': round(lon, 6),
            'sign': sign,
            'sign_index': sign_index,
            'degree_in_sign': round(sign_deg, 4),
            'house': house,
            'retrograde': retro,
            'speed': round(speed, 6),
            'strength_percentage': round(strength, 2),
            'strength_category': yoga_calculator.get_strength_category(strength)
        }

    # Build response (identical fields/structure)
    response = {
        "user_name": birth_data['user_name'],
        "birth_details": {
            "birth_date": birth_data['birth_date'],
            "birth_time": birth_data['birth_time'],
            "latitude": latitude,
            "longitude": longitude,
            "timezone_offset": timezone_offset,
            "ayanamsa": "Lahiri",
            "ayanamsa_value": round(ayanamsa_value, 6),
            "house_system": "Whole Sign"
        },
        "ascendant": {
            "sign": SIGNS[asc_sign_index],
            "longitude": round(ascendant_lon, 6),
            "degree_in_sign": round(ascendant_lon % 30, 4)
        },
        "planetary_positions": detailed_planets,
        "shubh_yoga_analysis": {
            "total_yogas_found": len(all_yogas),
            "overall_strength": round(total_strength, 2),
            "overall_category": overall_category,
            "summary": {
                "very_strong": len(very_strong_yogas),
                "strong": len(strong_yogas),
                "moderate": len(moderate_yogas),
                "weak": len(weak_yogas)
            },
            "yogas_by_category": {
                "very_strong": very_strong_yogas,
                "strong": strong_yogas,
                "moderate": moderate_yogas,
                "weak": weak_yogas
            },
            "all_yogas": all_yogas
        },
        "calculation_info": {
            "calculation_timestamp": datetime.now().isoformat(),
            "ephemeris": "Swiss Ephemeris",
            "coordinate_system": "Sidereal (Tropical - Ayanamsa)",
            "precision": "COMPLETE comprehensive yoga analysis with ALL classical combinations",
            "yoga_count": len(all_yogas),
            "comprehensive_coverage": [
                "✅ All Pancha Mahapurusha Yogas (Ruchaka, Bhadra, Hamsa, Malavya, Sasha)",
                "✅ Complete Gaj Kesari Yoga",
                "✅ All Parivartana (Exchange) Yogas (Maha, Kahala, Simple)",
                "✅ Complete Neecha Bhanga Raj Yoga with all cancellation factors",
                "✅ Chandra-Mangal Yoga (Moon-Mars wealth combination)",
                "✅ Enhanced Kartari Yogas (both Shubh and Paap)",
                "✅ Lakshmi, Saraswati, Amala Yogas",
                "✅ Complete Solar Yogas (Vosi, Veshi, Ubhayachari)",
                "✅ All Classical Raj and Dhana Yogas",
                "✅ Complete Budh-Aditya and Guru-Mangal Yogas",
                "✅ Comprehensive Stellium Analysis",
                "✅ UNIFIED consistent strength calculations throughout",
                "✅ Venus own sign strength fixed to 75% (Strong category)",
                "✅ All conjunction influences properly applied"
            ]
        }
    }

    return response
