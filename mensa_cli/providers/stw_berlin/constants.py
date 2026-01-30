"""Shared literals for the STW Berlin Mensa parser."""

# Comprehensive mappings for allergen and additive codes
ALLERGEN_ADDITIVES = {
    # Additives
    "2": {
        "name": "Schweinefleisch",
        "type": "additive",
        "description": "Schweinefleisch bzw. mit Gelatine vom Schwein",
    },
    "3": {"name": "Alkohol", "type": "additive", "description": "Alkohol"},
    "4": {
        "name": "Geschmacksverstärker",
        "type": "additive",
        "description": "Geschmacksverstärker",
    },
    "5": {"name": "gewachst", "type": "additive", "description": "gewachst"},
    "6": {"name": "konserviert", "type": "additive", "description": "konserviert"},
    "7": {
        "name": "Antioxidationsmittel",
        "type": "additive",
        "description": "Antioxidationsmittel",
    },
    "8": {"name": "Farbstoff", "type": "additive", "description": "Farbstoff"},
    "9": {"name": "Phosphat", "type": "additive", "description": "Phosphat"},
    "10": {"name": "geschwärzt", "type": "additive", "description": "geschwärzt"},
    "12": {
        "name": "Phenylalaninquelle",
        "type": "additive",
        "description": "enthält eine Phenylalaninquelle",
    },
    "13": {"name": "Süßungsmittel", "type": "additive", "description": "Süßungsmittel"},
    "14": {
        "name": "fein_zerkleinertes_fleisch",
        "type": "additive",
        "description": "mit zum Teil fein zerkleinertem Fleischanteil",
    },
    "16": {"name": "koffeinhaltig", "type": "additive", "description": "koffeinhaltig"},
    "17": {"name": "chininhaltig", "type": "additive", "description": "chininhaltig"},
    "19": {"name": "geschwefelt", "type": "additive", "description": "geschwefelt"},
    "20": {
        "name": "abführend_wirken",
        "type": "additive",
        "description": "kann abführend wirken",
    },
    # Allergens
    "21": {
        "name": "Gluten",
        "type": "allergen",
        "description": "Glutenhaltiges Getreide",
    },
    "21a": {"name": "Weizen", "type": "allergen", "description": "Weizen"},
    "21b": {"name": "Roggen", "type": "allergen", "description": "Roggen"},
    "21c": {"name": "Gerste", "type": "allergen", "description": "Gerste"},
    "21d": {"name": "Hafer", "type": "allergen", "description": "Hafer"},
    "21e": {"name": "Dinkel", "type": "allergen", "description": "Dinkel"},
    "21f": {"name": "Kamut", "type": "allergen", "description": "Kamut"},
    "22": {"name": "Krebstiere", "type": "allergen", "description": "Krebstiere"},
    "23": {"name": "Eier", "type": "allergen", "description": "Eier"},
    "24": {"name": "Fisch", "type": "allergen", "description": "Fisch"},
    "25": {"name": "Erdnüsse", "type": "allergen", "description": "Erdnüsse"},
    "26": {
        "name": "Schalenfrüchte",
        "type": "allergen",
        "description": "Schalenfrüchte",
    },
    "26a": {"name": "Mandeln", "type": "allergen", "description": "Mandeln"},
    "26b": {"name": "Haselnuss", "type": "allergen", "description": "Haselnuss"},
    "26c": {"name": "Walnuss", "type": "allergen", "description": "Walnuss"},
    "26d": {"name": "Kaschunuss", "type": "allergen", "description": "Kaschunuss"},
    "28": {"name": "Soja", "type": "allergen", "description": "Soja"},
    "29": {"name": "Senf", "type": "allergen", "description": "Senf"},
    "30": {
        "name": "Milch",
        "type": "allergen",
        "description": "Milch und Milchprodukte (einschließlich Laktose)",
    },
    "31": {
        "name": "Schalenfrüchte",
        "type": "allergen",
        "description": "Schalenfrüchte z.B. Mandeln, Haselnüsse, Walnüsse etc.",
    },
    "32": {"name": "Sellerie", "type": "allergen", "description": "Sellerie"},
    "33": {"name": "Senf", "type": "allergen", "description": "Senf"},
    "34": {"name": "Sesam", "type": "allergen", "description": "Sesam"},
    "35": {
        "name": "Schwefeldioxid",
        "type": "allergen",
        "description": "Schwefeldioxid und Sulfite",
    },
    "36": {"name": "Lupinen", "type": "allergen", "description": "Lupinen"},
    "37": {"name": "Weichtiere", "type": "allergen", "description": "Weichtiere"},
}

# Traffic light mapping
TRAFFIC_LIGHT_MAP = {
    "ampel_gruen": {
        "name": "Grün",
        "description": "Die beste Wahl – je öfter, desto besser",
    },
    "ampel_gelb": {
        "name": "Gelb",
        "description": "Eine gute Wahl – immer mal wieder",
    },
    "ampel_rot": {
        "name": "Rot",
        "description": "Eher selten – am besten mit Grün kombinieren",
    },
}

# Dietary icon mapping
DIETARY_ICON_MAP = {
    "1.png": {
        "name": "Vegetarisch",
        "description": "Gerichte werden ohne Fisch- und Fleischzutaten zubereitet",
    },
    "15.png": {
        "name": "Vegan",
        "description": "Gericht ist aus ausschließlich pflanzlichen Rohstoffen zubereitet",
    },
    # Add more icons as needed from actual HTML analysis
    "18.png": {"name": "Bio", "description": "Biologisch erzeugte Lebensmittel"},
    "38.png": {"name": "Klimaessen", "description": "Klimafreundliches Gericht"},
    "41.png": {
        "name": "Regionales Gericht",
        "description": "Regionale Zutaten verwendet",
    },
    "43.png": {"name": "Fair Trade", "description": "Fair-Trade-Zutaten verwendet"},
}
