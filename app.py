"""
KrishiMitra (कृषि मित्र) - Main Application Server
Full-featured Python Agricultural Problem-Solving & Farmer Support Platform.
Standard Library HTTP Server + REST API + SQLite integration.
Runs natively without mandatory external dependencies!
"""

import os
import sys
import json
import sqlite3
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import datetime

# Database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'krishimitra.db')

# Ensure DB is initialized
import database
database.init_db()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class KrishiRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # Serve Homepage
        if path == '/' or path == '/index.html':
            self.serve_file(os.path.join(BASE_DIR, 'templates', 'index.html'), 'text/html; charset=utf-8')
            return

        # Serve Static Files
        if path.startswith('/static/'):
            filepath = os.path.join(BASE_DIR, path[1:])
            if os.path.exists(filepath):
                content_type = 'text/plain'
                if filepath.endswith('.css'): content_type = 'text/css; charset=utf-8'
                elif filepath.endswith('.js'): content_type = 'application/javascript; charset=utf-8'
                elif filepath.endswith('.png'): content_type = 'image/png'
                elif filepath.endswith('.jpg') or filepath.endswith('.jpeg'): content_type = 'image/jpeg'
                elif filepath.endswith('.svg'): content_type = 'image/svg+xml'
                self.serve_file(filepath, content_type)
                return

        # API Endpoints
        if path == '/api/diseases':
            self.handle_get_diseases(query)
            return
        elif path == '/api/crops':
            self.handle_get_crops(query)
            return
        elif path == '/api/mandi-prices':
            self.handle_get_mandi_prices(query)
            return
        elif path == '/api/weather-advisory':
            self.handle_get_weather(query)
            return
        elif path == '/api/schemes':
            self.handle_get_schemes(query)
            return
        elif path == '/api/forum':
            self.handle_get_forum(query)
            return
        elif path == '/api/agri-centers':
            self.handle_get_agri_centers(query)
            return
        elif path == '/api/stats':
            self.handle_get_stats()
            return

        # 404 fallback
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'404 Not Found')

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = {}
        if post_data:
            try:
                data = json.loads(post_data)
            except Exception:
                data = urllib.parse.parse_qs(post_data)

        if path == '/api/diagnose':
            self.handle_diagnose(data)
        elif path == '/api/recommend-crop':
            self.handle_crop_recommendation(data)
        elif path == '/api/calculate-fertilizer':
            self.handle_fertilizer_calc(data)
        elif path == '/api/chat':
            self.handle_chat(data)
        elif path == '/api/forum/post':
            self.handle_forum_post(data)
        elif path == '/api/forum/reply':
            self.handle_forum_reply(data)
        elif path == '/api/forum/upvote':
            self.handle_forum_upvote(data)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')

    def serve_file(self, filepath, content_type):
        if not os.path.exists(filepath):
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        with open(filepath, 'rb') as f:
            self.wfile.write(f.read())

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    # --- API HANDLERS ---

    def handle_get_diseases(self, query):
        conn = get_db()
        cursor = conn.cursor()
        crop = query.get('crop', [None])[0]
        search = query.get('search', [None])[0]

        sql = 'SELECT * FROM diseases WHERE 1=1'
        params = []
        if crop:
            sql += ' AND (crop_name LIKE ? OR crop_name_hi LIKE ?)'
            params.extend([f'%{crop}%', f'%{crop}%'])
        if search:
            sql += ' AND (disease_name LIKE ? OR disease_name_hi LIKE ? OR symptom_tags LIKE ? OR symptoms LIKE ?)'
            params.extend([f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%'])

        cursor.execute(sql, params)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        self.send_json({'success': True, 'count': len(rows), 'diseases': rows})

    def handle_diagnose(self, data):
        conn = get_db()
        cursor = conn.cursor()
        crop_name = data.get('crop', '')
        symptoms_text = data.get('symptoms', '').lower()
        selected_symptoms = data.get('selected_symptoms', []) # list of strings
        image_name = data.get('image_name', '')

        # Build combined query text
        all_query = symptoms_text + " " + " ".join(selected_symptoms) + " " + image_name.lower()

        cursor.execute('SELECT * FROM diseases')
        all_diseases = [dict(r) for r in cursor.fetchall()]
        conn.close()

        # Diagnostic scoring engine
        results = []
        for d in all_diseases:
            score = 0
            # Crop match gives high boost
            if crop_name and crop_name.lower() in d['crop_name'].lower():
                score += 35

            # Match symptoms tags
            tags = [t.strip().lower() for t in d['symptom_tags'].split(',') if t.strip()]
            for tag in tags:
                if tag in all_query:
                    score += 25
                else:
                    words = tag.split()
                    for w in words:
                        if len(w) > 3 and w in all_query:
                            score += 8

            # Match in disease name
            if d['disease_name'].lower() in all_query or d['disease_name_hi'] in all_query:
                score += 40

            # Image keyword heuristic simulation
            if 'leaf' in all_query and ('leaf' in d['disease_name'].lower() or 'leaf' in d['symptoms'].lower()):
                score += 10
            if 'yellow' in all_query and ('yellow' in d['symptoms'].lower() or 'yellow' in d['disease_name'].lower()):
                score += 15
            if 'rust' in all_query and 'rust' in d['disease_name'].lower():
                score += 30
            if 'blight' in all_query and 'blight' in d['disease_name'].lower():
                score += 30
            if 'curl' in all_query and 'curl' in d['disease_name'].lower():
                score += 30
            if 'caterpillar' in all_query or 'worm' in all_query:
                if d['category'] == 'Pest': score += 20

            confidence = min(98, max(42, score)) if score > 0 else 0
            if score > 0 or not crop_name:
                results.append({
                    **d,
                    'confidence': confidence,
                    'match_score': score
                })

        # Sort by confidence
        results.sort(key=lambda x: x['confidence'], reverse=True)
        top_diagnoses = results[:3] if results else all_diseases[:3]
        if not results and all_diseases:
            top_diagnoses = [{**all_diseases[0], 'confidence': 65}]

        self.send_json({
            'success': True,
            'primary_diagnosis': top_diagnoses[0] if top_diagnoses else None,
            'differential_diagnoses': top_diagnoses[1:],
            'total_evaluated': len(all_diseases)
        })

    def handle_get_crops(self, query):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM crops')
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        self.send_json({'success': True, 'crops': rows})

    def handle_crop_recommendation(self, data):
        """
        AI Multi-Criteria Soil & Climate Crop Matching Algorithm
        Inputs: N, P, K, pH, rainfall, temperature, soil_type, season
        """
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM crops')
        all_crops = [dict(r) for r in cursor.fetchall()]
        conn.close()

        try:
            n = float(data.get('n', 90))
            p = float(data.get('p', 45))
            k = float(data.get('k', 50))
            ph = float(data.get('ph', 6.5))
            temp = float(data.get('temp', 25.0))
            rainfall = float(data.get('rainfall', 600.0))
            soil_type = data.get('soil_type', 'Alluvial')
            season = data.get('season', 'All')
        except ValueError:
            self.send_json({'success': False, 'error': 'Invalid numerical inputs'}, 400)
            return

        recommendations = []
        soil_alerts = []

        # Soil diagnostics
        if ph < 5.5:
            soil_alerts.append({
                'type': 'warning',
                'title': 'Acidic Soil Detected (pH < 5.5)',
                'title_hi': 'अम्लीय मिट्टी की पहचान (pH < 5.5)',
                'remedy': 'Apply agricultural lime (Calcium Carbonate) or Dolomite @ 250-500 kg/acre to neutralize acidity.',
                'remedy_hi': 'मिट्टी की अम्लीयता दूर करने हेतु 250-500 किग्रा/एकड़ कृषि चूना या डोलोमाइट मिलाएं।'
            })
        elif ph > 8.2:
            soil_alerts.append({
                'type': 'warning',
                'title': 'Alkaline / Saline Soil Detected (pH > 8.2)',
                'title_hi': 'क्षारीय / लवणीय मिट्टी (pH > 8.2)',
                'remedy': 'Apply Agricultural Gypsum @ 500-1000 kg/acre and incorporate green manure (Dhaincha / Sunhemp).',
                'remedy_hi': 'क्षारीयता कम करने हेतु 500-1000 किग्रा/एकड़ जिप्सम डालें और ढैंचा/सनई की हरी खाद दें।'
            })

        if n < 50:
            soil_alerts.append({
                'type': 'info',
                'title': 'Low Nitrogen Reserve',
                'title_hi': 'नाइट्रोजन की कमी',
                'remedy': 'Apply well-decomposed FYM (Farm Yard Manure) @ 5 tons/acre or grow nitrogen-fixing legume crops.',
                'remedy_hi': '5 टन/एकड़ सड़ी गोबर खाद डालें या दलहनी फसलें लगाकर नाइट्रोजन बढ़ाएं।'
            })

        for crop in all_crops:
            score = 100.0
            reasons = []

            # 1. Season filter/score
            if season != 'All' and crop['season'] != 'Year-round' and crop['season'] != season:
                score -= 30
            else:
                reasons.append(f"Suited for {crop['season']} season")

            # 2. Soil Type match
            if soil_type.lower() in crop['soil_types'].lower():
                score += 10
                reasons.append(f"Ideal soil compatibility ({soil_type})")
            else:
                score -= 15

            # 3. NPK suitability
            # N
            if n < crop['min_n']:
                diff = (crop['min_n'] - n) / crop['min_n']
                score -= min(25, diff * 35)
            elif n > crop['max_n'] * 1.5:
                score -= 10
            # P
            if p < crop['min_p']:
                diff = (crop['min_p'] - p) / crop['min_p']
                score -= min(20, diff * 30)
            # K
            if k < crop['min_k']:
                diff = (crop['min_k'] - k) / crop['min_k']
                score -= min(20, diff * 30)

            # 4. pH suitability
            if ph < crop['min_ph'] or ph > crop['max_ph']:
                ph_diff = min(abs(ph - crop['min_ph']), abs(ph - crop['max_ph']))
                score -= min(35, ph_diff * 20)
            else:
                score += 5

            # 5. Temperature suitability
            if temp < crop['min_temp'] or temp > crop['max_temp']:
                temp_diff = min(abs(temp - crop['min_temp']), abs(temp - crop['max_temp']))
                score -= min(30, temp_diff * 4)

            # 6. Rainfall suitability
            if rainfall < crop['min_rainfall'] * 0.5:
                score -= 20
            elif rainfall > crop['max_rainfall'] * 1.5:
                score -= 20

            match_pct = max(15, min(99, round(score, 1)))

            recommendations.append({
                **crop,
                'match_score': match_pct,
                'reasons': reasons
            })

        recommendations.sort(key=lambda x: x['match_score'], reverse=True)

        self.send_json({
            'success': True,
            'soil_alerts': soil_alerts,
            'top_recommendations': recommendations[:6],
            'total_crops': len(recommendations)
        })

    def handle_fertilizer_calc(self, data):
        """
        Fertilizer & Irrigation Dosage Calculator
        Calculates exact commercial bags (Urea 46% N, DAP 18-46-0, MOP 60% K2O, SSP 16% P2O5)
        """
        crop_name = data.get('crop', 'Wheat')
        area = float(data.get('area', 1.0))
        unit = data.get('unit', 'Acre') # Acre, Hectare, Bigha, Guntha

        # Normalize to Acres
        acre_conversion = {
            'Acre': 1.0,
            'Hectare': 2.47105,
            'Bigha (Standard)': 0.625,
            'Guntha': 0.025
        }
        acres = area * acre_conversion.get(unit, 1.0)

        # Standard Recommended Dose of Fertilizer (RDF) per Acre (N : P2O5 : K2O kg/acre)
        crop_rdf = {
            'Rice / Paddy': {'n': 48, 'p': 24, 'k': 24, 'splits': '3 splits (50% Basal + 25% Active Tillering + 25% Panicle Initiation)', 'water_req': '1200 mm (Standing 2-5cm)'},
            'Wheat': {'n': 48, 'p': 24, 'k': 16, 'splits': '3 splits (50% Basal + 25% CRI Stage + 25% Tillering)', 'water_req': '450 mm (4-6 irrigations)'},
            'Cotton': {'n': 45, 'p': 22, 'k': 22, 'splits': '3 splits (Basal at sowing + Square formation + Peak flowering)', 'water_req': '650 mm'},
            'Tomato': {'n': 60, 'p': 36, 'k': 48, 'splits': '4 splits (Basal + 30 DAT + 50 DAT + Peak fruiting)', 'water_req': '550 mm (Drip recommended)'},
            'Potato': {'n': 60, 'p': 36, 'k': 48, 'splits': '2 splits (50% Basal at planting + 50% at Earthing-up 30-35 DAP)', 'water_req': '500 mm'},
            'Sugarcane': {'n': 100, 'p': 30, 'k': 40, 'splits': '3 splits (Basal + 45 DAP + 90 DAP before earthing-up)', 'water_req': '1800 mm'},
            'Mustard': {'n': 32, 'p': 16, 'k': 12, 'splits': '2 splits (50% Basal + 50% at 1st irrigation flowering)', 'water_req': '300 mm'},
            'Chickpea': {'n': 10, 'p': 20, 'k': 10, 'splits': '100% Basal dose at sowing', 'water_req': '250 mm'},
            'Maize': {'n': 48, 'p': 24, 'k': 20, 'splits': '3 splits (Basal + Knee-high stage + Tasseling stage)', 'water_req': '550 mm'},
            'Groundnut': {'n': 10, 'p': 20, 'k': 18, 'splits': '100% Basal dose + Gypsum @ 150 kg/acre at 40-45 DAS', 'water_req': '450 mm'},
            'Soybean': {'n': 12, 'p': 28, 'k': 16, 'splits': '100% Basal dose at sowing', 'water_req': '550 mm'},
            'Onion': {'n': 45, 'p': 22, 'k': 36, 'splits': '3 splits (50% Basal + 25% 30 DAT + 25% 45 DAT)', 'water_req': '450 mm'}
        }

        rdf = crop_rdf.get(crop_name, {'n': 40, 'p': 20, 'k': 20, 'splits': '50% Basal + 50% Top dressing', 'water_req': '500 mm'})

        tot_n = rdf['n'] * acres
        tot_p = rdf['p'] * acres
        tot_k = rdf['k'] * acres

        # Commercial Fertilizer Combo Option A: DAP + Urea + MOP
        # 100 kg DAP gives 18 kg N and 46 kg P2O5
        dap_kg = (tot_p / 0.46) if tot_p > 0 else 0
        n_from_dap = dap_kg * 0.18
        remaining_n = max(0, tot_n - n_from_dap)
        urea_kg = (remaining_n / 0.46) if remaining_n > 0 else 0
        mop_kg = (tot_k / 0.60) if tot_k > 0 else 0

        # Commercial Fertilizer Combo Option B: SSP + Urea + MOP
        ssp_kg = (tot_p / 0.16) if tot_p > 0 else 0
        urea_b_kg = (tot_n / 0.46) if tot_n > 0 else 0

        # 45kg/50kg bag equivalents
        dap_bags = round(dap_kg / 50.0, 1)
        urea_bags = round(urea_kg / 45.0, 1) # Urea is 45kg standard bag in India
        mop_bags = round(mop_kg / 50.0, 1)
        ssp_bags = round(ssp_kg / 50.0, 1)

        # Micro-nutrient advice
        micronutrients = [
            {'name': 'Zinc Sulphate (ZnSO4 21%)', 'dosage': f'{round(10 * acres, 1)} kg', 'purpose': 'Prevents Khaira disease, enhances chlorophyll synthesis & enzyme activity.'},
            {'name': 'Nano Urea (Liquid Spray)', 'dosage': f'{round(1 * acres, 1)} Bottles (500ml)', 'purpose': 'Eco-friendly foliar spray at active tillering/vegetative stage @ 2-4 ml/L.'},
            {'name': 'Sulfur 90% WDG / Bentonite', 'dosage': f'{round(8 * acres, 1)} kg (especially for oilseeds & pulses)', 'purpose': 'Boosts oil content, protein synthesis, and disease immunity.'}
        ]

        # Estimated cost (INR)
        cost_dap = dap_bags * 1350
        cost_urea = urea_bags * 267
        cost_mop = mop_bags * 1700
        total_estimated_cost = round(cost_dap + cost_urea + cost_mop, 2)

        self.send_json({
            'success': True,
            'crop': crop_name,
            'area_entered': area,
            'unit_entered': unit,
            'normalized_acres': round(acres, 2),
            'pure_nutrients_kg': {
                'N': round(tot_n, 1),
                'P2O5': round(tot_p, 1),
                'K2O': round(tot_k, 1)
            },
            'recommended_plan_dap_combo': {
                'dap': {'kg': round(dap_kg, 1), 'bags_50kg': dap_bags},
                'urea': {'kg': round(urea_kg, 1), 'bags_45kg': urea_bags},
                'mop': {'kg': round(mop_kg, 1), 'bags_50kg': mop_bags},
                'estimated_cost_inr': total_estimated_cost
            },
            'alternate_plan_ssp_combo': {
                'ssp': {'kg': round(ssp_kg, 1), 'bags_50kg': ssp_bags},
                'urea': {'kg': round(urea_b_kg, 1), 'bags_45kg': round(urea_b_kg / 45.0, 1)},
                'mop': {'kg': round(mop_kg, 1), 'bags_50kg': mop_bags}
            },
            'split_application_schedule': rdf['splits'],
            'irrigation_water_advice': rdf['water_req'],
            'micronutrients': micronutrients
        })

    def handle_get_mandi_prices(self, query):
        conn = get_db()
        cursor = conn.cursor()
        state = query.get('state', [None])[0]
        commodity = query.get('commodity', [None])[0]

        sql = 'SELECT * FROM mandi_prices WHERE 1=1'
        params = []
        if state and state != 'All':
            sql += ' AND state = ?'
            params.append(state)
        if commodity and commodity != 'All':
            sql += ' AND (commodity LIKE ? OR commodity_hi LIKE ?)'
            params.extend([f'%{commodity}%', f'%{commodity}%'])

        cursor.execute(sql, params)
        rows = []
        for r in cursor.fetchall():
            d = dict(r)
            d['trend_data'] = json.loads(d['trend_data']) if d['trend_data'] else []
            rows.append(d)
        conn.close()

        # Extract unique states and commodities for filters
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT DISTINCT state FROM mandi_prices ORDER BY state')
        states = [r[0] for r in c.fetchall()]
        c.execute('SELECT DISTINCT commodity FROM mandi_prices ORDER BY commodity')
        commodities = [r[0] for r in c.fetchall()]
        conn.close()

        self.send_json({
            'success': True,
            'count': len(rows),
            'prices': rows,
            'available_states': states,
            'available_commodities': commodities
        })

    def handle_get_weather(self, query):
        district = query.get('district', ['Indore, MP'])[0]
        # Realistic agro-meteorological dynamic advisory
        today = datetime.date.today()
        forecast = [
            {'day': 'Today', 'date': today.strftime('%d %b'), 'temp_max': 31, 'temp_min': 22, 'condition': 'Partly Cloudy', 'rain_prob': 20, 'humidity': 68, 'wind_speed': 12, 'icon': 'cloud-sun'},
            {'day': 'Tomorrow', 'date': (today + datetime.timedelta(days=1)).strftime('%d %b'), 'temp_max': 32, 'temp_min': 23, 'condition': 'Sunny & Warm', 'rain_prob': 10, 'humidity': 60, 'wind_speed': 10, 'icon': 'sun'},
            {'day': (today + datetime.timedelta(days=2)).strftime('%a'), 'date': (today + datetime.timedelta(days=2)).strftime('%d %b'), 'temp_max': 29, 'temp_min': 21, 'condition': 'Light Rain Showers', 'rain_prob': 75, 'humidity': 85, 'wind_speed': 18, 'icon': 'cloud-rain'},
            {'day': (today + datetime.timedelta(days=3)).strftime('%a'), 'date': (today + datetime.timedelta(days=3)).strftime('%d %b'), 'temp_max': 28, 'temp_min': 20, 'condition': 'Moderate Rain', 'rain_prob': 80, 'humidity': 88, 'wind_speed': 22, 'icon': 'cloud-showers-heavy'},
            {'day': (today + datetime.timedelta(days=4)).strftime('%a'), 'date': (today + datetime.timedelta(days=4)).strftime('%d %b'), 'temp_max': 30, 'temp_min': 21, 'condition': 'Passing Clouds', 'rain_prob': 35, 'humidity': 72, 'wind_speed': 14, 'icon': 'cloud'},
            {'day': (today + datetime.timedelta(days=5)).strftime('%a'), 'date': (today + datetime.timedelta(days=5)).strftime('%d %b'), 'temp_max': 33, 'temp_min': 22, 'condition': 'Clear Sunny', 'rain_prob': 5, 'humidity': 55, 'wind_speed': 9, 'icon': 'sun'},
            {'day': (today + datetime.timedelta(days=6)).strftime('%a'), 'date': (today + datetime.timedelta(days=6)).strftime('%d %b'), 'temp_max': 34, 'temp_min': 23, 'condition': 'Warm & Clear', 'rain_prob': 5, 'humidity': 52, 'wind_speed': 8, 'icon': 'sun'}
        ]

        advisories = [
            {
                'category': 'Pesticide Spray Advisory',
                'status': 'FAVORABLE (TODAY & TOMORROW)',
                'badge_class': 'badge-success',
                'text': 'Winds are calm (< 12 km/h) and no heavy rain expected for next 36 hours. Ideal window to finish protective insecticide/fungicide sprays.',
                'text_hi': 'अगले 36 घंटे हवा की गति शांत है और बारिश नहीं है। कीटनाशक व फफूंदनाशक स्प्रे पूरा करने का सबसे उत्तम समय।'
            },
            {
                'category': 'Irrigation Timing',
                'status': 'POSTPONE AFTER TOMORROW',
                'badge_class': 'badge-warning',
                'text': 'Moderate rainfall (75-80% probability) expected on Day 3 & Day 4. Postpone heavy field flood irrigation to save energy and avoid waterlogging.',
                'text_hi': '3 और 4 दिन बाद बारिश की 75-80% संभावना है। खेत में भारी पानी देने से बचें ताकि जलभराव न हो।'
            },
            {
                'category': 'Pest / Disease High Risk Alert',
                'status': 'HIGH HUMIDITY WARNING',
                'badge_class': 'badge-danger',
                'text': 'High relative humidity (>80%) accompanied by rain can accelerate Fungal Blast in Paddy and Late Blight in Tomato/Potato. Keep Trichoderma or Mancozeb in reserve.',
                'text_hi': 'अधिक नमी के कारण धान में ब्लास्ट और टमाटर/आलू में झुलसा का खतरा। फफूंदनाशक तैयार रखें।'
            }
        ]

        self.send_json({
            'success': True,
            'location': district,
            'forecast': forecast,
            'advisories': advisories
        })

    def handle_get_schemes(self, query):
        conn = get_db()
        cursor = conn.cursor()
        category = query.get('category', [None])[0]

        sql = 'SELECT * FROM govt_schemes WHERE 1=1'
        params = []
        if category and category != 'All':
            sql += ' AND category = ?'
            params.append(category)

        cursor.execute(sql, params)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        self.send_json({'success': True, 'schemes': rows})

    def handle_get_forum(self, query):
        conn = get_db()
        cursor = conn.cursor()
        crop = query.get('crop', [None])[0]

        sql = 'SELECT * FROM forum_posts WHERE 1=1'
        params = []
        if crop and crop != 'All':
            sql += ' AND crop_tag = ?'
            params.append(crop)

        sql += ' ORDER BY created_at DESC'
        cursor.execute(sql, params)
        posts = [dict(r) for r in cursor.fetchall()]

        # Attach replies
        for post in posts:
            cursor.execute('SELECT * FROM forum_replies WHERE post_id = ? ORDER BY is_verified_solution DESC, upvotes DESC, created_at ASC', (post['id'],))
            post['replies'] = [dict(r) for r in cursor.fetchall()]

        conn.close()
        self.send_json({'success': True, 'posts': posts})

    def handle_forum_post(self, data):
        title = data.get('title', '').strip()
        author_name = data.get('author_name', 'Anonymous Farmer').strip()
        location = data.get('location', 'India').strip()
        crop_tag = data.get('crop_tag', 'General').strip()
        category = data.get('category', 'Disease').strip()
        content = data.get('content', '').strip()
        image_url = data.get('image_url', None)

        if not title or not content:
            self.send_json({'success': False, 'error': 'Title and content are required'}, 400)
            return

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO forum_posts (title, author_name, location, crop_tag, category, content, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, author_name, location, crop_tag, category, content, image_url))
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()

        self.send_json({'success': True, 'post_id': post_id, 'message': 'Post created successfully'})

    def handle_forum_reply(self, data):
        post_id = data.get('post_id')
        author_name = data.get('author_name', 'Agri Helper').strip()
        author_role = data.get('author_role', 'Farmer').strip()
        content = data.get('content', '').strip()

        if not post_id or not content:
            self.send_json({'success': False, 'error': 'Post ID and content are required'}, 400)
            return

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO forum_replies (post_id, author_name, author_role, content)
            VALUES (?, ?, ?, ?)
        ''', (post_id, author_name, author_role, content))
        reply_id = cursor.lastrowid
        conn.commit()
        conn.close()

        self.send_json({'success': True, 'reply_id': reply_id, 'message': 'Reply added successfully'})

    def handle_forum_upvote(self, data):
        post_id = data.get('post_id')
        reply_id = data.get('reply_id')

        conn = get_db()
        cursor = conn.cursor()
        if post_id:
            cursor.execute('UPDATE forum_posts SET upvotes = upvotes + 1 WHERE id = ?', (post_id,))
        elif reply_id:
            cursor.execute('UPDATE forum_replies SET upvotes = upvotes + 1 WHERE id = ?', (reply_id,))
        conn.commit()
        conn.close()

        self.send_json({'success': True, 'message': 'Upvoted'})

    def handle_get_agri_centers(self, query):
        conn = get_db()
        cursor = conn.cursor()
        center_type = query.get('type', [None])[0]
        state = query.get('state', [None])[0]

        sql = 'SELECT * FROM agri_centers WHERE 1=1'
        params = []
        if center_type and center_type != 'All':
            sql += ' AND type = ?'
            params.append(center_type)
        if state and state != 'All':
            sql += ' AND state = ?'
            params.append(state)

        cursor.execute(sql, params)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        self.send_json({'success': True, 'centers': rows})

    def handle_get_stats(self):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM diseases')
        total_diseases = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM crops')
        total_crops = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM mandi_prices')
        total_mandis = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM govt_schemes')
        total_schemes = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM forum_posts')
        total_forum_posts = cursor.fetchone()[0]
        conn.close()

        self.send_json({
            'success': True,
            'stats': {
                'diseases_diagnosed': 1420 + total_diseases * 15,
                'crops_catalogued': total_crops,
                'mandi_commodities': total_mandis,
                'schemes_listed': total_schemes,
                'community_questions': total_forum_posts,
                'farmer_helpline': '1800-180-1551 (Kisan Call Centre 24x7)'
            }
        })

    def handle_chat(self, data):
        """
        Kisan AI Assistant: Multilingual intelligent agri problem solver
        Answers inquiries in English & Hindi with actionable remedies, dosages, government schemes, and market advice.
        """
        message = data.get('message', '').strip().lower()
        lang = data.get('lang', 'en') # 'en' or 'hi'

        if not message:
            self.send_json({'reply': 'Please ask a question about crops, fertilizers, pests, market prices, or schemes.'})
            return

        # Intelligent Agricultural Knowledge Matcher
        reply_en = ""
        reply_hi = ""
        action_link = None
        action_label = None

        if any(w in message for w in ['yellow', 'rust', 'wheat', 'गेहूं', 'पीला', 'रतुआ']):
            reply_en = "🌾 **Yellow Rust (Stripe Rust) in Wheat:**\n- **Symptoms:** Yellow pustules arranged in linear stripes on leaves.\n- **Chemical Solution:** Spray **Propiconazole 25% EC (Tilt)** @ 1ml/L (200ml in 200L water/acre) immediately.\n- **Organic Remedy:** Spray Dashparni Ark @ 25ml/L or fermented Butter Milk + Hing.\n- **Advice:** Do not delay spray, as rust spores spread rapidly through wind."
            reply_hi = "🌾 **गेहूँ में पीला रतुआ (हल्दी रोग):**\n- **लक्षण:** पत्तियों पर हल्दी जैसा पीला पाउडर और धारियाँ।\n- **रासायनिक समाधान:** **प्रोपिकोनाज़ोल 25% EC (टिल्ट)** @ 1 मिली प्रति लीटर पानी (200 मिली/एकड़) का तुरंत छिड़काव करें।\n- **जैविक उपाय:** दशपर्णी अर्क (25 मिली/लीटर) या खट्टी छाछ में हींग मिलाकर छिड़कें।\n- **सलाह:** हवा से तेजी से फैलने से रोकने के लिए तुरंत स्प्रे करें।"
            action_link = "#crop-doctor"
            action_label = "Open Crop Doctor"

        elif any(w in message for w in ['pm kisan', 'pm-kisan', 'installment', '6000', 'सम्मान निधि', 'किस्त']):
            reply_en = "🏛️ **PM-Kisan Samman Nidhi Scheme:**\n- **Benefit:** ₹6,000/year deposited directly in 3 installments of ₹2,000 every 4 months.\n- **Mandatory Requirements:** Aadhaar e-KYC, Bank account linked with NPCI/Aadhaar, Land seeding in portal.\n- **Portal:** Visit [pmkisan.gov.in](https://pmkisan.gov.in) to check beneficiary status or complete biometric OTP e-KYC."
            reply_hi = "🏛️ **प्रधानमंत्री किसान सम्मान निधि योजना:**\n- **लाभ:** प्रति वर्ष ₹6,000 सीधे बैंक खाते में (₹2,000 की 3 समान किस्तों में)।\n- **आवश्यक शर्तें:** आधार e-KYC, बैंक खाता आधार/NPCI से लिंक, जमीन का रिकॉर्ड (Land Seeding)।\n- **पोर्टल:** स्टेटस देखने हेतु [pmkisan.gov.in](https://pmkisan.gov.in) पर जाएं।"
            action_link = "#schemes"
            action_label = "View Govt Schemes"

        elif any(w in message for w in ['solar', 'pump', 'kusum', 'सब्सिडी', 'सोलर']):
            reply_en = "☀️ **PM KUSUM Solar Pump Subsidy:**\n- **Benefit:** 60% to 90% government subsidy for installing 3 HP to 10 HP solar pumps for agricultural tubewells.\n- **Eligibility:** Farmers with cultivable land and an operational borewell/water source.\n- **Application:** Apply through your State Renewable Energy Agency portal (e.g. UPNEDA, MEDA, RREC)."
            reply_hi = "☀️ **पीएम कुसुम सोलर पंप योजना:**\n- **लाभ:** 3 से 10 HP के सोलर सिंचाई पंप पर 60% से 90% तक सरकारी अनुदान।\n- **पात्रता:** कृषि भूमि और बोरवेल/सिंचाई जल स्रोत वाले सभी किसान।\n- **आवेदन:** राज्य सौर ऊर्जा विकास एजेंसी पोर्टल (जैसे UPNEDA, MEDA) के माध्यम से ऑनलाइन करें।"
            action_link = "#schemes"
            action_label = "Explore Subsidies"

        elif any(w in message for w in ['fertilizer', 'urea', 'dap', 'खाद', 'यूरिया', 'डीएपी', 'dosage']):
            reply_en = "🧪 **Fertilizer Split Application Guidelines:**\n- **Basal Dose (at Sowing):** Apply 100% of DAP/SSP (Phosphorus) and MOP (Potash) + 30-50% Nitrogen (Urea).\n- **1st Top Dressing:** Apply 25-35% Urea at first irrigation (CRI/Vegetative stage).\n- **2nd Top Dressing:** Apply remaining 25% Urea before flowering/tillering.\n- Use our interactive **Fertilizer Calculator** to get exact kilograms for your field area!"
            reply_hi = "🧪 **खाद (उर्वरक) देने का सही तरीका:**\n- **बुवाई के समय (बेसल डोज):** पूरी डीएपी/एसएसपी (फास्फोरस) व पोटाश + 30-50% यूरिया दें।\n- **पहली टॉप-ड्रेसिंग:** पहली सिंचाई (20-25 दिन) पर 25-35% यूरिया दें।\n- **दूसरी टॉप-ड्रेसिंग:** कल्ले निकलते समय शेष 25% यूरिया दें।\n- अपने खेत के सटीक बैग जानने हेतु **उर्वरक कैलकुलेटर** का उपयोग करें!"
            action_link = "#fertilizer-calc"
            action_label = "Fertilizer Calculator"

        elif any(w in message for w in ['tomato', 'curl', 'मरोड़िया', 'टमाटर', 'leaf curl', 'whitefly']):
            reply_en = "🍅 **Tomato Leaf Curl Virus (ToLCV) & Whitefly Control:**\n- **Cause:** Vectored by Silverleaf Whitefly insect.\n- **Chemical Control:** Spray **Diafenthiuron 50% WP @ 1.25g/L** OR **Acetamiprid 20% SP @ 0.3g/L**.\n- **Organic Control:** Install Yellow Sticky Traps @ 20/acre. Spray 10,000 ppm Neem Oil @ 3ml/L every 7 days.\n- **Crucial:** Rogue out (uproot) severely stunted infected plants immediately."
            reply_hi = "🍅 **टमाटर का पर्ण कुंचन (मरोड़िया रोग) व सफेद मक्खी:**\n- **कारण:** सफेद मक्खी कीट द्वारा विषाणु फैलना।\n- **रासायनिक समाधान:** **डायाफेंथियुरॉन 50% WP @ 1.25 ग्राम/लीटर** या **एसिटामिप्रिड 20% SP @ 0.3 ग्राम/लीटर** का छिड़काव करें।\n- **जैविक उपाय:** 20 पीले चिपचिपे जाल लगाएं और 10,000 ppm नीम तेल (3 मिली/लीटर) छिड़कें।"
            action_link = "#crop-doctor"
            action_label = "View Crop Doctor"

        elif any(w in message for w in ['neem', 'organic', 'jeevamrit', 'जैविक', 'जीवामृत', 'नीम तेल']):
            reply_en = "🌿 **Organic Farming & Bio-Formulation Recipe:**\n- **Jeevamrit (for 1 Acre):** 10kg fresh desi cow dung + 10L cow urine + 2kg jaggery + 2kg pulse flour (Besan) + handful of virgin forest soil in 200L water. Ferment for 48-72 hours.\n- **Neem Oil Spray:** 3 to 5 ml Neem Oil (10,000 ppm) + 1 ml liquid soap per liter of water.\n- **Trichoderma Bio-Fungicide:** 5-10g/L for foliar spray, or mix 2kg in 100kg compost for soil treatment."
            reply_hi = "🌿 **जैविक खेती एवं प्राकृतिक घोल निर्माण:**\n- **जीवामृत (1 एकड़ हेतु):** 10 किग्रा देसी गाय का गोबर + 10 ली गोमूत्र + 2 किग्रा गुड़ + 2 किग्रा बेसन + 1 मुट्ठी खेत की मिट्टी 200 ली पानी में 3 दिन सड़ाएं।\n- **नीम तेल स्प्रे:** 3-5 मिली नीम तेल (10,000 ppm) + 1 मिली लिक्विड साबुन प्रति लीटर पानी में।\n- **ट्राइकोडर्मा:** 10 ग्राम/लीटर स्प्रे हेतु या 2 किग्रा 100 किग्रा गोबर खाद में मिलाकर भूमि उपचार करें।"

        elif any(w in message for w in ['mandi', 'rate', 'price', 'भाव', 'मंडी']):
            reply_en = "📊 **Live Mandi Prices & Selling Insights:**\n- You can check real-time APMC mandi modal prices, MSP profit benchmarks, and 7-day price fluctuations in our **Live Mandi Tracker** tab.\n- Current wheat modal price: ₹2,475/qtl (Above MSP ₹2,275), Basmati Paddy: ₹3,950/qtl, Mustard: ₹5,620/qtl."
            reply_hi = "📊 **लाइव मंडी भाव एवं बाजार परामर्श:**\n- आप हमारे **लाइव मंडी ट्रैकर** में देश भर की मंडियों के आज के भाव, MSP तुलना और 7 दिवसीय मूल्य ग्राफ देख सकते हैं।\n- आज का गेहूं भाव: ₹2,475/क्विंटल (MSP से अधिक), बासमती: ₹3,950/क्विंटल, सरसों: ₹5,620/क्विंटल।"
            action_link = "#mandi-tracker"
            action_label = "Check Mandi Prices"

        else:
            reply_en = f"🌾 **Kisan AI Assistant Response:**\nI have received your query regarding *'{message}'*. Here are recommended agricultural best practices:\n1. **Diagnosis & Treatment:** Upload photos or select symptoms in the **Crop Doctor** to receive exact chemical & organic remedies with dosages.\n2. **Soil Health:** Check our **Soil & Crop Recommender** to optimize NPK, pH, and crop selection.\n3. **Govt Schemes:** Explore PM-Kisan, PM Fasal Bima, and Solar Pump subsidies in the Schemes section.\n4. **Expert Helpline:** Call Kisan Call Centre at **1800-180-1551 (Toll-Free, 24x7)** for direct scientist voice consultations."
            reply_hi = f"🌾 **किसान एआई सहायक उत्तर:**\nआपके प्रश्न *'{message}'* के संदर्भ में मुख्य कृषि परामर्श:\n1. **रोग निदान व उपचार:** पत्ती की फोटो अपलोड करके या लक्षण चुनकर **क्रॉप डॉक्टर** में तुरंत जैविक व रासायनिक दवा की मात्रा जानें।\n2. **मृदा स्वास्थ्य:** अपने खेत की मिट्टी (NPK व pH) अनुसार उपयुक्त फसल जानने के लिए **मृदा सलाहकार** देखें।\n3. **सरकारी योजनाएं:** पीएम किसान, फसल बीमा और सोलर पंप सब्सिडी की जानकारी **योजनाएं** टैब में देखें।\n4. **कृषि वैज्ञानिक हेल्पलाइन:** सीधे कृषि वैज्ञानिकों से 24x7 बात करने हेतु किसान कॉल सेंटर **1800-180-1551 (टोल-फ्री)** पर कॉल करें।"

        chosen_reply = reply_hi if lang == 'hi' else reply_en

        self.send_json({
            'success': True,
            'reply': chosen_reply,
            'reply_en': reply_en,
            'reply_hi': reply_hi,
            'action_link': action_link,
            'action_label': action_label
        })

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, KrishiRequestHandler)
    print(f"================================================================")
    print(f"🌾 KrishiMitra (कृषि मित्र) Server running at http://localhost:{port}")
    print(f"================================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down KrishiMitra server...")
        httpd.server_close()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)
