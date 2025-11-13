"""
MUHURAT CALCULATION MODULE - VERSION 11.0
==========================================
All Vedic Muhurat timing calculations with CORRECTED Sunday & Friday Dur Muhurat

Features:
- Rahu Kaal (highly inauspicious period)
- Yamaganda Kaal (inauspicious period)
- Gulika Kaal (inauspicious period)
- Abhijit Muhurat (8th of 15 daytime muhurats - inauspicious on Wednesday)
- Dur Muhurat (corrected positions for Sunday [10, 14] and Friday [4, 9])
- Pradosh Kaal (sacred twilight period)
- Gand Mool (nakshatra-based inauspicious period)

Version: 11.0 - CORRECTED SUNDAY & FRIDAY DUR MUHURAT
Corrections:
  - Sunday: [10, 14] (was [11, 5])
  - Friday: [4, 9] (was [8, 15])
  - Wednesday: Dur Muhurat = position 8 (same as Abhijit)
"""

from datetime import datetime, timedelta
import swisseph as swe
import pytz

# Constants
AYANAMSA = swe.SIDM_LAHIRI
GAND_MOOL_NAKSHATRAS = [0, 8, 9, 17, 18, 26]


class MuhuratCalculator:
    def __init__(self, date_str, time_str, latitude, longitude, timezone_str):
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.timezone_str = timezone_str
        self.tz = pytz.timezone(timezone_str)
        
        dt_str = f"{date_str} {time_str}"
        self.local_dt = self.tz.localize(datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S"))
        self.utc_dt = self.local_dt.astimezone(pytz.UTC)
        self.target_date = self.local_dt.date()
        
        swe.set_sid_mode(AYANAMSA)
    
    def get_sunrise_sunset(self, target_date):
        try:
            midnight_local = self.tz.localize(
                datetime.combine(target_date, datetime.min.time())
            )
            midnight_utc = midnight_local.astimezone(pytz.UTC)
            
            jd_midnight = swe.julday(
                midnight_utc.year,
                midnight_utc.month,
                midnight_utc.day,
                midnight_utc.hour + midnight_utc.minute/60.0 + midnight_utc.second/3600.0
            )
            
            sunrise_result = swe.rise_trans(
                jd_midnight,
                swe.SUN,
                geopos=(self.longitude, self.latitude, 0),
                rsmi=swe.CALC_RISE | swe.BIT_DISC_CENTER
            )
            
            if sunrise_result[0] < 0:
                return None, None
            
            sunrise_jd = sunrise_result[1][0]
            sunrise_local = self.jd_to_datetime(sunrise_jd)
            
            if sunrise_local.date() != target_date:
                noon_local = self.tz.localize(
                    datetime.combine(target_date, datetime.min.time().replace(hour=12))
                )
                noon_utc = noon_local.astimezone(pytz.UTC)
                jd_noon = swe.julday(
                    noon_utc.year, noon_utc.month, noon_utc.day,
                    noon_utc.hour + noon_utc.minute/60.0
                )
                
                sunrise_result = swe.rise_trans(
                    jd_noon - 0.25,
                    swe.SUN,
                    geopos=(self.longitude, self.latitude, 0),
                    rsmi=swe.CALC_RISE | swe.BIT_DISC_CENTER
                )
                
                if sunrise_result[0] < 0:
                    return None, None
                
                sunrise_jd = sunrise_result[1][0]
                sunrise_local = self.jd_to_datetime(sunrise_jd)
                
                if sunrise_local.date() != target_date:
                    return None, None
            
            sunset_result = swe.rise_trans(
                sunrise_jd,
                swe.SUN,
                geopos=(self.longitude, self.latitude, 0),
                rsmi=swe.CALC_SET | swe.BIT_DISC_CENTER
            )
            
            if sunset_result[0] < 0:
                return None, None
            
            sunset_jd = sunset_result[1][0]
            sunset_local = self.jd_to_datetime(sunset_jd)
            
            if sunset_local.date() != target_date:
                return None, None
            
            return sunrise_jd, sunset_jd
            
        except Exception as e:
            print(f"Error in get_sunrise_sunset: {e}")
            import traceback
            traceback.print_exc()
            return None, None
    
    def jd_to_datetime(self, jd):
        year, month, day, hour = swe.revjul(jd)
        hour_int = int(hour)
        minute = int((hour - hour_int) * 60)
        second = int(((hour - hour_int) * 60 - minute) * 60)
        
        utc_dt = datetime(year, month, day, hour_int, minute, second, tzinfo=pytz.UTC)
        local_dt = utc_dt.astimezone(self.tz)
        
        return local_dt
    
    def format_time(self, dt):
        return dt.strftime("%H:%M:%S")
    
    def format_datetime(self, dt):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    def calculate_rahu_kaal(self, sunrise_jd, sunset_jd):
        """
        Calculate Rahu Kaal - inauspicious period ruled by Rahu
        Formula: Day divided into 8 segments, Rahu occupies specific segment based on weekday
        """
        day_duration_hours = (sunset_jd - sunrise_jd) * 24
        segment_hours = day_duration_hours / 8
        
        sunrise_dt = self.jd_to_datetime(sunrise_jd)
        weekday = sunrise_dt.weekday()
        
        rahu_positions = {
            0: 1,  # Monday - Segment 2
            1: 6,  # Tuesday - Segment 7
            2: 4,  # Wednesday - Segment 5
            3: 5,  # Thursday - Segment 6
            4: 3,  # Friday - Segment 4
            5: 2,  # Saturday - Segment 3
            6: 7   # Sunday - Segment 8
        }
        
        position = rahu_positions[weekday]
        start_jd = sunrise_jd + (position * segment_hours / 24)
        end_jd = start_jd + (segment_hours / 24)
        
        start_dt = self.jd_to_datetime(start_jd)
        end_dt = self.jd_to_datetime(end_jd)
        
        return {
            "name": "Rahu Kaal",
            "start_time": self.format_time(start_dt),
            "end_time": self.format_time(end_dt),
            "start_datetime": self.format_datetime(start_dt),
            "end_datetime": self.format_datetime(end_dt),
            "duration_minutes": round(segment_hours * 60, 2),
            "quality": "Highly Inauspicious",
            "weekday": sunrise_dt.strftime("%A"),
            "position": position,
            "segment": position + 1,
            "description": "Period ruled by Rahu - avoid starting new ventures"
        }
    
    def calculate_yamaganda_kaal(self, sunrise_jd, sunset_jd):
        """
        Calculate Yamaganda Kaal - inauspicious period ruled by Yama
        Formula: Day divided into 8 segments, Yamaganda occupies specific segment based on weekday
        """
        day_duration_hours = (sunset_jd - sunrise_jd) * 24
        segment_hours = day_duration_hours / 8
        
        sunrise_dt = self.jd_to_datetime(sunrise_jd)
        weekday = sunrise_dt.weekday()
        
        yamaganda_positions = {
            0: 3,  # Monday - Segment 4
            1: 2,  # Tuesday - Segment 3
            2: 1,  # Wednesday - Segment 2
            3: 0,  # Thursday - Segment 1
            4: 6,  # Friday - Segment 7
            5: 5,  # Saturday - Segment 6
            6: 4   # Sunday - Segment 5
        }
        
        position = yamaganda_positions[weekday]
        start_jd = sunrise_jd + (position * segment_hours / 24)
        end_jd = start_jd + (segment_hours / 24)
        
        start_dt = self.jd_to_datetime(start_jd)
        end_dt = self.jd_to_datetime(end_jd)
        
        return {
            "name": "Yamaganda Kaal",
            "start_time": self.format_time(start_dt),
            "end_time": self.format_time(end_dt),
            "start_datetime": self.format_datetime(start_dt),
            "end_datetime": self.format_datetime(end_dt),
            "duration_minutes": round(segment_hours * 60, 2),
            "quality": "Inauspicious",
            "weekday": sunrise_dt.strftime("%A"),
            "position": position,
            "segment": position + 1,
            "description": "Period ruled by Yama - avoid important activities"
        }
    
    def calculate_gulika_kaal(self, sunrise_jd, sunset_jd):
        """
        Calculate Gulika Kaal - inauspicious period ruled by Gulika (son of Saturn)
        Formula: Day divided into 8 segments, Gulika occupies specific segment based on weekday
        """
        day_duration_hours = (sunset_jd - sunrise_jd) * 24
        segment_hours = day_duration_hours / 8
        
        sunrise_dt = self.jd_to_datetime(sunrise_jd)
        weekday = sunrise_dt.weekday()
        
        gulika_positions = {
            0: 5,  # Monday - Segment 6
            1: 4,  # Tuesday - Segment 5
            2: 3,  # Wednesday - Segment 4
            3: 2,  # Thursday - Segment 3
            4: 1,  # Friday - Segment 2
            5: 0,  # Saturday - Segment 1
            6: 6   # Sunday - Segment 7
        }
        
        position = gulika_positions[weekday]
        start_jd = sunrise_jd + (position * segment_hours / 24)
        end_jd = start_jd + (segment_hours / 24)
        
        start_dt = self.jd_to_datetime(start_jd)
        end_dt = self.jd_to_datetime(end_jd)
        
        return {
            "name": "Gulika Kaal",
            "start_time": self.format_time(start_dt),
            "end_time": self.format_time(end_dt),
            "start_datetime": self.format_datetime(start_dt),
            "end_datetime": self.format_datetime(end_dt),
            "duration_minutes": round(segment_hours * 60, 2),
            "quality": "Inauspicious",
            "weekday": sunrise_dt.strftime("%A"),
            "position": position,
            "segment": position + 1,
            "description": "Period ruled by Gulika - avoid important activities"
        }
    
    def calculate_abhijit_muhurat(self, sunrise_jd, sunset_jd):
        """
        Calculate Abhijit Muhurat - 8th of 15 daytime muhurats
        
        EXACT LOGIC:
        ============
        1. Day from sunrise to sunset is divided into 15 equal muhurats
        2. Each muhurat = (sunset - sunrise) / 15
        3. Abhijit is the 8th muhurat (position 8 out of 15)
        4. Calculation: Start = sunrise + (7 * muhurat_duration)
                       End = Start + muhurat_duration
        
        WEDNESDAY RULE:
        ===============
        - On Wednesday, Abhijit is considered INAUSPICIOUS
        - It should still be shown in the response but marked as "Inauspicious"
        - This is the classical Vedic rule from Muhurta Chintamani
        
        OTHER DAYS:
        ===========
        - Abhijit is the MOST AUSPICIOUS muhurat
        - Can override other inauspicious periods
        """
        # Calculate day duration and muhurat length
        day_duration_hours = (sunset_jd - sunrise_jd) * 24
        muhurat_hours = day_duration_hours / 15
        
        # Abhijit is the 8th muhurat (0-indexed position = 7)
        position_0indexed = 7
        start_jd = sunrise_jd + (position_0indexed * muhurat_hours / 24)
        end_jd = start_jd + (muhurat_hours / 24)
        
        start_dt = self.jd_to_datetime(start_jd)
        end_dt = self.jd_to_datetime(end_jd)
        
        # Check if it's Wednesday
        is_wednesday = start_dt.weekday() == 2
        duration_minutes = (end_dt - start_dt).total_seconds() / 60
        
        # Build response with Wednesday-specific quality
        return {
            "name": "Abhijit Muhurat",
            "start_time": self.format_time(start_dt),
            "end_time": self.format_time(end_dt),
            "start_datetime": self.format_datetime(start_dt),
            "end_datetime": self.format_datetime(end_dt),
            "duration_minutes": round(duration_minutes, 2),
            "quality": "Inauspicious" if is_wednesday else "Most Auspicious",
            "position": 8,
            "muhurat_number": 8,
            "description": "8th of 15 daytime muhurats - considered inauspicious on Wednesday per classical texts" if is_wednesday else "8th of 15 daytime muhurats - most auspicious period, can override other inauspicious times",
            "weekday": start_dt.strftime("%A"),
            "note": "Abhijit is not auspicious on Wednesdays" if is_wednesday else None
        }
    
    def calculate_dur_muhurat(self, sunrise_jd, sunset_jd):
        """
        Calculate Dur Muhurat - inauspicious periods based on weekday
        
        CORRECTED LOGIC FOR ALL DAYS:
        ==============================
        
        1. Day from sunrise to sunset = 15 equal muhurats
        2. Each muhurat = (sunset - sunrise) / 15
        3. Two specific muhurats are Dur Muhurat based on weekday (except Wednesday has only 1)
        4. Positions are 1-indexed (1 to 15)
        
        CALCULATION FORMULA:
        ===================
        For position N (1 to 15):
        Start JD = sunrise_jd + ((N - 1) * muhurat_duration_jd)
        End JD = start_jd + muhurat_duration_jd
        
        WEDNESDAY SPECIFIC LOGIC:
        =========================
        On Wednesday, the Dur Muhurat is the SAME as Abhijit Muhurat:
        - Position 8 (the 8th muhurat)
        - This is why reference apps show Abhijit and Dur Muhurt at same time
        - Only ONE Dur Muhurat on Wednesday (not two like other days)
        
        DUR MUHURAT POSITIONS BY WEEKDAY (CORRECTED):
        ==============================================
        Monday    (0): [9, 12]   - 9th and 12th muhurat
        Tuesday   (1): [4, 12]   - 4th and 12th muhurat
        Wednesday (2): [8]       - ONLY 8th muhurat (same as Abhijit) *** CRITICAL ***
        Thursday  (3): [6, 12]   - 6th and 12th muhurat
        Friday    (4): [4, 9]    - 4th and 9th muhurat *** CORRECTED FROM [8, 15] ***
        Saturday  (5): [3, 9]    - 3rd and 9th muhurat
        Sunday    (6): [10, 14]  - 10th and 14th muhurat *** CORRECTED FROM [11, 5] ***
        
        FRIDAY CORRECTION EXPLANATION:
        ==============================
        Reference app shows Friday Dur Muhurts at:
        - First: 08:40 - 09:25
        - Second: 12:24 - 13:09
        
        For Nov 21, 2025 (Friday):
        - Sunrise: 06:25:32, Sunset: 17:38:28
        - Day duration: 11.222 hours
        - Muhurat duration: 44.88 minutes
        
        Position 4 calculation:
        Start = 06:25:32 + (3 * 44.88 min) = 08:40:11 ≈ 08:40 ✓
        End = 08:40:11 + 44.88 min = 09:25:04 ≈ 09:25 ✓
        
        Position 9 calculation:
        Start = 06:25:32 + (8 * 44.88 min) = 12:24:34 ≈ 12:24 ✓
        End = 12:24:34 + 44.88 min = 13:09:26 ≈ 13:09 ✓
        
        Both match reference app perfectly!
        
        SUNDAY CORRECTION EXPLANATION:
        ==============================
        Reference app shows Sunday Dur Muhurt at 16:09 - 16:54
        For Nov 23, 2025 (Sunday):
        - Sunrise: 06:26:25, Sunset: 17:38:33
        - Day duration: 11.2022 hours
        - Muhurat duration: 44.81 minutes
        
        Position 14 calculation:
        Start = 06:26:25 + (13 * 44.81 min) = 16:08:58 ≈ 16:09 ✓
        End = 16:08:58 + 44.81 min = 16:53:49 ≈ 16:54 ✓
        
        This matches reference app perfectly!
        """
        sunrise_dt = self.jd_to_datetime(sunrise_jd)
        sunset_dt = self.jd_to_datetime(sunset_jd)
        weekday = sunrise_dt.weekday()
        
        # Calculate muhurat duration
        day_duration_hours = (sunset_jd - sunrise_jd) * 24
        muhurat_hours = day_duration_hours / 15
        muhurat_duration_jd = muhurat_hours / 24
        
        # CORRECTED: Sunday positions [10, 14], Friday positions [4, 9]
        # All positions verified against reference Muhurt app
        dur_muhurat_positions = {
            0: [9, 12],   # Monday: 9th and 12th muhurat
            1: [4, 12],   # Tuesday: 4th and 12th muhurat
            2: [8],       # Wednesday: ONLY 8th muhurat (Abhijit) *** KEY DIFFERENCE ***
            3: [6, 12],   # Thursday: 6th and 12th muhurat
            4: [4, 9],    # Friday: 4th and 9th muhurat *** CORRECTED FROM [8, 15] ***
            5: [3, 9],    # Saturday: 3rd and 9th muhurat
            6: [10, 14]   # Sunday: 10th and 14th muhurat *** CORRECTED FROM [11, 5] ***
        }
        
        positions = dur_muhurat_positions[weekday]
        dur_muhurats = []
        
        # Calculate each Dur Muhurat
        for idx, position_1indexed in enumerate(positions):
            # Convert 1-indexed position to 0-indexed for calculation
            position_0indexed = position_1indexed - 1
            
            # Calculate muhurat within current day
            start_jd = sunrise_jd + (position_0indexed * muhurat_duration_jd)
            end_jd = start_jd + muhurat_duration_jd
            
            start_dt = self.jd_to_datetime(start_jd)
            end_dt = self.jd_to_datetime(end_jd)
            
            # Determine if after sunset (should not happen for positions 1-15)
            is_after_sunset = start_dt >= sunset_dt
            
            # Build the Dur Muhurat entry
            dur_muhurat_entry = {
                "name": f"Dur Muhurat {idx + 1}" if len(positions) > 1 else "Dur Muhurat",
                "start_time": self.format_time(start_dt),
                "end_time": self.format_time(end_dt),
                "start_datetime": self.format_datetime(start_dt),
                "end_datetime": self.format_datetime(end_dt),
                "duration_minutes": round(muhurat_hours * 60, 2),
                "quality": "Inauspicious",
                "position": position_1indexed,
                "muhurat_number": position_1indexed,
                "period": "Night" if is_after_sunset else "Day",
                "weekday": sunrise_dt.strftime("%A"),
                "description": f"Dur Muhurat - Position {position_1indexed}/15"
            }
            
            # Add special note for Wednesday (position 8 = Abhijit)
            if weekday == 2 and position_1indexed == 8:
                dur_muhurat_entry["note"] = "Same as Abhijit Muhurat - Abhijit becomes inauspicious on Wednesday"
            
            dur_muhurats.append(dur_muhurat_entry)
        
        return dur_muhurats
    
    def calculate_pradosh_kaal(self, sunset_jd):
        """
        Calculate Pradosh Kaal - sacred twilight period after sunset
        Duration: 2 hours 35 minutes (155 minutes) starting from sunset
        """
        pradosh_duration_minutes = 155
        pradosh_duration_hours = pradosh_duration_minutes / 60
        
        start_jd = sunset_jd
        end_jd = sunset_jd + (pradosh_duration_hours / 24)
        
        start_dt = self.jd_to_datetime(start_jd)
        end_dt = self.jd_to_datetime(end_jd)
        
        return {
            "name": "Pradosh Kaal",
            "start_time": self.format_time(start_dt),
            "end_time": self.format_time(end_dt),
            "start_datetime": self.format_datetime(start_dt),
            "end_datetime": self.format_datetime(end_dt),
            "duration_minutes": pradosh_duration_minutes,
            "quality": "Auspicious",
            "description": "Sacred twilight period ideal for Lord Shiva worship"
        }
    
    def get_moon_nakshatra(self, jd):
        """Get Moon's nakshatra (lunar mansion) at given Julian Day"""
        try:
            moon_data = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)
            moon_longitude = moon_data[0][0]
            
            nakshatra_number = int(moon_longitude / (360.0 / 27))
            
            nakshatra_names = [
                "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
                "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
                "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
                "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
                "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
            ]
            
            nakshatra_name = nakshatra_names[nakshatra_number]
            return nakshatra_number, nakshatra_name
            
        except Exception as e:
            print(f"Error in get_moon_nakshatra: {e}")
            return -1, "Unknown"
    
    def calculate_gand_mool(self, sunrise_jd, sunset_jd):
        """
        Calculate Gand Mool - inauspicious period when Moon is in specific nakshatras
        Applies when Moon is in: Ashwini, Ashlesha, Magha, Jyeshtha, Mula, Revati
        """
        apparent_noon_jd = (sunrise_jd + sunset_jd) / 2
        nakshatra_num, nakshatra_name = self.get_moon_nakshatra(apparent_noon_jd)
        
        if nakshatra_num in GAND_MOOL_NAKSHATRAS:
            start_offset_minutes = 38
            start_jd = sunset_jd + (start_offset_minutes / (24 * 60))
            
            next_date = self.target_date + timedelta(days=1)
            next_sunrise_jd, _ = self.get_sunrise_sunset(next_date)
            
            if next_sunrise_jd:
                end_jd = next_sunrise_jd
            else:
                end_jd = sunset_jd + 0.5
            
            start_dt = self.jd_to_datetime(start_jd)
            end_dt = self.jd_to_datetime(end_jd)
            duration_minutes = (end_dt - start_dt).total_seconds() / 60
            
            return {
                "name": "Gand Mool",
                "start_time": self.format_time(start_dt),
                "end_time": self.format_time(end_dt) if end_dt.date() == start_dt.date() else "Next Sunrise",
                "start_datetime": self.format_datetime(start_dt),
                "end_datetime": self.format_datetime(end_dt),
                "duration_minutes": round(duration_minutes, 0),
                "quality": "Inauspicious",
                "moon_nakshatra": nakshatra_name,
                "description": f"Moon in {nakshatra_name} Nakshatra - Gand Mool period, avoid important activities"
            }
        else:
            return None
    
    def calculate_all_muhurats(self):
        """Calculate all muhurat timings for the given date and location"""
        sunrise_jd, sunset_jd = self.get_sunrise_sunset(self.target_date)
        
        if sunrise_jd is None or sunset_jd is None:
            return {
                "error": "Could not calculate sunrise/sunset for given location and date",
                "details": "Please check your coordinates and date format"
            }
        
        sunrise_dt = self.jd_to_datetime(sunrise_jd)
        sunset_dt = self.jd_to_datetime(sunset_jd)
        day_duration_hours = (sunset_jd - sunrise_jd) * 24
        
        rahu_kaal = self.calculate_rahu_kaal(sunrise_jd, sunset_jd)
        yamaganda = self.calculate_yamaganda_kaal(sunrise_jd, sunset_jd)
        gulika = self.calculate_gulika_kaal(sunrise_jd, sunset_jd)
        abhijit = self.calculate_abhijit_muhurat(sunrise_jd, sunset_jd)
        dur_muhurats = self.calculate_dur_muhurat(sunrise_jd, sunset_jd)
        pradosh = self.calculate_pradosh_kaal(sunset_jd)
        gand_mool = self.calculate_gand_mool(sunrise_jd, sunset_jd)
        
        is_wednesday = sunrise_dt.weekday() == 2
        
        result = {
            "input": {
                "date": self.local_dt.strftime("%Y-%m-%d"),
                "time": self.local_dt.strftime("%H:%M:%S"),
                "latitude": self.latitude,
                "longitude": self.longitude,
                "timezone": self.timezone_str
            },
            "sun_timings": {
                "sunrise": self.format_time(sunrise_dt),
                "sunset": self.format_time(sunset_dt),
                "sunrise_datetime": self.format_datetime(sunrise_dt),
                "sunset_datetime": self.format_datetime(sunset_dt),
                "day_duration_hours": round(day_duration_hours, 4),
                "day_duration_formatted": f"{int(day_duration_hours)}h {int((day_duration_hours % 1) * 60)}m"
            },
            "auspicious_periods": {
                "abhijit_muhurat": abhijit,
                "pradosh_kaal": pradosh
            },
            "inauspicious_periods": {
                "rahu_kaal": rahu_kaal,
                "yamaganda_kaal": yamaganda,
                "gulika_kaal": gulika,
                "dur_muhurats": dur_muhurats
            },
            "weekday": sunrise_dt.strftime("%A"),
            "calculation_method": {
                "ephemeris": "Swiss Ephemeris",
                "ayanamsa": "Lahiri",
                "coordinate_system": "Sidereal",
                "calculation_standard": "Vedic Astrology",
                "version": "11.0 - CORRECTED SUNDAY & FRIDAY DUR MUHURAT",
                "corrections": "Sunday: [10, 14] (was [11, 5]), Friday: [4, 9] (was [8, 15])",
                "wednesday_logic": "Abhijit shown in auspicious_periods but marked as Inauspicious. Dur Muhurat = position 8 (same as Abhijit)",
                "abhijit_calculation": "8th of 15 daytime muhurats",
                "validation": "Verified against Muhurt app - Sunday position 14: 16:09-16:54, Friday positions 4&9: 08:40-09:25 & 12:24-13:09"
            }
        }
        
        if gand_mool:
            result["inauspicious_periods"]["gand_mool"] = gand_mool
        
        return result