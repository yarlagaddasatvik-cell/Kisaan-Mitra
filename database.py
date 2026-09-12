"""
KrishiMitra (कृषि मित्र) - Database & Agricultural Knowledge Engine
SQLite Database initialization with comprehensive agricultural datasets:
- Crop Disease & Pest Diagnostic Knowledge Base (Organic & Chemical Treatments)
- Crop Profiles & Optimal Soil Parameters (NPK, pH, Rainfall, Temperature, Season)
- Fertilizer Formulations & Basal/Top-dressing Schedules
- APMC Mandi Market Prices with MSP benchmarks and 7-day trends
- Central & State Government Farmer Welfare Schemes & Subsidies
- Krishi Vigyan Kendras (KVK) & Custom Hiring Centers (CHC) Directory
- Community Problem-Solving Q&A Forum
"""

import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'krishimitra.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Diseases & Pests Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diseases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_name TEXT NOT NULL,
            crop_name_hi TEXT NOT NULL,
            disease_name TEXT NOT NULL,
            disease_name_hi TEXT NOT NULL,
            scientific_name TEXT,
            category TEXT NOT NULL, -- Fungal, Bacterial, Viral, Pest, Deficiency
            severity TEXT NOT NULL, -- Low, Medium, High, Critical
            symptoms TEXT NOT NULL,
            symptoms_hi TEXT NOT NULL,
            symptom_tags TEXT NOT NULL, -- comma separated keywords for search
            organic_treatment TEXT NOT NULL,
            organic_treatment_hi TEXT NOT NULL,
            chemical_treatment TEXT NOT NULL,
            chemical_treatment_hi TEXT NOT NULL,
            dosage_guideline TEXT NOT NULL,
            prevention TEXT NOT NULL,
            prevention_hi TEXT NOT NULL,
            sample_image TEXT
        )
    ''')

    # 2. Crops & Soil Requirements Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_name TEXT NOT NULL,
            crop_name_hi TEXT NOT NULL,
            category TEXT NOT NULL, -- Cereals, Pulses, Oilseeds, Vegetables, Fruits, Cash Crops
            season TEXT NOT NULL, -- Kharif, Rabi, Zaid, Year-round
            min_n REAL, max_n REAL,
            min_p REAL, max_p REAL,
            min_k REAL, max_k REAL,
            min_ph REAL, max_ph REAL,
            min_temp REAL, max_temp REAL,
            min_rainfall REAL, max_rainfall REAL,
            soil_types TEXT NOT NULL, -- Alluvial, Black, Red, Sandy, Clay, Loamy
            growth_duration_days INTEGER,
            expected_yield_qtl_per_acre REAL,
            water_requirement TEXT, -- Low, Medium, High
            profit_potential TEXT, -- Moderate, High, Very High
            description TEXT,
            description_hi TEXT
        )
    ''')

    # 3. Mandi Market Prices Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mandi_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state TEXT NOT NULL,
            district TEXT NOT NULL,
            market_name TEXT NOT NULL,
            commodity TEXT NOT NULL,
            commodity_hi TEXT NOT NULL,
            variety TEXT NOT NULL,
            arrival_date TEXT NOT NULL,
            min_price REAL NOT NULL,
            max_price REAL NOT NULL,
            modal_price REAL NOT NULL,
            msp_price REAL,
            price_change_7d REAL, -- % change
            trend_data TEXT -- JSON array of 7-day prices
        )
    ''')

    # 4. Government Schemes & Subsidies Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS govt_schemes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            name_hi TEXT NOT NULL,
            category TEXT NOT NULL, -- Income Support, Insurance, Solar/Irrigation, Machinery, Credit
            short_desc TEXT NOT NULL,
            short_desc_hi TEXT NOT NULL,
            benefit_amount TEXT NOT NULL,
            benefit_amount_hi TEXT NOT NULL,
            eligibility TEXT NOT NULL,
            eligibility_hi TEXT NOT NULL,
            required_documents TEXT NOT NULL,
            required_documents_hi TEXT NOT NULL,
            application_process TEXT NOT NULL,
            portal_url TEXT,
            tags TEXT
        )
    ''')

    # 5. Community Q&A Forum Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forum_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author_name TEXT NOT NULL,
            location TEXT NOT NULL,
            crop_tag TEXT NOT NULL,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            image_url TEXT,
            upvotes INTEGER DEFAULT 0,
            is_solved INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forum_replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            author_name TEXT NOT NULL,
            author_role TEXT DEFAULT 'Farmer', -- Farmer, Agronomist, Agri-Expert, KVK Officer
            content TEXT NOT NULL,
            is_verified_solution INTEGER DEFAULT 0,
            upvotes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES forum_posts(id)
        )
    ''')

    # 6. Equipment Rental & KVK Centers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agri_centers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            center_name TEXT NOT NULL,
            type TEXT NOT NULL, -- KVK, CHC_Rental, ColdStorage, CertifiedSeedHub
            state TEXT NOT NULL,
            district TEXT NOT NULL,
            contact_person TEXT,
            phone TEXT,
            services_offered TEXT NOT NULL,
            services_offered_hi TEXT NOT NULL,
            hourly_or_unit_rate TEXT,
            address TEXT
        )
    ''')

    conn.commit()
    seed_data(cursor, conn)
    conn.close()
    print("KrishiMitra database initialized successfully!")

def seed_data(cursor, conn):
    # Check if data already exists
    cursor.execute('SELECT COUNT(*) FROM diseases')
    if cursor.fetchone()[0] > 0:
        return

    print("Seeding initial agricultural knowledge database...")

    # --- 1. DISEASES DATA ---
    diseases = [
        (
            "Rice / Paddy", "धान (चावल)",
            "Blast Disease (Magnaporthe oryzae)", "झुलसा रोग (ब्लास्ट)",
            "Magnaporthe oryzae", "Fungal", "Critical",
            "Spindle-shaped elliptical lesions with gray/white center and brown-reddish margins on leaves. Node blast causes black rings and lodging. Neck blast causes empty, broken panicles.",
            "पत्तियों पर नाव या आँख के आकार के धब्बे जिनका केंद्र भूरा-सफेद और किनारा लाल-भूरा होता है। तने की गांठों पर काले छल्ले और बाली का सूखना।",
            "spindle lesion, leaf blast, neck rot, diamond spots, gray center, rice leaf dry, drying panicle",
            "Spray fermented butter-milk (Chaach) with hing (Asafoetida) @ 5L buttermilk in 100L water. Apply Trichoderma harzianum @ 10g/L. Dust wood ash on morning dew.",
            "खट्टी छाछ में हींग मिलाकर (5 लीटर छाछ + 50 ग्राम हींग 100 ली पानी में) छिड़कें। ट्राइकोडर्मा हरजिएनम 10 ग्राम/लीटर का पर्णीय छिड़काव करें।",
            "Tricyclazole 75% WP @ 0.6g/L of water OR Isoprothiolane 40% EC @ 1.5ml/L OR Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1ml/L.",
            "ट्राइसाइक्लाजोल 75% WP @ 0.6 ग्राम प्रति लीटर पानी या आइसोप्रोथियोलेन 40% EC @ 1.5 मिली/लीटर का छिड़काव करें।",
            "Spray during early morning or evening when winds are low. Repeat after 12-15 days if cloudy weather persists.",
            "Use certified resistant varieties (e.g., Pusa Basmati 1637). Avoid excessive Nitrogen fertilizer. Maintain optimal field drainage during cloudy weather.",
            "रोग प्रतिरोधी किस्मों का चयन करें। नाइट्रोजन उर्वरक की अत्यधिक मात्रा से बचें। खेत में पानी की उचित निकासी रखें।",
            "https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?w=600&auto=format&fit=crop&q=80"
        ),
        (
            "Rice / Paddy", "धान (चावल)",
            "Brown Plant Hopper (BPH)", "भूरा फुदका (माहू)",
            "Nilaparvata lugens", "Pest", "High",
            "Hoppers suck sap at base of plant. Leaves turn yellow then orange-brown and dry up completely, creating circular dried patches known as 'Hopper Burn'.",
            "पौधों के आधार पर कीट रस चूसते हैं। पत्तियां पीली पड़कर सूख जाती हैं और खेत में गोल सूखे चट्टे (हॉपर बर्न) दिखाई देते हैं।",
            "hopper burn, yellowing base, tiny brown insects, dried circles in paddy, sap sucking, sticky residue",
            "Alternate wetting and drying (AWD) of fields. Spray 5% Neem Seed Kernel Extract (NSKE) or Neem Oil (10,000 ppm) @ 3ml/L water at base of tillers.",
            "खेत का पानी 2-3 दिन के लिए निकाल दें। 5% नीम गिरी का काढ़ा या नीम तेल 3 मिली प्रति लीटर पानी के हिसाब से तने के निचले भाग पर स्प्रे करें।",
            "Pymetrozine 50% WDG @ 0.6g/L OR Dinotefuran 20% SG @ 0.4g/L OR Triflumezopyrim 10% SC @ 0.5ml/L directed at plant base.",
            "पाइमेट्रोज़ीन 50% WDG @ 0.6 ग्राम/लीटर या डाइनोटेफ्यूरॉन 20% SG @ 0.4 ग्राम/लीटर का पौधों की जड़ों के पास छिड़काव करें।",
            "Direct the spray nozzle towards the base of the tillers. Use minimum 200 liters water per acre.",
            "Avoid excessive synthetic pyrethroids which kill natural spider predators. Plant alleyways (skip rows every 2-3 meters) for aeration.",
            "मित्र कीटों (मकड़ियों) को बचाएं। हवा के संचार के लिए खेत में हर 2-3 मीटर पर खाली गली (रास्ता) छोड़ें।",
            "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&auto=format&fit=crop&q=80"
        ),
        (
            "Wheat", "गेहूँ",
            "Yellow / Stripe Rust", "पीला रतुआ (हल्दी रोग)",
            "Puccinia striiformis", "Fungal", "Critical",
            "Yellow to bright orange pustules arranged in narrow linear stripes along leaf veins. Yellow powdery dust rubs off easily on fingers.",
            "पत्तियों की नसों के समानांतर पीले-नारंगी रंग की धारियाँ और पाउडर जैसा पदार्थ जो छूने पर उंगली पर हल्दी की तरह लगता है।",
            "yellow stripes, yellow powder on leaves, turmeric color dust, linear yellow pustules, cold weather rust",
            "Spray Dashparni Ark @ 25ml/L or fermented Cow Urine (Gomutra) 10% solution + Hing. Dust sulfur in early morning.",
            "दशपर्णी अर्क 25 मिली/लीटर या 10% गोमूत्र घोल में हींग मिलाकर छिड़कें। सुबह ओस के समय गंधक का बुरकाव करें।",
            "Propiconazole 25% EC (Tilt) @ 1ml/L (200ml/acre) OR Tebuconazole 25.9% EC @ 1.25ml/L in 200L water.",
            "प्रोपिकोनाज़ोल 25% EC (टिल्ट) @ 1 मिली/लीटर पानी (200 मिली प्रति एकड़) 200 लीटर पानी में मिलाकर तुरंत छिड़कें।",
            "Spray at first sight of yellow pustules. Do not delay as it spreads rapidly through wind currents.",
            "Sow rust-resistant varieties (HD-2967, HD-3086, DBW-187, DBW-222). Avoid late sowing in sub-mountainous zones.",
            "रतुआ प्रतिरोधी किस्में (DBW-187, DBW-222, HD-3086) लगाएं। समय पर बुवाई करें।",
            "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600&auto=format&fit=crop&q=80"
        ),
        (
            "Cotton", "कपास",
            "Pink Bollworm", "गुलाबी सुंडी",
            "Pectinophora gossypiella", "Pest", "Critical",
            "Rosetted flowers that fail to open properly. Bore holes on developing bolls sealed with frass. Damaged locules, stained lint, and premature boll opening.",
            "गुलाब जैसे मुड़े हुए फूल जो पूरी तरह नहीं खिलते। टिंडों में छेद और अंदर गुलाबी रंग की इल्ली जो बीजों व रेशे को खा जाती है।",
            "pink caterpillar inside boll, rosette flower, damaged cotton lint, premature boll opening, bore hole in boll",
            "Install Pheromone Traps (Phero-traps) with Gossyplure @ 5 traps/acre for monitoring, 10 traps/acre for mass trapping. Release Trichogramma egg parasitoids @ 60,000/acre.",
            "खेत में फेरोमोन ट्रैप (5-10 प्रति एकड़) लगाएं। ट्राइकोग्रामा परजीवी ततैया (60,000 अंडे/एकड़) छोड़ें। 5% नीम तेल का छिड़काव करें।",
            "Profenofos 50% EC @ 2ml/L OR Emamectin Benzoate 5% SG @ 0.5g/L OR Chlorantraniliprole 18.5% SC (Coragen) @ 0.3ml/L.",
            "इमामेक्टिन बेंजोएट 5% SG @ 0.5 ग्राम/लीटर या क्लोरेंट्रानिलिप्रोल 18.5% SC @ 0.3 मिली/लीटर पानी में छिड़कें।",
            "Spray when moth catch exceeds 8 moths/trap/night for 3 consecutive days or 10% rosette flowers.",
            "Destroy crop residue and cotton stalks after harvest. Avoid extending cotton season into ratoon crop.",
            "फसल समाप्ति के बाद खेत में लकड़ियां न छोड़ें और पेड़ी (Ratoon) फसल न लें।",
            "https://images.unsplash.com/photo-1605000797499-95a51c5269ae?w=600&auto=format&fit=crop&q=80"
        ),
        (
            "Tomato", "टमाटर",
            "Early & Late Blight", "अगेती व पछेती झुलसा",
            "Alternaria solani / Phytophthora infestans", "Fungal", "High",
            "Concentric rings ('target board' spots) on lower leaves for Early Blight. Water-soaked dark brown irregular lesions with white mold underneath in cool humid conditions for Late Blight.",
            "पत्तियों पर छल्लेदार गोल भूरे धब्बे (अगेती) या पत्तियों व फलों पर तेजी से फैलने वाले गीले भूरे-काले धब्बे और सफेद फफूंद (पछेती झुलसा)।",
            "target board spots, black leaves, water soaked tomato fruit, concentric rings, leaf mold, rotting green tomato",
            "Spray Trichoderma viride @ 5g/L + Pseudomonas fluorescens @ 5g/L. Spray diluted sour milk with copper water.",
            "ट्राइकोडर्मा विरिडी 5 ग्राम + स्यूडोमोनास 5 ग्राम प्रति लीटर पानी में मिलाकर स्प्रे करें। जीवामृत का छिड़काव करें।",
            "Mancozeb 75% WP @ 2.5g/L OR Metalaxyl 8% + Mancozeb 64% WP (Ridomil Gold) @ 2g/L OR Cymoxanil 8% + Mancozeb 64% @ 2g/L.",
            "मेटालेक्सिल + मैंकोज़ेब (रिडोमिल गोल्ड) @ 2 ग्राम/लीटर या साइमोक्सानिल + मैंकोज़ेब @ 2 ग्राम/लीटर पानी में स्प्रे करें।",
            "Spray immediately at the onset of cool, misty, or overcast weather.",
            "Ensure proper plant staking, prune bottom 12 inches of foliage, and avoid overhead sprinkler irrigation.",
            "टमाटर के पौधों को सहारा (Staking) दें, नीचे की सूखी पत्तियों को काटें और ड्रिप सिंचाई का उपयोग करें।",
            "https://images.unsplash.com/photo-1592841200221-a6898f307baa?w=600&auto=format&fit=crop&q=80"
        ),
        (
            "Tomato", "टमाटर",
            "Leaf Curl Virus (ToLCV)", "पर्ण कुंचन विषाणु (मरोड़िया रोग)",
            "Tomato Leaf Curl Virus (Vectored by Whitefly)", "Viral", "Critical",
            "Upward or downward curling, puckering, thickening and yellowing of leaves. Severe plant stunting, bushy appearance, dropped flowers and no fruit set.",
            "पत्तियां ऊपर या नीचे की ओर मुड़कर कटोरी जैसी हो जाती हैं, छोटी व पीली पड़ जाती हैं। पौधा बौना रह जाता है और फल नहीं लगते।",
            "curled leaves, yellow margins, upward cupping, stunted tomato plant, whitefly infestation, leaf wrinkle",
            "Erect Yellow Sticky Traps @ 15-20 traps/acre to trap Whiteflies. Spray Neem Oil 10,000 ppm @ 3ml/L every 7 days.",
            "खेत में पीले चिपचिपे कार्ड (15-20 प्रति एकड़) लगाएं। नीम तेल (10,000 ppm) 3 मिली/लीटर का साप्ताहिक छिड़काव करें।",
            "Control Whitefly vector: Diafenthiuron 50% WP @ 1.25g/L OR Acetamiprid 20% SP @ 0.3g/L OR Spiromesifen 22.9% SC @ 1ml/L.",
            "सफेद मक्खी की रोकथाम हेतु डायाफेंथियुरॉन 50% WP @ 1.25 ग्राम/लीटर या एसिटामिप्रिड 20% SP @ 0.3 ग्राम/लीटर का छिड़काव करें।",
            "Virus has no direct chemical cure. Roguing (uprooting & burning) infected plants early prevents spread.",
            "Grow vector-resistant hybrids (e.g., US-440, ToLCV tolerant). Use 40-mesh insect net in nursery beds.",
            "शुरुआती संक्रमित पौधों को उखाड़कर गाड़ दें। नर्सरी में 40-मेश कीट जाली का प्रयोग करें।",
            "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=600&auto=format&fit=crop&q=80"
        ),
        (
            "Potato", "आलू",
            "Late Blight of Potato", "आलू का पछेती झुलसा",
            "Phytophthora infestans", "Fungal", "Critical",
            "Water-soaked lesions on leaf tips/margins, rapidly turning purplish-brown/black. White cottony growth on underside of leaves in humid mornings. Tubers develop dry brown rot.",
            "पत्तियों के किनारों पर पानी जैसे धब्बे जो काले पड़ जाते हैं और पत्तियों के नीचे सफेद रुई जैसी फफूंद दिखती है। कंदों में सड़ांध।",
            "potato black leaf, late blight, rotting tuber, white fungal powder underside leaf, rapid blackening",
            "Bordeaux mixture (1%) spray or Copper Oxychloride 50% WP @ 3g/L before canopy closure. Spray wood ash slurry.",
            "बोर्डो मिश्रण (1%) या कॉपर ऑक्सीक्लोराइड 3 ग्राम/लीटर का सुरक्षात्मक छिड़काव करें।",
            "Dimethomorph 50% WP @ 1g/L + Mancozeb @ 2g/L OR Mandipropamid 23.4% SC @ 0.8ml/L OR Fenamidone 10% + Mancozeb 50% WDG @ 2.5g/L.",
            "डाइमेथोमॉर्फ 50% WP @ 1 ग्राम + मैंकोज़ेब @ 2 ग्राम/लीटर या मेंडिप्रोपामाइड @ 0.8 मिली/लीटर का छिड़काव करें।",
            "Spray must cover both upper and lower leaf surfaces thoroughly.",
            "Use certified disease-free seed tubers. High earthing-up to prevent spores washing into soil tubers.",
            "प्रमाणित बीज का उपयोग करें। आलू पर अच्छी मिट्टी चढ़ाएं (Earthing-up) ताकि कंद सुरक्षित रहें।",
            "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=600&auto=format&fit=crop&q=80"
        ),
        (
            "Mustard / Rapeseed", "सरसों",
            "Mustard Aphids (Lipaphis erysimi)", "सरसों का चेपा / माहू",
            "Lipaphis erysimi", "Pest", "High",
            "Masses of small green-yellowish insects covering inflorescence, tender stems, and pods. Leaves curl, dry up; plants produce shriveled seeds or no pods.",
            "कोमल तनों, फूलों और फलियों पर हरे-पीले छोटे कीटों का झुंड। रस चूसने से पौधे कमजोर होकर सूख जाते हैं और फलियां नहीं बनतीं।",
            "green small insects on mustard, sticky stem, aphid cluster, curling mustard leaf, honey dew",
            "Spray solution of crushed garlic + green chili extract @ 10ml/L or 5% Neem seed kernel extract (NSKE).",
            "लहसुन-मिर्च का काढ़ा 10 मिली/लीटर या 5% नीम तेल (3 मिली/ली) का छिड़काव करें।",
            "Dimethoate 30% EC (Rogor) @ 1.7ml/L OR Thiamethoxam 25% WDG @ 0.3g/L OR Imidacloprid 17.8% SL @ 0.5ml/L.",
            "थायमेथोक्सम 25% WDG @ 0.3 ग्राम/लीटर या इमिडाक्लोप्रिड 17.8% SL @ 0.5 मिली/लीटर पानी में छिड़काव करें।",
            "Spray in afternoon hours when pollinators like honeybees are less active.",
            "Early sowing in October helps crop escape heavy aphid buildup in January.",
            "अक्टूबर के प्रथम पखवाड़े में समय पर बुवाई करें ताकि माहू के प्रकोप से बचा जा सके।",
            "https://images.unsplash.com/photo-1508873696983-2df5293cb32b?w=600&auto=format&fit=crop&q=80"
        ),
        (
            "Sugarcane", "गन्ना",
            "Red Rot Disease", "गन्ने का लाल सड़न रोग (कैंसर)",
            "Colletotrichum falcatum", "Fungal", "Critical",
            "Third or fourth leaf from crown turns yellow and withers. Splitting open the stalk reveals dark red internal tissues with crosswise white patches and alcoholic sour odor.",
            "गन्ने की चोटी की पत्तियां पीली पड़कर सूखने लगती हैं। गन्ने को बीच से चीरने पर अंदर का गूदा लाल व बीच-बीच में सफेद चकत्तेदार दिखता है और सिरके जैसी गंध आती है।",
            "red stalk inside, white transverse patches, alcoholic smell sugarcane, dying top leaves, hollow cane",
            "Soak seed setts in Trichoderma viride culture (10g/L) for 30 minutes before planting. Treat soil with bio-fungicides.",
            "बीज गंडों को ट्राइकोडर्मा विरिडी (10 ग्राम/लीटर) के घोल में 30 मिनट भिगोकर बोएं।",
            "Soak setts in Carbendazim 50% WP @ 2g/L (Bavistin) for 15-20 mins before planting. No chemical cure for mature standing crop.",
            "बुवाई से पूर्व गंडों को कार्बेन्डाजिम 50% WP @ 2 ग्राम/लीटर के घोल में उपचारित करें। खड़ी फसल में कोई रासायनिक इलाज संभव नहीं।",
            "Uproot and burn diseased clumps immediately to prevent spreading via irrigation water.",
            "Use red-rot resistant varieties (e.g., Co-0238 alternatives like Co-15023, Co-0118). Practice crop rotation with paddy or green manure.",
            "लाल सड़न प्रतिरोधी किस्मों की बुवाई करें। संक्रमित खेत में कम से कम 2 वर्ष तक गन्ने की फसल न लें।",
            "https://images.unsplash.com/photo-1587593810167-a84920ea0781?w=600&auto=format&fit=crop&q=80"
        ),
        (
            "Chili / Pepper", "मिर्च",
            "Chili Thrips & Mites (Murda Disease)", "मिर्च का मरोड़िया / थ्रिप्स व माइट",
            "Scirtothrips dorsalis / Polyphagotarsonemus latus", "Pest", "High",
            "Thrips cause upward boat-shaped leaf curling with bronzing. Mites cause downward curl (inverted cup), brittle dark green leaves, and elongated petioles.",
            "थ्रिप्स से पत्तियां ऊपर की तरफ नाव जैसी मुड़ती हैं और खुरदरी हो जाती हैं। माइट से पत्तियां नीचे की ओर मुड़कर गहरी हरी व मोटी हो जाती हैं।",
            "upward curling chili, boat shaped leaves, downward cupping, brittle dark leaves, flower drop",
            "Spray Agniastra @ 20ml/L or fermented butter milk + copper wire solution. Blue and Yellow sticky traps @ 20/acre.",
            "अग्निअस्त्र 20 मिली/लीटर या खट्टी छाछ का छिड़काव करें। खेत में 10 नीले और 10 पीले चिपचिपे जाल लगाएं।",
            "For Thrips: Fipronil 5% SC @ 2ml/L OR Spinetoram 11.7% SC @ 1ml/L. For Mites: Spiromesifen 22.9% SC @ 1ml/L OR Diafenthiuron 50% WP @ 1.25g/L.",
            "थ्रिप्स हेतु फिप्रोनिल 5% SC @ 2 मिली/लीटर या स्पाइनेटोरम @ 1 मिली/लीटर। माइट हेतु स्पाइरोमेसिफेन @ 1 मिली/लीटर का छिड़काव करें।",
            "Ensure spray droplets reach under-surface of leaves where pests shelter.",
            "Avoid planting chili near onions or cotton which harbor thrips. Use silver reflective mulching sheets.",
            "सिल्वर-ब्लैक प्लास्टिक मल्चिंग का प्रयोग करें और खेत के चारों ओर मक्का/ज्वार की बफर पट्टी लगाएं।",
            "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&auto=format&fit=crop&q=80"
        ),
        (
            "Maize / Corn", "मक्का",
            "Fall Armyworm (FAW)", "फॉल आर्मीवर्म (सैनिक कीट)",
            "Spodoptera frugiperda", "Pest", "Critical",
            "Pinholes and large ragged shot-holes in whorl leaves. Abundant sawdust-like brownish fecal matter (frass) packed deep inside whorls. Inflorescence & ear damage.",
            "मक्के के पोंगे (Whorl) में छेद और पत्तियों का फटा-कटा होना। पोंगे के अंदर लकड़ी के बुरादे जैसा कीट का मल भरा होना।",
            "shot holes in maize leaves, caterpillar in whorl, sawdust frass, damaged corn cob, chewed leaf edge",
            "Apply neem cake in whorls. Pour sand mixed with lime (9:1) or wood ash directly into central whorls of plants.",
            "पौधे के पोंगे में बारीक सूखी रेत और चूने का मिश्रण (9:1) या नीम की खली का चूर्ण डालें।",
            "Chlorantraniliprole 18.5% SC (Coragen) @ 0.4ml/L OR Spinetoram 11.7% SC @ 0.5ml/L OR Emamectin Benzoate 5% SG @ 0.5g/L directed into whorls.",
            "क्लोरेंट्रानिलिप्रोल 18.5% SC @ 0.4 मिली/लीटर या इमामेक्टिन बेंजोएट @ 0.5 ग्राम/लीटर का घोल बनाकर सीधे पोंगे के अंदर डालें।",
            "Use a backpack sprayer with nozzle directed straight down into the leaf whorl.",
            "Intercrop maize with pulses (Cowpea/Desmodium). Pheromone traps @ 5/acre for early detection.",
            "मक्के के साथ लोबिया या दलहनी फसलों की अंतर-फसली खेती करें। फेरोमोन ट्रैप लगाएं।",
            "https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=600&auto=format&fit=crop&q=80"
        ),
        (
            "Groundnut / Peanut", "मूंगफली",
            "Tikka Disease (Leaf Spot)", "टिक्का रोग (पर्ण धब्बा)",
            "Cercospora arachidicola / Cercosporidium personatum", "Fungal", "Medium",
            "Early leaf spots are circular reddish-brown with yellow halo on upper leaf surface. Late spots are dark brown-black without halo. Causes severe premature defoliation.",
            "पत्तियों पर गोल भूरे-काले धब्बे जिनके चारों ओर पीला छल्ला (Halo) होता है। पुरानी पत्तियां समय से पहले पीली पड़कर झड़ने लगती हैं।",
            "tikka spots, brown circle yellow halo, peanut leaf spots, premature leaf drop groundnut",
            "Spray Panchagavya 3% or Cow dung slurry supernatant + Gomutra. Seed treatment with Trichoderma @ 10g/kg seed.",
            "पंचगव्य (3%) का पर्णीय छिड़काव करें। ट्राइकोडर्मा विरिडी 10 ग्राम प्रति किलो बीज से बीजोपचार करें।",
            "Carbendazim 12% + Mancozeb 63% WP (SAAF) @ 2g/L OR Hexaconazole 5% EC @ 1.5ml/L OR Tebuconazole 25.9% EC @ 1ml/L.",
            "कार्बेन्डाजिम + मैंकोज़ेब (साफ) @ 2 ग्राम/लीटर या हेक्साकोनाज़ोल 5% EC @ 1.5 मिली/लीटर पानी में स्प्रे करें।",
            "Apply at first appearance of spots (around 30-35 days after sowing). Repeat after 15 days.",
            "Practice crop rotation with cereals. Burn or bury infected crop residue after harvest.",
            "फसल चक्र अपनाएं और कटाई के बाद खेत की गहरी जुताई करें।",
            "https://images.unsplash.com/photo-1568644396922-5c3bfae12521?w=600&auto=format&fit=crop&q=80"
        )
    ]

    cursor.executemany('''
        INSERT INTO diseases (
            crop_name, crop_name_hi, disease_name, disease_name_hi,
            scientific_name, category, severity, symptoms, symptoms_hi,
            symptom_tags, organic_treatment, organic_treatment_hi,
            chemical_treatment, chemical_treatment_hi, dosage_guideline,
            prevention, prevention_hi, sample_image
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', diseases)

    # --- 2. CROPS DATA ---
    crops = [
        (
            "Rice / Paddy", "धान", "Cereals", "Kharif",
            80, 120, 40, 60, 40, 60, 5.5, 7.5, 20, 38, 1000, 2500,
            "Clay, Clay Loam, Alluvial", 120, 25.0, "High", "High",
            "Staple cereal crop thriving in warm, humid climates with standing water during vegetative stages.",
            "गर्म और आर्द्र जलवायु में अच्छी जलधारण क्षमता वाली मिट्टी में उगाई जाने वाली प्रमुख खाद्यान्न फसल।"
        ),
        (
            "Wheat", "गेहूँ", "Cereals", "Rabi",
            100, 140, 50, 70, 40, 60, 6.0, 7.5, 12, 25, 350, 600,
            "Loamy, Alluvial, Clay Loam", 130, 22.0, "Medium", "High",
            "Primary winter cereal requiring cool growing season and warm sunny ripening conditions.",
            "सर्दियों की प्रमुख फसल जिसे पकते समय खिली धूप और ठंडे मौसम की आवश्यकता होती है।"
        ),
        (
            "Cotton", "कपास", "Cash Crops", "Kharif",
            90, 130, 45, 65, 45, 70, 6.0, 8.5, 21, 35, 500, 900,
            "Black Soil (Regur), Deep Alluvial", 160, 12.0, "Medium", "Very High",
            "Major commercial fiber crop well suited to deep black soils with good moisture retention.",
            "काली मिट्टी में सबसे उपयुक्त प्रमुख नकदी रेशा फसल जिससे अच्छा मुनाफा प्राप्त होता है।"
        ),
        (
            "Tomato", "टमाटर", "Vegetables", "Year-round",
            120, 160, 60, 90, 80, 120, 6.0, 7.0, 18, 30, 400, 600,
            "Sandy Loam, Loam, Well-drained Red Soil", 100, 180.0, "Medium", "Very High",
            "High-value solanaceous vegetable requiring fertile, well-drained soils and staking support.",
            "उर्वर व जल निकास वाली दोमट मिट्टी में उगाई जाने वाली उच्च मुनाफा देने वाली सब्जी फसल।"
        ),
        (
            "Potato", "आलू", "Vegetables", "Rabi",
            120, 180, 80, 100, 100, 150, 5.2, 6.8, 15, 25, 400, 600,
            "Loose Sandy Loam, Peat, Loamy Soil", 90, 120.0, "Medium", "High",
            "Cool-season tuber crop requiring loose, friable soil for optimal tuber expansion.",
            "भुरभुरी रेतीली दोमट मिट्टी में उच्च कंद उत्पादन देने वाली सर्दियों की प्रमुख सब्जी फसल।"
        ),
        (
            "Sugarcane", "गन्ना", "Cash Crops", "Year-round",
            150, 250, 60, 90, 80, 120, 6.5, 8.0, 24, 38, 1500, 2500,
            "Deep Alluvial, Clayey Loam, Black Soil", 360, 350.0, "High", "Very High",
            "Long-duration cash crop requiring abundant sunshine, high irrigation, and fertile loam soils.",
            "साल भर की नकदी फसल जिसे प्रचुर जल, धूप और गहरी दोमट मिट्टी की आवश्यकता होती है।"
        ),
        (
            "Mustard / Rapeseed", "सरसों", "Oilseeds", "Rabi",
            60, 90, 30, 50, 25, 40, 6.0, 7.5, 10, 25, 250, 450,
            "Sandy Loam, Loamy, Light Alluvial", 115, 8.5, "Low", "High",
            "Drought-hardy winter oilseed crop with low water requirement and high oil yield.",
            "कम पानी में तैयार होने वाली रबी की प्रमुख तिलहनी फसल जो पाले से बचाव चाहती है।"
        ),
        (
            "Chickpea / Gram", "चना", "Pulses", "Rabi",
            20, 40, 40, 60, 20, 35, 6.0, 8.0, 15, 28, 300, 500,
            "Sandy Loam to Clay Loam, Black Soil", 110, 8.0, "Low", "High",
            "Legume crop that fixes atmospheric nitrogen, highly suited for rainfed conditions.",
            "जमीन में नाइट्रोजन स्थिर करने वाली दलहनी फसल, कम सिंचाई में भी बेहतरीन उत्पादन।"
        ),
        (
            "Maize / Corn", "मक्का", "Cereals", "Kharif",
            100, 150, 50, 75, 40, 60, 5.8, 7.5, 20, 32, 500, 800,
            "Well-drained Fertile Loam, Silt Loam", 100, 28.0, "Medium", "High",
            "Queen of cereals with high photosynthetic efficiency and versatile food/feed usage.",
            "तेजी से बढ़ने वाली बहुउपयोगी फसल जिसे जलभराव बिल्कुल पसंद नहीं है।"
        ),
        (
            "Groundnut / Peanut", "मूंगफली", "Oilseeds", "Kharif",
            25, 45, 40, 60, 30, 50, 5.8, 7.2, 22, 32, 450, 750,
            "Well-drained Sandy Loam, Red Sandy Soil", 120, 12.0, "Medium", "High",
            "Nutritious oilseed requiring light loose soil for effortless peg penetration and pod formation.",
            "हल्की भुरभुरी रेतीली दोमट मिट्टी में सुगमता से पेग्स (सूइयां) जमीन में जाने वाली तिलहनी फसल।"
        ),
        (
            "Soybean", "सोयाबीन", "Oilseeds", "Kharif",
            30, 50, 60, 80, 40, 60, 6.0, 7.5, 20, 32, 600, 1000,
            "Black Cotton Soil, Well-drained Loam", 95, 10.0, "Medium", "High",
            "Miracle golden bean rich in protein and oil, ideal for central Indian black soils.",
            "मध्य भारत की काली मिट्टी में प्रोटीन व तेल से भरपूर उच्च मांग वाली खरीफ फसल।"
        ),
        (
            "Onion", "प्याज", "Vegetables", "Rabi",
            80, 120, 40, 60, 60, 90, 6.0, 7.5, 13, 28, 350, 550,
            "Rich Sandy Loam, Alluvial, Red Loam", 130, 120.0, "Medium", "Very High",
            "Crucial kitchen bulb crop demanding high potassium, good organic matter, and regular light irrigations.",
            "पोटाश और जैविक खाद की अच्छी मात्रा चाहने वाली अत्यधिक लाभकारी व्यावसायिक सब्जी।"
        )
    ]

    cursor.executemany('''
        INSERT INTO crops (
            crop_name, crop_name_hi, category, season,
            min_n, max_n, min_p, max_p, min_k, max_k,
            min_ph, max_ph, min_temp, max_temp, min_rainfall, max_rainfall,
            soil_types, growth_duration_days, expected_yield_qtl_per_acre,
            water_requirement, profit_potential, description, description_hi
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', crops)

    # --- 3. MANDI PRICES DATA ---
    mandi_records = [
        ("Punjab", "Ludhiana", "Ludhiana Mandi", "Wheat", "गेहूँ", "PBW-725 / Sharbati", "2026-09-12", 2350, 2550, 2475, 2275, 3.2, json.dumps([2400, 2410, 2425, 2440, 2450, 2465, 2475])),
        ("Punjab", "Khanna", "Khanna Grain Market", "Paddy (Basmati)", "धान (बासमती)", "1121 Pusa", "2026-09-12", 3600, 4100, 3950, 2183, -1.5, json.dumps([4050, 4020, 4000, 3980, 3960, 3940, 3950])),
        ("Haryana", "Karnal", "Karnal Mandi", "Paddy (Basmati)", "धान (बासमती)", "1509 Pusa", "2026-09-12", 3300, 3750, 3600, 2183, 2.1, json.dumps([3520, 3540, 3550, 3570, 3590, 3610, 3600])),
        ("Haryana", "Sirsa", "Sirsa APMC", "Cotton (Kapas)", "कपास (नरमा)", "Medium Staple", "2026-09-12", 6800, 7450, 7200, 6620, 4.5, json.dumps([6900, 6950, 7020, 7080, 7150, 7180, 7200])),
        ("Madhya Pradesh", "Indore", "Indore Mandi", "Soybean", "सोयाबीन", "Yellow JS-9560", "2026-09-12", 4400, 4850, 4680, 4600, 1.8, json.dumps([4590, 4600, 4620, 4640, 4650, 4670, 4680])),
        ("Madhya Pradesh", "Ujjain", "Ujjain Mandi", "Chickpea (Chana)", "चना (देसी)", "Desi Bold", "2026-09-12", 5600, 6200, 5950, 5440, 5.3, json.dumps([5650, 5700, 5750, 5820, 5880, 5920, 5950])),
        ("Maharashtra", "Nashik", "Lasalgaon APMC", "Onion", "प्याज", "Red Medium", "2026-09-12", 1800, 2800, 2450, 0, 8.4, json.dumps([2250, 2280, 2320, 2370, 2400, 2420, 2450])),
        ("Maharashtra", "Nagpur", "Nagpur APMC", "Cotton (Kapas)", "कपास", "H4 / Hybrid", "2026-09-12", 6900, 7500, 7320, 6620, 2.0, json.dumps([7180, 7200, 7230, 7260, 7290, 7300, 7320])),
        ("Maharashtra", "Pune", "Pune Market Yard", "Tomato", "टमाटर", "Hybrid Red", "2026-09-12", 1200, 2200, 1750, 0, -6.5, json.dumps([1900, 1880, 1850, 1820, 1790, 1760, 1750])),
        ("Uttar Pradesh", "Agra", "Agra Mandi", "Potato", "आलू", "Kufri Bahar", "2026-09-12", 1400, 1850, 1680, 0, 4.2, json.dumps([1600, 1620, 1630, 1650, 1660, 1670, 1680])),
        ("Uttar Pradesh", "Meerut", "Meerut APMC", "Sugarcane", "गन्ना", "Co-0238", "2026-09-12", 370, 400, 390, 340, 0.0, json.dumps([390, 390, 390, 390, 390, 390, 390])),
        ("Rajasthan", "Jaipur", "Jaipur Surajpole", "Mustard", "सरसों", "42% Oil Grade", "2026-09-12", 5350, 5800, 5620, 5650, -0.8, json.dumps([5660, 5650, 5640, 5630, 5620, 5610, 5620])),
        ("Rajasthan", "Kota", "Kota Bhamashah Mandi", "Maize", "मक्का", "Yellow Hybrid", "2026-09-12", 2100, 2400, 2280, 2090, 1.5, json.dumps([2240, 2250, 2250, 2260, 2270, 2275, 2280])),
        ("Gujarat", "Rajkot", "Rajkot Mandi", "Groundnut", "मूंगफली", "G-20 Pods", "2026-09-12", 6100, 6850, 6540, 6377, 3.8, json.dumps([6300, 6340, 6390, 6440, 6480, 6510, 6540])),
        ("Andhra Pradesh", "Guntur", "Guntur Mirchi Yard", "Chili (Dry)", "सूखी लाल मिर्च", "Teja / S17", "2026-09-12", 16500, 21500, 19200, 0, 6.7, json.dumps([18000, 18200, 18500, 18700, 18900, 19100, 19200]))
    ]

    cursor.executemany('''
        INSERT INTO mandi_prices (
            state, district, market_name, commodity, commodity_hi,
            variety, arrival_date, min_price, max_price, modal_price,
            msp_price, price_change_7d, trend_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', mandi_records)

    # --- 4. GOVT SCHEMES DATA ---
    schemes = [
        (
            "PM-Kisan Samman Nidhi Yojana", "प्रधानमंत्री किसान सम्मान निधि योजना",
            "Income Support",
            "Direct income transfer of Rs. 6,000 per year in three 4-monthly installments of Rs. 2,000 directly into farmer bank accounts.",
            "सभी पात्र किसान परिवारों को प्रति वर्ष ₹6,000 की प्रत्यक्ष आर्थिक सहायता (₹2,000 की 3 समान किस्तों में बैंक खाते में)।",
            "₹6,000 / year (Direct DBT)", "₹6,000 प्रति वर्ष (सीधे बैंक खाते में)",
            "All landholding farmer families with cultivable land in their names. Excludes institutional landholders, income tax payees, and constitutional post holders.",
            "जिनके नाम पर कृषि योग्य भूमि है। (संवैधानिक पदधारक एवं आयकर दाता किसान पात्र नहीं हैं)।",
            "Aadhaar Card, Land Ownership Papers (Khatauni/Khasra), Active Bank Account linked with NPCI/Aadhaar, Mobile Number.",
            "आधार कार्ड, खतौनी/जमाबंदी नकल, आधार से लिंक बैंक पासबुक, मोबाइल नंबर।",
            "Self-register at pmkisan.gov.in or visit the nearest Common Service Centre (CSC). Complete e-KYC via OTP or biometric.",
            "https://pmkisan.gov.in", "direct cash, income, small farmer, central scheme"
        ),
        (
            "Pradhan Mantri Fasal Bima Yojana (PMFBY)", "प्रधानमंत्री फसल बीमा योजना",
            "Insurance",
            "Comprehensive low-cost insurance cover against non-preventable natural risks (drought, flood, pests, hailstorm, post-harvest losses).",
            "बाढ़, सूखा, कीट आक्रमण व ओलावृष्टि से फसल क्षति पर न्यूनतम प्रीमियम (1.5% से 2%) पर व्यापक बीमा सुरक्षा।",
            "Up to 100% sum insured against crop loss", "फसल नुकसान पर बीमा राशि का 100% तक मुआवजा",
            "All farmers growing notified crops in notified areas (both loanee and non-loanee sharecroppers/tenant farmers).",
            "अधिसूचित क्षेत्रों में अधिसूचित फसल उगाने वाले सभी ऋणी व गैर-ऋणी किसान।",
            "Sowing Certificate (Patwari report), Land Revenue Record (RoR/7-12/Khasra), Aadhaar, Bank Details, Cancelled Cheque.",
            "बुवाई प्रमाण पत्र, भूमि स्वामित्व रिकॉर्ड (खसरा/खतौनी), आधार कार्ड, बैंक खाता विवरण।",
            "Apply online through National Crop Insurance Portal (pmfby.gov.in), through lending banks or nearest CSC within notified cutoff dates.",
            "https://pmfby.gov.in", "insurance, drought, flood, hailstorm, crop loss compensation"
        ),
        (
            "PM-KUSUM (Solar Agricultural Pump Subsidy)", "पीएम-कुसुम सौर ऊर्जा पंप योजना",
            "Solar/Irrigation",
            "Up to 60-90% subsidy for installing standalone off-grid solar agriculture pumps (3HP to 10HP) and solarizing existing grid pumps.",
            "खेतों में 3 से 10 HP के सोलर सिंचाई पंप लगाने हेतु 60% से 90% तक की भारी सरकारी सब्सिडी।",
            "60% to 90% Subsidy on Solar Pump Cost", "सोलर पंप की लागत पर 60% से 90% अनुदान",
            "Individual farmers, water user associations, farmer producer organizations (FPOs) with cultivable land and water source.",
            "व्यक्तिगत किसान, कृषक समूह, एफपीओ जिनके पास भूमि व सिंचाई का जल स्रोत उपलब्ध है।",
            "Land Registry/Khasra, Identity Proof (Aadhaar), Bank Passbook, Ground Water Authority clearance (where applicable).",
            "जमीन के कागजात, आधार कार्ड, बैंक पासबुक, सिंचाई स्रोत विवरण।",
            "Apply via State Renewable Energy Development Agency portal (e.g., UPNEDA, MEDA, RREC) or pmkusum.mnre.gov.in.",
            "https://pmkusum.mnre.gov.in", "solar pump, electricity free irrigation, tubewell, subsidy"
        ),
        (
            "Pradhan Mantri Krishi Sinchayee Yojana (Per Drop More Crop)", "प्रधानमंत्री कृषि सिंचाई योजना (ड्रिप व फव्वारा)",
            "Solar/Irrigation",
            "55% subsidy for Small & Marginal farmers and 45% for other farmers for installing Drip & Sprinkler micro-irrigation systems.",
            "ड्रिप (टपक) व स्प्रिंकलर (फव्वारा) सिंचाई संयंत्र स्थापित करने पर लघु व सीमांत किसानों को 55% तथा अन्य को 45% अनुदान।",
            "45% to 55% Subsidy (Up to ₹50,000/acre)", "45% से 55% तक सब्सिडी (ड्रिप व स्प्रिंकलर पर)",
            "Farmers possessing cultivable land with an assured water source (borewell, pond, canal).",
            "कृषि योग्य भूमि तथा सुनिश्चित जल स्रोत वाले सभी किसान।",
            "Land ownership record, Aadhaar card, Soil and Water test report, Electricity connection / water source proof.",
            "खतौनी, आधार कार्ड, जल स्रोत का प्रमाण, बैंक पासबुक।",
            "Register on State Horticulture / Agriculture Department portal or submit application at district Krishi Bhawan.",
            "https://pmksy.gov.in", "drip irrigation, sprinkler, water saving, micro irrigation subsidy"
        ),
        (
            "Kisan Credit Card (KCC) Scheme", "किसान क्रेडिट कार्ड (केसीसी)",
            "Credit",
            "Concessional agricultural short-term production credit up to Rs. 3 Lakh at an effective subsidized interest rate of just 4% p.a. (with prompt repayment).",
            "खेती की लागत व बीज-खाद हेतु 4% रियायती ब्याज दर पर ₹3 लाख तक का आसान फसली ऋण।",
            "Credit limit up to ₹3,00,000 at 4% interest", "₹3 लाख तक का ऋण मात्र 4% प्रभावी वार्षिक ब्याज पर",
            "Owner cultivators, tenant farmers, oral lessees, and sharecroppers as well as animal husbandry / fishery farmers.",
            "सभी किसान, काश्तकार, पट्टेदार और पशुपालन व मत्स्य पालक।",
            "Application form, Land Record (Khatauni), Aadhaar, PAN card, 2 passport photos, No-dues certificate from local banks.",
            "आवेदन पत्र, भूमि दस्तावेज, आधार कार्ड, पैन कार्ड, पासपोर्ट फोटो।",
            "Fill standard 1-page simplified KCC form at your local bank branch, cooperative society, or apply online via bank portals.",
            "https://myscheme.gov.in/schemes/kcc", "loan, credit, low interest, fertilizer seeds money"
        ),
        (
            "Sub-Mission on Agricultural Mechanization (SMAM)", "कृषि यंत्रीकरण उप-मिशन (ट्रैक्टर व कृषि यंत्र अनुदान)",
            "Machinery",
            "40% to 50% financial assistance for purchasing modern farm equipment: Tractors, Rotavators, Laser Levellers, Seed Drills, Harvesters & Agricultural Drones.",
            "ट्रैक्टर, रोटावेटर, लेजर लैंड लेवलर, कंबाइन और कृषि ड्रोन खरीदने पर 40% से 50% तक की वित्तीय सहायता।",
            "40% to 50% Subsidy on Machinery & Custom Hiring", "कृषि यंत्रों पर 40% से 50% तक सरकारी अनुदान",
            "Individual farmers, Women farmers, SC/ST farmers (given priority), and registered SHGs / FPOs.",
            "सभी वर्ग के किसान (महिला, लघु एवं अनुसूचित जाति/जनजाति किसानों को विशेष प्राथमिकता)।",
            "Aadhaar Card, Land Revenue Papers, Bank Passbook, Caste Certificate (for SC/ST), Machinery quotation from authorized dealer.",
            "आधार कार्ड, जमीन की खतौनी, बैंक पासबुक, जाति प्रमाण पत्र, अधिकृत डीलर का कोटेशन।",
            "Apply online through the State Agriculture Mechanization Portal (agrimachinery.nic.in) during subsidy release windows.",
            "https://agrimachinery.nic.in", "tractor subsidy, rotavator, drone sprayer, farm machinery"
        )
    ]

    cursor.executemany('''
        INSERT INTO govt_schemes (
            name, name_hi, category, short_desc, short_desc_hi,
            benefit_amount, benefit_amount_hi, eligibility, eligibility_hi,
            required_documents, required_documents_hi, application_process,
            portal_url, tags
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', schemes)

    # --- 5. FORUM POSTS DATA ---
    forum_posts = [
        (
            "Urgent: White powder spots under tomato leaves and stems wilting",
            "Ramesh Patel", "Anand, Gujarat", "Tomato", "Disease",
            "Hello experts, I noticed white cottony powdery growth underneath my tomato leaves 3 days ago after heavy rain. Now brown water-soaked lesions are spreading fast across green fruits and stems. What should I spray immediately?",
            "https://images.unsplash.com/photo-1592841200221-a6898f307baa?w=600&auto=format&fit=crop&q=80",
            14, 1
        ),
        (
            "Best fertilizer split schedule for Wheat in Black Soil (2.5 Acres)?",
            "Sukhwinder Singh", "Ludhiana, Punjab", "Wheat", "Fertilizer",
            "Sowing DBW-187 wheat next week. Soil test shows N: Low, P: Medium, K: High. How much DAP and Urea should I apply at sowing vs 1st irrigation crown root stage?",
            None,
            9, 1
        ),
        (
            "Cotton leaves turning yellow and curled upwards like a cup",
            "Balram Yadav", "Akola, Maharashtra", "Cotton", "Pest",
            "My 50-day old cotton crop has severe upward curling in terminal leaves. Underside has tiny pale insects moving around. Is this Thrips or Leaf Curl Virus?",
            "https://images.unsplash.com/photo-1605000797499-95a51c5269ae?w=600&auto=format&fit=crop&q=80",
            8, 0
        )
    ]

    cursor.executemany('''
        INSERT INTO forum_posts (
            title, author_name, location, crop_tag, category,
            content, image_url, upvotes, is_solved
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', forum_posts)

    # Replies
    forum_replies = [
        (
            1, "Dr. Arvind Sharma", "Agronomist (KVK Anand)",
            "This is classical Late Blight (Phytophthora infestans) triggered by high humidity post-rain. Spray Metalaxyl 8% + Mancozeb 64% WP (Ridomil Gold) @ 2g per liter of water immediately. Ensure full spray coverage under the canopy. Avoid evening irrigation.",
            1, 18
        ),
        (
            1, "Kishan Bhai", "Farmer",
            "Along with Ridomil, make sure you prune the bottom infected leaves touching the wet soil to stop spore bounce back. It helped save my crop last year.",
            0, 7
        ),
        (
            2, "Dr. Manpreet Kaur", "Agri-Extension Specialist (PAU)",
            "For 2.5 acres Wheat with Low N and High K: Apply Basal dose at sowing: 130 kg DAP + 30 kg Urea. At 1st Irrigation (21-25 days CRI stage): Top-dress 75 kg Urea. At 2nd Irrigation (45 days Tillering): Top-dress remaining 75 kg Urea. No extra MOP (Potash) required since soil K is already high.",
            1, 12
        ),
        (
            3, "Vikas Deshmukh", "Agronomist",
            "Upward boat-shaped curling indicates Chili Thrips or Cotton Thrips infestation, not Leaf Curl Virus. Spray Fipronil 5% SC @ 2ml/L or Spinetoram 11.7% SC @ 1ml/L. Install Blue sticky traps @ 10 traps per acre to catch adults.",
            0, 6
        )
    ]

    cursor.executemany('''
        INSERT INTO forum_replies (
            post_id, author_name, author_role, content,
            is_verified_solution, upvotes
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', forum_replies)

    # --- 6. AGRI CENTERS DATA ---
    agri_centers = [
        ("Krishi Vigyan Kendra (KVK) Ludhiana", "KVK", "Punjab", "Ludhiana", "Dr. H.S. Dhaliwal", "+91 161 2401960", "Soil & Water Testing, Certified Seed Sales (DBW/HD wheat), Free Agronomist Consultations, Crop Training", "मिट्टी व पानी जांच, प्रमाणित बीज, कृषि वैज्ञानिक सलाह, प्रशिक्षण", "Free Consult / ₹100 Soil Test", "PAU Campus, Ferozepur Road, Ludhiana"),
        ("Krishi Vigyan Kendra (KVK) Indore", "KVK", "Madhya Pradesh", "Indore", "Dr. A.K. Dixit", "+91 731 2470555", "Soybean & Pulse Seed Nursery, Soil Health Card Issuance, Bio-Fertilizer (Rhizobium) Supply", "सोयाबीन बीज, मृदा स्वास्थ्य कार्ड, राइजोबियम जैव-उर्वरक", "Free Consult / ₹50 Bio-pack", "Kasturbagram, Khandwa Road, Indore"),
        ("Krishi Vigyan Kendra (KVK) Nashik", "KVK", "Maharashtra", "Nashik", "Dr. S.B. Patil", "+91 253 2376222", "Grape & Onion Advisory, Pest Trap Distribution, Weather-Linked Spray Advisory", "अंगूर व प्याज परामर्श, फेरोमोन ट्रैप वितरण", "Free Advisory", "Yashwantrao Chavan Maharashtra Open Univ, Nashik"),
        ("CHC Kisan Agri Machinery Hub", "CHC_Rental", "Haryana", "Karnal", "Gurmeet Singh", "+91 98765 43210", "Tractor 55HP (4WD), Laser Land Leveller, Happy Seeder / Super Seeder, Drone Sprayer for Nano Urea", "ट्रैक्टर 55HP, लेजर लेवलर, सुपर सीडर, ड्रोन स्प्रेयर", "₹600 - ₹1200 / Acre", "GT Road, Near Anaj Mandi, Karnal"),
        ("Maharashtra Agro Custom Hiring Center", "CHC_Rental", "Maharashtra", "Nagpur", "Pramod Tayade", "+91 94221 88990", "Combine Harvester, Cotton Stalk Shredder, High-clearance Boom Sprayer, Rotary Tiller", "कंबाइन हार्वेस्टर, कॉटन श्रेडर, बूम स्प्रेयर, रोटावेटर", "₹800 - ₹1800 / Hour", "MIDC Butibori, Nagpur"),
        ("National Cold Chain & Seed Hub", "ColdStorage", "Uttar Pradesh", "Agra", "Manoj Agarwal", "+91 98370 11223", "Controlled Atmosphere Potato Cold Storage, Certified Kufri Seed Tubers Distribution", "आलू कोल्ड स्टोरेज, प्रमाणित कुफरी बीज कंद", "₹120 / Bag / Season", "Fatehabad Road, Agra")
    ]

    cursor.executemany('''
        INSERT INTO agri_centers (
            center_name, type, state, district, contact_person,
            phone, services_offered, services_offered_hi,
            hourly_or_unit_rate, address
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', agri_centers)

    conn.commit()
    print("Agricultural database seeded successfully!")

if __name__ == '__main__':
    init_db()
