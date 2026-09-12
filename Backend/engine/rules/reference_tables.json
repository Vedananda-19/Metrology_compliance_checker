{
  "meta": {
    "source": "The Legal Metrology (Packaged Commodities) Rules, 2011 — GSR 202(E), 7 March 2011 (text as uploaded, incl. GSR 748(E) notes)",
    "base_units": {
      "mass": "g",
      "volume": "ml",
      "length": "cm",
      "area": "cm2",
      "number": "count"
    },
    "band_interpretation": "Band 'A to B' is read as (A, B]; 'up to A' is [0, A]. The First Schedule bands are continuous at every boundary (e.g. 9% of 50 = 4.5 g; 4.5% of 200 = 9 g), so this choice does not change any MPE value. Exception created by the rounding rule itself: just above 1000 g the percentage MPE rounds UP to the next whole gram (1001 g -> 16 g, while 1000 g -> 15 g).",
    "status_note": "These are 2011 values. The Second Schedule was later omitted and several tables amended — see amendment_register in lmpc_2011_rules.json."
  },
  "first_schedule_mpe_weight_volume": {
    "provision": "First Schedule, para 1, Table I; Rule 2(e), Rule 22",
    "unit": "g or ml",
    "bands": [
      {
        "above": 0,
        "up_to": 50,
        "percent": 9.0
      },
      {
        "above": 50,
        "up_to": 100,
        "absolute": 4.5
      },
      {
        "above": 100,
        "up_to": 200,
        "percent": 4.5
      },
      {
        "above": 200,
        "up_to": 300,
        "absolute": 9
      },
      {
        "above": 300,
        "up_to": 500,
        "percent": 3.0
      },
      {
        "above": 500,
        "up_to": 1000,
        "absolute": 15
      },
      {
        "above": 1000,
        "up_to": 10000,
        "percent": 1.5
      },
      {
        "above": 10000,
        "up_to": 15000,
        "absolute": 150
      },
      {
        "above": 15000,
        "up_to": null,
        "percent": 1.0
      }
    ],
    "rounding": {
      "provision": "First Schedule, para 1(2)",
      "declared_up_to_1000": "round percentage-derived MPE to nearest 0.1 g/ml",
      "declared_above_1000": "round percentage-derived MPE up to the next whole g/ml"
    }
  },
  "first_schedule_mpe_length_area_number": {
    "provision": "First Schedule, para 2, Table II",
    "length": {
      "threshold_cm": 1000,
      "percent_up_to_threshold": 2.0,
      "percent_above_threshold": 1.0
    },
    "area": {
      "threshold_cm2": 100000,
      "percent_up_to_threshold": 4.0,
      "percent_above_threshold": 1.0
    },
    "number": {
      "percent": 2.0
    },
    "interpretation_flag": "Text says '2% up to 10 metre and thereafter 1% of declared quantity'. Implemented as: declared <= 10 m -> 2% of declared; declared > 10 m -> 1% of declared. Confirm with Legal Metrology officer (alternative reading is marginal)."
  },
  "rule7_table1_numeral_height_weight_volume": {
    "provision": "Rule 7(2)(i), Table-I",
    "key": "net quantity in g or ml",
    "bands": [
      {
        "above": 0,
        "up_to": 200,
        "normal_mm": 1,
        "embossed_mm": 2
      },
      {
        "above": 200,
        "up_to": 500,
        "normal_mm": 2,
        "embossed_mm": 4
      },
      {
        "above": 500,
        "up_to": null,
        "normal_mm": 4,
        "embossed_mm": 6
      }
    ]
  },
  "rule7_table2_numeral_height_length_area_number": {
    "provision": "Rule 7(2)(ii), Table-II",
    "key": "area of principal display panel in cm2",
    "bands": [
      {
        "above": 0,
        "up_to": 100,
        "normal_mm": 1,
        "embossed_mm": 2
      },
      {
        "above": 100,
        "up_to": 500,
        "normal_mm": 2,
        "embossed_mm": 4
      },
      {
        "above": 500,
        "up_to": 2500,
        "normal_mm": 4,
        "embossed_mm": 6
      },
      {
        "above": 2500,
        "up_to": null,
        "normal_mm": 6,
        "embossed_mm": 6
      }
    ]
  },
  "rule7_letter_size": {
    "provision": "Rule 7(3)",
    "min_letter_height_mm": {
      "normal": 1,
      "embossed": 2
    },
    "min_width_to_height_ratio": 0.3333,
    "ratio_exempt_glyphs": [
      "1",
      "i",
      "I",
      "l"
    ]
  },
  "rule8_quantity_clear_space": {
    "provision": "Rule 8(1) proviso",
    "min_vertical_clearance_x_numeral_height": 1.0,
    "min_horizontal_clearance_x_numeral_height": 2.0,
    "note": "Scale-invariant: can be computed from pixel bounding boxes without knowing physical size."
  },
  "second_schedule_standard_sizes": {
    "provision": "Rule 5 read with Second Schedule",
    "effective_from": "2011-04-01",
    "effective_to": "2022-03-31",
    "effective_to_status": "VERIFY — reported omitted by the 2021/2022 amendments; confirm the exact commencement date from the Gazette notification before relying on it",
    "commodities": {
      "baby_food": {
        "sl": "1",
        "dimension": "mass",
        "explicit": [
          100,
          200,
          300,
          400,
          500,
          600,
          700,
          800,
          900,
          1000,
          2000,
          5000,
          10000
        ]
      },
      "weaning_food": {
        "sl": "2",
        "dimension": "mass",
        "explicit": [
          100,
          200,
          300,
          400,
          500,
          600,
          700,
          800,
          900,
          1000,
          2000,
          5000,
          10000
        ]
      },
      "biscuits": {
        "sl": "3",
        "dimension": "mass",
        "explicit": [
          25,
          50,
          75,
          100,
          150,
          200,
          250,
          300
        ],
        "thereafter_multiples_of": 100,
        "multiples_up_to": 1000
      },
      "bread": {
        "sl": "4",
        "dimension": "mass",
        "explicit": [
          100
        ],
        "thereafter_multiples_of": 100,
        "note": "includes brown bread, excludes bun"
      },
      "butter_margarine_uncanned": {
        "sl": "5",
        "dimension": "mass",
        "explicit": [
          25,
          50,
          100,
          200,
          500,
          1000,
          2000,
          5000
        ],
        "thereafter_multiples_of": 5000
      },
      "cereals_pulses": {
        "sl": "6",
        "dimension": "mass",
        "explicit": [
          100,
          200,
          500,
          1000,
          2000,
          5000
        ],
        "thereafter_multiples_of": 5000
      },
      "coffee": {
        "sl": "7",
        "dimension": "mass",
        "explicit": [
          25,
          50,
          100,
          200,
          250,
          500,
          1000
        ],
        "thereafter_multiples_of": 1000
      },
      "tea": {
        "sl": "8",
        "dimension": "mass",
        "explicit": [
          25,
          50,
          100,
          125,
          250,
          500,
          1000
        ],
        "thereafter_multiples_of": 1000
      },
      "beverage_material": {
        "sl": "9",
        "dimension": "mass",
        "explicit": [
          25,
          50,
          100,
          200,
          500,
          1000
        ],
        "thereafter_multiples_of": 1000
      },
      "edible_oil_ghee": {
        "sl": "10",
        "dimension": "mass_or_volume",
        "explicit": [
          50,
          100,
          200,
          500,
          1000,
          2000,
          3000,
          5000
        ],
        "thereafter_multiples_of": 5000,
        "extra_requirement": "If declared by volume, equivalent mass to be declared in brackets in the same size of letters/numerals"
      },
      "milk_powder": {
        "sl": "11",
        "dimension": "mass",
        "explicit": [
          50,
          100,
          200,
          500,
          1000
        ],
        "thereafter_multiples_of": 500,
        "below_no_restriction": 50
      },
      "detergent_powder": {
        "sl": "12",
        "dimension": "mass",
        "explicit": [
          50,
          100,
          200,
          500,
          700,
          1000,
          1500,
          2000
        ],
        "thereafter_multiples_of": 1000,
        "below_no_restriction": 50
      },
      "rice_flour_atta_rawa_suji": {
        "sl": "13",
        "dimension": "mass",
        "explicit": [
          100,
          200,
          500,
          1000,
          2000,
          5000
        ],
        "thereafter_multiples_of": 5000
      },
      "salt": {
        "sl": "14",
        "dimension": "mass",
        "explicit": [
          50,
          100,
          200,
          500,
          750,
          1000,
          2000,
          5000
        ],
        "thereafter_multiples_of": 5000,
        "below_first_explicit_multiples_of": 10
      },
      "laundry_soap": {
        "sl": "15a",
        "dimension": "mass",
        "explicit": [
          50,
          75,
          100
        ],
        "thereafter_multiples_of": 50
      },
      "detergent_cake": {
        "sl": "15b",
        "dimension": "mass",
        "explicit": [
          50,
          75,
          100,
          125,
          150,
          200,
          250,
          300
        ],
        "thereafter_multiples_of": 100
      },
      "toilet_soap": {
        "sl": "15c",
        "dimension": "mass",
        "explicit": [
          25,
          50,
          75,
          100,
          125,
          150
        ],
        "thereafter_multiples_of": 50
      },
      "soft_drink_non_alcoholic": {
        "sl": "16",
        "dimension": "volume",
        "explicit": [
          65,
          100,
          125,
          150,
          200,
          250,
          300,
          330,
          500,
          750,
          1000,
          1500,
          2000,
          3000,
          4000,
          5000
        ],
        "conditional_sizes": {
          "65": "fruit_based_drink",
          "125": "fruit_based_drink",
          "330": "can"
        }
      },
      "drinking_water": {
        "sl": "17",
        "dimension": "volume",
        "explicit": [
          100,
          150,
          200,
          250,
          300,
          500,
          750,
          1000,
          1500,
          2000,
          3000,
          4000,
          5000
        ]
      },
      "cement_bag": {
        "sl": "18",
        "dimension": "mass",
        "explicit": [
          1000,
          2000,
          5000,
          10000,
          20000,
          25000,
          40000,
          50000
        ],
        "conditional_sizes": {
          "40000": "white_cement"
        }
      },
      "paint_liquid": {
        "sl": "19a",
        "dimension": "volume",
        "explicit": [
          50,
          100,
          200,
          500,
          1000,
          2000,
          3000,
          4000,
          5000
        ],
        "thereafter_multiples_of": 5000
      },
      "paint_paste_solid": {
        "sl": "19b",
        "dimension": "mass",
        "explicit": [
          500,
          1000,
          1500,
          2000,
          3000,
          5000,
          7000
        ],
        "thereafter_multiples_of": 5000
      },
      "paint_base": {
        "sl": "19c",
        "dimension": "volume",
        "explicit": [
          450,
          500,
          900,
          925,
          950,
          975,
          1000,
          3600,
          3700,
          3800,
          3900,
          4000
        ],
        "above_no_restriction": 4000
      }
    }
  },
  "third_schedule_when_packed": {
    "provision": "Rule 11(4) read with Third Schedule",
    "tags": [
      "soap",
      "lotion",
      "cream_non_dairy"
    ],
    "labels": [
      "All kinds of soaps",
      "Lotions",
      "Cream (other than cream of milk)"
    ]
  },
  "fourth_schedule_unit_exceptions": {
    "provision": "Rule 12(2) read with Fourth Schedule",
    "entries": [
      {
        "sl": 1,
        "tag": "aerosol",
        "allowed": [
          [
            "mass"
          ]
        ]
      },
      {
        "sl": 2,
        "tag": "acid_liquid",
        "allowed": [
          [
            "mass"
          ],
          [
            "volume"
          ]
        ]
      },
      {
        "sl": 3,
        "tag": "compressed_gas_non_lpg",
        "allowed": [
          [
            "mass",
            "volume"
          ]
        ],
        "note": "weight AND equivalent volume at stated temperature and pressure"
      },
      {
        "sl": 4,
        "tag": "curd",
        "allowed": [
          [
            "mass"
          ]
        ]
      },
      {
        "sl": 5,
        "tag": "electric_cable",
        "allowed": [
          [
            "length"
          ],
          [
            "mass"
          ]
        ]
      },
      {
        "sl": 6,
        "tag": "electric_wire",
        "allowed": [
          [
            "length"
          ],
          [
            "mass"
          ]
        ]
      },
      {
        "sl": 7,
        "tag": "fencing_wire",
        "allowed": [
          [
            "number"
          ],
          [
            "mass"
          ]
        ]
      },
      {
        "sl": 8,
        "tag": "fruit",
        "allowed": [
          [
            "number"
          ],
          [
            "mass"
          ]
        ]
      },
      {
        "sl": 9,
        "tag": "furnace_oil",
        "allowed": [
          [
            "mass"
          ],
          [
            "volume"
          ]
        ]
      },
      {
        "sl": 10,
        "tag": "non_edible_vegetable_oil",
        "allowed": [
          [
            "mass"
          ],
          [
            "volume"
          ]
        ]
      },
      {
        "sl": 11,
        "tag": "edible_oil_ghee",
        "allowed": [
          [
            "mass"
          ],
          [
            "volume"
          ]
        ]
      },
      {
        "sl": 12,
        "tag": "heavy_residual_fuel_oil",
        "allowed": [
          [
            "mass"
          ]
        ]
      },
      {
        "sl": 13,
        "tag": "industrial_diesel",
        "allowed": [
          [
            "volume"
          ]
        ]
      },
      {
        "sl": 14,
        "tag": "honey_syrup",
        "allowed": [
          [
            "mass"
          ]
        ]
      },
      {
        "sl": 15,
        "tag": "ice_cream",
        "allowed": [
          [
            "volume"
          ]
        ],
        "effective_from": "2011-04-01",
        "effective_to": "2012-06-30"
      },
      {
        "sl": 15,
        "tag": "ice_cream",
        "allowed": [
          [
            "mass"
          ]
        ],
        "effective_from": "2012-07-01",
        "effective_to": null,
        "amended_by": "GSR 748(E) dated 24.10.2011"
      },
      {
        "sl": 16,
        "tag": "liquid_chemical",
        "allowed": [
          [
            "mass"
          ],
          [
            "volume"
          ]
        ]
      },
      {
        "sl": 17,
        "tag": "lpg",
        "allowed": [
          [
            "mass"
          ]
        ]
      },
      {
        "sl": 18,
        "tag": "nails_screws",
        "allowed": [
          [
            "number"
          ],
          [
            "mass"
          ]
        ]
      },
      {
        "sl": 19,
        "tag": "paint_liquid",
        "allowed": [
          [
            "volume"
          ]
        ]
      },
      {
        "sl": 20,
        "tag": "paint_paste_solid",
        "allowed": [
          [
            "mass"
          ]
        ]
      },
      {
        "sl": 21,
        "tag": "sweet_preparation",
        "allowed": [
          [
            "mass"
          ]
        ]
      },
      {
        "sl": 22,
        "tag": "readymade_garment",
        "allowed": [
          [
            "number"
          ]
        ]
      },
      {
        "sl": 23,
        "tag": "sauce",
        "allowed": [
          [
            "mass"
          ]
        ]
      },
      {
        "sl": 24,
        "tag": "tyre_tube",
        "allowed": [
          [
            "number"
          ]
        ]
      },
      {
        "sl": 25,
        "tag": "yarn",
        "allowed": [
          [
            "mass"
          ],
          [
            "length"
          ]
        ]
      },
      {
        "sl": 26,
        "tag": "cosmetic",
        "allowed": [
          [
            "mass"
          ],
          [
            "volume"
          ]
        ],
        "note": "cosmetics incl. creams, shampoo, lotions, perfumes: weight or measure"
      }
    ]
  },
  "rule12_default_dimension_by_state": {
    "provision": "Rule 12(2)(a)-(e)",
    "solid": "mass",
    "semi_solid": "mass",
    "viscous": "mass",
    "solid_liquid_mixture": "mass",
    "liquid": "volume",
    "cubic_measure": "volume",
    "linear": "length",
    "area": "area",
    "countable": "number"
  },
  "rule13_unit_conventions": {
    "provision": "Rule 13(2), 13(3) and proviso",
    "mass": {
      "below_threshold_unit": "g",
      "threshold_base": 1000,
      "at_or_above_unit": "kg",
      "exactly_threshold_may_use": "g"
    },
    "volume": {
      "below_threshold_unit": "ml",
      "threshold_base": 1000,
      "at_or_above_unit": "l",
      "exactly_threshold_may_use": "ml"
    },
    "length": {
      "below_threshold_unit": "cm",
      "threshold_base": 100,
      "at_or_above_unit": "m",
      "exactly_threshold_may_use": "cm"
    },
    "area": {
      "below_threshold_unit": "dm2",
      "threshold_base": 10000,
      "at_or_above_unit": "m2",
      "exactly_threshold_may_use": "dm2"
    },
    "gap_flag": "Rule 13(2)(d)/(e) on cubic volume (m3, dm3, cm3) are internally inconsistent in the text; cubic-measure commodities return REQUIRES_VERIFICATION."
  },
  "units": {
    "provision": "Rule 13(5)(i) — SI units only; Rule 13(4) — no dozen/score/gross",
    "si_unit_aliases": {
      "g": [
        "g",
        "gm",
        "gms",
        "gram",
        "grams"
      ],
      "kg": [
        "kg",
        "kgs",
        "kilogram",
        "kilograms"
      ],
      "mg": [
        "mg"
      ],
      "ml": [
        "ml",
        "mL",
        "millilitre",
        "milliliter"
      ],
      "l": [
        "l",
        "L",
        "ltr",
        "litre",
        "liter",
        "litres",
        "liters"
      ],
      "cm": [
        "cm",
        "centimetre"
      ],
      "m": [
        "m",
        "metre",
        "meter"
      ],
      "mm": [
        "mm"
      ],
      "dm2": [
        "dm2",
        "sq dm"
      ],
      "m2": [
        "m2",
        "sq m",
        "sq. m"
      ],
      "cm2": [
        "cm2",
        "sq cm"
      ],
      "cc": [
        "cc",
        "cm3"
      ],
      "count_2011": [
        "N",
        "U"
      ]
    },
    "to_base": {
      "g": [
        1,
        "mass"
      ],
      "kg": [
        1000,
        "mass"
      ],
      "mg": [
        0.001,
        "mass"
      ],
      "ml": [
        1,
        "volume"
      ],
      "l": [
        1000,
        "volume"
      ],
      "cc": [
        1,
        "volume"
      ],
      "cm": [
        1,
        "length"
      ],
      "m": [
        100,
        "length"
      ],
      "mm": [
        0.1,
        "length"
      ],
      "cm2": [
        1,
        "area"
      ],
      "dm2": [
        100,
        "area"
      ],
      "m2": [
        10000,
        "area"
      ],
      "N": [
        1,
        "number"
      ],
      "U": [
        1,
        "number"
      ]
    },
    "banned_non_si_terms": [
      "oz",
      "fl oz",
      "fl. oz",
      "lb",
      "lbs",
      "pound",
      "ounce",
      "gallon",
      "pint",
      "quart",
      "inch",
      "inches",
      "feet",
      "ft",
      "yard",
      "sq ft",
      "sq. ft"
    ],
    "banned_count_terms": [
      "dozen",
      "score",
      "gross",
      "great gross"
    ]
  },
  "rule12_6_misleading_quantity_terms": {
    "provision": "Rule 12(6)",
    "versions": [
      {
        "effective_from": "2011-04-01",
        "effective_to": "2012-06-30",
        "mode": "enumerated_examples",
        "terms": [
          "minimum",
          "min.",
          "not less than",
          "average",
          "avg.",
          "about",
          "approximately",
          "approx",
          "approx."
        ]
      },
      {
        "effective_from": "2012-07-01",
        "effective_to": null,
        "mode": "any_word_whatsoever",
        "amended_by": "GSR 748(E) dated 24.10.2011",
        "terms": [
          "minimum",
          "min.",
          "not less than",
          "average",
          "avg.",
          "about",
          "approximately",
          "approx",
          "approx.",
          "upto",
          "up to",
          "around",
          "nearly",
          "atleast",
          "at least",
          "extra",
          "bonus",
          "*"
        ],
        "note": "Amended text prohibits ANY word tending to mislead — list is an engineering seed; unrecognised extra words next to quantity -> REQUIRES_VERIFICATION."
      }
    ]
  },
  "rule14_textile_commodities": {
    "provision": "Rule 14",
    "tags": [
      "bed_sheet",
      "hemmed_fabric",
      "dhoti",
      "saree",
      "napkin",
      "pillow_cover",
      "towel",
      "table_cloth",
      "similar_textile"
    ]
  },
  "rule16_sheet_commodities": {
    "provision": "Rule 16",
    "tags": [
      "aluminium_foil",
      "facial_tissue",
      "waxed_paper",
      "toilet_paper",
      "sheet_other"
    ]
  },
  "rule26_exemptions": {
    "provision": "Rule 26",
    "items": {
      "a": "net weight or measure <= 10 g or 10 ml (if sold by weight/measure)",
      "a_proviso": "MRP and net quantity to be declared on 10-20 g / 10-20 ml packages — withdrawn w.e.f. 01.07.2012 (GSR 748(E))",
      "b": "fast food items packed by restaurant/hotel and the like",
      "c": "scheduled and non-scheduled formulations under Drugs (Price Control) Order, 1995",
      "d": "agricultural farm produce in packages above 50 kg"
    }
  },
  "rule3_scope_exclusions": {
    "provision": "Rule 3",
    "max_retail_quantity_base": 25000,
    "cement_fertilizer_bag_max_base": 50000,
    "excluded_consumers": [
      "industrial",
      "institutional"
    ]
  },
  "fifth_schedule_sample_size": {
    "provision": "Rule 19 read with Fifth Schedule",
    "bands": [
      {
        "lot_below": 4000,
        "sample_size": 32
      },
      {
        "lot_above": 4000,
        "sample_size": 80
      }
    ],
    "gap_flag": "Lot size of exactly 4000 is not covered by the text. Engine uses 80 (conservative) and flags it."
  },
  "sixth_schedule_tare": {
    "provision": "Sixth Schedule, Part II, para 3",
    "single_tare_valid_if_tare_le_x_mpe": 0.3,
    "five_tare_spread_le_x_mpe": 0.4
  },
  "rule32_penalties": {
    "provision": "Rule 32",
    "effective_from": "2011-04-01",
    "rules_27_to_31_fine_inr": 4000,
    "other_rules_without_specific_penalty_fine_inr": 2000,
    "status": "AMENDED_VERIFY — later amendments reportedly revised penalty amounts; Act (sections 36 etc.) prescribes penalties for declaration offences"
  },
  "mrp_format": {
    "provision": "Rule 2(m)",
    "patterns_2011": [
      "(?i)(maximum|max\\.?)\\s*retail\\s*price\\s*(rs\\.?|₹|inr)\\s*/?\\s*[0-9][0-9,]*(\\.[0-9]{1,2})?\\s*\\(?\\s*inclusive\\s+of\\s+all\\s+taxes",
      "(?i)m\\.?\\s*r\\.?\\s*p\\.?\\s*[:\\-]?\\s*(rs\\.?|₹|inr)\\s*/?\\s*[0-9][0-9,]*(\\.[0-9]{1,2})?\\s*\\(?\\s*incl(\\.|usive)?\\s*,?\\s*(of\\s+)?all\\s+taxes"
    ],
    "returnable_bottle_pattern": "(?i)m\\.?\\s*r\\.?\\s*p\\.?\\s*[:\\-]?\\s*(rs\\.?|₹|inr)\\s*/?\\s*[0-9]",
    "rounding_allowed_paise_2011": [
      0,
      50
    ],
    "engineering_note": "Rule text uses 'Rs'. The ₹ symbol and 'INR' are accepted as the same currency — a policy choice, flagged in rule notes."
  },
  "engineering_policy": {
    "_note": "NOT LAW. Thresholds chosen by the team; every result that depends on these is labelled threshold_source=ENGINEERING_POLICY.",
    "min_extraction_confidence": 0.85,
    "min_contrast_ratio_for_conspicuous": 3.0,
    "min_ocr_confidence_for_legible": 0.8
  }
}