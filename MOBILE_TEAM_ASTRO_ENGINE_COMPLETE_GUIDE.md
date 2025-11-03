# 📱 ASTRO ENGINE - COMPLETE GUIDE FOR MOBILE DEVELOPMENT TEAM
## React Native + TypeScript Integration

**Version:** 1.3.0
**Target Platform:** React Native (iOS + Android)
**Last Updated:** October 30, 2025
**Status:** 🟢 PRODUCTION READY

---

## 📋 TABLE OF CONTENTS

1. [Executive Summary](#executive-summary)
2. [What is Astro Engine?](#what-is-astro-engine)
3. [Core Capabilities & Features](#core-capabilities--features)
4. [API Architecture Overview](#api-architecture-overview)
5. [Authentication & Security](#authentication--security)
6. [Complete API Reference](#complete-api-reference)
7. [React Native Integration](#react-native-integration)
8. [TypeScript Interfaces](#typescript-interfaces)
9. [Error Handling](#error-handling)
10. [Performance Optimization](#performance-optimization)
11. [Best Practices](#best-practices)
12. [Complete Code Examples](#complete-code-examples)
13. [Testing Strategy](#testing-strategy)
14. [Troubleshooting](#troubleshooting)

---

## 🎯 EXECUTIVE SUMMARY

**Astro Engine is the Heart of AstroCorp Mobile Application**

Astro Engine is a **production-grade Vedic Astrology calculation engine** that provides:
- ✅ **95+ API Endpoints** for all astrological calculations
- ✅ **3 Ayanamsa Systems:** Lahiri, Raman, KP New
- ✅ **Enterprise-Grade:** Rate limiting, caching, monitoring, error handling
- ✅ **Global CDN:** CloudFlare-powered, < 500ms response time
- ✅ **Fully Typed:** Complete TypeScript support
- ✅ **Battle-Tested:** 40,676+ lines of calculation code

**Your mobile app will:**
1. Send user birth details (date, time, location)
2. Receive complete astrological calculations (charts, dashas, yogas, doshas)
3. Display beautiful UI with the calculation results

**This document contains EVERYTHING you need to integrate.**

---

## 🔮 WHAT IS ASTRO ENGINE?

### **Purpose**
Astro Engine is a **REST API service** that performs complex Vedic astrological calculations using Swiss Ephemeris data. It's the computational brain behind every astrological feature in the AstroCorp mobile app.

### **Technology Stack**
- **Backend:** Python 3.13 + Flask 3.1.2
- **Calculations:** Swiss Ephemeris (pyswisseph 2.10.3.2)
- **Deployment:** DigitalOcean App Platform (Bangalore, India)
- **CDN:** CloudFlare (300+ global edge locations)
- **Authentication:** API Key-based (per-service keys)

### **Production URL**
```
https://astroengine.astrocorp.in
```

### **What Makes It Special?**
1. **Accuracy:** Uses Swiss Ephemeris - the gold standard for astronomical calculations
2. **Complete:** Covers natal charts, divisional charts (D1-D60), dashas, yogas, doshas, numerology
3. **Fast:** Optimized algorithms with optional Redis caching
4. **Reliable:** Enterprise error handling, graceful degradation, circuit breakers
5. **Scalable:** Designed to handle 1M+ users

---

## 🚀 CORE CAPABILITIES & FEATURES

### **1. NATAL CHARTS (Birth Charts)**
Calculate complete birth chart with planetary positions, houses, nakshatras.

**What You Get:**
- Planetary positions (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu)
- Ascendant (Lagna) details
- 12 Houses with sign placements
- Nakshatra and Pada for each planet
- Retrograde status
- Ayanamsa value

**Use Case:** Main birth chart screen in your app

---

### **2. DIVISIONAL CHARTS (Varga Charts)**
16 divisional charts from D2 to D60 for detailed life analysis.

**Available Charts:**
| Chart | Name | Purpose |
|-------|------|---------|
| D1 | Rasi | Birth chart (main) |
| D2 | Hora | Wealth & prosperity |
| D3 | Drekkana | Siblings & courage |
| D4 | Chaturthamsha | Property & assets |
| D7 | Saptamsha | Children & progeny |
| D9 | Navamsa | Spouse & marriage (most important) |
| D10 | Dashamsha | Career & profession |
| D12 | Dwadashamsha | Parents |
| D16 | Shodashamsha | Vehicles & comforts |
| D20 | Vimshams | Spiritual practices |
| D24 | Chaturvimshamsha | Education & learning |
| D27 | Saptavimshamsha | Strengths & weaknesses |
| D30 | Trimshamsha | Misfortunes & troubles |
| D40 | Khavedamsha | Auspicious events |
| D45 | Akshavedamsha | Character & personality |
| D60 | Shashtiamsha | Karma & past life |

**Use Case:** Detailed analysis sections (Marriage compatibility, Career prospects, etc.)

---

### **3. DASHA SYSTEMS (Planetary Periods)**
Vimshottari Dasha system with 5 levels of precision.

**Levels:**
1. **Mahadasha** - Major period (up to 20 years)
2. **Antardasha** - Sub-period (within Mahadasha)
3. **Pratyantardasha** - Sub-sub-period
4. **Sookshma Dasha** - Micro period
5. **Prana Dasha** - Ultra-fine period (days/hours)

**Available Durations:**
- Current dasha (right now)
- Day, Week, Month
- 1 year, 2 years, 3 years
- 3 months, 6 months
- Full 120-year cycle

**Use Case:** "Current Planetary Period" feature, Daily predictions, Timeline view

---

### **4. SPECIAL LAGNAS (Ascendants)**
9 different types of ascendants for various predictions.

**Types:**
- **Bhava Lagna** - For house-based predictions
- **Hora Lagna** - For wealth timing
- **Sripathi Bhava** - Unequal house system
- **KP Bhava** - KP system houses
- **Equal Bhava** - Equal house system
- **Arudha Lagna** - Material manifestations
- **Karkamsha Lagna (D1)** - Soul's purpose
- **Karkamsha Lagna (D9)** - Spouse's nature
- **Moon Chart** - Emotions & mind
- **Sun Chart** - Soul & vitality

**Use Case:** Advanced analysis features, Prediction refinement

---

### **5. ASHTAKAVARGHA (Strength Analysis)**
Quantitative strength analysis of houses and planets.

**Types:**
- **Bhinnashtakavarga** - Individual planet strength in each house
- **Sarvashtakavarga** - Combined strength of all planets
- **Shodasha Varga Summary** - Strength across 16 divisional charts

**Output:** Numerical scores (0-8 points per house)

**Use Case:** "House Strength" feature, Timing predictions, Remedies

---

### **6. YOGAS (Planetary Combinations)**
Special planetary combinations that indicate specific results.

**Implemented Yogas:**
- **Gaja Kesari Yoga** - Jupiter-Moon combination (wealth, wisdom)
- **Guru Mangal Yoga** - Jupiter-Mars combination (success, property)
- **Budha Aditya Yoga** - Mercury-Sun combination (intelligence)
- **Chandra Mangal Yoga** - Moon-Mars combination (wealth, property)

**Output:**
- Yoga present or not
- Strength (0-100%)
- Planets involved
- Houses involved
- Detailed analysis

**Use Case:** "Special Yogas" section, Personality traits

---

### **7. DOSHAS (Afflictions)**
Negative planetary combinations that may cause challenges.

**Implemented Doshas:**
- **Mangal Dosha (Angarak)** - Mars affliction (marriage delays)
- **Guru Chandal Dosha** - Jupiter-Rahu conjunction (judgment issues)
- **Shrapit Dosha** - Saturn-Rahu conjunction (curses)
- **Sade Sati** - Saturn's 7.5-year transit period (challenges)

**Output:**
- Dosha present or not
- Severity level
- Current phase (if applicable)
- Remedies (textual)
- Start/End dates

**Use Case:** "Doshas & Remedies" feature, Compatibility analysis

---

### **8. NUMEROLOGY**
Numerological calculations based on name and birth date.

**Types:**
- **Chaldean Numerology** - Ancient Chaldean system
- **Lo Shu Grid** - Chinese grid-based analysis

**Output:**
- Life path number
- Destiny number
- Soul urge number
- Personality number
- Grid analysis (missing numbers, plane strengths)

**Use Case:** "Numerology" section, Name recommendations

---

### **9. SPECIAL CHARTS**
Unique chart types for specific purposes.

- **Sudarshan Chakra** - Triple-ring chart (Lagna, Moon, Sun)
- **Transit Chart** - Current planetary positions
- **Horary (Prashna)** - Question-based astrology (KP system)

**Use Case:** Daily predictions, Q&A feature

---

### **10. RULING PLANETS (KP System)**
Current ruling planets for timing and predictions.

**Output:**
- Day lord
- Lagna lord, Nakshatra lord, Sub-lord
- Moon lord, Nakshatra lord, Sub-lord
- Combined ruling planets list
- Balance of Dasha

**Use Case:** KP system features, Timing predictions

---

## 🏗️ API ARCHITECTURE OVERVIEW

### **Three Ayanamsa Systems**
Astro Engine supports 3 different ayanamsa (zodiac) systems:

| System | Prefix | Use Case | Ayanamsa Type |
|--------|--------|----------|---------------|
| **Lahiri** | `/lahiri/*` | Traditional Vedic (India standard) | Lahiri (Chitra Paksha) |
| **Raman** | `/raman/*` | B.V. Raman system | Raman |
| **KP** | `/kp/*` | Krishnamurti Paddhati | KP New (Krishnamurti) |

**Important:** All three systems can calculate the same features, but with different zodiac references.

### **Base URL Structure**
```
https://astroengine.astrocorp.in/{system}/{feature}
```

**Examples:**
- `https://astroengine.astrocorp.in/lahiri/natal` - Lahiri natal chart
- `https://astroengine.astrocorp.in/raman/natal` - Raman natal chart
- `https://astroengine.astrocorp.in/kp/calculate_kp_planets_cusps` - KP planets

### **HTTP Methods**
- **POST** - All calculation endpoints use POST (even for read operations)
- **GET** - Only for health/status endpoints

### **Request Format**
All requests:
- **Content-Type:** `application/json`
- **Authorization:** `X-API-Key: <your-api-key>`
- **Body:** JSON with birth details

### **Response Format**
All responses:
- **Content-Type:** `application/json`
- **Status Codes:** 200 (success), 400 (validation error), 401 (auth error), 500 (server error)
- **Compression:** Automatic gzip/brotli (60-80% size reduction)

---

## 🔐 AUTHENTICATION & SECURITY

### **API Key Authentication**
Every request must include an API key in the header.

**Header Format:**
```http
X-API-Key: astro_corp_backend_F5XpEFrnQI-NZHlRWZVmcHT0uDvoPVXv
```

**Your API Key:**
```
astro_corp_backend_F5XpEFrnQI-NZHlRWZVmcHT0uDvoPVXv
```

**IMPORTANT SECURITY RULES:**
1. ⚠️ **NEVER** commit API keys to GitHub
2. ⚠️ **NEVER** hardcode API keys in source code
3. ✅ **ALWAYS** store in environment variables
4. ✅ **ALWAYS** use .env files (excluded from git)

### **Environment Variable Setup**
```bash
# .env file (add to .gitignore!)
ASTRO_ENGINE_URL=https://astroengine.astrocorp.in
ASTRO_ENGINE_API_KEY=astro_corp_backend_F5XpEFrnQI-NZHlRWZVmcHT0uDvoPVXv
```

### **Rate Limits**
- **Limit:** 1,000,000 requests/hour (unlimited for internal use)
- **Response Headers:**
  - `X-RateLimit-Limit`: 1000000
  - `X-RateLimit-Period`: hour
  - `X-RateLimit-Remaining`: (varies)

**Note:** Rate limiting is intentionally set very high for internal services. No need to worry about hitting limits during development or production.

---

## 📚 COMPLETE API REFERENCE

### **INPUT FORMAT (Common to All Endpoints)**

All calculation endpoints accept birth details in this format:

```typescript
interface BirthData {
  user_name: string;          // User's name (1-100 chars)
  birth_date: string;         // Format: "YYYY-MM-DD" (e.g., "1990-05-15")
  birth_time: string;         // Format: "HH:MM:SS" (24-hour, e.g., "14:30:00")
  latitude: number;           // -90 to 90 (e.g., 28.6139 for Delhi)
  longitude: number;          // -180 to 180 (e.g., 77.2090 for Delhi)
  timezone_offset: number;    // Hours from UTC (e.g., 5.5 for IST)
}
```

**Validation Rules:**
- `user_name`: Required, 1-100 characters
- `birth_date`: Required, valid date in YYYY-MM-DD format
- `birth_time`: Required, valid time in HH:MM:SS format (00:00:00 to 23:59:59)
- `latitude`: Required, -90.0 to 90.0
- `longitude`: Required, -180.0 to 180.0
- `timezone_offset`: Required, -12.0 to 14.0

**Special Cases Handled:**
- ✅ Polar regions (extreme latitudes)
- ✅ Midnight births (00:00:00)
- ✅ Date line locations (±180° longitude)
- ✅ Equator births (0° latitude)
- ✅ Retrograde planets
- ✅ Out-of-bounds declinations

---

### **🌟 NATAL CHART ENDPOINTS**

#### **1. Lahiri Natal Chart**
```http
POST /lahiri/natal
```

**Purpose:** Calculate complete birth chart using Lahiri ayanamsa.

**Request Body:**
```json
{
  "user_name": "Rahul Sharma",
  "birth_date": "1990-05-15",
  "birth_time": "14:30:00",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "timezone_offset": 5.5
}
```

**Response (200 OK):**
```json
{
  "user_name": "Rahul Sharma",
  "birth_details": {
    "birth_date": "1990-05-15",
    "birth_time": "14:30:00",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "timezone_offset": 5.5
  },
  "planetary_positions": {
    "Sun": {
      "sign": "Taurus",
      "degrees": "00° 45' 12\"",
      "retrograde": false,
      "house": 10,
      "nakshatra": "Krittika",
      "pada": 2
    },
    "Moon": {
      "sign": "Cancer",
      "degrees": "15° 23' 45\"",
      "retrograde": false,
      "house": 12,
      "nakshatra": "Pushya",
      "pada": 3
    },
    "Mars": {
      "sign": "Aquarius",
      "degrees": "25° 12' 30\"",
      "retrograde": false,
      "house": 7,
      "nakshatra": "Purva Bhadra",
      "pada": 1
    },
    "Mercury": {
      "sign": "Aries",
      "degrees": "10° 05' 18\"",
      "retrograde": true,
      "house": 9,
      "nakshatra": "Ashwini",
      "pada": 2
    },
    "Jupiter": {
      "sign": "Gemini",
      "degrees": "20° 40' 55\"",
      "retrograde": false,
      "house": 11,
      "nakshatra": "Punarvasu",
      "pada": 4
    },
    "Venus": {
      "sign": "Pisces",
      "degrees": "28° 15' 22\"",
      "retrograde": false,
      "house": 8,
      "nakshatra": "Revati",
      "pada": 1
    },
    "Saturn": {
      "sign": "Capricorn",
      "degrees": "22° 33' 44\"",
      "retrograde": false,
      "house": 6,
      "nakshatra": "Shravana",
      "pada": 3
    },
    "Rahu": {
      "sign": "Capricorn",
      "degrees": "08° 12' 15\"",
      "retrograde": true,
      "house": 6,
      "nakshatra": "Uttara Ashadha",
      "pada": 2
    },
    "Ketu": {
      "sign": "Cancer",
      "degrees": "08° 12' 15\"",
      "retrograde": true,
      "house": 12,
      "nakshatra": "Pushya",
      "pada": 1
    }
  },
  "ascendant": {
    "sign": "Leo",
    "degrees": "12° 34' 56\"",
    "nakshatra": "Magha",
    "pada": 2
  },
  "notes": {
    "ayanamsa": "Lahiri",
    "ayanamsa_value": "23.856743",
    "chart_type": "Rasi",
    "house_system": "Whole Sign"
  }
}
```

#### **2. Raman Natal Chart**
```http
POST /raman/natal
```
Same structure as Lahiri, but uses Raman ayanamsa.

#### **3. Transit Chart**
```http
POST /lahiri/transit
```

**Purpose:** Get current planetary positions (for daily predictions).

**Request:** Same birth data + current date/time

**Response:** Same structure as natal chart, but for current moment.

---

### **📊 DIVISIONAL CHARTS ENDPOINTS**

All divisional charts follow similar structure:

#### **D9 - Navamsa (Most Important for Marriage)**
```http
POST /lahiri/navamsa
POST /raman/navamsha_d9
```

**Purpose:** Marriage, spouse analysis, second half of life.

**Response:**
```json
{
  "user_name": "Rahul Sharma",
  "d9_chart": {
    "Ascendant": {
      "sign": "Sagittarius",
      "degrees": "05° 23' 12\"",
      "nakshatra": "Mula",
      "pada": 1,
      "house": 1
    },
    "Sun": {
      "sign": "Aquarius",
      "degrees": "12° 45' 30\"",
      "nakshatra": "Shatabhisha",
      "pada": 3,
      "house": 3,
      "retrograde": false
    },
    // ... other planets
  },
  "metadata": {
    "ayanamsa": "Lahiri",
    "house_system": "Whole Sign",
    "chart_type": "Navamsa D9"
  }
}
```

#### **All Divisional Chart Endpoints:**

**Lahiri System:**
- `POST /lahiri/calculate_d2_hora` - D2 (Wealth)
- `POST /lahiri/calculate_d3` - D3 (Siblings)
- `POST /lahiri/calculate_d4` - D4 (Property)
- `POST /lahiri/calculate_d7_chart` - D7 (Children)
- `POST /lahiri/navamsa` - D9 (Marriage) ⭐ Most Important
- `POST /lahiri/calculate_d10` - D10 (Career)
- `POST /lahiri/calculate_d12` - D12 (Parents)
- `POST /lahiri/calculate_d16` - D16 (Vehicles)
- `POST /lahiri/calculate_d20` - D20 (Spiritual)
- `POST /lahiri/calculate_d24` - D24 (Education)
- `POST /lahiri/calculate_d27` - D27 (Strengths)
- `POST /lahiri/calculate_d30` - D30 (Misfortunes)
- `POST /lahiri/calculate_d40` - D40 (Auspicious events)
- `POST /lahiri/calculate_d45` - D45 (Character)
- `POST /lahiri/calculate_d60` - D60 (Karma)

**Raman System:** Same endpoints with `/raman/` prefix

**Input:** Standard birth data
**Output:** Chart with planetary positions in divisional sign placements

---

### **⏰ DASHA ENDPOINTS (Planetary Periods)**

#### **1. Mahadasha + Antardasha**
```http
POST /lahiri/calculate_antar_dasha
POST /raman/calculate_maha_antar_dashas
POST /kp/calculate_maha_antar_dasha
```

**Purpose:** Get major and sub-periods for life planning.

**Response:**
```json
{
  "user_name": "Rahul Sharma",
  "birth_date": "1990-05-15 14:30:00",
  "nakshatra_at_birth": "Pushya",
  "moon_longitude": 105.3956,
  "mahadashas": [
    {
      "planet": "Saturn",
      "start_date": "1990-05-15",
      "end_date": "2009-05-15",
      "duration_years": 19.0,
      "status": "completed",
      "balance_at_birth_years": 15.2345,
      "antardashas": [
        {
          "planet": "Saturn",
          "start_date": "1990-05-15",
          "end_date": "1993-06-23",
          "duration_years": 3.05,
          "status": "completed"
        },
        {
          "planet": "Mercury",
          "start_date": "1993-06-23",
          "end_date": "1996-04-01",
          "duration_years": 2.77,
          "status": "completed"
        },
        // ... more antardashas
      ]
    },
    {
      "planet": "Mercury",
      "start_date": "2009-05-15",
      "end_date": "2026-05-15",
      "duration_years": 17.0,
      "status": "current",
      "antardashas": [
        // ... antardashas
      ]
    },
    // ... more mahadashas
  ]
}
```

**Status Values:**
- `completed` - Past period
- `current` - Currently running
- `upcoming` - Future period

#### **2. Full Dasha Hierarchy (5 Levels)**
```http
POST /lahiri/calculate_sookshma_prana_dashas
POST /raman/calculate_raman_prana_dasha
POST /kp/calculate_maha_antar_pratyantar_pran_dasha
```

**Purpose:** Ultra-precise timing (down to days/hours).

**Response:** Nested structure with 5 levels:
- Mahadasha → Antardasha → Pratyantardasha → Sookshma → Prana

#### **3. Dasha for Specific Duration**
```http
POST /lahiri/dasha_for_day       - Next 24 hours
POST /lahiri/dasha_for_week      - Next 7 days
POST /lahiri/dasha_for_month     - Next 30 days
POST /lahiri/calculate_vimshottari_dasha_3months
POST /lahiri/calculate_vimshottari_dasha_6months
POST /lahiri/dasha_report_1year
POST /lahiri/dasha_report_2years
POST /lahiri/dasha_report_3years
```

**Use Case:** Show "Current Dasha" or "Upcoming Dashas" in app.

---

### **🏠 SPECIAL LAGNA ENDPOINTS**

#### **Bhava Lagna**
```http
POST /lahiri/calculate_bhava_lagna
POST /raman/calculate_bhava_lagna
```

**Purpose:** House-based predictions.

**Response:**
```json
{
  "bhava_lagna": {
    "sign": "Virgo",
    "degrees": "18° 45' 32\"",
    "nakshatra": "Hasta",
    "nakshatra_lord": "Moon",
    "pada": 2
  },
  "planets": {
    "Sun": {
      "degrees": "00° 45' 12\"",
      "sign": "Taurus",
      "retrograde": "",
      "house": 9,
      "nakshatra": "Krittika",
      "nakshatra_lord": "Sun",
      "pada": 2
    },
    // ... other planets
  }
}
```

#### **All Lagna Endpoints:**
- `POST /lahiri/calculate_bhava_lagna` - Bhava Lagna
- `POST /lahiri/calculate_hora_lagna` - Hora Lagna (wealth timing)
- `POST /lahiri/calculate_sripathi_bhava` - Sripathi houses
- `POST /lahiri/calculate_kp_bhava` - KP system houses
- `POST /lahiri/calculate_equal_bhava_lagna` - Equal house system
- `POST /lahiri/calculate_arudha_lagna` - Material manifestations
- `POST /lahiri/calculate_d1_karkamsha` - Karkamsha (D1)
- `POST /lahiri/calculate_karkamsha_d9` - Karkamsha (D9)
- `POST /lahiri/calculate_moon_chart` - Moon chart
- `POST /lahiri/calculate_sun_chart` - Sun chart

(Same endpoints available with `/raman/` prefix)

---

### **💪 ASHTAKAVARGHA ENDPOINTS**

#### **Bhinnashtakavarga (Individual Strengths)**
```http
POST /lahiri/calculate_binnatakvarga
POST /raman/calculate_bhinnashtakavarga
```

**Response:**
```json
{
  "user_name": "Rahul Sharma",
  "ashtakvarga": {
    "Sun": {
      "Aries": 5,
      "Taurus": 4,
      "Gemini": 3,
      // ... all 12 signs with points (0-8)
    },
    "Moon": {
      "Aries": 6,
      "Taurus": 5,
      // ... all 12 signs
    },
    // ... for all 7 planets
  }
}
```

**Interpretation:**
- 0-2 points: Weak house
- 3-4 points: Average house
- 5-6 points: Good house
- 7-8 points: Excellent house

#### **Sarvashtakavarga (Combined Strengths)**
```http
POST /lahiri/calculate_sarvashtakavarga
POST /raman/calculate_sarvashtakavarga
```

**Response:** Combined points from all planets (max 56 points per house)

#### **Shodasha Varga Summary**
```http
POST /lahiri/shodasha_varga_summary
POST /raman/shodasha_varga_signs
POST /kp/shodasha_varga_signs
```

**Purpose:** Planet strength across all 16 divisional charts.

**Response:**
```json
{
  "ayanamsa": "Lahiri",
  "shodasha_varga_signs": {
    "Sun": {
      "D1": {"sign": "Taurus"},
      "D2": {"sign": "Leo"},
      "D3": {"sign": "Capricorn"},
      "D4": {"sign": "Taurus"},
      // ... all 16 charts
    },
    "Moon": {
      "D1": {"sign": "Cancer"},
      // ... all 16 charts
    },
    // ... all planets
  }
}
```

---

### **✨ YOGA ENDPOINTS**

#### **Gaja Kesari Yoga**
```http
POST /lahiri/comprehensive_gaja_kesari
```

**Response:**
```json
{
  "user_name": "Rahul Sharma",
  "gaja_kesari_yoga": {
    "present": true,
    "strength_percentage": 75.5,
    "jupiter": {
      "sign": "Gemini",
      "house": 11,
      "nakshatra": "Punarvasu"
    },
    "moon": {
      "sign": "Cancer",
      "house": 12,
      "nakshatra": "Pushya"
    },
    "house_relationship": "Moon in 2nd from Jupiter",
    "analysis": {
      "positive_factors": [
        "Jupiter in friend's sign",
        "Moon waxing",
        "Angular house placement"
      ],
      "negative_factors": [
        "Jupiter aspected by malefic"
      ]
    },
    "interpretation": "Strong Gaja Kesari Yoga indicates wisdom, prosperity, and respect in society."
  }
}
```

#### **All Yoga Endpoints:**
- `POST /lahiri/comprehensive_gaja_kesari` - Jupiter-Moon yoga
- `POST /lahiri/comprehensive_guru_mangal` - Jupiter-Mars yoga
- `POST /lahiri/guru-mangal-only` - Simplified version
- `POST /lahiri/budha-aditya-yoga` - Mercury-Sun yoga
- `POST /lahiri/chandra-mangal-yoga` - Moon-Mars yoga

---

### **⚠️ DOSHA ENDPOINTS**

#### **Mangal Dosha (Angarak)**
```http
POST /lahiri/calculate-angarak-dosha
```

**Response:**
```json
{
  "user_name": "Rahul Sharma",
  "angarak_dosha": {
    "present": true,
    "severity": "moderate",
    "mars_position": {
      "sign": "Aquarius",
      "house": 7,
      "retrograde": false
    },
    "dosha_houses": [1, 4, 7, 8, 12],
    "mars_in_dosha_house": true,
    "analysis": {
      "reasons": [
        "Mars in 7th house causes Mangal Dosha",
        "Affects marriage and partnerships"
      ],
      "cancellation_factors": [
        "Partner should also have Mangal Dosha"
      ]
    },
    "remedies": [
      "Worship Lord Hanuman on Tuesdays",
      "Recite Hanuman Chalisa daily",
      "Wear red coral gemstone after consultation",
      "Marry after age 28"
    ]
  }
}
```

#### **Guru Chandal Dosha**
```http
POST /lahiri/guru-chandal-analysis
```

**Response:**
```json
{
  "guru_chandal_dosha": {
    "present": false,
    "jupiter": {
      "sign": "Gemini",
      "longitude": 80.6823
    },
    "rahu": {
      "sign": "Capricorn",
      "longitude": 278.2042
    },
    "conjunction_degree": 197.5219,
    "is_conjunction": false,
    "analysis": "No Guru Chandal Dosha present. Jupiter and Rahu are not in conjunction."
  }
}
```

#### **Sade Sati**
```http
POST /lahiri/calculate-sade-sati
```

**Response:**
```json
{
  "sade_sati": {
    "currently_in_sade_sati": true,
    "current_phase": "second_phase",
    "phase_description": "Saturn transiting over natal Moon - Peak phase",
    "saturn_current_sign": "Cancer",
    "moon_natal_sign": "Cancer",
    "start_date": "2023-01-17",
    "end_date": "2025-03-29",
    "duration_remaining_days": 485,
    "intensity": "high",
    "effects": [
      "Mental stress and anxiety",
      "Health issues related to bones",
      "Delays in important work",
      "Financial constraints"
    ],
    "remedies": [
      "Worship Lord Shani on Saturdays",
      "Light oil lamp under Peepal tree",
      "Donate black sesame seeds",
      "Feed crows regularly"
    ]
  }
}
```

#### **All Dosha Endpoints:**
- `POST /lahiri/calculate-angarak-dosha` - Mangal Dosha
- `POST /lahiri/guru-chandal-analysis` - Jupiter-Rahu conjunction
- `POST /lahiri/calculate-shrapit-dosha` - Saturn-Rahu conjunction
- `POST /lahiri/calculate-sade-sati` - Saturn transit

---

### **🔢 NUMEROLOGY ENDPOINTS**

#### **Chaldean Numerology**
```http
POST /lahiri/chaldean_numerology
```

**Request:**
```json
{
  "user_name": "Rahul Sharma",
  "birth_date": "1990-05-15",
  "birth_time": "14:30:00",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "timezone_offset": 5.5
}
```

**Response:**
```json
{
  "user_name": "Rahul Sharma",
  "chaldean_numerology": {
    "name_analysis": {
      "full_name": "Rahul Sharma",
      "name_number": 8,
      "destiny_number": 8,
      "soul_urge_number": 3,
      "personality_number": 5
    },
    "birth_date_analysis": {
      "life_path_number": 3,
      "birth_day_number": 15,
      "birth_month_number": 5,
      "birth_year_number": 1
    },
    "compatibility": {
      "lucky_numbers": [3, 5, 6, 8],
      "friendly_numbers": [1, 7, 9],
      "neutral_numbers": [2, 4],
      "challenging_numbers": []
    },
    "interpretations": {
      "name_number": "Number 8 represents power, ambition, and material success...",
      "life_path_number": "Number 3 indicates creativity, expression, and social abilities..."
    }
  }
}
```

#### **Lo Shu Grid**
```http
POST /lahiri/lo_shu_grid_numerology
```

**Response:**
```json
{
  "lo_shu_grid": {
    "grid": [
      [0, 0, 0],
      [0, 5, 0],
      [0, 0, 0]
    ],
    "filled_numbers": [5],
    "missing_numbers": [1, 2, 3, 4, 6, 7, 8, 9],
    "planes": {
      "mental_plane": 0,
      "emotional_plane": 1,
      "practical_plane": 0,
      "thought_plane": 0,
      "will_plane": 1,
      "action_plane": 0,
      "horizontal_plane": 0,
      "vertical_plane": 1
    },
    "analysis": {
      "strong_planes": ["Emotional", "Will"],
      "weak_planes": ["Mental", "Practical", "Thought", "Action"],
      "suggestions": [
        "Develop mental abilities through study",
        "Focus on practical implementation of ideas"
      ]
    }
  }
}
```

---

### **🎯 KP SYSTEM ENDPOINTS**

#### **KP Planets & Cusps**
```http
POST /kp/calculate_kp_planets_cusps
```

**Purpose:** KP system chart with Placidus houses and sub-lords.

**Response:**
```json
{
  "user_name": "Rahul Sharma",
  "ascendant": {
    "longitude": "12° 34' 56\"",
    "sign": "Leo"
  },
  "house_cusps": {
    "1": {
      "longitude": "12° 34' 56\"",
      "sign": "Leo",
      "nakshatra": "Magha",
      "star_lord": "Ketu",
      "sub_lord": "Venus"
    },
    // ... all 12 cusps
  },
  "planets": {
    "Sun": {
      "longitude": "00° 45' 12\"",
      "sign": "Taurus",
      "nakshatra": "Krittika",
      "star_lord": "Sun",
      "sub_lord": "Mercury",
      "house": 10
    },
    // ... all planets
  },
  "significators": {
    "house_1": ["Mars", "Sun", "Ketu"],
    "house_2": ["Venus", "Jupiter"],
    // ... all 12 houses with significator planets
  }
}
```

#### **KP Ruling Planets**
```http
POST /kp/calculate_ruling_planets
```

**Purpose:** Current ruling planets for timing.

**Response:**
```json
{
  "ruling_planets": ["Sun", "Moon", "Mars", "Mercury"],
  "details": {
    "day_lord": "Tuesday",
    "lagna_lord": "Sun",
    "lagna_nakshatra_lord": "Ketu",
    "lagna_sub_lord": "Venus",
    "moon_rashi_lord": "Moon",
    "moon_nakshatra_lord": "Saturn",
    "moon_sub_lord": "Mercury",
    "fortuna": 245.6789,
    "balance_of_dasha": {
      "dasha_lord": "Saturn",
      "balance_years": 12.3456
    }
  }
}
```

#### **KP Horary (Prashna)**
```http
POST /kp/kp_horary
```

**Purpose:** Answer specific questions using KP horary.

**Request:**
```json
{
  "horary_number": 108,
  "date": "2025-10-30",
  "time": "14:30:00",
  "tz_offset": 5.5,
  "latitude": 28.6139,
  "longitude": 77.2090,
  "question": "Will I get the new job?",
  "main_house": 10
}
```

**Response:**
```json
{
  "question": "Will I get the new job?",
  "final_judgment": {
    "yes_no": "YES",
    "confidence": "HIGH",
    "rationale": "Sub-lord chain verdict: Favorable. Event window: 2025-12-15 to 2026-01-20.",
    "timing_estimate": {
      "dasha_level": "Antardasha",
      "ruling_planet": "Mercury",
      "start_date": "2025-12-15",
      "end_date": "2026-01-20",
      "event_estimate": "Event likely during Mercury Antardasha"
    }
  },
  "ruling_planets": ["Sun", "Mercury", "Saturn"],
  "significators": {
    "house_10": ["Mercury", "Venus", "Saturn"]
  },
  "chart_radicality": {
    "is_radical": true,
    "reason": "Ascendant in strong position"
  }
}
```

#### **All KP Endpoints:**
- `POST /kp/calculate_kp_planets_cusps` - Planets & houses
- `POST /kp/calculate_ruling_planets` - Ruling planets
- `POST /kp/calculate_bhava_details` - Bhava details
- `POST /kp/calculate_significations` - House significators
- `POST /kp/kp_horary` - Horary/Prashna
- `POST /kp/calculate_maha_antar_dasha` - Dashas
- `POST /kp/shodasha_varga_signs` - Divisional strength

---

### **🎴 SPECIAL CHARTS**

#### **Sudarshan Chakra**
```http
POST /lahiri/calculate_sudarshan_chakra
POST /raman/calculate_sudarshan_chakra
```

**Purpose:** Triple-ring chart for comprehensive analysis.

**Response:**
```json
{
  "user_name": "Rahul Sharma",
  "sudarshan_chakra": {
    "lagna_chart": {
      "center": "Leo",
      "planets_in_signs": {
        "Aries": ["Mercury"],
        "Taurus": ["Sun"],
        "Cancer": ["Moon", "Ketu"],
        // ... all 12 signs
      }
    },
    "moon_chart": {
      "center": "Cancer",
      "planets_in_signs": {
        // ... relative to Moon
      }
    },
    "sun_chart": {
      "center": "Taurus",
      "planets_in_signs": {
        // ... relative to Sun
      }
    }
  }
}
```

---

### **🏥 HEALTH CHECK ENDPOINT**

```http
GET /health
```

**Purpose:** Check API health and status (no authentication required).

**Response:**
```json
{
  "status": "healthy",
  "version": "1.3.0",
  "timestamp": "2025-10-30T12:48:59.736387",
  "components": {
    "authentication": {
      "status": "healthy",
      "enabled": true,
      "keys_configured": 4
    },
    "circuit_breakers": {
      "status": "healthy",
      "open_breakers": 0
    },
    "redis_cache": {
      "status": "degraded",
      "message": "Cache unavailable, running without cache"
    },
    "swiss_ephemeris": {
      "status": "healthy",
      "message": "Ephemeris calculations working"
    },
    "system": {
      "status": "healthy",
      "cpu_percent": 0.0,
      "disk_percent": 80.0,
      "memory_percent": 60.2
    }
  },
  "summary": {
    "healthy_components": 4,
    "total_components": 5,
    "overall_healthy": true
  }
}
```

**Use Case:**
- App startup health check
- Network connectivity test
- Display "API Status" in settings

---

## 📱 REACT NATIVE INTEGRATION

### **Setup**

#### **1. Install Dependencies**
```bash
npm install axios
npm install @react-native-async-storage/async-storage
npm install react-native-dotenv
```

#### **2. Environment Configuration**
Create `.env` file:
```bash
ASTRO_ENGINE_URL=https://astroengine.astrocorp.in
ASTRO_ENGINE_API_KEY=astro_corp_backend_F5XpEFrnQI-NZHlRWZVmcHT0uDvoPVXv
```

Add to `.gitignore`:
```
.env
.env.local
.env.*.local
```

#### **3. Create API Service**
Create `src/services/AstroEngineAPI.ts`:

```typescript
import axios, { AxiosInstance, AxiosError } from 'axios';
import Config from 'react-native-config';

/**
 * Astro Engine API Service
 *
 * Handles all communication with Astro Engine backend.
 * Includes authentication, error handling, and retry logic.
 */
class AstroEngineAPI {
  private axiosInstance: AxiosInstance;
  private baseURL: string;
  private apiKey: string;

  constructor() {
    this.baseURL = Config.ASTRO_ENGINE_URL || 'https://astroengine.astrocorp.in';
    this.apiKey = Config.ASTRO_ENGINE_API_KEY || '';

    if (!this.apiKey) {
      console.error('⚠️ ASTRO_ENGINE_API_KEY not found in environment variables!');
    }

    // Create axios instance with default config
    this.axiosInstance = axios.create({
      baseURL: this.baseURL,
      timeout: 30000, // 30 seconds
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.apiKey,
      },
    });

    // Add request interceptor
    this.axiosInstance.interceptors.request.use(
      (config) => {
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('❌ Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Add response interceptor
    this.axiosInstance.interceptors.response.use(
      (response) => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error: AxiosError) => {
        console.error('❌ Response Error:', this.formatError(error));
        return Promise.reject(this.formatError(error));
      }
    );
  }

  /**
   * Format error for consistent error handling
   */
  private formatError(error: AxiosError): AstroEngineError {
    if (error.response) {
      // Server responded with error status
      return {
        type: 'API_ERROR',
        message: (error.response.data as any)?.error || 'API request failed',
        statusCode: error.response.status,
        details: error.response.data,
      };
    } else if (error.request) {
      // Request made but no response
      return {
        type: 'NETWORK_ERROR',
        message: 'No response from server. Please check your internet connection.',
        statusCode: 0,
      };
    } else {
      // Something else happened
      return {
        type: 'UNKNOWN_ERROR',
        message: error.message || 'An unknown error occurred',
        statusCode: 0,
      };
    }
  }

  /**
   * Check API health
   */
  async checkHealth(): Promise<HealthResponse> {
    const response = await axios.get(`${this.baseURL}/health`);
    return response.data;
  }

  /**
   * Calculate Lahiri Natal Chart
   */
  async calculateLahiriNatal(birthData: BirthData): Promise<NatalChartResponse> {
    const response = await this.axiosInstance.post('/lahiri/natal', birthData);
    return response.data;
  }

  /**
   * Calculate Raman Natal Chart
   */
  async calculateRamanNatal(birthData: BirthData): Promise<NatalChartResponse> {
    const response = await this.axiosInstance.post('/raman/natal', birthData);
    return response.data;
  }

  /**
   * Calculate Navamsa (D9) Chart - Marriage
   */
  async calculateNavamsa(birthData: BirthData, system: 'lahiri' | 'raman' = 'lahiri'): Promise<DivisionalChartResponse> {
    const endpoint = system === 'lahiri' ? '/lahiri/navamsa' : '/raman/navamsha_d9';
    const response = await this.axiosInstance.post(endpoint, birthData);
    return response.data;
  }

  /**
   * Calculate any Divisional Chart
   */
  async calculateDivisionalChart(
    birthData: BirthData,
    chartType: DivisionalChartType,
    system: 'lahiri' | 'raman' = 'lahiri'
  ): Promise<DivisionalChartResponse> {
    const endpoint = `/${system}/${chartType}`;
    const response = await this.axiosInstance.post(endpoint, birthData);
    return response.data;
  }

  /**
   * Calculate Vimshottari Dasha (Mahadasha + Antardasha)
   */
  async calculateDasha(birthData: BirthData, system: 'lahiri' | 'raman' | 'kp' = 'lahiri'): Promise<DashaResponse> {
    const endpoints = {
      lahiri: '/lahiri/calculate_antar_dasha',
      raman: '/raman/calculate_maha_antar_dashas',
      kp: '/kp/calculate_maha_antar_dasha',
    };
    const response = await this.axiosInstance.post(endpoints[system], birthData);
    return response.data;
  }

  /**
   * Calculate current dasha for specific duration
   */
  async calculateCurrentDasha(
    birthData: BirthData,
    duration: 'day' | 'week' | 'month' = 'month'
  ): Promise<DashaResponse> {
    const endpoint = `/lahiri/dasha_for_${duration}`;
    const response = await this.axiosInstance.post(endpoint, birthData);
    return response.data;
  }

  /**
   * Check Gaja Kesari Yoga
   */
  async checkGajaKesariYoga(birthData: BirthData): Promise<YogaResponse> {
    const response = await this.axiosInstance.post('/lahiri/comprehensive_gaja_kesari', birthData);
    return response.data;
  }

  /**
   * Check Mangal Dosha
   */
  async checkMangalDosha(birthData: BirthData): Promise<DoshaResponse> {
    const response = await this.axiosInstance.post('/lahiri/calculate-angarak-dosha', birthData);
    return response.data;
  }

  /**
   * Check Sade Sati
   */
  async checkSadeSati(birthData: BirthData): Promise<SadeSatiResponse> {
    const response = await this.axiosInstance.post('/lahiri/calculate-sade-sati', birthData);
    return response.data;
  }

  /**
   * Calculate Ashtakavargha (strength analysis)
   */
  async calculateAshtakavargha(birthData: BirthData): Promise<AshtakavarghaResponse> {
    const response = await this.axiosInstance.post('/lahiri/calculate_binnatakvarga', birthData);
    return response.data;
  }

  /**
   * Calculate Chaldean Numerology
   */
  async calculateNumerology(birthData: BirthData): Promise<NumerologyResponse> {
    const response = await this.axiosInstance.post('/lahiri/chaldean_numerology', birthData);
    return response.data;
  }

  /**
   * Calculate KP Planets and Cusps
   */
  async calculateKPChart(birthData: BirthData): Promise<KPChartResponse> {
    const response = await this.axiosInstance.post('/kp/calculate_kp_planets_cusps', birthData);
    return response.data;
  }

  /**
   * Calculate KP Ruling Planets
   */
  async calculateRulingPlanets(birthData: BirthData): Promise<RulingPlanetsResponse> {
    const response = await this.axiosInstance.post('/kp/calculate_ruling_planets', birthData);
    return response.data;
  }

  /**
   * KP Horary (Prashna) - Answer specific questions
   */
  async askHoraryQuestion(question: HoraryQuestion): Promise<HoraryResponse> {
    const response = await this.axiosInstance.post('/kp/kp_horary', question);
    return response.data;
  }

  /**
   * Generic POST request for any endpoint
   */
  async post<T>(endpoint: string, data: any): Promise<T> {
    const response = await this.axiosInstance.post(endpoint, data);
    return response.data;
  }
}

// Export singleton instance
export default new AstroEngineAPI();
```

---

## 🎯 TYPESCRIPT INTERFACES

Create `src/types/AstroEngine.ts`:

```typescript
/**
 * Birth Data Input
 */
export interface BirthData {
  user_name: string;
  birth_date: string;        // "YYYY-MM-DD"
  birth_time: string;        // "HH:MM:SS"
  latitude: number;          // -90 to 90
  longitude: number;         // -180 to 180
  timezone_offset: number;   // -12 to 14
}

/**
 * Planetary Position
 */
export interface PlanetPosition {
  sign: string;
  degrees: string;           // "DD° MM' SS\""
  retrograde: boolean;
  house: number;
  nakshatra: string;
  pada: number;
}

/**
 * Ascendant Details
 */
export interface Ascendant {
  sign: string;
  degrees: string;
  nakshatra: string;
  pada: number;
}

/**
 * Natal Chart Response
 */
export interface NatalChartResponse {
  user_name: string;
  birth_details: {
    birth_date: string;
    birth_time: string;
    latitude: number;
    longitude: number;
    timezone_offset: number;
  };
  planetary_positions: {
    Sun: PlanetPosition;
    Moon: PlanetPosition;
    Mars: PlanetPosition;
    Mercury: PlanetPosition;
    Jupiter: PlanetPosition;
    Venus: PlanetPosition;
    Saturn: PlanetPosition;
    Rahu: PlanetPosition;
    Ketu: PlanetPosition;
  };
  ascendant: Ascendant;
  notes: {
    ayanamsa: string;
    ayanamsa_value: string;
    chart_type: string;
    house_system: string;
  };
}

/**
 * Divisional Chart Response
 */
export interface DivisionalChartResponse {
  user_name: string;
  d9_chart?: DivisionalPlanetPositions;  // For D9
  d2_hora_chart?: DivisionalPlanetPositions;  // For D2
  // ... other chart types
  metadata?: {
    ayanamsa: string;
    house_system: string;
    chart_type: string;
  };
}

export interface DivisionalPlanetPositions {
  Ascendant: DivisionalPosition;
  Sun: DivisionalPosition;
  Moon: DivisionalPosition;
  Mars: DivisionalPosition;
  Mercury: DivisionalPosition;
  Jupiter: DivisionalPosition;
  Venus: DivisionalPosition;
  Saturn: DivisionalPosition;
  Rahu: DivisionalPosition;
  Ketu: DivisionalPosition;
}

export interface DivisionalPosition {
  sign: string;
  degrees: string;
  nakshatra: string;
  pada: number;
  house: number;
  retrograde: boolean;
}

/**
 * Dasha Response
 */
export interface DashaResponse {
  user_name: string;
  birth_date?: string;
  nakshatra_at_birth: string;
  moon_longitude: number;
  mahadashas: Mahadasha[];
}

export interface Mahadasha {
  planet: string;
  start_date: string;
  end_date: string;
  duration_years: number;
  status: 'completed' | 'current' | 'upcoming';
  balance_at_birth_years?: number;
  antardashas: Antardasha[];
}

export interface Antardasha {
  planet: string;
  start_date: string;
  end_date: string;
  duration_years: number;
  status: 'completed' | 'current' | 'upcoming';
}

/**
 * Yoga Response
 */
export interface YogaResponse {
  user_name: string;
  gaja_kesari_yoga?: {
    present: boolean;
    strength_percentage: number;
    jupiter: YogaPlanet;
    moon: YogaPlanet;
    house_relationship: string;
    analysis: {
      positive_factors: string[];
      negative_factors: string[];
    };
    interpretation: string;
  };
  // ... other yogas
}

export interface YogaPlanet {
  sign: string;
  house: number;
  nakshatra: string;
}

/**
 * Dosha Response
 */
export interface DoshaResponse {
  user_name: string;
  angarak_dosha?: {
    present: boolean;
    severity: 'mild' | 'moderate' | 'severe';
    mars_position: {
      sign: string;
      house: number;
      retrograde: boolean;
    };
    dosha_houses: number[];
    mars_in_dosha_house: boolean;
    analysis: {
      reasons: string[];
      cancellation_factors: string[];
    };
    remedies: string[];
  };
}

/**
 * Sade Sati Response
 */
export interface SadeSatiResponse {
  sade_sati: {
    currently_in_sade_sati: boolean;
    current_phase?: 'first_phase' | 'second_phase' | 'third_phase';
    phase_description?: string;
    saturn_current_sign: string;
    moon_natal_sign: string;
    start_date?: string;
    end_date?: string;
    duration_remaining_days?: number;
    intensity?: 'low' | 'moderate' | 'high';
    effects?: string[];
    remedies?: string[];
  };
}

/**
 * Ashtakavargha Response
 */
export interface AshtakavarghaResponse {
  user_name: string;
  birth_details: BirthData;
  planetary_positions: Record<string, PlanetPosition>;
  ascendant: Ascendant;
  ashtakvarga: {
    Sun: Record<string, number>;
    Moon: Record<string, number>;
    Mars: Record<string, number>;
    Mercury: Record<string, number>;
    Jupiter: Record<string, number>;
    Venus: Record<string, number;
    Saturn: Record<string, number>;
  };
  notes: {
    ayanamsa: string;
    ayanamsa_value: string;
    chart_type: string;
    house_system: string;
  };
}

/**
 * Numerology Response
 */
export interface NumerologyResponse {
  user_name: string;
  chaldean_numerology: {
    name_analysis: {
      full_name: string;
      name_number: number;
      destiny_number: number;
      soul_urge_number: number;
      personality_number: number;
    };
    birth_date_analysis: {
      life_path_number: number;
      birth_day_number: number;
      birth_month_number: number;
      birth_year_number: number;
    };
    compatibility: {
      lucky_numbers: number[];
      friendly_numbers: number[];
      neutral_numbers: number[];
      challenging_numbers: number[];
    };
    interpretations: {
      name_number: string;
      life_path_number: string;
    };
  };
}

/**
 * KP Chart Response
 */
export interface KPChartResponse {
  user_name: string;
  ascendant: {
    longitude: string;
    sign: string;
  };
  house_cusps: Record<string, KPCusp>;
  planets: Record<string, KPPlanet>;
  significators: Record<string, string[]>;
  metadata: {
    ayanamsa: string;
    house_system: string;
    calculation_time: string;
  };
}

export interface KPCusp {
  longitude: string;
  sign: string;
  nakshatra: string;
  star_lord: string;
  sub_lord: string;
}

export interface KPPlanet {
  longitude: string;
  sign: string;
  nakshatra: string;
  star_lord: string;
  sub_lord: string;
  house: number;
}

/**
 * Ruling Planets Response
 */
export interface RulingPlanetsResponse {
  ruling_planets: string[];
  details: {
    day_lord: string;
    lagna_lord: string;
    lagna_nakshatra_lord: string;
    lagna_sub_lord: string;
    moon_rashi_lord: string;
    moon_nakshatra_lord: string;
    moon_sub_lord: string;
    fortuna: number;
    balance_of_dasha: {
      dasha_lord: string;
      balance_years: number;
    };
  };
}

/**
 * Horary Question Input
 */
export interface HoraryQuestion {
  horary_number: number;      // 1-249
  date: string;               // "YYYY-MM-DD"
  time: string;               // "HH:MM:SS"
  tz_offset: number;
  latitude: number;
  longitude: number;
  question: string;
  main_house?: number;        // 1-12 (auto-detected if not provided)
}

/**
 * Horary Response
 */
export interface HoraryResponse {
  question: string;
  horary_number: number;
  final_judgment: {
    yes_no: 'YES' | 'NO' | 'MAYBE';
    confidence: 'LOW' | 'MEDIUM' | 'HIGH';
    rationale: string;
    timing_estimate?: {
      dasha_level: string;
      ruling_planet: string;
      start_date: string;
      end_date: string;
      event_estimate: string;
    };
  };
  ruling_planets: string[];
  significators: Record<string, string[]>;
  chart_radicality: {
    is_radical: boolean;
    reason: string;
  };
}

/**
 * Health Check Response
 */
export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  timestamp: string;
  components: {
    authentication: {
      status: string;
      enabled: boolean;
      keys_configured: number;
    };
    circuit_breakers: {
      status: string;
      open_breakers: number;
    };
    redis_cache: {
      status: string;
      message: string;
    };
    swiss_ephemeris: {
      status: string;
      message: string;
    };
    system: {
      status: string;
      cpu_percent: number;
      disk_percent: number;
      memory_percent: number;
    };
  };
  summary: {
    healthy_components: number;
    total_components: number;
    overall_healthy: boolean;
  };
}

/**
 * Error Response
 */
export interface AstroEngineError {
  type: 'API_ERROR' | 'NETWORK_ERROR' | 'VALIDATION_ERROR' | 'UNKNOWN_ERROR';
  message: string;
  statusCode: number;
  details?: any;
}

/**
 * Divisional Chart Types
 */
export type DivisionalChartType =
  | 'calculate_d2_hora'      // D2 - Wealth
  | 'calculate_d3'           // D3 - Siblings
  | 'calculate_d4'           // D4 - Property
  | 'calculate_d7_chart'     // D7 - Children
  | 'navamsa'                // D9 - Marriage
  | 'calculate_d10'          // D10 - Career
  | 'calculate_d12'          // D12 - Parents
  | 'calculate_d16'          // D16 - Vehicles
  | 'calculate_d20'          // D20 - Spiritual
  | 'calculate_d24'          // D24 - Education
  | 'calculate_d27'          // D27 - Strengths
  | 'calculate_d30'          // D30 - Misfortunes
  | 'calculate_d40'          // D40 - Auspicious
  | 'calculate_d45'          // D45 - Character
  | 'calculate_d60';         // D60 - Karma
```

---

## ⚠️ ERROR HANDLING

### **Error Types**

Astro Engine provides standardized error responses:

```typescript
interface APIErrorResponse {
  error: string;              // Human-readable error message
  error_code?: string;        // Machine-readable error code
  error_type?: string;        // Error category
  details?: any;              // Additional error details
  request_id?: string;        // For debugging/support
}
```

### **HTTP Status Codes**

| Code | Meaning | Cause | Solution |
|------|---------|-------|----------|
| 200 | Success | Request completed successfully | None |
| 400 | Bad Request | Invalid input data | Check birth data format |
| 401 | Unauthorized | Missing or invalid API key | Verify API key in headers |
| 404 | Not Found | Invalid endpoint | Check endpoint URL |
| 429 | Too Many Requests | Rate limit exceeded | Wait and retry |
| 500 | Server Error | Internal calculation error | Retry or contact support |
| 503 | Service Unavailable | Server down/maintenance | Retry after delay |

### **Common Validation Errors**

```json
{
  "error": "Invalid input: birth_date must be in YYYY-MM-DD format",
  "error_code": "VALIDATION_ERROR_1001"
}
```

**Validation Error Codes:**
- `1001` - Invalid date format
- `1002` - Invalid time format
- `1003` - Invalid latitude (must be -90 to 90)
- `1004` - Invalid longitude (must be -180 to 180)
- `1005` - Invalid timezone offset
- `1006` - Missing required field

### **Error Handling Best Practices**

```typescript
import AstroEngineAPI from './services/AstroEngineAPI';
import { AstroEngineError } from './types/AstroEngine';

async function calculateChart(birthData: BirthData) {
  try {
    const chart = await AstroEngineAPI.calculateLahiriNatal(birthData);
    return { success: true, data: chart };
  } catch (error) {
    const astroError = error as AstroEngineError;

    // Handle different error types
    switch (astroError.type) {
      case 'NETWORK_ERROR':
        // Show "No internet connection" message
        return {
          success: false,
          message: 'Please check your internet connection and try again.',
        };

      case 'API_ERROR':
        if (astroError.statusCode === 401) {
          // API key issue
          return {
            success: false,
            message: 'Authentication failed. Please contact support.',
          };
        } else if (astroError.statusCode === 400) {
          // Validation error
          return {
            success: false,
            message: astroError.message,
          };
        }
        break;

      case 'UNKNOWN_ERROR':
      default:
        // Generic error
        return {
          success: false,
          message: 'An unexpected error occurred. Please try again.',
        };
    }
  }
}
```

### **Retry Logic**

For network errors, implement exponential backoff:

```typescript
async function calculateWithRetry(
  birthData: BirthData,
  maxRetries: number = 3
): Promise<NatalChartResponse> {
  let lastError: AstroEngineError;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await AstroEngineAPI.calculateLahiriNatal(birthData);
    } catch (error) {
      lastError = error as AstroEngineError;

      // Only retry on network errors
      if (lastError.type !== 'NETWORK_ERROR') {
        throw lastError;
      }

      // Exponential backoff: 1s, 2s, 4s
      const delay = Math.pow(2, attempt) * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));

      console.log(`Retry attempt ${attempt + 1}/${maxRetries}...`);
    }
  }

  throw lastError!;
}
```

---

## ⚡ PERFORMANCE OPTIMIZATION

### **1. Response Caching**

Cache responses locally to avoid repeated API calls:

```typescript
import AsyncStorage from '@react-native-async-storage/async-storage';

class CachedAstroEngineAPI {
  private cacheKeyPrefix = 'astro_cache_';
  private cacheDuration = 24 * 60 * 60 * 1000; // 24 hours

  /**
   * Generate cache key from birth data
   */
  private generateCacheKey(birthData: BirthData, endpoint: string): string {
    const key = `${birthData.birth_date}_${birthData.birth_time}_${birthData.latitude}_${birthData.longitude}_${endpoint}`;
    return `${this.cacheKeyPrefix}${key}`;
  }

  /**
   * Get cached response
   */
  private async getCached<T>(cacheKey: string): Promise<T | null> {
    try {
      const cached = await AsyncStorage.getItem(cacheKey);
      if (!cached) return null;

      const { data, timestamp } = JSON.parse(cached);
      const age = Date.now() - timestamp;

      // Check if cache is still valid
      if (age < this.cacheDuration) {
        console.log('✅ Using cached response');
        return data as T;
      }

      // Cache expired, remove it
      await AsyncStorage.removeItem(cacheKey);
      return null;
    } catch (error) {
      console.error('Cache read error:', error);
      return null;
    }
  }

  /**
   * Save response to cache
   */
  private async setCached(cacheKey: string, data: any): Promise<void> {
    try {
      const cacheData = {
        data,
        timestamp: Date.now(),
      };
      await AsyncStorage.setItem(cacheKey, JSON.stringify(cacheData));
      console.log('💾 Response cached');
    } catch (error) {
      console.error('Cache write error:', error);
    }
  }

  /**
   * Calculate natal chart with caching
   */
  async calculateLahiriNatalCached(birthData: BirthData): Promise<NatalChartResponse> {
    const cacheKey = this.generateCacheKey(birthData, 'lahiri_natal');

    // Try cache first
    const cached = await this.getCached<NatalChartResponse>(cacheKey);
    if (cached) return cached;

    // Cache miss, fetch from API
    const response = await AstroEngineAPI.calculateLahiriNatal(birthData);

    // Save to cache
    await this.setCached(cacheKey, response);

    return response;
  }
}

export default new CachedAstroEngineAPI();
```

### **2. Request Batching**

Batch multiple calculations to reduce network overhead:

```typescript
interface BatchRequest {
  endpoint: string;
  data: BirthData;
  id: string;
}

class BatchedAstroEngineAPI {
  private queue: BatchRequest[] = [];
  private batchDelay = 500; // 500ms
  private batchTimeout: NodeJS.Timeout | null = null;

  /**
   * Add request to batch queue
   */
  async queueRequest(endpoint: string, data: BirthData): Promise<any> {
    return new Promise((resolve, reject) => {
      const id = `${Date.now()}_${Math.random()}`;

      this.queue.push({
        endpoint,
        data,
        id,
      });

      // Store resolve/reject for later
      (this.queue[this.queue.length - 1] as any).resolve = resolve;
      (this.queue[this.queue.length - 1] as any).reject = reject;

      // Schedule batch execution
      if (!this.batchTimeout) {
        this.batchTimeout = setTimeout(() => this.executeBatch(), this.batchDelay);
      }
    });
  }

  /**
   * Execute all queued requests
   */
  private async executeBatch(): Promise<void> {
    if (this.queue.length === 0) return;

    const batch = [...this.queue];
    this.queue = [];
    this.batchTimeout = null;

    console.log(`🚀 Executing batch of ${batch.length} requests`);

    // Execute all requests in parallel
    const results = await Promise.allSettled(
      batch.map(req => AstroEngineAPI.post(req.endpoint, req.data))
    );

    // Resolve/reject each promise
    results.forEach((result, index) => {
      const req = batch[index] as any;
      if (result.status === 'fulfilled') {
        req.resolve(result.value);
      } else {
        req.reject(result.reason);
      }
    });
  }
}
```

### **3. Progressive Loading**

Load data progressively to improve perceived performance:

```typescript
/**
 * Load birth chart data in stages
 */
async function loadBirthChartProgressive(birthData: BirthData) {
  // Stage 1: Load basic natal chart (fastest)
  const natalPromise = AstroEngineAPI.calculateLahiriNatal(birthData);

  // Stage 2: Load important charts (D9 for marriage)
  const d9Promise = AstroEngineAPI.calculateNavamsa(birthData);

  // Stage 3: Load dashas (for timing)
  const dashaPromise = AstroEngineAPI.calculateDasha(birthData);

  // Stage 4: Load yogas and doshas (for analysis)
  const yogaPromise = AstroEngineAPI.checkGajaKesariYoga(birthData);
  const doshaPromise = AstroEngineAPI.checkMangalDosha(birthData);

  // Return results as they complete
  return {
    natal: await natalPromise,          // Show first (basic chart)
    d9: await d9Promise,                // Show second (marriage)
    dasha: await dashaPromise,          // Show third (timing)
    yoga: await yogaPromise,            // Show fourth (analysis)
    dosha: await doshaPromise,          // Show fifth (warnings)
  };
}
```

### **4. Compression**

Astro Engine automatically compresses responses (gzip/brotli). Ensure your axios instance accepts compressed responses:

```typescript
// Already configured in our AstroEngineAPI class
headers: {
  'Accept-Encoding': 'gzip, deflate, br',
}
```

**Typical compression savings:** 60-80% reduction in response size

---

## ✅ BEST PRACTICES

### **1. Input Validation**

Always validate user input before sending to API:

```typescript
function validateBirthData(birthData: BirthData): { valid: boolean; error?: string } {
  // Check user name
  if (!birthData.user_name || birthData.user_name.length < 1 || birthData.user_name.length > 100) {
    return { valid: false, error: 'Name must be 1-100 characters' };
  }

  // Check date format (YYYY-MM-DD)
  const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
  if (!dateRegex.test(birthData.birth_date)) {
    return { valid: false, error: 'Date must be in YYYY-MM-DD format' };
  }

  // Check time format (HH:MM:SS)
  const timeRegex = /^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$/;
  if (!timeRegex.test(birthData.birth_time)) {
    return { valid: false, error: 'Time must be in HH:MM:SS format (24-hour)' };
  }

  // Check latitude
  if (birthData.latitude < -90 || birthData.latitude > 90) {
    return { valid: false, error: 'Latitude must be between -90 and 90' };
  }

  // Check longitude
  if (birthData.longitude < -180 || birthData.longitude > 180) {
    return { valid: false, error: 'Longitude must be between -180 and 180' };
  }

  // Check timezone offset
  if (birthData.timezone_offset < -12 || birthData.timezone_offset > 14) {
    return { valid: false, error: 'Timezone offset must be between -12 and 14' };
  }

  return { valid: true };
}
```

### **2. Date/Time Handling**

Use libraries for proper date/time handling:

```bash
npm install moment-timezone
```

```typescript
import moment from 'moment-timezone';

/**
 * Convert user's local time to API format
 */
function formatBirthDateTime(
  date: Date,
  timezone: string = 'Asia/Kolkata'
): { birth_date: string; birth_time: string; timezone_offset: number } {
  const m = moment(date).tz(timezone);

  return {
    birth_date: m.format('YYYY-MM-DD'),
    birth_time: m.format('HH:mm:ss'),
    timezone_offset: m.utcOffset() / 60,  // Convert minutes to hours
  };
}
```

### **3. Loading States**

Always show loading indicators:

```typescript
const [loading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
const [chart, setChart] = useState<NatalChartResponse | null>(null);

async function loadChart(birthData: BirthData) {
  setLoading(true);
  setError(null);

  try {
    const result = await AstroEngineAPI.calculateLahiriNatal(birthData);
    setChart(result);
  } catch (err) {
    const astroError = err as AstroEngineError;
    setError(astroError.message);
  } finally {
    setLoading(false);
  }
}
```

### **4. Offline Support**

Cache previous calculations for offline access:

```typescript
async function loadChartWithOfflineSupport(birthData: BirthData) {
  try {
    // Try online first
    const chart = await CachedAstroEngineAPI.calculateLahiriNatalCached(birthData);
    return { online: true, data: chart };
  } catch (error) {
    const astroError = error as AstroEngineError;

    if (astroError.type === 'NETWORK_ERROR') {
      // Try to load from cache
      const cached = await loadFromCache(birthData);
      if (cached) {
        return { online: false, data: cached };
      }
    }

    throw error;
  }
}
```

### **5. Security Best Practices**

```typescript
// ❌ NEVER DO THIS
const API_KEY = "astro_corp_backend_F5XpEFrnQI...";  // Hardcoded!

// ✅ ALWAYS DO THIS
import Config from 'react-native-config';
const API_KEY = Config.ASTRO_ENGINE_API_KEY;  // From .env

// ❌ NEVER log API keys
console.log('API Key:', apiKey);

// ✅ Log safely
console.log('API Key:', apiKey ? '***configured***' : 'missing');
```

---

## 💻 COMPLETE CODE EXAMPLES

### **Example 1: Birth Chart Screen**

```typescript
// screens/BirthChartScreen.tsx
import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, ActivityIndicator, StyleSheet } from 'react-native';
import AstroEngineAPI from '../services/AstroEngineAPI';
import { BirthData, NatalChartResponse } from '../types/AstroEngine';

interface Props {
  birthData: BirthData;
}

const BirthChartScreen: React.FC<Props> = ({ birthData }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chart, setChart] = useState<NatalChartResponse | null>(null);

  useEffect(() => {
    loadChart();
  }, [birthData]);

  async function loadChart() {
    setLoading(true);
    setError(null);

    try {
      const result = await AstroEngineAPI.calculateLahiriNatal(birthData);
      setChart(result);
    } catch (err: any) {
      setError(err.message || 'Failed to load birth chart');
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#6200EE" />
        <Text style={styles.loadingText}>Calculating your birth chart...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>{error}</Text>
      </View>
    );
  }

  if (!chart) return null;

  return (
    <ScrollView style={styles.container}>
      {/* Ascendant */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Ascendant (Lagna)</Text>
        <Text style={styles.data}>
          {chart.ascendant.sign} - {chart.ascendant.degrees}
        </Text>
        <Text style={styles.subData}>
          {chart.ascendant.nakshatra} (Pada {chart.ascendant.pada})
        </Text>
      </View>

      {/* Planets */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Planetary Positions</Text>
        {Object.entries(chart.planetary_positions).map(([planet, data]) => (
          <View key={planet} style={styles.planetRow}>
            <Text style={styles.planetName}>{planet}</Text>
            <View>
              <Text style={styles.planetData}>
                {data.sign} - {data.degrees}
                {data.retrograde && ' (R)'}
              </Text>
              <Text style={styles.planetSubData}>
                House {data.house} • {data.nakshatra} (Pada {data.pada})
              </Text>
            </View>
          </View>
        ))}
      </View>

      {/* Chart Info */}
      <View style={styles.section}>
        <Text style={styles.infoText}>
          Ayanamsa: {chart.notes.ayanamsa} ({chart.notes.ayanamsa_value})
        </Text>
        <Text style={styles.infoText}>
          House System: {chart.notes.house_system}
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  errorText: {
    fontSize: 16,
    color: '#D32F2F',
    textAlign: 'center',
    paddingHorizontal: 32,
  },
  section: {
    backgroundColor: '#FFF',
    marginVertical: 8,
    marginHorizontal: 16,
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#6200EE',
    marginBottom: 12,
  },
  data: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  subData: {
    fontSize: 14,
    color: '#666',
  },
  planetRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  planetName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    width: 80,
  },
  planetData: {
    fontSize: 14,
    color: '#333',
    marginBottom: 2,
  },
  planetSubData: {
    fontSize: 12,
    color: '#666',
  },
  infoText: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
});

export default BirthChartScreen;
```

### **Example 2: Dasha Timeline**

```typescript
// components/DashaTimeline.tsx
import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import AstroEngineAPI from '../services/AstroEngineAPI';
import { BirthData, DashaResponse, Mahadasha } from '../types/AstroEngine';
import moment from 'moment';

interface Props {
  birthData: BirthData;
}

const DashaTimeline: React.FC<Props> = ({ birthData }) => {
  const [dashas, setDashas] = useState<Mahadasha[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashas();
  }, []);

  async function loadDashas() {
    try {
      const result = await AstroEngineAPI.calculateDasha(birthData, 'lahiri');
      setDashas(result.mahadashas);
    } catch (error) {
      console.error('Failed to load dashas:', error);
    } finally {
      setLoading(false);
    }
  }

  function getDashaColor(status: string): string {
    switch (status) {
      case 'completed': return '#9E9E9E';
      case 'current': return '#4CAF50';
      case 'upcoming': return '#2196F3';
      default: return '#757575';
    }
  }

  function formatDate(dateStr: string): string {
    return moment(dateStr).format('MMM DD, YYYY');
  }

  function renderMahadasha({ item }: { item: Mahadasha }) {
    return (
      <View style={styles.dashaCard}>
        <View style={[styles.statusDot, { backgroundColor: getDashaColor(item.status) }]} />
        <View style={styles.dashaContent}>
          <Text style={styles.dashaTitle}>{item.planet} Mahadasha</Text>
          <Text style={styles.dashaDate}>
            {formatDate(item.start_date)} - {formatDate(item.end_date)}
          </Text>
          <Text style={styles.dashaDuration}>
            Duration: {item.duration_years} years • Status: {item.status.toUpperCase()}
          </Text>

          {/* Show antardashas for current mahadasha */}
          {item.status === 'current' && item.antardashas && (
            <View style={styles.antardashaContainer}>
              <Text style={styles.antardashaTitle}>Current Antardashas:</Text>
              {item.antardashas.slice(0, 3).map((antar, index) => (
                <Text key={index} style={styles.antardashaText}>
                  • {antar.planet}: {formatDate(antar.start_date)} - {formatDate(antar.end_date)}
                </Text>
              ))}
            </View>
          )}
        </View>
      </View>
    );
  }

  if (loading) {
    return (
      <View style={styles.center}>
        <Text>Loading dashas...</Text>
      </View>
    );
  }

  return (
    <FlatList
      data={dashas}
      renderItem={renderMahadasha}
      keyExtractor={(item, index) => `${item.planet}_${index}`}
      contentContainerStyle={styles.listContainer}
    />
  );
};

const styles = StyleSheet.create({
  listContainer: {
    padding: 16,
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  dashaCard: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statusDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginTop: 4,
    marginRight: 12,
  },
  dashaContent: {
    flex: 1,
  },
  dashaTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  dashaDate: {
    fontSize: 14,
    color: '#666',
    marginBottom: 2,
  },
  dashaDuration: {
    fontSize: 12,
    color: '#999',
  },
  antardashaContainer: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  antardashaTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6200EE',
    marginBottom: 6,
  },
  antardashaText: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
});

export default DashaTimeline;
```

### **Example 3: Yoga & Dosha Checker**

```typescript
// screens/YogaDoshaScreen.tsx
import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import AstroEngineAPI from '../services/AstroEngineAPI';
import { BirthData } from '../types/AstroEngine';

interface Props {
  birthData: BirthData;
}

const YogaDoshaScreen: React.FC<Props> = ({ birthData }) => {
  const [yogas, setYogas] = useState<any>({});
  const [doshas, setDoshas] = useState<any>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAll();
  }, []);

  async function loadAll() {
    try {
      // Load all yogas and doshas in parallel
      const [gajaKesari, mangalDosha, sadeSati] = await Promise.all([
        AstroEngineAPI.checkGajaKesariYoga(birthData),
        AstroEngineAPI.checkMangalDosha(birthData),
        AstroEngineAPI.checkSadeSati(birthData),
      ]);

      setYogas({ gajaKesari });
      setDoshas({ mangalDosha, sadeSati });
    } catch (error) {
      console.error('Failed to load yogas/doshas:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <View style={styles.center}>
        <Text>Analyzing your chart...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Yogas Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Auspicious Yogas</Text>

        {/* Gaja Kesari Yoga */}
        {yogas.gajaKesari?.gaja_kesari_yoga && (
          <View style={[
            styles.card,
            yogas.gajaKesari.gaja_kesari_yoga.present
              ? styles.cardPositive
              : styles.cardNeutral
          ]}>
            <Text style={styles.cardTitle}>
              Gaja Kesari Yoga {yogas.gajaKesari.gaja_kesari_yoga.present ? '✓' : '✗'}
            </Text>
            {yogas.gajaKesari.gaja_kesari_yoga.present && (
              <>
                <Text style={styles.cardText}>
                  Strength: {yogas.gajaKesari.gaja_kesari_yoga.strength_percentage}%
                </Text>
                <Text style={styles.cardDescription}>
                  {yogas.gajaKesari.gaja_kesari_yoga.interpretation}
                </Text>
              </>
            )}
          </View>
        )}
      </View>

      {/* Doshas Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Doshas</Text>

        {/* Mangal Dosha */}
        {doshas.mangalDosha?.angarak_dosha && (
          <View style={[
            styles.card,
            doshas.mangalDosha.angarak_dosha.present
              ? styles.cardNegative
              : styles.cardPositive
          ]}>
            <Text style={styles.cardTitle}>
              Mangal Dosha {doshas.mangalDosha.angarak_dosha.present ? '⚠' : '✓'}
            </Text>
            {doshas.mangalDosha.angarak_dosha.present && (
              <>
                <Text style={styles.cardText}>
                  Severity: {doshas.mangalDosha.angarak_dosha.severity.toUpperCase()}
                </Text>
                <Text style={styles.cardSubtitle}>Remedies:</Text>
                {doshas.mangalDosha.angarak_dosha.remedies.map((remedy: string, index: number) => (
                  <Text key={index} style={styles.remedyText}>• {remedy}</Text>
                ))}
              </>
            )}
          </View>
        )}

        {/* Sade Sati */}
        {doshas.sadeSati?.sade_sati && (
          <View style={[
            styles.card,
            doshas.sadeSati.sade_sati.currently_in_sade_sati
              ? styles.cardNegative
              : styles.cardPositive
          ]}>
            <Text style={styles.cardTitle}>
              Sade Sati {doshas.sadeSati.sade_sati.currently_in_sade_sati ? '⚠' : '✓'}
            </Text>
            {doshas.sadeSati.sade_sati.currently_in_sade_sati && (
              <>
                <Text style={styles.cardText}>
                  Phase: {doshas.sadeSati.sade_sati.current_phase?.replace('_', ' ').toUpperCase()}
                </Text>
                <Text style={styles.cardText}>
                  {doshas.sadeSati.sade_sati.phase_description}
                </Text>
                <Text style={styles.cardText}>
                  Days Remaining: {doshas.sadeSati.sade_sati.duration_remaining_days}
                </Text>
                <Text style={styles.cardSubtitle}>Remedies:</Text>
                {doshas.sadeSati.sade_sati.remedies?.map((remedy: string, index: number) => (
                  <Text key={index} style={styles.remedyText}>• {remedy}</Text>
                ))}
              </>
            )}
          </View>
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  section: {
    marginVertical: 8,
    marginHorizontal: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  card: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardPositive: {
    borderLeftWidth: 4,
    borderLeftColor: '#4CAF50',
  },
  cardNegative: {
    borderLeftWidth: 4,
    borderLeftColor: '#F44336',
  },
  cardNeutral: {
    borderLeftWidth: 4,
    borderLeftColor: '#9E9E9E',
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  cardText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  cardDescription: {
    fontSize: 14,
    color: '#666',
    fontStyle: 'italic',
    marginTop: 8,
  },
  cardSubtitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6200EE',
    marginTop: 12,
    marginBottom: 4,
  },
  remedyText: {
    fontSize: 13,
    color: '#666',
    marginBottom: 2,
  },
});

export default YogaDoshaScreen;
```

---

## 🧪 TESTING STRATEGY

### **1. Unit Tests**

Test API service methods:

```typescript
// __tests__/AstroEngineAPI.test.ts
import AstroEngineAPI from '../services/AstroEngineAPI';
import { BirthData } from '../types/AstroEngine';

describe('AstroEngineAPI', () => {
  const testBirthData: BirthData = {
    user_name: 'Test User',
    birth_date: '1990-05-15',
    birth_time: '14:30:00',
    latitude: 28.6139,
    longitude: 77.2090,
    timezone_offset: 5.5,
  };

  it('should calculate Lahiri natal chart', async () => {
    const chart = await AstroEngineAPI.calculateLahiriNatal(testBirthData);

    expect(chart).toBeDefined();
    expect(chart.user_name).toBe('Test User');
    expect(chart.planetary_positions).toBeDefined();
    expect(chart.ascendant).toBeDefined();
  });

  it('should handle invalid birth data', async () => {
    const invalidData = { ...testBirthData, latitude: 100 };  // Invalid latitude

    await expect(
      AstroEngineAPI.calculateLahiriNatal(invalidData)
    ).rejects.toThrow();
  });

  it('should handle network errors', async () => {
    // Mock network failure
    jest.spyOn(global, 'fetch').mockRejectedValueOnce(new Error('Network error'));

    await expect(
      AstroEngineAPI.calculateLahiriNatal(testBirthData)
    ).rejects.toThrow('Network error');
  });
});
```

### **2. Integration Tests**

Test complete flows:

```typescript
// __tests__/ChartFlow.integration.test.ts
import { render, waitFor, fireEvent } from '@testing-library/react-native';
import BirthChartScreen from '../screens/BirthChartScreen';

describe('Birth Chart Flow', () => {
  it('should load and display birth chart', async () => {
    const { getByText, getByTestID } = render(
      <BirthChartScreen birthData={testBirthData} />
    );

    // Should show loading initially
    expect(getByText('Calculating your birth chart...')).toBeDefined();

    // Wait for chart to load
    await waitFor(() => {
      expect(getByText('Ascendant (Lagna)')).toBeDefined();
    });

    // Check if planets are displayed
    expect(getByText('Sun')).toBeDefined();
    expect(getByText('Moon')).toBeDefined();
  });
});
```

### **3. Manual Testing Checklist**

```markdown
## Manual Testing Checklist

### Basic Functionality
- [ ] Health check works (no auth required)
- [ ] Natal chart loads successfully
- [ ] Divisional charts load (D9 especially)
- [ ] Dashas load and display correctly
- [ ] Yogas and Doshas detected properly

### Error Handling
- [ ] Invalid birth date shows error
- [ ] Invalid latitude shows error
- [ ] Network error shows friendly message
- [ ] API key error shows appropriate message

### Performance
- [ ] Charts load in < 3 seconds on 4G
- [ ] Multiple charts can be loaded in parallel
- [ ] App doesn't freeze during calculations
- [ ] Memory usage stays reasonable

### Edge Cases
- [ ] Midnight birth (00:00:00) works
- [ ] Polar region coordinates work
- [ ] Date line locations work
- [ ] Retrograde planets detected correctly

### Offline Behavior
- [ ] Cached charts load offline
- [ ] Appropriate offline message shown
- [ ] App doesn't crash when offline
```

---

## 🔧 TROUBLESHOOTING

### **Common Issues & Solutions**

#### **Issue 1: "API Key Invalid" Error**

**Symptoms:**
```json
{
  "error": "Invalid API key",
  "error_code": "AUTH_001"
}
```

**Solutions:**
1. Check `.env` file has correct API key
2. Verify API key is being loaded: `console.log(Config.ASTRO_ENGINE_API_KEY)`
3. Check header is being sent: Add request interceptor log
4. Restart React Native bundler after changing `.env`

**Correct API Key:**
```
astro_corp_backend_F5XpEFrnQI-NZHlRWZVmcHT0uDvoPVXv
```

---

#### **Issue 2: "Network Request Failed"**

**Symptoms:**
- API calls timeout
- Error: "Network request failed"

**Solutions:**
1. Check internet connection
2. Verify firewall/VPN not blocking requests
3. Check base URL is correct: `https://astroengine.astrocorp.in`
4. Test with health endpoint first (no auth required)
5. Increase timeout: `timeout: 60000` (60 seconds)

---

#### **Issue 3: "Invalid Birth Data" Errors**

**Symptoms:**
```json
{
  "error": "Invalid input: latitude must be between -90 and 90"
}
```

**Solutions:**
1. Validate input before sending:
   - Date format: `YYYY-MM-DD`
   - Time format: `HH:MM:SS` (24-hour)
   - Latitude: `-90` to `90`
   - Longitude: `-180` to `180`
   - Timezone: `-12` to `14`
2. Use validation function (see Best Practices section)
3. Handle user input carefully (trim whitespace, validate format)

---

#### **Issue 4: Response Too Slow**

**Symptoms:**
- API calls take > 5 seconds
- App feels slow/unresponsive

**Solutions:**
1. Implement caching (see Performance Optimization)
2. Load charts progressively (don't wait for all at once)
3. Use loading indicators so users know something is happening
4. Reduce number of simultaneous requests
5. Check if you're on slow network (3G/2G)

---

#### **Issue 5: App Crashes on Chart Display**

**Symptoms:**
- App crashes when displaying chart data
- "Cannot read property 'X' of undefined"

**Solutions:**
1. Always check if data exists before rendering:
   ```typescript
   if (!chart?.planetary_positions) return null;
   ```
2. Use optional chaining: `chart?.ascendant?.sign`
3. Provide default values: `chart?.ascendant?.sign || 'N/A'`
4. Add proper null/undefined checks
5. Use TypeScript strictly (`strict: true` in tsconfig)

---

#### **Issue 6: Dates/Times Not Working**

**Symptoms:**
- Birth time off by hours
- Wrong planetary positions

**Solutions:**
1. Always use 24-hour format: `14:30:00` not `2:30 PM`
2. Verify timezone offset is correct:
   - IST (India): `5.5`
   - EST (US East): `-5`
   - GMT: `0`
3. Don't rely on device timezone - ask user explicitly
4. Test with known birth data and verify results

---

### **Debug Mode**

Enable detailed logging:

```typescript
class DebugAstroEngineAPI extends AstroEngineAPI {
  constructor() {
    super();

    // Log all requests
    this.axiosInstance.interceptors.request.use((config) => {
      console.log('========== API REQUEST ==========');
      console.log('URL:', config.url);
      console.log('Method:', config.method);
      console.log('Headers:', config.headers);
      console.log('Data:', JSON.stringify(config.data, null, 2));
      console.log('=================================');
      return config;
    });

    // Log all responses
    this.axiosInstance.interceptors.response.use((response) => {
      console.log('========== API RESPONSE ==========');
      console.log('Status:', response.status);
      console.log('Data:', JSON.stringify(response.data, null, 2));
      console.log('==================================');
      return response;
    });
  }
}
```

---

### **Contact Support**

If you encounter issues not covered here:

1. **Check Health Endpoint:**
   ```bash
   curl https://astroengine.astrocorp.in/health
   ```

2. **Collect Debug Info:**
   - Error message
   - Request data (birth details)
   - Request headers (API key hidden)
   - Network conditions
   - Device info (iOS/Android, OS version)

3. **Share with Backend Team:**
   - Provide correlation ID from response headers: `X-Correlation-Id`
   - Screenshots of error
   - Steps to reproduce

---

## 🎓 LEARNING RESOURCES

### **Understanding Vedic Astrology**

To build effective UI/UX, understand these key concepts:

1. **Planets (Grahas):**
   - Sun (Surya) - Soul, vitality, father
   - Moon (Chandra) - Mind, emotions, mother
   - Mars (Mangal) - Energy, courage, siblings
   - Mercury (Budha) - Intelligence, communication
   - Jupiter (Guru) - Wisdom, knowledge, children
   - Venus (Shukra) - Love, beauty, spouse
   - Saturn (Shani) - Discipline, delays, karma
   - Rahu - Obsessions, material desires
   - Ketu - Spirituality, detachment

2. **Signs (Rashis):**
   - 12 zodiac signs (Aries to Pisces)
   - Each sign has unique characteristics
   - Affects how planets express themselves

3. **Houses (Bhavas):**
   - 12 houses representing life areas:
     - 1st: Self, personality
     - 2nd: Wealth, family
     - 3rd: Siblings, courage
     - 4th: Home, mother
     - 5th: Children, creativity
     - 6th: Health, enemies
     - 7th: Spouse, partnerships
     - 8th: Longevity, inheritance
     - 9th: Fortune, father
     - 10th: Career, status
     - 11th: Gains, friends
     - 12th: Losses, moksha

4. **Nakshatras:**
   - 27 lunar mansions
   - Divide zodiac into 27 parts
   - Each 13°20' long
   - Further divided into 4 Padas (quarters)

5. **Dashas:**
   - Planetary periods
   - Show timing of events
   - Mahadasha = major period
   - Antardasha = sub-period within Mahadasha

6. **Yogas:**
   - Special planetary combinations
   - Indicate specific results (good or bad)
   - Enhance or diminish life areas

7. **Doshas:**
   - Afflictions or challenging combinations
   - Mangal Dosha = marriage delays
   - Sade Sati = Saturn's challenging transit
   - Often have remedies

### **UI/UX Recommendations**

Based on astrological concepts:

1. **Color Coding:**
   - Benefics (good planets): Green, gold
   - Malefics (challenging planets): Red, dark colors
   - Current dasha: Highlight in blue
   - Yogas: Green badges
   - Doshas: Red/orange warnings

2. **Iconography:**
   - Use planet symbols (☉☽♂☿♃♀♄)
   - Use zodiac symbols (♈♉♊♋♌♍♎♏♐♑♒♓)
   - Visual house wheel
   - Timeline for dashas

3. **Information Hierarchy:**
   - Most important: Natal chart, D9, Current Dasha
   - Medium: Other divisional charts, Yogas
   - Detailed: Ashtakavargha, Numerology
   - Advanced: KP system, Horary

4. **Progressive Disclosure:**
   - Show basic info first (signs, houses)
   - Expand to show details (nakshatras, degrees)
   - Expert mode for technical details (longitudes, sub-lords)

5. **Interpretations:**
   - Always include human-readable interpretations
   - Don't just show raw data
   - Explain what each thing means
   - Provide context and remedies

---

## 🎉 CONCLUSION

**You now have everything you need to integrate Astro Engine into the AstroCorp mobile app!**

### **Quick Start Checklist:**

1. ✅ Add API key to `.env` file
2. ✅ Install dependencies (`axios`, `async-storage`, `moment-timezone`)
3. ✅ Copy `AstroEngineAPI.ts` service file
4. ✅ Copy TypeScript interfaces
5. ✅ Test with health endpoint
6. ✅ Implement birth chart screen
7. ✅ Add error handling
8. ✅ Implement caching
9. ✅ Build remaining features progressively

### **Remember:**

- **Astro Engine is production-ready** - it's already handling calculations reliably
- **Authentication is required** - always include API key
- **Validate inputs** - prevent errors before they happen
- **Handle errors gracefully** - network issues will occur
- **Cache aggressively** - birth data doesn't change
- **Load progressively** - don't block UI waiting for everything
- **Test thoroughly** - edge cases matter in astrology

### **Next Steps:**

1. Start with **natal chart** feature (most important)
2. Add **D9 (Navamsa)** for marriage features
3. Implement **current dasha** display
4. Add **yogas and doshas** for insights
5. Build remaining features based on priority

### **Need Help?**

- Review this document thoroughly
- Check code examples
- Test with sample data first
- Reach out to backend team with correlation IDs

---

**Good luck building an amazing astrology app! 🌟**

**May the planets align in your favor! 🔮**

---

**Document Version:** 1.0
**Last Updated:** October 30, 2025
**Author:** Goutham K & Claude Code
**API Version:** 1.3.0
**Production URL:** https://astroengine.astrocorp.in
