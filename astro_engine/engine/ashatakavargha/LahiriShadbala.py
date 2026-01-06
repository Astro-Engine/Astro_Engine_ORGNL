"""
Shadbala Calculator - Complete Corrected Implementation
All calculation logic
Uses: Sidereal Zodiac, Lahiri Ayanamsa, Whole Sign House System
"""

import swisseph as swe
import math
from datetime import datetime, timedelta
import os

# Set Swiss Ephemeris path
swe.set_ephe_path('astro_api/ephe')


class ShadbalaCalculator:
    """Complete Shadbala calculator with all corrections"""
    
    def __init__(self):
        # Planet constants
        self.planets = [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS, swe.SATURN]
        self.planet_names = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
        
        # Exaltation points (absolute longitude 0-360)
        self.exaltation_points = {
            swe.SUN: 10.0,      # 10° Aries
            swe.MOON: 33.0,     # 3° Taurus  
            swe.MARS: 298.0,    # 28° Capricorn
            swe.MERCURY: 165.0, # 15° Virgo
            swe.JUPITER: 95.0,  # 5° Cancer
            swe.VENUS: 357.0,   # 27° Pisces
            swe.SATURN: 200.0   # 20° Libra
        }
        
        # Debilitation points (absolute longitude 0-360)
        self.debilitation_points = {
            swe.SUN: 190.0,     # 10° Libra
            swe.MOON: 213.0,    # 3° Scorpio
            swe.MARS: 118.0,    # 28° Cancer
            swe.MERCURY: 345.0, # 15° Pisces
            swe.JUPITER: 275.0, # 5° Capricorn
            swe.VENUS: 177.0,   # 27° Virgo
            swe.SATURN: 20.0    # 20° Aries
        }
        
        # Exaltation signs (0-11)
        self.exaltation_signs = {
            swe.SUN: 0, swe.MOON: 1, swe.MARS: 9, swe.MERCURY: 5,
            swe.JUPITER: 3, swe.VENUS: 11, swe.SATURN: 6
        }
        
        # Debilitation signs (0-11)
        self.debilitation_signs = {
            swe.SUN: 6, swe.MOON: 7, swe.MARS: 3, swe.MERCURY: 11,
            swe.JUPITER: 9, swe.VENUS: 5, swe.SATURN: 0
        }
        
        # Own signs (0-11)
        self.own_signs = {
            swe.SUN: [4],           # Leo
            swe.MOON: [3],          # Cancer
            swe.MARS: [0, 7],       # Aries, Scorpio
            swe.MERCURY: [2, 5],    # Gemini, Virgo
            swe.JUPITER: [8, 11],   # Sagittarius, Pisces
            swe.VENUS: [1, 6],      # Taurus, Libra
            swe.SATURN: [9, 10]     # Capricorn, Aquarius
        }
        
        # Moolatrikona with degree ranges
        self.moolatrikona = {
            swe.SUN: {'sign': 4, 'start': 0, 'end': 20},      # 0-20° Leo
            swe.MOON: {'sign': 1, 'start': 3, 'end': 30},     # 3-30° Taurus
            swe.MARS: {'sign': 0, 'start': 0, 'end': 12},     # 0-12° Aries
            swe.MERCURY: {'sign': 5, 'start': 15, 'end': 20}, # 15-20° Virgo
            swe.JUPITER: {'sign': 8, 'start': 0, 'end': 10},  # 0-10° Sagittarius
            swe.VENUS: {'sign': 6, 'start': 0, 'end': 15},    # 0-15° Libra
            swe.SATURN: {'sign': 10, 'start': 0, 'end': 20}   # 0-20° Aquarius
        }
        
        # Sign lords
        self.sign_lords = {
            0: swe.MARS, 1: swe.VENUS, 2: swe.MERCURY, 3: swe.MOON,
            4: swe.SUN, 5: swe.MERCURY, 6: swe.VENUS, 7: swe.MARS,
            8: swe.JUPITER, 9: swe.SATURN, 10: swe.SATURN, 11: swe.JUPITER
        }
        
        # Natural friendships
        self.natural_friends = {
            swe.SUN: [swe.MOON, swe.MARS, swe.JUPITER],
            swe.MOON: [swe.SUN, swe.MERCURY],
            swe.MARS: [swe.SUN, swe.MOON, swe.JUPITER],
            swe.MERCURY: [swe.SUN, swe.VENUS],
            swe.JUPITER: [swe.SUN, swe.MOON, swe.MARS],
            swe.VENUS: [swe.MERCURY, swe.SATURN],
            swe.SATURN: [swe.MERCURY, swe.VENUS]
        }
        
        self.natural_enemies = {
            swe.SUN: [swe.VENUS, swe.SATURN],
            swe.MOON: [],
            swe.MARS: [swe.MERCURY],
            swe.MERCURY: [swe.MOON],
            swe.JUPITER: [swe.MERCURY, swe.VENUS],
            swe.VENUS: [swe.SUN, swe.MOON],
            swe.SATURN: [swe.SUN, swe.MOON, swe.MARS]
        }
        
        # Planet classifications
        self.male_planets = [swe.SUN, swe.MARS, swe.JUPITER]
        self.female_planets = [swe.MOON, swe.VENUS]
        self.hermaphrodite_planets = [swe.MERCURY, swe.SATURN]
        
        self.benefics = [swe.JUPITER, swe.VENUS, swe.MERCURY, swe.MOON]
        self.malefics = [swe.SUN, swe.MARS, swe.SATURN]
        
        self.diurnal_planets = [swe.SUN, swe.JUPITER, swe.VENUS]
        self.nocturnal_planets = [swe.MOON, swe.MARS, swe.SATURN]
        
        # Dig Bala strong houses
        self.dig_bala_strong = {
            swe.JUPITER: 1, swe.MERCURY: 1,  # East
            swe.MOON: 4, swe.VENUS: 4,       # North
            swe.SATURN: 7,                    # West
            swe.SUN: 10, swe.MARS: 10        # South
        }
        
        # Naisargika Bala (fixed values in virupas)
        self.naisargika_bala = {
            swe.SUN: 60.0, swe.MOON: 51.43, swe.VENUS: 42.86,
            swe.JUPITER: 34.29, swe.MERCURY: 25.71, swe.MARS: 17.14, swe.SATURN: 8.57
        }
        
        # Mean daily motion for Chesta Bala
        self.mean_motion = {
            swe.MARS: 0.52, swe.MERCURY: 1.38, swe.JUPITER: 0.083,
            swe.VENUS: 1.6, swe.SATURN: 0.033
        }
        
        # Tribhaga lords
        self.day_tribhaga_lords = [swe.JUPITER, swe.MERCURY, swe.SATURN]
        self.night_tribhaga_lords = [swe.MOON, swe.VENUS, swe.MARS]
        
        # Weekday lords (Sunday=0 to Saturday=6)
        self.weekday_lords = [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, 
                             swe.JUPITER, swe.VENUS, swe.SATURN]
        
        # Required minimum strength (in rupas)
        self.required_strength = {
            'Sun': 6.5, 'Moon': 6.0, 'Mars': 5.0, 'Mercury': 7.0,
            'Jupiter': 6.5, 'Venus': 5.5, 'Saturn': 5.0
        }

    def get_julian_day(self, date_str, time_str, timezone_offset):
        """Convert date/time to Julian Day"""
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        utc_dt = dt - timedelta(hours=timezone_offset)
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 
                       utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)
        return jd

    def get_ayanamsa(self, jd):
        """Get Lahiri Ayanamsa"""
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        return swe.get_ayanamsa(jd)

    def get_planet_positions(self, jd):
        """Get sidereal positions of all planets"""
        ayanamsa = self.get_ayanamsa(jd)
        positions = {}
        
        for planet in self.planets:
            result = swe.calc_ut(jd, planet)
            pos = result[0]
            sidereal_long = (pos[0] - ayanamsa) % 360
            
            positions[planet] = {
                'longitude': sidereal_long,
                'latitude': pos[1],
                'speed': pos[3],
                'distance': pos[2],
                'tropical_longitude': pos[0]
            }
        
        return positions, ayanamsa

    def get_houses(self, jd, lat, lon):
        """Calculate house cusps (Whole Sign system)"""
        ayanamsa = self.get_ayanamsa(jd)
        house_result = swe.houses(jd, lat, lon, b'W')
        houses = house_result[0]
        sidereal_houses = [(h - ayanamsa) % 360 for h in houses]
        ascendant = sidereal_houses[0]
        
        # Whole sign houses
        house_cusps = []
        asc_sign = int(ascendant // 30)
        for i in range(12):
            house_sign = (asc_sign + i) % 12
            house_cusps.append(house_sign * 30)
        
        return house_cusps, ascendant

    def get_sign(self, longitude):
        """Get zodiac sign (0-11)"""
        return int(longitude // 30) % 12

    def get_degree_in_sign(self, longitude):
        """Get degree within sign (0-30)"""
        return longitude % 30

    def angular_distance(self, angle1, angle2):
        """Calculate shortest angular distance"""
        diff = abs(angle1 - angle2)
        if diff > 180:
            diff = 360 - diff
        return diff

    def get_divisional_chart(self, positions, division):
        """Calculate divisional charts (D1-D30)"""
        divisional_positions = {}
        
        for planet, pos in positions.items():
            long = pos['longitude']
            sign = self.get_sign(long)
            degree_in_sign = self.get_degree_in_sign(long)
            
            if division == 1:
                div_long = long
            elif division == 2:  # Hora
                if sign % 2 == 0:  # Odd signs
                    div_sign = 4 if degree_in_sign < 15 else 3
                else:  # Even signs
                    div_sign = 3 if degree_in_sign < 15 else 4
                div_long = div_sign * 30 + (degree_in_sign % 15) * 2
            elif division == 3:  # Drekkana
                drekkana = int(degree_in_sign // 10)
                base_sign = (sign + drekkana * 4) % 12
                div_long = base_sign * 30 + (degree_in_sign % 10) * 3
            elif division == 7:  # Saptamsa
                saptamsa = int(degree_in_sign // (30/7))
                if sign % 2 == 0:
                    base_sign = (sign + saptamsa) % 12
                else:
                    base_sign = (sign + 6 + saptamsa) % 12
                div_long = base_sign * 30
            elif division == 9:  # Navamsa
                navamsa = int(degree_in_sign // (30/9))
                if sign in [0, 3, 6, 9]:  # Movable
                    base_sign = (0 + navamsa) % 12
                elif sign in [1, 4, 7, 10]:  # Fixed
                    base_sign = (3 + navamsa) % 12
                else:  # Dual
                    base_sign = (6 + navamsa) % 12
                div_long = base_sign * 30
            elif division == 12:  # Dvadasamsa
                dvadasamsa = int(degree_in_sign // 2.5)
                base_sign = (sign + dvadasamsa) % 12
                div_long = base_sign * 30
            elif division == 30:  # Trimsamsa
                if sign % 2 == 0:
                    rulers = [swe.MARS, swe.SATURN, swe.JUPITER, swe.MERCURY, swe.VENUS]
                    degrees = [5, 5, 8, 7, 5]
                else:
                    rulers = [swe.VENUS, swe.MERCURY, swe.JUPITER, swe.SATURN, swe.MARS]
                    degrees = [5, 7, 8, 5, 5]
                
                cumulative = 0
                div_long = sign * 30
                for i, deg in enumerate(degrees):
                    if degree_in_sign < cumulative + deg:
                        div_long = self.own_signs[rulers[i]][0] * 30
                        break
                    cumulative += deg
            else:
                div_long = long
            
            divisional_positions[planet] = {'longitude': div_long % 360}
        
        return divisional_positions

    def get_relationship(self, planet1, planet2, positions):
        """Determine relationship between planets (0-4)"""
        p1_sign = self.get_sign(positions[planet1]['longitude'])
        p2_sign = self.get_sign(positions[planet2]['longitude'])
        distance = min(abs(p1_sign - p2_sign), 12 - abs(p1_sign - p2_sign))
        
        # Temporal friendship
        if distance in [1, 2, 3, 4, 8, 9, 10, 11]:
            temporal = 2
        elif distance in [5, 7]:
            temporal = 1
        else:
            temporal = 0
        
        # Natural relationship
        if planet2 in self.natural_friends.get(planet1, []):
            natural = 2
        elif planet2 in self.natural_enemies.get(planet1, []):
            natural = 0
        else:
            natural = 1
        
        # Combined
        combined = natural + temporal
        if combined >= 4:
            return 4  # Great Friend
        elif combined == 3:
            return 3  # Friend
        elif combined == 2:
            return 2  # Neutral
        elif combined == 1:
            return 1  # Enemy
        else:
            return 0  # Great Enemy

    def calculate_uchcha_bala(self, planet, longitude):
        """Calculate Uchcha Bala (Exaltation Strength)"""
        debil_point = self.debilitation_points[planet]
        diff = (longitude - debil_point + 360) % 360
        if diff > 180:
            diff = 360 - diff
        uchcha_bala = diff / 3.0
        return round(min(max(uchcha_bala, 0.0), 60.0), 2)

    def calculate_saptavargaja_bala(self, planet, positions):
        """Calculate Saptavargaja Bala (7 Divisional Strength)"""
        divisions = [1, 2, 3, 7, 9, 12, 30]
        total_bala = 0
        
        for div in divisions:
            div_chart = self.get_divisional_chart(positions, div)
            planet_long = div_chart[planet]['longitude']
            planet_sign = self.get_sign(planet_long)
            planet_degree = self.get_degree_in_sign(planet_long)
            
            # Check in priority order
            if planet_sign == self.exaltation_signs.get(planet):
                strength = 20
            elif planet_sign == self.debilitation_signs.get(planet):
                strength = 0
            elif planet in self.moolatrikona:
                mool_data = self.moolatrikona[planet]
                if planet_sign == mool_data['sign']:
                    if mool_data['start'] <= planet_degree <= mool_data['end']:
                        strength = 45
                    else:
                        strength = 30
                elif planet_sign in self.own_signs.get(planet, []):
                    strength = 30
                else:
                    sign_lord = self.sign_lords.get(planet_sign)
                    if sign_lord:
                        rel = self.get_relationship(planet, sign_lord, positions)
                        strength = {4: 22.5, 3: 15, 2: 7.5, 1: 3.75, 0: 1.875}.get(rel, 7.5)
                    else:
                        strength = 7.5
            elif planet_sign in self.own_signs.get(planet, []):
                strength = 30
            else:
                sign_lord = self.sign_lords.get(planet_sign)
                if sign_lord:
                    rel = self.get_relationship(planet, sign_lord, positions)
                    strength = {4: 22.5, 3: 15, 2: 7.5, 1: 3.75, 0: 1.875}.get(rel, 7.5)
                else:
                    strength = 7.5
            
            total_bala += strength
        
        return round(total_bala / len(divisions), 2)

    def calculate_ojayugma_bala(self, planet, positions):
        """Calculate Ojayugma Bala (Odd-Even Strength)"""
        bala = 0
        
        # D1
        d1_sign = self.get_sign(positions[planet]['longitude'])
        is_odd_sign = (d1_sign % 2 == 0)
        
        if planet in self.male_planets and is_odd_sign:
            bala += 15
        elif planet in self.female_planets and not is_odd_sign:
            bala += 15
        elif planet in self.hermaphrodite_planets:
            bala += 15
        
        # D9
        d9_chart = self.get_divisional_chart(positions, 9)
        d9_sign = self.get_sign(d9_chart[planet]['longitude'])
        is_odd_sign_d9 = (d9_sign % 2 == 0)
        
        if planet in self.male_planets and is_odd_sign_d9:
            bala += 15
        elif planet in self.female_planets and not is_odd_sign_d9:
            bala += 15
        elif planet in self.hermaphrodite_planets:
            bala += 15
        
        return round(bala, 2)

    def calculate_kendradi_bala(self, planet, positions, houses):
        """Calculate Kendradi Bala (Angular Strength)"""
        planet_sign = self.get_sign(positions[planet]['longitude'])
        asc_sign = self.get_sign(houses[0])
        house_num = ((planet_sign - asc_sign) % 12) + 1
        
        if house_num in [1, 4, 7, 10]:
            return 60.0
        elif house_num in [2, 5, 8, 11]:
            return 30.0
        else:
            return 15.0

    def calculate_drekkana_bala(self, planet, longitude):
        """Calculate Drekkana Bala"""
        degree_in_sign = self.get_degree_in_sign(longitude)
        
        if degree_in_sign < 10:
            drekkana = 1
        elif degree_in_sign < 20:
            drekkana = 2
        else:
            drekkana = 3
        
        if planet in self.male_planets and drekkana == 1:
            return 15.0
        elif planet in self.hermaphrodite_planets and drekkana == 2:
            return 15.0
        elif planet in self.female_planets and drekkana == 3:
            return 15.0
        else:
            return 0.0

    def calculate_sthana_bala(self, planet, positions, houses):
        """Calculate total Sthana Bala"""
        longitude = positions[planet]['longitude']
        
        uchcha = self.calculate_uchcha_bala(planet, longitude)
        saptavargaja = self.calculate_saptavargaja_bala(planet, positions)
        ojayugma = self.calculate_ojayugma_bala(planet, positions)
        kendradi = self.calculate_kendradi_bala(planet, positions, houses)
        drekkana = self.calculate_drekkana_bala(planet, longitude)
        
        total = uchcha + saptavargaja + ojayugma + kendradi + drekkana
        
        return {
            'total': round(total, 2),
            'uchcha_bala': round(uchcha, 2),
            'saptavargaja_bala': round(saptavargaja, 2),
            'ojayugma_bala': round(ojayugma, 2),
            'kendradi_bala': round(kendradi, 2),
            'drekkana_bala': round(drekkana, 2)
        }

    def calculate_dig_bala(self, planet, positions, houses):
        """
        Calculate Dig Bala (Directional Strength) - CRITICAL FORMULA
        
        Formula: Dig Bala = 60 × |cos(θ)|
        where θ = angular distance from planet to its strong house bhava madhya
        
        Maximum (60) when planet is at strong house
        Minimum (0) when planet is opposite to strong house
        """
        strong_house = self.dig_bala_strong.get(planet, 1)
        strong_house_cusp = houses[strong_house - 1]
        strong_point = (strong_house_cusp + 15) % 360  # Bhava madhya
        
        planet_long = positions[planet]['longitude']
        diff = self.angular_distance(planet_long, strong_point)
        
        # CRITICAL: Use cosine formula
        dig_bala = 60 * abs(math.cos(math.radians(diff)))
        
        return round(dig_bala, 2)

    def calculate_natonnata_bala(self, planet, time_decimal):
        """Calculate Natonnata Bala (Day/Night strength)"""
        if 6 <= time_decimal < 18:  # Daytime
            time_from_sunrise = time_decimal - 6
            day_strength = 60 * (1 - abs(6 - time_from_sunrise) / 6)
            night_strength = 60 - day_strength
        else:  # Nighttime
            if time_decimal >= 18:
                time_from_sunset = time_decimal - 18
            else:
                time_from_sunset = time_decimal + 6
            night_strength = 60 * (1 - abs(6 - time_from_sunset) / 6)
            day_strength = 60 - night_strength
        
        if planet in self.diurnal_planets:
            return round(day_strength, 2)
        elif planet in self.nocturnal_planets:
            return round(night_strength, 2)
        else:  # Mercury
            return 60.0

    def calculate_paksha_bala(self, planet, sun_long, moon_long):
        """
        Calculate Paksha Bala (Lunar phase strength) - CRITICAL FORMULA
        
        Uses DIRECTIONAL elongation (not absolute)
        Benefics: Strong in waxing (0-180°)
        Malefics: Strong in waning (180-360°)
        """
        elongation = (moon_long - sun_long + 360) % 360
        
        if planet in self.benefics:
            if elongation <= 180:
                paksha_bala = elongation / 3.0
            else:
                paksha_bala = (360 - elongation) / 3.0
        else:  # Malefics
            if elongation <= 180:
                paksha_bala = (180 - elongation) / 3.0
            else:
                paksha_bala = (elongation - 180) / 3.0
        
        return round(min(paksha_bala, 60.0), 2)

    def calculate_tribhaga_bala(self, planet, time_decimal):
        """Calculate Tribhaga Bala (Day/Night thirds)"""
        if 6 <= time_decimal < 18:  # Day
            day_hour = time_decimal - 6
            day_part = min(int(day_hour / 4), 2)
            return 60.0 if planet == self.day_tribhaga_lords[day_part] else 0.0
        else:  # Night
            if time_decimal >= 18:
                night_hour = time_decimal - 18
            else:
                night_hour = time_decimal + 6
            night_part = min(int(night_hour / 4), 2)
            return 60.0 if planet == self.night_tribhaga_lords[night_part] else 0.0

    def calculate_abda_bala(self, planet, jd):
        """Calculate Abda Bala (Year lord)"""
        greg_date = swe.revjul(jd)
        year = greg_date[0]
        years_from_epoch = year + 3102
        year_position = years_from_epoch % 7
        return 15.0 if planet == self.weekday_lords[year_position] else 0.0

    def calculate_masa_bala(self, planet, sun_sign):
        """Calculate Masa Bala (Month lord)"""
        month_lord = self.sign_lords.get(sun_sign)
        return 30.0 if planet == month_lord else 0.0

    def calculate_vara_bala(self, planet, jd):
        """Calculate Vara Bala (Weekday lord) - CORRECTED weekday conversion"""
        greg_date = swe.revjul(jd)
        year, month, day = int(greg_date[0]), int(greg_date[1]), int(greg_date[2])
        birth_date = datetime(year, month, day)
        python_weekday = birth_date.weekday()
        astro_weekday = (python_weekday + 1) % 7  # Convert to Sunday=0
        return 45.0 if planet == self.weekday_lords[astro_weekday] else 0.0

    def calculate_hora_bala(self, planet, jd, time_decimal):
        """Calculate Hora Bala (Planetary hour)"""
        greg_date = swe.revjul(jd)
        year, month, day = int(greg_date[0]), int(greg_date[1]), int(greg_date[2])
        birth_date = datetime(year, month, day)
        astro_weekday = (birth_date.weekday() + 1) % 7
        
        if time_decimal >= 6:
            hours_from_sunrise = time_decimal - 6
        else:
            hours_from_sunrise = time_decimal + 18
        
        hora_number = int(hours_from_sunrise) % 24
        hora_lord_index = (astro_weekday + hora_number) % 7
        return 60.0 if planet == self.weekday_lords[hora_lord_index] else 0.0

    def calculate_ayana_bala(self, planet, jd):
        """
        Calculate Ayana Bala (Declination strength) - CORRECTED
        
        Gets actual declination from Swiss Ephemeris
        Sun/Mars/Jupiter/Venus/Mercury: Strong in north
        Moon/Saturn: Strong in south
        """
        result = swe.calc_ut(jd, planet)
        if not result or len(result) < 1:
            return 0.0
        
        declination = result[0][1]
        
        if planet in [swe.SUN, swe.MARS, swe.JUPITER, swe.VENUS, swe.MERCURY]:
            if declination >= 0:
                ayana_bala = (abs(declination) / 24.0) * 60.0
            else:
                ayana_bala = 0.0
        else:  # Moon and Saturn
            if declination < 0:
                ayana_bala = (abs(declination) / 24.0) * 60.0
            else:
                ayana_bala = 0.0
        
        return round(min(ayana_bala, 60.0), 2)

    def calculate_kala_bala(self, planet, positions, jd, birth_time):
        """Calculate complete Kala Bala with all 8 sub-components"""
        time_parts = birth_time.split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        second = int(time_parts[2]) if len(time_parts) > 2 else 0
        time_decimal = hour + minute/60.0 + second/3600.0
        
        sun_long = positions[swe.SUN]['longitude']
        moon_long = positions[swe.MOON]['longitude']
        sun_sign = self.get_sign(sun_long)
        
        natonnata = self.calculate_natonnata_bala(planet, time_decimal)
        paksha = self.calculate_paksha_bala(planet, sun_long, moon_long)
        tribhaga = self.calculate_tribhaga_bala(planet, time_decimal)
        abda = self.calculate_abda_bala(planet, jd)
        masa = self.calculate_masa_bala(planet, sun_sign)
        vara = self.calculate_vara_bala(planet, jd)
        hora = self.calculate_hora_bala(planet, jd, time_decimal)
        ayana = self.calculate_ayana_bala(planet, jd)
        
        total = natonnata + paksha + tribhaga + abda + masa + vara + hora + ayana
        
        return {
            'total': round(total, 2),
            'natonnata_bala': round(natonnata, 2),
            'paksha_bala': round(paksha, 2),
            'tribhaga_bala': round(tribhaga, 2),
            'abda_bala': round(abda, 2),
            'masa_bala': round(masa, 2),
            'vara_bala': round(vara, 2),
            'hora_bala': round(hora, 2),
            'ayana_bala': round(ayana, 2)
        }

    def calculate_chesta_bala(self, planet, positions, jd):
        """Calculate Chesta Bala (Motional Strength)"""
        if planet == swe.SUN:
            result = swe.calc_ut(jd, swe.SUN)
            if result and len(result) > 0:
                declination = result[0][1]
                chesta_bala = 60 * (1 - abs(declination) / 24.0)
                return round(max(chesta_bala, 0), 2)
            return 30.0
        
        elif planet == swe.MOON:
            distance = positions[planet].get('distance', 0.00257)
            avg_distance = 0.00257
            if distance > 0:
                chesta_bala = 60 * (avg_distance / distance)
            else:
                chesta_bala = 30
            return round(min(max(chesta_bala, 0), 60), 2)
        
        else:
            speed = positions[planet]['speed']
            mean_speed = self.mean_motion.get(planet, 1.0)
            
            if speed < 0:
                return 60.0
            elif abs(speed) < mean_speed * 0.1:
                return 15.0
            elif speed < mean_speed * 0.5:
                return 15.0
            elif speed < mean_speed:
                return 30.0
            elif speed < mean_speed * 1.5:
                return 45.0
            else:
                return 60.0

    def calculate_drik_bala(self, planet, positions):
        """Calculate Drik Bala (Aspectual Strength)"""
        total_drik = 0
        planet_long = positions[planet]['longitude']
        orb = 15.0
        
        for other_planet, other_pos in positions.items():
            if other_planet == planet:
                continue
            
            other_long = other_pos['longitude']
            diff = self.angular_distance(planet_long, other_long)
            aspect_strength = 0
            
            # 7th house aspect (180°)
            if abs(diff - 180) <= orb:
                orb_factor = 1 - (abs(diff - 180) / orb)
                aspect_strength = 60 * orb_factor
            
            # Mars special aspects
            elif other_planet == swe.MARS:
                if abs(diff - 90) <= orb:
                    aspect_strength = 45 * (1 - abs(diff - 90) / orb)
                elif abs(diff - 240) <= orb:
                    aspect_strength = 45 * (1 - abs(diff - 240) / orb)
            
            # Jupiter special aspects
            elif other_planet == swe.JUPITER:
                if abs(diff - 120) <= orb:
                    aspect_strength = 45 * (1 - abs(diff - 120) / orb)
                elif abs(diff - 240) <= orb:
                    aspect_strength = 45 * (1 - abs(diff - 240) / orb)
            
            # Saturn special aspects
            elif other_planet == swe.SATURN:
                if abs(diff - 60) <= orb:
                    aspect_strength = 45 * (1 - abs(diff - 60) / orb)
                elif abs(diff - 270) <= orb:
                    aspect_strength = 45 * (1 - abs(diff - 270) / orb)
            
            if aspect_strength > 0:
                if other_planet in self.benefics:
                    total_drik += aspect_strength / 4.0
                else:
                    total_drik -= aspect_strength / 4.0
        
        return round(total_drik, 2)

    def calculate_ishta_kashta_phala(self, sthana_total, uchcha_bala):
        """Calculate Ishta Phala (benefic results) and Kashta Phala (malefic results)"""
        ishta_numerator = uchcha_bala + sthana_total
        ishta_denominator = 60 + 360
        ishta_phala = (ishta_numerator / ishta_denominator) * 60
        kashta_phala = 60 - ishta_phala
        return round(ishta_phala, 2), round(kashta_phala, 2)

    def calculate_shadbala(self, birth_data):
        """Calculate complete Shadbala for all planets"""
        jd = self.get_julian_day(birth_data['birth_date'], birth_data['birth_time'], 
                                 birth_data['timezone_offset'])
        
        positions, ayanamsa = self.get_planet_positions(jd)
        houses, ascendant = self.get_houses(jd, float(birth_data['latitude']), 
                                          float(birth_data['longitude']))
        
        results = {}
        
        for i, planet in enumerate(self.planets):
            planet_name = self.planet_names[i]
            
            # Calculate all six balas
            sthana = self.calculate_sthana_bala(planet, positions, houses)
            dig = self.calculate_dig_bala(planet, positions, houses)
            kala = self.calculate_kala_bala(planet, positions, jd, birth_data['birth_time'])
            chesta = self.calculate_chesta_bala(planet, positions, jd)
            naisargika = self.naisargika_bala[planet]
            drik = self.calculate_drik_bala(planet, positions)
            
            # Total Shadbala
            total_virupas = sthana['total'] + dig + kala['total'] + chesta + naisargika + drik
            total_rupas = total_virupas / 60.0
            
            # Minimum required
            min_required_rupas = self.required_strength.get(planet_name, 5.0)
            is_strong = total_rupas >= min_required_rupas
            
            strength_percentage = (total_rupas / min_required_rupas * 100) if min_required_rupas > 0 else 0.0
            strength_percentage = round(max(0.0, min(strength_percentage, 999.99)), 2)
            
            ishta_phala, kashta_phala = self.calculate_ishta_kashta_phala(
                sthana['total'], sthana['uchcha_bala']
            )
            
            # House position
            planet_sign = self.get_sign(positions[planet]['longitude'])
            asc_sign = self.get_sign(houses[0])
            house_num = ((planet_sign - asc_sign) % 12) + 1
            
            results[planet_name] = {
                'position': {
                    'longitude': round(positions[planet]['longitude'], 4),
                    'sign': self.get_sign_name(planet_sign),
                    'degree_in_sign': round(self.get_degree_in_sign(positions[planet]['longitude']), 4),
                    'house': house_num
                },
                'speed': round(positions[planet]['speed'], 4),
                'is_retrograde': positions[planet]['speed'] < 0,
                'total_rupas': round(total_rupas, 2),
                'total_virupas': round(total_virupas, 2),
                'minimum_required': min_required_rupas,
                'is_strong': is_strong,
                'strength_percentage': strength_percentage,
                'sthana_bala': {
                    'total': sthana['total'],
                    'uccha_bala': sthana['uchcha_bala'],
                    'saptavargaja_bala': sthana['saptavargaja_bala'],
                    'ojayugma_bala': sthana['ojayugma_bala'],
                    'kendradi_bala': sthana['kendradi_bala'],
                    'drekkana_bala': sthana['drekkana_bala']
                },
                'dig_bala': dig,
                'kala_bala': {
                    'total': kala['total'],
                    'nathonnata_bala': kala['natonnata_bala'],
                    'paksha_bala': kala['paksha_bala'],
                    'tribhaga_bala': kala['tribhaga_bala'],
                    'abda_masa_vara_hora_bala': round(
                        kala['abda_bala'] + kala['masa_bala'] + 
                        kala['vara_bala'] + kala['hora_bala'], 2
                    ),
                    'ayana_bala': kala['ayana_bala']
                },
                'chesta_bala': chesta,
                'naisargika_bala': naisargika,
                'drik_bala': drik,
                'ishta_phala': ishta_phala,
                'kashta_phala': kashta_phala
            }
        
        total_strength = sum(results[p]['total_virupas'] for p in results)
        avg_strength = total_strength / len(results)
        strong_planets = [p for p in results if results[p]['is_strong']]
        
        return {
            'user_name': birth_data['user_name'],
            'birth_details': {
                'date': birth_data['birth_date'],
                'time': birth_data['birth_time'],
                'latitude': birth_data['latitude'],
                'longitude': birth_data['longitude'],
                'timezone_offset': birth_data['timezone_offset'],
                'ayanamsa': round(ayanamsa, 6),
                'ascendant': round(ascendant, 2),
                'ascendant_sign': self.get_sign_name(self.get_sign(ascendant))
            },
            'summary': {
                'total_strength': round(total_strength, 2),
                'average_strength': round(avg_strength, 2),
                'strong_planets': strong_planets,
                'strong_planet_count': len(strong_planets)
            },
            'shadbala_results': results
        }

    def get_sign_name(self, sign_num):
        """Get sign name from number"""
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        return signs[sign_num % 12]