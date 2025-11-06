# daridra_calculations.py
import swisseph as swe
from datetime import datetime, timedelta

# Set Swiss Ephemeris path and ayanamsa
swe.set_ephe_path('astro_api/ephe')

# -------------------------
# Astrological Constants (unchanged)
# -------------------------
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

HOUSE_LORDS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
    'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
    'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}

NATURAL_BENEFICS = ['Jupiter', 'Venus', 'Mercury', 'Moon']
NATURAL_MALEFICS = ['Saturn', 'Mars', 'Rahu', 'Ketu', 'Sun']
DUSTHANA_HOUSES = [6, 8, 12]
WEALTH_HOUSES = [2, 11]
KENDRA_HOUSES = [1, 4, 7, 10]
TRIKONA_HOUSES = [1, 5, 9]

DEBILITATION_POINTS = {
    'Sun': ('Libra', 10), 'Moon': ('Scorpio', 3), 'Mars': ('Cancer', 28),
    'Mercury': ('Pisces', 15), 'Jupiter': ('Capricorn', 5), 
    'Venus': ('Virgo', 27), 'Saturn': ('Aries', 20)
}

EXALTATION_POINTS = {
    'Sun': ('Aries', 10), 'Moon': ('Taurus', 3), 'Mars': ('Capricorn', 28),
    'Mercury': ('Virgo', 15), 'Jupiter': ('Cancer', 5),
    'Venus': ('Pisces', 27), 'Saturn': ('Libra', 20)
}

PLANET_ASPECTS = {
    'Sun': [7], 'Moon': [7], 'Mercury': [7], 'Venus': [7],
    'Mars': [4, 7, 8], 'Jupiter': [5, 7, 9], 'Saturn': [3, 7, 10],
    'Rahu': [5, 7, 9], 'Ketu': [5, 7, 9]
}

# -------------------------
# Utilities (exact logic)
# -------------------------
def longitude_to_sign_degree(deg):
    """Convert longitude to sign and degree within sign"""
    deg = deg % 360
    sign_index = int(deg // 30)
    sign = SIGNS[sign_index]
    sign_deg = deg % 30
    return sign, sign_deg

def get_house_whole_sign(lon, asc_sign_index):
    """Calculate house number using Whole Sign system"""
    sign_index = int(lon // 30) % 12
    house_index = (sign_index - asc_sign_index) % 12
    return house_index + 1

# -------------------------
# Core Calculator (unchanged logic)
# -------------------------
class EnhancedDaridraYogaCalculator:
    """Complete Enhanced Daridra Yoga calculator with all improvements"""
    
    def __init__(self, planetary_data, ascendant_sign, jd_ut, latitude, longitude):
        self.planetary_data = planetary_data
        self.ascendant_sign = ascendant_sign
        self.jd_ut = jd_ut
        self.latitude = latitude
        self.longitude = longitude
        self.house_lords = self._calculate_house_lords()
        self.navamsa_data = self._calculate_navamsa()
        self.detected_yogas = []
        
    def _calculate_house_lords(self):
        asc_index = SIGNS.index(self.ascendant_sign)
        house_lords = {}
        for house in range(1, 13):
            sign_index = (asc_index + house - 1) % 12
            sign_name = SIGNS[sign_index]
            house_lords[house] = HOUSE_LORDS[sign_name]
        return house_lords
    
    def _calculate_navamsa(self):
        navamsa_positions = {}
        for planet, data in self.planetary_data.items():
            if planet == 'Ketu':
                rahu_navamsa = navamsa_positions.get('Rahu')
                if rahu_navamsa:
                    ketu_navamsa_index = (SIGNS.index(rahu_navamsa) + 6) % 12
                    navamsa_positions['Ketu'] = SIGNS[ketu_navamsa_index]
                continue
            longitude = data['longitude']
            sign_num = int(longitude // 30)
            degree_in_sign = longitude % 30
            navamsa_num = int(degree_in_sign * 9 / 30)
            if sign_num in [0, 3, 6, 9]:
                navamsa_sign_index = (navamsa_num) % 12
            elif sign_num in [1, 4, 7, 10]:
                navamsa_sign_index = (navamsa_num + 3) % 12
            else:
                navamsa_sign_index = (navamsa_num + 6) % 12
            navamsa_positions[planet] = SIGNS[navamsa_sign_index]
        return navamsa_positions
    
    def _get_planet_aspects(self, planet, from_house):
        if planet not in PLANET_ASPECTS:
            return [7]
        aspects = []
        for aspect in PLANET_ASPECTS[planet]:
            aspected_house = ((from_house + aspect - 1) % 12) + 1
            aspects.append(aspected_house)
        return aspects
    
    def _is_planet_debilitated(self, planet, sign, degree):
        if planet not in DEBILITATION_POINTS:
            return False, "none"
        deb_sign, deb_degree = DEBILITATION_POINTS[planet]
        if sign == deb_sign:
            degree_diff = abs(degree - deb_degree)
            if degree_diff <= 5:
                return True, "exact"
            else:
                return True, "sign"
        return False, "none"
    
    def _is_planet_exalted(self, planet, sign, degree):
        if planet not in EXALTATION_POINTS:
            return False, "none"
        exalt_sign, exalt_degree = EXALTATION_POINTS[planet]
        if sign == exalt_sign:
            degree_diff = abs(degree - exalt_degree)
            if degree_diff <= 5:
                return True, "exact"
            else:
                return True, "sign"
        return False, "none"
    
    def _get_maraka_lords(self):
        return [self.house_lords[2], self.house_lords[7]]
    
    def _planets_in_same_house(self, planet1, planet2):
        return self.planetary_data[planet1]['house'] == self.planetary_data[planet2]['house']
    
    def _planet_aspects_house(self, planet, target_house):
        planet_house = self.planetary_data[planet]['house']
        aspected_houses = self._get_planet_aspects(planet, planet_house)
        return target_house in aspected_houses
    
    def _planet_aspects_planet(self, aspecting_planet, target_planet):
        target_house = self.planetary_data[target_planet]['house']
        return self._planet_aspects_house(aspecting_planet, target_house)
    
    def _get_planets_aspecting(self, target_planet):
        aspecting_planets = []
        for planet in self.planetary_data:
            if planet != target_planet and self._planet_aspects_planet(planet, target_planet):
                aspecting_planets.append(planet)
        return aspecting_planets
    
    # ------------ All checks (unchanged) ------------
    def detect_all_daridra_yogas(self):
        self.detected_yogas = []
        self._check_basic_formation_1()
        self._check_basic_formation_2()
        self._check_basic_formation_3_enhanced()
        self._check_basic_formation_4()
        self._check_type_a_exchange()
        self._check_type_b_exchange()
        self._check_type_c_ketu_moon()
        self._check_type_d_eighth_house()
        self._check_type_e_malefic_combination()
        self._check_type_f_association_enhanced()
        self._check_type_g_fifth_lord()
        self._check_type_h_fifth_lord_aspect()
        self._check_type_i_natural_malefic()
        self._check_type_j_dual_affliction()
        self._check_kemadruma_yoga()
        self._check_sakata_yoga()
        self._check_dharidra_yoga()
        self._check_sixth_house_stellium()
        self._check_moon_ketu_conjunction_12th()
        return {
            "total_daridra_yogas": len(self.detected_yogas),
            "detected_yogas": self.detected_yogas,
            "overall_severity": self._calculate_overall_severity(),
            "financial_outlook": self._get_financial_outlook(),
            "cancellation_factors": self._check_cancellation_factors_corrected()
        }
    
    # --- all the _check_* methods and helpers remain IDENTICAL to previous message ---
    # (omitted here for brevity; keep exactly as provided earlier)
    # >>> START of unchanged block
    def _check_basic_formation_1(self):
        eleventh_lord = self.house_lords[11]
        eleventh_lord_house = self.planetary_data[eleventh_lord]['house']
        if eleventh_lord_house in DUSTHANA_HOUSES:
            self.detected_yogas.append({
                "type": "Basic Formation 1",
                "name": "11th Lord in Dusthana",
                "description": f"11th house lord {eleventh_lord} is in {eleventh_lord_house}th house",
                "severity": "Medium",
                "effect": "Irregular income, difficulty in gains",
                "planets_involved": [eleventh_lord],
                "houses_involved": [11, eleventh_lord_house],
                "formation_strength": "Active"
            })
    def _check_basic_formation_2(self):
        second_lord = self.house_lords[2]
        second_lord_house = self.planetary_data[second_lord]['house']
        if second_lord_house in DUSTHANA_HOUSES:
            self.detected_yogas.append({
                "type": "Basic Formation 2",
                "name": "2nd Lord in Dusthana",
                "description": f"2nd house lord {second_lord} is in {second_lord_house}th house",
                "severity": "High",
                "effect": "Loss of family wealth, financial expenses",
                "planets_involved": [second_lord],
                "houses_involved": [2, second_lord_house],
                "formation_strength": "Strong"
            })
    def _check_basic_formation_3_enhanced(self):
        jupiter_sign = self.planetary_data['Jupiter']['sign']
        jupiter_degree = self.planetary_data['Jupiter']['degree_in_sign']
        jupiter_house = self.planetary_data['Jupiter']['house']
        is_debilitated, debil_type = self._is_planet_debilitated('Jupiter', jupiter_sign, jupiter_degree)
        malefic_afflictions = []
        aspecting_planets = self._get_planets_aspecting('Jupiter')
        for planet in aspecting_planets:
            if planet in NATURAL_MALEFICS:
                malefic_afflictions.append(f"aspected by {planet}")
        for malefic in NATURAL_MALEFICS:
            if self._planets_in_same_house('Jupiter', malefic):
                malefic_afflictions.append(f"conjunct {malefic}")
        yoga_exists = False
        severity = "Medium"
        formation_strength = "Weak"
        if is_debilitated and debil_type == "exact":
            yoga_exists = True; severity = "Very High"; formation_strength = "Very Strong"
        elif is_debilitated and debil_type == "sign" and len(malefic_afflictions) >= 1:
            yoga_exists = True; severity = "High"; formation_strength = "Strong"
        elif len(malefic_afflictions) >= 3:
            yoga_exists = True; severity = "High"; formation_strength = "Medium"
        elif len(malefic_afflictions) >= 2:
            yoga_exists = True; severity = "Medium-High"; formation_strength = "Medium"
        if yoga_exists:
            affliction_desc = " and ".join(malefic_afflictions) if malefic_afflictions else ""
            description = f"Jupiter in {jupiter_sign}"
            if is_debilitated:
                description += f" ({debil_type} debilitation)"
            if affliction_desc:
                description += f" {affliction_desc}"
            self.detected_yogas.append({
                "type": "Basic Formation 3",
                "name": "Jupiter Afflicted",
                "description": description,
                "severity": severity,
                "effect": "Poor financial wisdom, bad investment decisions",
                "planets_involved": ['Jupiter'] + [p.split()[-1] for p in malefic_afflictions if 'aspected by' in p or 'conjunct' in p],
                "houses_involved": [jupiter_house],
                "formation_strength": formation_strength
            })
    def _check_basic_formation_4(self):
        second_lord = self.house_lords[2]
        eleventh_lord = self.house_lords[11]
        second_lord_house = self.planetary_data[second_lord]['house']
        eleventh_lord_house = self.planetary_data[eleventh_lord]['house']
        second_weak = (second_lord_house in DUSTHANA_HOUSES or 
                       self._is_planet_debilitated(second_lord, 
                            self.planetary_data[second_lord]['sign'],
                            self.planetary_data[second_lord]['degree_in_sign'])[0])
        eleventh_weak = (eleventh_lord_house in DUSTHANA_HOUSES or
                         self._is_planet_debilitated(eleventh_lord,
                            self.planetary_data[eleventh_lord]['sign'], 
                            self.planetary_data[eleventh_lord]['degree_in_sign'])[0])
        if second_weak and eleventh_weak:
            self.detected_yogas.append({
                "type": "Basic Formation 4", 
                "name": "Double Wealth House Affliction",
                "description": f"Both 2nd lord {second_lord} and 11th lord {eleventh_lord} are weak",
                "severity": "Very High",
                "effect": "Complete lack of money accumulation",
                "planets_involved": [second_lord, eleventh_lord],
                "houses_involved": [2, 11, second_lord_house, eleventh_lord_house],
                "formation_strength": "Very Strong"
            })
    def _check_type_a_exchange(self):
        lagna_lord = self.house_lords[1]
        twelfth_lord = self.house_lords[12]
        seventh_lord = self.house_lords[7]
        lagna_lord_house = self.planetary_data[lagna_lord]['house']
        twelfth_lord_house = self.planetary_data[twelfth_lord]['house']
        exchange = (lagna_lord_house == 12 and twelfth_lord_house == 1)
        seventh_lord_influence = (self._planet_aspects_planet(seventh_lord, lagna_lord) or
                                  self._planet_aspects_planet(seventh_lord, twelfth_lord))
        if exchange and seventh_lord_influence:
            self.detected_yogas.append({
                "type": "Type A - Exchange Yoga",
                "name": "Lagna-12th Perfect Exchange",
                "description": f"Perfect exchange between {lagna_lord} (Lagna lord) and {twelfth_lord} (12th lord) with {seventh_lord} (7th lord) influence",
                "severity": "Very High",
                "effect": "Self-caused financial destruction through partnerships",
                "planets_involved": [lagna_lord, twelfth_lord, seventh_lord],
                "houses_involved": [1, 12, 7],
                "formation_strength": "Very Strong"
            })
    def _check_type_b_exchange(self):
        lagna_lord = self.house_lords[1]
        sixth_lord = self.house_lords[6]
        maraka_lords = self._get_maraka_lords()
        lagna_lord_house = self.planetary_data[lagna_lord]['house']
        sixth_lord_house = self.planetary_data[sixth_lord]['house']
        exchange = (lagna_lord_house == 6 and sixth_lord_house == 1)
        moon_aspected_by_maraka = any(self._planet_aspects_planet(lord, 'Moon') for lord in maraka_lords)
        if exchange and moon_aspected_by_maraka:
            self.detected_yogas.append({
                "type": "Type B - Exchange Yoga",
                "name": "Lagna-6th Exchange with Moon Affliction",
                "description": f"Exchange between {lagna_lord} and {sixth_lord} with Moon aspected by maraka lords",
                "severity": "High",
                "effect": "Self-sabotage through conflicts, emotional financial decisions",
                "planets_involved": [lagna_lord, sixth_lord, 'Moon'] + maraka_lords,
                "houses_involved": [1, 6, 2, 7],
                "formation_strength": "Strong"
            })
    def _check_type_c_ketu_moon(self):
        moon_house = self.planetary_data['Moon']['house']
        ketu_house = self.planetary_data['Ketu']['house']
        if moon_house == 1 and ketu_house == 1:
            self.detected_yogas.append({
                "type": "Type C - Ketu-Moon Yoga",
                "name": "Ketu-Moon in Lagna",
                "description": "Ketu and Moon conjunct in 1st house (Lagna)",
                "severity": "Medium-High",
                "effect": "Spiritual detachment from material wealth",
                "planets_involved": ['Moon', 'Ketu'],
                "houses_involved": [1],
                "formation_strength": "Medium"
            })
    def _check_type_d_eighth_house(self):
        lagna_lord = self.house_lords[1]
        lagna_lord_house = self.planetary_data[lagna_lord]['house']
        maraka_lords = self._get_maraka_lords()
        if lagna_lord_house == 8:
            maraka_aspects = [lord for lord in maraka_lords 
                              if self._planet_aspects_planet(lord, lagna_lord)]
            if maraka_aspects:
                self.detected_yogas.append({
                    "type": "Type D - 8th House Yoga",
                    "name": "Lagna Lord in 8th with Maraka Aspect",
                    "description": f"Lagna lord {lagna_lord} in 8th house aspected by {maraka_aspects}",
                    "severity": "High",
                    "effect": "Hidden enemies destroying wealth",
                    "planets_involved": [lagna_lord] + maraka_aspects,
                    "houses_involved": [1, 8, 2, 7],
                    "formation_strength": "Strong"
                })
    def _check_type_e_malefic_combination(self):
        lagna_lord = self.house_lords[1]
        lagna_lord_house = self.planetary_data[lagna_lord]['house']
        maraka_lords = self._get_maraka_lords()
        if lagna_lord_house in DUSTHANA_HOUSES:
            malefics_with_lagna_lord = [malefic for malefic in NATURAL_MALEFICS
                                        if self._planets_in_same_house(lagna_lord, malefic)]
            maraka_aspects = [lord for lord in maraka_lords
                              if self._planet_aspects_planet(lord, lagna_lord)]
            if malefics_with_lagna_lord and maraka_aspects:
                self.detected_yogas.append({
                    "type": "Type E - Malefic Combination",
                    "name": "Lagna Lord with Malefic in Dusthana",
                    "description": f"Lagna lord {lagna_lord} in {lagna_lord_house}th house with {malefics_with_lagna_lord} and aspected by {maraka_aspects}",
                    "severity": "Very High", 
                    "effect": "Multiple financial crises simultaneously",
                    "planets_involved": [lagna_lord] + malefics_with_lagna_lord + maraka_aspects,
                    "houses_involved": [1, lagna_lord_house, 2, 7],
                    "formation_strength": "Very Strong"
                })
    def _check_type_f_association_enhanced(self):
        lagna_lord = self.house_lords[1]
        associations = []
        for house in DUSTHANA_HOUSES:
            dusthana_lord = self.house_lords[house]
            if dusthana_lord == lagna_lord:
                continue
            association_type = None
            if self._planets_in_same_house(lagna_lord, dusthana_lord):
                association_type = "conjunction"
            elif self._planet_aspects_planet(lagna_lord, dusthana_lord):
                association_type = "lagna_lord_aspects"
            elif self._planet_aspects_planet(dusthana_lord, lagna_lord):
                association_type = "dusthana_lord_aspects"
            if association_type:
                associations.append((dusthana_lord, f"{house}th lord", association_type))
        malefic_aspects = []
        for malefic in NATURAL_MALEFICS:
            if malefic not in [lagna_lord] + [assoc[0] for assoc in associations]:
                if self._planet_aspects_planet(malefic, lagna_lord):
                    malefic_aspects.append(malefic)
        if len(associations) >= 1 and (malefic_aspects or len(associations) >= 2):
            description = f"Lagna lord {lagna_lord} associated with "
            description += ", ".join([f"{assoc[0]} ({assoc[1]}) by {assoc[2]}" for assoc in associations])
            if malefic_aspects:
                description += f" under {malefic_aspects} aspects"
            self.detected_yogas.append({
                "type": "Type F - Association Yoga",
                "name": "Lagna Lord with Dusthana Lords",
                "description": description,
                "severity": "Very High" if malefic_aspects else "High",
                "effect": "Constant money troubles through bad associations",
                "planets_involved": [lagna_lord] + [assoc[0] for assoc in associations] + malefic_aspects,
                "houses_involved": [1] + DUSTHANA_HOUSES,
                "formation_strength": "Very Strong" if malefic_aspects else "Strong"
            })
    def _check_type_g_fifth_lord(self):
        fifth_lord = self.house_lords[5]
        dusthana_lords = [self.house_lords[house] for house in DUSTHANA_HOUSES]
        conjunct_dusthana_lords = [lord for lord in dusthana_lords
                                   if self._planets_in_same_house(fifth_lord, lord)]
        if conjunct_dusthana_lords:
            benefic_aspects = [benefic for benefic in NATURAL_BENEFICS
                               if self._planet_aspects_planet(benefic, fifth_lord)]
            if not benefic_aspects:
                self.detected_yogas.append({
                    "type": "Type G - 5th Lord Yoga",
                    "name": "5th Lord with Dusthana Lords",
                    "description": f"5th lord {fifth_lord} conjunct {conjunct_dusthana_lords} without benefic protection",
                    "severity": "Medium-High",
                    "effect": "Intelligence misused leading to financial losses",
                    "planets_involved": [fifth_lord] + conjunct_dusthana_lords,
                    "houses_involved": [5] + DUSTHANA_HOUSES,
                    "formation_strength": "Medium"
                })
    def _check_type_h_fifth_lord_aspect(self):
        fifth_lord = self.house_lords[5]
        fifth_lord_house = self.planetary_data[fifth_lord]['house']
        if fifth_lord_house in [6, 10]:
            malefic_house_lords = [self.house_lords[house] for house in [2, 6, 7, 8, 12]]
            aspecting_lords = [lord for lord in malefic_house_lords
                               if self._planet_aspects_planet(lord, fifth_lord)]
            if len(aspecting_lords) >= 2:
                self.detected_yogas.append({
                    "type": "Type H - 5th Lord Aspect",
                    "name": "5th Lord Under Multiple Malefic Aspects",
                    "description": f"5th lord {fifth_lord} in {fifth_lord_house}th house aspected by {aspecting_lords}",
                    "severity": "High",
                    "effect": "Career and intelligence misused for losses",
                    "planets_involved": [fifth_lord] + aspecting_lords,
                    "houses_involved": [5, fifth_lord_house] + [2, 6, 7, 8, 12],
                    "formation_strength": "Strong"
                })
    def _check_type_i_natural_malefic(self):
        malefics_in_lagna = [malefic for malefic in NATURAL_MALEFICS
                             if self.planetary_data[malefic]['house'] == 1]
        if malefics_in_lagna:
            maraka_lords = self._get_maraka_lords()
            maraka_aspects = []
            for malefic in malefics_in_lagna:
                for maraka in maraka_lords:
                    if maraka != malefic and self._planet_aspects_planet(maraka, malefic):
                        if maraka not in maraka_aspects:
                            maraka_aspects.append(maraka)
            if maraka_aspects:
                if len(malefics_in_lagna) >= 2 and len(maraka_aspects) >= 2:
                    severity = "Extreme"; formation_strength = "Extreme"
                elif len(malefics_in_lagna) >= 2 or len(maraka_aspects) >= 2:
                    severity = "Very High"; formation_strength = "Very Strong"
                else:
                    severity = "High"; formation_strength = "Strong"
                self.detected_yogas.append({
                    "type": "Type I - Natural Malefic",
                    "name": "Malefics in Lagna with Maraka Aspects",
                    "description": f"Natural malefics {malefics_in_lagna} in Lagna aspected by maraka lords {maraka_aspects}",
                    "severity": severity,
                    "effect": "Severe poverty with health issues",
                    "planets_involved": malefics_in_lagna + maraka_aspects,
                    "houses_involved": [1, 2, 7],
                    "formation_strength": formation_strength
                })
    def _check_type_j_dual_affliction(self):
        lagna_lord = self.house_lords[1]
        lagna_lord_house = self.planetary_data[lagna_lord]['house']
        navamsa_asc_sign = self.navamsa_data.get('navamsa_ascendant', self.ascendant_sign)
        navamsa_lagna_lord = HOUSE_LORDS.get(navamsa_asc_sign, lagna_lord)
        navamsa_lagna_lord_house = self.planetary_data.get(navamsa_lagna_lord, {}).get('house', 1)
        if (lagna_lord_house in DUSTHANA_HOUSES and 
            navamsa_lagna_lord_house in DUSTHANA_HOUSES):
            self.detected_yogas.append({
                "type": "Type J - Dual Affliction",
                "name": "Both Birth and Navamsa Lagna Lords Afflicted",
                "description": f"Birth lagna lord {lagna_lord} in {lagna_lord_house}th and Navamsa lagna lord {navamsa_lagna_lord} in {navamsa_lagna_lord_house}th house",
                "severity": "Extreme",
                "effect": "Karmic poverty affecting entire lifetime",
                "planets_involved": [lagna_lord, navamsa_lagna_lord],
                "houses_involved": [1, lagna_lord_house, navamsa_lagna_lord_house],
                "formation_strength": "Extreme"
            })
    def _check_kemadruma_yoga(self):
        moon_house = self.planetary_data['Moon']['house']
        second_from_moon = (moon_house % 12) + 1
        twelfth_from_moon = ((moon_house - 2) % 12) + 1
        planets_around_moon = []
        for planet, data in self.planetary_data.items():
            if (planet not in ['Moon', 'Ketu'] and 
                data['house'] in [second_from_moon, twelfth_from_moon]):
                planets_around_moon.append(planet)
        planets_with_moon = []
        for planet, data in self.planetary_data.items():
            if planet != 'Moon' and data['house'] == moon_house:
                planets_with_moon.append(planet)
        moon_in_kendra = moon_house in KENDRA_HOUSES
        if not planets_around_moon and not planets_with_moon:
            severity = "Medium" if moon_in_kendra else "Medium-High"
            effect = "Mental isolation, dependence on others"
            if not moon_in_kendra:
                effect += ", emotional instability"
            self.detected_yogas.append({
                "type": "Kemadruma Yoga",
                "name": "Moon Isolated",
                "description": f"Moon alone in {moon_house}th house with no planets in adjacent houses" +
                              (" (in Kendra - partially cancelled)" if moon_in_kendra else ""),
                "severity": severity,
                "effect": effect,
                "planets_involved": ['Moon'],
                "houses_involved": [moon_house],
                "formation_strength": "Medium" if moon_in_kendra else "Strong"
            })
    def _check_sakata_yoga(self):
        moon_house = self.planetary_data['Moon']['house']
        jupiter_house = self.planetary_data['Jupiter']['house']
        moon_from_jupiter = ((moon_house - jupiter_house) % 12)
        if moon_from_jupiter == 0:
            moon_from_jupiter = 12
        if moon_from_jupiter in [6, 8, 12]:
            cancellation_factors = []
            jupiter_exalted = self._is_planet_exalted('Jupiter', 
                                                     self.planetary_data['Jupiter']['sign'],
                                                     self.planetary_data['Jupiter']['degree_in_sign'])[0]
            if jupiter_exalted:
                cancellation_factors.append("Jupiter exalted")
            moon_with_benefics = []
            for benefic in NATURAL_BENEFICS:
                if benefic != 'Moon' and self._planets_in_same_house('Moon', benefic):
                    moon_with_benefics.append(benefic)
            if moon_with_benefics:
                cancellation_factors.append(f"Moon with {moon_with_benefics}")
            severity = "Low" if cancellation_factors else "Medium"
            description = f"Moon in {moon_from_jupiter}th house from Jupiter"
            if cancellation_factors:
                description += f" (cancelled by: {', '.join(cancellation_factors)})"
            self.detected_yogas.append({
                "type": "Sakata Yoga",
                "name": "Moon-Jupiter Separation",
                "description": description,
                "severity": severity,
                "effect": "Financial ups and downs, emotional decisions without wisdom" +
                         (" - effects reduced due to cancellation" if cancellation_factors else ""),
                "planets_involved": ['Moon', 'Jupiter'],
                "houses_involved": [moon_house, jupiter_house],
                "formation_strength": "Weak" if cancellation_factors else "Medium"
            })
    def _check_dharidra_yoga(self):
        kendras_with_benefics = True
        for kendra in KENDRA_HOUSES:
            planets_in_kendra = [planet for planet, data in self.planetary_data.items()
                               if data['house'] == kendra and planet in NATURAL_BENEFICS]
            if not planets_in_kendra:
                kendras_with_benefics = False
                break
        malefics_in_second = [planet for planet, data in self.planetary_data.items()
                             if data['house'] == 2 and planet in NATURAL_MALEFICS]
        if kendras_with_benefics and malefics_in_second:
            self.detected_yogas.append({
                "type": "Dharidra Yoga",
                "name": "False Prosperity",
                "description": f"All Kendras occupied by benefics but malefics {malefics_in_second} in 2nd house",
                "severity": "High",
                "effect": "Lifestyle expenses exceed income",
                "planets_involved": malefics_in_second,
                "houses_involved": KENDRA_HOUSES + [2],
                "formation_strength": "Strong"
            })
    def _check_sixth_house_stellium(self):
        sixth_house_planets = []
        for planet, data in self.planetary_data.items():
            if data['house'] == 6 and planet not in ['Ketu']:
                sixth_house_planets.append(planet)
        if len(sixth_house_planets) >= 3:
            benefics_in_sixth = [p for p in sixth_house_planets if p in NATURAL_BENEFICS]
            malefics_in_sixth = [p for p in sixth_house_planets if p in NATURAL_MALEFICS]
            severity = "High" if len(malefics_in_sixth) >= 2 else "Medium-High"
            self.detected_yogas.append({
                "type": "Additional - 6th House Stellium",
                "name": "Multiple Planets in 6th House (Ripu Yoga)",
                "description": f"Planets {sixth_house_planets} in 6th house of enemies and debts",
                "severity": severity,
                "effect": "Constant conflicts, legal issues, health problems affecting wealth",
                "planets_involved": sixth_house_planets,
                "houses_involved": [6],
                "formation_strength": "Strong" if len(malefics_in_sixth) >= 2 else "Medium"
            })
    def _check_moon_ketu_conjunction_12th(self):
        moon_house = self.planetary_data['Moon']['house']
        ketu_house = self.planetary_data['Ketu']['house']
        if moon_house == 12 and ketu_house == 12:
            self.detected_yogas.append({
                "type": "Additional - Moon-Ketu 12th House",
                "name": "Moon-Ketu Conjunction in 12th House",
                "description": "Moon and Ketu conjunct in 12th house of losses and expenses",
                "severity": "Medium-High",
                "effect": "Spiritual inclination over material gains, expenses on spiritual activities",
                "planets_involved": ['Moon', 'Ketu'],
                "houses_involved": [12],
                "formation_strength": "Medium"
            })
    def _check_cancellation_factors_corrected(self):
        cancellation_factors = []
        lagna_lord = self.house_lords[1]
        eleventh_lord = self.house_lords[11]
        if (self.planetary_data[lagna_lord]['house'] == 11 and 
            self.planetary_data[eleventh_lord]['house'] == 1):
            cancellation_factors.append("Jupiter-Saturn exchange (1st-11th lords)")
        second_lord = self.house_lords[2]
        second_lord_house = self.planetary_data[second_lord]['house']
        if second_lord_house in KENDRA_HOUSES:
            cancellation_factors.append(f"2nd lord {second_lord} in Kendra ({second_lord_house}st house)")
        if self.planetary_data[eleventh_lord]['house'] == 1:
            cancellation_factors.append(f"11th lord {eleventh_lord} in Lagna (gains through self-effort)")
        for kendra in KENDRA_HOUSES:
            for benefic in ['Jupiter', 'Venus']:
                if (self.planetary_data[benefic]['house'] == kendra and
                    self._is_planet_exalted(benefic, 
                        self.planetary_data[benefic]['sign'],
                        self.planetary_data[benefic]['degree_in_sign'])[0]):
                    cancellation_factors.append(f"{benefic} exalted in {kendra}st house")
        moon_house = self.planetary_data['Moon']['house']
        second_from_moon = (moon_house % 12) + 1
        twelfth_from_moon = ((moon_house - 2) % 12) + 1
        planets_supporting_moon = []
        for planet, data in self.planetary_data.items():
            if (planet not in ['Moon', 'Ketu'] and 
                data['house'] in [second_from_moon, twelfth_from_moon]):
                planets_supporting_moon.append(planet)
        if planets_supporting_moon:
            cancellation_factors.append(f"Moon supported by {planets_supporting_moon}")
        return cancellation_factors
    def _calculate_overall_severity(self):
        if not self.detected_yogas:
            return "None"
        severity_weights = {
            "Low": 0.5, "Medium": 1, "Medium-High": 2, "High": 3, 
            "Very High": 4, "Extreme": 5
        }
        total_weight = sum(severity_weights.get(yoga["severity"], 1) for yoga in self.detected_yogas)
        avg_severity = total_weight / len(self.detected_yogas)
        cancellation_factors = self._check_cancellation_factors_corrected()
        if cancellation_factors:
            avg_severity *= (1 - len(cancellation_factors) * 0.15)
        if avg_severity >= 4.5: return "Extreme"
        elif avg_severity >= 3.5: return "Very High"
        elif avg_severity >= 2.5: return "High" 
        elif avg_severity >= 1.5: return "Medium-High"
        elif avg_severity >= 0.8: return "Medium"
        else: return "Low"
    def _get_financial_outlook(self):
        if not self.detected_yogas:
            return "Excellent financial potential - no major poverty yogas detected"
        severity = self._calculate_overall_severity()
        yoga_count = len(self.detected_yogas)
        cancellation_factors = self._check_cancellation_factors_corrected()
        cancellation_note = f" However, {len(cancellation_factors)} cancellation factors provide relief." if cancellation_factors else ""
        outlooks = {
            "Low": f"{yoga_count} minor financial challenges easily overcome.{cancellation_note}",
            "Medium": f"{yoga_count} moderate financial challenges. Manageable with effort.{cancellation_note}",
            "Medium-High": f"{yoga_count} significant financial struggles requiring focused remedies.{cancellation_note}",
            "High": f"{yoga_count} major financial difficulties. Strong remedial actions needed.{cancellation_note}",
            "Very High": f"{yoga_count} severe financial problems. Intensive remedies required.{cancellation_note}",
            "Extreme": f"{yoga_count} extreme financial challenges. Comprehensive intervention necessary.{cancellation_note}"
        }
        return outlooks.get(severity, "Financial assessment requires individual consultation")
    # <<< END of unchanged block

# -------------------------
# Remedials (moved here so daridraYoga can return them)
# -------------------------
def get_remedial_measures():
    return {
        "immediate_actions": [
            "Chant 'Om Shreem Mahalakshmiyei Namaha' 108 times daily before sunrise",
            "Donate food to the needy every Thursday (Jupiter's day)",
            "Light sesame oil lamp every Saturday for Saturn",
            "Perform Lakshmi Puja every Friday evening"
        ],
        "weekly_practices": [
            "Fast on Thursdays and donate yellow items (turmeric, clothes)",
            "Visit Vishnu or Lakshmi temple on Fridays",
            "Chant 'Om Gurave Namaha' 108 times on Thursdays",
            "Avoid non-vegetarian food on Tuesdays and Saturdays"
        ],
        "monthly_rituals": [
            "Perform Satyanarayan Puja on full moon days",
            "Donate to educational institutions or feed cows",
            "Organize community service activities",
            "Recite Vishnu Sahasranama once monthly"
        ],
        "gemstone_recommendations": [
            "Yellow Sapphire (Pukhraj) for Jupiter strength - wear on Thursday in gold",
            "Emerald for Mercury enhancement - wear on Wednesday",
            "Natural Pearl for Moon strength - wear on Monday",
            "Blue Sapphire for Saturn (only after careful consultation)"
        ],
        "lifestyle_changes": [
            "Maintain regular meditation and prayer schedule",
            "Practice gratitude and contentment (Santosha)",
            "Avoid speculation, gambling, and risky investments",
            "Focus on skill development and steady career growth",
            "Live within means and save regularly"
        ]
    }

# -------------------------
# Public function (requested name)
# -------------------------
def daridraYoga(planetary_data, ascendant_sign, jd_ut, latitude, longitude):
    """
    Public entrypoint that performs the Daridra Yoga analysis
    using the exact class logic above, and ALSO returns remedial_measures.
    """
    calc = EnhancedDaridraYogaCalculator(
        planetary_data=planetary_data,
        ascendant_sign=ascendant_sign,
        jd_ut=jd_ut,
        latitude=latitude,
        longitude=longitude
    )
    analysis = calc.detect_all_daridra_yogas()
    return {
        "daridra_yoga_analysis": analysis,
        "remedial_measures": get_remedial_measures()
    }

# -------------------------
# Helper to reproduce endpoint computations for positions/houses
# -------------------------
def compute_core_from_birth(birth_data):
    latitude = float(birth_data['latitude'])
    longitude = float(birth_data['longitude'])
    timezone_offset = float(birth_data['timezone_offset'])

    birth_date = datetime.strptime(birth_data['birth_date'], '%Y-%m-%d')
    birth_time = datetime.strptime(birth_data['birth_time'], '%H:%M:%S').time()
    local_datetime = datetime.combine(birth_date, birth_time)
    ut_datetime = local_datetime - timedelta(hours=timezone_offset)
    hour_decimal = ut_datetime.hour + ut_datetime.minute / 60.0 + ut_datetime.second / 3600.0
    jd_ut = swe.julday(ut_datetime.year, ut_datetime.month, ut_datetime.day, hour_decimal)

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa_value = swe.get_ayanamsa_ut(jd_ut)

    planets = [
        (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MARS, 'Mars'),
        (swe.MERCURY, 'Mercury'), (swe.JUPITER, 'Jupiter'), (swe.VENUS, 'Venus'),
        (swe.SATURN, 'Saturn'), (swe.TRUE_NODE, 'Rahu')
    ]
    flag = swe.FLG_SIDEREAL | swe.FLG_SPEED
    planetary_data = {}
    for planet_id, planet_name in planets:
        pos, ret = swe.calc_ut(jd_ut, planet_id, flag)
        if ret < 0:
            raise RuntimeError(f"Error calculating {planet_name}: Swiss Ephemeris error {ret}")
        lon = pos[0] % 360
        sign, degree_in_sign = longitude_to_sign_degree(lon)
        planetary_data[planet_name] = {
            'longitude': lon,
            'sign': sign,
            'degree_in_sign': degree_in_sign,
            'speed': pos[3],
            'retrograde': 'R' if pos[3] < 0 else ''
        }

    rahu_lon = planetary_data['Rahu']['longitude']
    ketu_lon = (rahu_lon + 180) % 360
    ketu_sign, ketu_degree = longitude_to_sign_degree(ketu_lon)
    planetary_data['Ketu'] = {
        'longitude': ketu_lon,
        'sign': ketu_sign,
        'degree_in_sign': ketu_degree,
        'speed': 0,
        'retrograde': ''
    }

    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'W', flags=swe.FLG_SIDEREAL)
    ascendant_lon = ascmc[0] % 360
    asc_sign_index = int(ascendant_lon // 30)
    asc_sign = SIGNS[asc_sign_index]

    for planet_name in planetary_data:
        lon = planetary_data[planet_name]['longitude']
        house = get_house_whole_sign(lon, asc_sign_index)
        planetary_data[planet_name]['house'] = house

    return {
        "planetary_data": planetary_data,
        "asc_sign": asc_sign,
        "ascendant_lon": ascendant_lon,
        "asc_sign_index": asc_sign_index,
        "jd_ut": jd_ut,
        "ayanamsa_value": ayanamsa_value,
        "ut_datetime": ut_datetime,
        "latitude": latitude,
        "longitude": longitude,
        "timezone_offset": timezone_offset
    }
