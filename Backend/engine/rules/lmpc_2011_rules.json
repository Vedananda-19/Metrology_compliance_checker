{
  "rule_set_id": "LMPC-2011-TEXT",
  "rule_set_version": "2026.09-draft1",
  "title": "Legal Metrology (Packaged Commodities) Rules, 2011 — machine-readable rules (as per uploaded 2011 text)",
  "jurisdiction": "India",
  "legal_basis": "GSR 202(E) dated 7 March 2011 under section 52 of the Legal Metrology Act, 2009",
  "authoring_status": "DRAFT — generated from the 2011 text; must be reviewed by a Legal Metrology officer and updated with later amendments before production use",
  "result_states": [
    "COMPLIANT",
    "NON_COMPLIANT",
    "REQUIRES_VERIFICATION",
    "NOT_APPLICABLE",
    "EXEMPT",
    "OBSERVATION"
  ],
  "verification_modes": {
    "LABEL_AUTOMATED": "decidable from OCR/structured facts",
    "VISION_AUTOMATED": "decidable from image analysis (layout, stickers, contrast); probabilistic",
    "MEASUREMENT_REQUIRED": "needs physical measurement or image scale",
    "MANUAL_INSPECTION": "officer must check physically; goes to checklist",
    "MANUAL_INPUT": "officer supplies a value (e.g. selling price)",
    "EXTERNAL_LOOKUP": "needs a registry/database lookup"
  },
  "condition_language": {
    "leaf": "{fact, op, value}  ops: exists, eq, ne, in, not_in, contains, contains_any, matches_regex, gt, gte, lt, lte, between",
    "combinators": "{all:[...]}, {any:[...]}, {not:{...}} — three-valued (Kleene) logic: TRUE / FALSE / UNKNOWN",
    "each": "{each: <array fact>, require: <condition using $item.*>}",
    "macro": "{macro: NAME} — expands from macros",
    "fn": "{fn: name, args} — named domain operator implemented once in the engine (table lookups, unit maths, MPE)",
    "policy_value": "{policy: key} — value from reference_tables.engineering_policy (NOT law)",
    "absent_as": "optional on a leaf: truth value to use when the fact is absent (e.g. no outer wrapper reported -> false). Every use is logged as an ASSUMPTION in the result. Without it: absent fact -> UNKNOWN, except exists-in-applicability -> FALSE, and label/vision checks with extraction.coverage_complete -> FALSE"
  },
  "macros": {
    "RETAIL_SCOPE": {
      "description": "Chapter II applies: retail package, not industrial/institutional, not >25 kg/l (cement & fertilizer bags up to 50 kg stay in scope). Rule 3.",
      "condition": {
        "all": [
          {
            "fact": "package.level",
            "op": "eq",
            "value": "retail"
          },
          {
            "fact": "package.intended_for",
            "op": "not_in",
            "value": [
              "industrial",
              "institutional"
            ],
            "absent_as": true
          },
          {
            "any": [
              {
                "not": {
                  "fact": "net_quantity.dimension",
                  "op": "in",
                  "value": [
                    "mass",
                    "volume"
                  ],
                  "absent_as": false
                }
              },
              {
                "fact": "net_quantity.base_value",
                "op": "lte",
                "value": 25000
              },
              {
                "all": [
                  {
                    "fact": "product.tags",
                    "op": "contains_any",
                    "value": [
                      "cement",
                      "fertilizer"
                    ]
                  },
                  {
                    "fact": "net_quantity.base_value",
                    "op": "lte",
                    "value": 50000
                  }
                ]
              }
            ]
          }
        ]
      }
    },
    "RULE26_EXEMPT": {
      "description": "Whole Rules do not apply (Rule 26 a-d).",
      "condition": {
        "any": [
          {
            "all": [
              {
                "fact": "net_quantity.dimension",
                "op": "in",
                "value": [
                  "mass",
                  "volume"
                ],
                "absent_as": false
              },
              {
                "fact": "net_quantity.base_value",
                "op": "lte",
                "value": 10
              }
            ]
          },
          {
            "fact": "product.tags",
            "op": "contains",
            "value": "fast_food_restaurant_packed"
          },
          {
            "fact": "product.tags",
            "op": "contains",
            "value": "drug_dpco_formulation"
          },
          {
            "all": [
              {
                "fact": "product.tags",
                "op": "contains",
                "value": "agricultural_farm_produce"
              },
              {
                "fact": "net_quantity.base_value",
                "op": "gt",
                "value": 50000
              }
            ]
          }
        ]
      }
    },
    "SMALL_PACKAGE_5CC": {
      "description": "Package capacity 5 cubic cm or less (Rules 7(1), 10(1) proviso, 12(7)).",
      "condition": {
        "fact": "package.capacity_cc",
        "op": "lte",
        "value": 5,
        "absent_as": false
      }
    }
  },
  "fact_vocabulary": {
    "_convention": "Every fact is {value, confidence, evidence:{image_id,bbox}, human_value?, verification_status?}. Engine uses human_value when verification_status == VERIFIED.",
    "inspection.date": "date the inspection is judged under (selects rule versions)",
    "inspection.input_type": "package | advertisement",
    "extraction.coverage_complete": "true when all panels were photographed and OCR quality passed; lets a missing declaration count as ABSENT (not just undetected)",
    "product.tags": "array of commodity classes (food, cosmetic, biscuits, soap, towel, alcoholic_beverage, ...) from classifier/officer",
    "product.physical_state": "solid | semi_solid | viscous | solid_liquid_mixture | liquid | cubic_measure | linear | area | countable",
    "product.common_name": "generic name",
    "product.is_imported": "bool",
    "product.country_of_manufacture": "string",
    "product.packed_in_india": "bool",
    "package.level": "retail | wholesale | export",
    "package.intended_for": "consumer | industrial | institutional",
    "package.capacity_cc": "number",
    "package.is_multi_product": "bool",
    "package.components": "[{name, quantity}]",
    "package.is_component_set": "bool",
    "package.has_outer_wrapper": "bool",
    "package.retail_package_count": "number",
    "manufacturer|packer|importer.name": "string",
    "manufacturer|packer|importer.address": "{text, street, city, state, pin, country}",
    "manufacturer.role_qualified": "bool — 'Manufactured by'/'Packed by'/'Marketed by' present",
    "parties.packer_is_distinct": "bool",
    "net_quantity.text": "raw declaration text",
    "net_quantity.value": "number",
    "net_quantity.unit": "string",
    "net_quantity.dimension": "DERIVED mass|volume|length|area|number",
    "net_quantity.base_value": "DERIVED value in g/ml/cm/cm2/count",
    "net_quantity.clearance": "{above, below, left, right, numeral_height} in pixels (vision)",
    "net_quantity.contrast_ratio | mrp.contrast_ratio": "number (vision)",
    "date_of_manufacture": "{month, year, print_method}",
    "mrp.text": "raw",
    "mrp.value": "number (INR)",
    "mrp.tamper_detected": "bool (vision)",
    "mrp.on_crown_cap_or_bottle": "bool",
    "consumer_care": "{name, designation, address, phone, email}",
    "dimensions": "{text, item_count, pieces_differ, pieces:[{dimensions, rsp}]}",
    "sheets": "{count, dimensions}",
    "containers": "{shape, count, length, width, depth, diameter}",
    "label.full_text": "all OCR text",
    "label.declaration_languages": "array of BCP-47-ish codes: en, hi-Deva, ...",
    "label.stickers": "[{type, covers_mandatory_declaration, revised_mrp, covers_original_mrp}]",
    "label.numeral_height_mm | label.pdp_area_cm2 | label.min_letter_height_mm | label.min_letter_width_ratio": "MEASUREMENT (needs scale)",
    "label.is_embossed": "bool",
    "label.min_declaration_ocr_confidence": "number",
    "label.all_declarations_grouped_on_pdp": "bool (vision)",
    "measurement.actual_net_quantity_base": "number (officer)",
    "measurement.sample_net_quantities_base": "array (officer)",
    "measurement.lot_size": "number",
    "transaction.selling_price": "number (officer)",
    "registry.*": "external lookups",
    "other_law.*": "flags telling the engine another statute governs"
  },
  "rules": [
    {
      "rule_id": "LMPC-R4-001",
      "version": 1,
      "status": "active",
      "title": "Declarations borne on package or on a securely affixed label",
      "category": "MANDATORY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "4",
        "pdf_page": 4,
        "text_excerpt": "no person shall pre-pack ... unless the package ... bears thereon or, a label is securely affixed thereto such declarations as are required"
      },
      "verification_mode": "MANUAL_INSPECTION",
      "severity": "HIGH",
      "applies_when": {
        "macro": "RETAIL_SCOPE"
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fact": "label.affixation",
        "op": "in",
        "value": [
          "printed_on_package",
          "securely_affixed_label"
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Declarations are not printed on the package or on a securely affixed label.",
      "evidence_facts": [
        "label.affixation"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R5-001",
      "version": 1,
      "status": "active",
      "title": "Commodity packed in a Second Schedule standard quantity",
      "category": "STANDARD_PACK_SIZE",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "5 + Second Schedule",
        "pdf_page": 4,
        "text_excerpt": "The commodities specified in the Second Schedule shall be packed ... in such standard quantities as are specified in that Schedule"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fn": "is_second_schedule_commodity",
            "args": {}
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fn": "standard_pack_size_ok",
        "args": {}
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Declared quantity is not a standard pack size for this commodity under the Second Schedule.",
      "evidence_facts": [
        "net_quantity"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": "2022-03-31",
      "amendment_status": "OMITTED_LATER_VERIFY_DATE",
      "notes": "Rule 5 and the Second Schedule were reportedly omitted by the 2021/2022 amendments. effective_to must be confirmed from the Gazette."
    },
    {
      "rule_id": "LMPC-R5-002",
      "version": 1,
      "status": "active",
      "title": "Non-standard size package carries 'Not a standard pack size' declaration",
      "category": "STANDARD_PACK_SIZE",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "5 proviso",
        "pdf_page": 4,
        "text_excerpt": "a declaration that 'Not a standard pack size under the Legal Metrology (Packaged Commodities) Rules, 2011' ... shall be made prominently"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "MEDIUM",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fn": "is_second_schedule_commodity",
            "args": {}
          },
          {
            "not": {
              "fn": "standard_pack_size_ok",
              "args": {}
            }
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fact": "label.full_text",
        "op": "matches_regex",
        "value": "(?i)(not\\s+a\\s+standard\\s+pack\\s+size|non[\\s-]*standard\\s+size)"
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Non-standard pack size without the required 'Not a standard pack size' declaration.",
      "evidence_facts": [
        "label.full_text"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": "2012-06-30",
      "amendment_status": "WITHDRAWN_IN_TEXT",
      "notes": "Proviso withdrawn w.e.f. 01.07.2012 vide GSR 748(E) dated 24.10.2011 (noted in the PDF). After withdrawal, a non-standard size is simply non-compliant under LMPC-R5-001."
    },
    {
      "rule_id": "LMPC-SCH2-10-001",
      "version": 1,
      "status": "active",
      "title": "Edible oil/ghee declared by volume also declares equivalent mass in brackets",
      "category": "QUANTITY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "Second Schedule, Sl. 10",
        "pdf_page": 30,
        "text_excerpt": "If the net quantity is declared by volume, then the equivalent quantity in terms of mass to be declared in brackets in same size of letters/numerals"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "MEDIUM",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "product.tags",
            "op": "contains",
            "value": "edible_oil_ghee"
          },
          {
            "fact": "net_quantity.dimension",
            "op": "eq",
            "value": "volume"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fact": "net_quantity.mass_equivalent",
        "op": "exists"
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Edible oil declared by volume without equivalent mass in brackets.",
      "evidence_facts": [
        "net_quantity",
        "net_quantity.mass_equivalent"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": "2022-03-31",
      "amendment_status": "OMITTED_LATER_VERIFY_DATE"
    },
    {
      "rule_id": "LMPC-R6-1a-001",
      "version": 1,
      "status": "active",
      "title": "Name of manufacturer declared",
      "category": "MANDATORY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "6(1)(a), 10(1)",
        "pdf_page": 5,
        "text_excerpt": "the name and address of the manufacturer ... shall be mentioned"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "CRITICAL",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "not": {
              "macro": "SMALL_PACKAGE_5CC"
            }
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        },
        {
          "exemption_ref": "6(1)(a) Expl. III / 6(1)(d) 1st proviso",
          "when": {
            "fact": "product.tags",
            "op": "contains",
            "value": "food"
          },
          "reason": "Food packages: requirement governed by food law (PFA Act 1954 in the text; now Food Safety and Standards Act, 2006 and its labelling regulations). Route to FSS rule pack."
        }
      ],
      "check": {
        "fact": "manufacturer.name",
        "op": "exists"
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Manufacturer name was not detected on the package.",
      "evidence_facts": [
        "manufacturer.name"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R6-1a-002",
      "version": 1,
      "status": "active",
      "title": "Complete address of manufacturer declared",
      "category": "MANDATORY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "6(1)(a), 10(1) Explanation",
        "pdf_page": 11,
        "text_excerpt": "'complete address' means ... the name of the street, number (if any) ... and either the name of the city and State ... or the Postal Index Number [PIN] Code"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "not": {
              "macro": "SMALL_PACKAGE_5CC"
            }
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        },
        {
          "exemption_ref": "6(1)(a) Expl. III / 6(1)(d) 1st proviso",
          "when": {
            "fact": "product.tags",
            "op": "contains",
            "value": "food"
          },
          "reason": "Food packages: requirement governed by food law (PFA Act 1954 in the text; now Food Safety and Standards Act, 2006 and its labelling regulations). Route to FSS rule pack."
        },
        {
          "exemption_ref": "Rule 28",
          "when": {
            "fact": "registry.manufacturer_short_address_registered",
            "op": "eq",
            "value": true
          },
          "reason": "Registered shorter address may be used (Rule 28)."
        }
      ],
      "check": {
        "all": [
          {
            "fact": "manufacturer.address.text",
            "op": "exists"
          },
          {
            "any": [
              {
                "fact": "manufacturer.address.pin",
                "op": "matches_regex",
                "value": "^[1-9][0-9]{5}$"
              },
              {
                "all": [
                  {
                    "fact": "manufacturer.address.city",
                    "op": "exists"
                  },
                  {
                    "fact": "manufacturer.address.state",
                    "op": "exists"
                  }
                ]
              },
              {
                "all": [
                  {
                    "fact": "manufacturer.address.country",
                    "op": "ne",
                    "value": "India"
                  },
                  {
                    "fact": "manufacturer.address.city",
                    "op": "exists"
                  }
                ]
              }
            ]
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Manufacturer address is missing or incomplete (needs city + State, or a valid 6-digit PIN).",
      "evidence_facts": [
        "manufacturer.address"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT",
      "notes": "Foreign manufacturer: city + country accepted (PIN/State are Indian concepts) — interpretation, confirm with officer."
    },
    {
      "rule_id": "LMPC-R6-1a-003",
      "version": 1,
      "status": "active",
      "title": "Name and address of packer where packer is not the manufacturer",
      "category": "MANDATORY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "6(1)(a), 10(1)",
        "pdf_page": 5,
        "text_excerpt": "where the manufacturer is not the packer, the name and address of the manufacturer and packer"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "parties.packer_is_distinct",
            "op": "eq",
            "value": true,
            "absent_as": false
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        },
        {
          "exemption_ref": "6(1)(a) Expl. III / 6(1)(d) 1st proviso",
          "when": {
            "fact": "product.tags",
            "op": "contains",
            "value": "food"
          },
          "reason": "Food packages: requirement governed by food law (PFA Act 1954 in the text; now Food Safety and Standards Act, 2006 and its labelling regulations). Route to FSS rule pack."
        }
      ],
      "check": {
        "all": [
          {
            "fact": "packer.name",
            "op": "exists"
          },
          {
            "fact": "packer.address.text",
            "op": "exists"
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Package indicates a separate packer but packer name/address was not found.",
      "evidence_facts": [
        "packer"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R6-1a-004",
      "version": 1,
      "status": "active",
      "title": "Name and address of importer on imported packages",
      "category": "MANDATORY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "6(1)(a), 10(1)",
        "pdf_page": 5,
        "text_excerpt": "for any imported package the name and address of the importer shall be mentioned"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "CRITICAL",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "product.is_imported",
            "op": "eq",
            "value": true
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "all": [
          {
            "fact": "importer.name",
            "op": "exists"
          },
          {
            "fact": "importer.address.text",
            "op": "exists"
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Imported package without importer name and address.",
      "evidence_facts": [
        "importer"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R10-1-001",
      "version": 1,
      "status": "active",
      "title": "Foreign-made commodity packed in India shows Indian packer/importer on PDP",
      "category": "MANDATORY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "10(1) second proviso",
        "pdf_page": 11,
        "text_excerpt": "where any commodity manufactured outside India is packed in India, the package shall also contain on the principal display panel the name and complete address of the packer or the importer in India"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "product.country_of_manufacture",
            "op": "ne",
            "value": "India"
          },
          {
            "fact": "product.packed_in_india",
            "op": "eq",
            "value": true,
            "absent_as": false
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "any": [
          {
            "all": [
              {
                "fact": "packer.name",
                "op": "exists"
              },
              {
                "fact": "packer.address.country",
                "op": "eq",
                "value": "India"
              }
            ]
          },
          {
            "all": [
              {
                "fact": "importer.name",
                "op": "exists"
              },
              {
                "fact": "importer.address.country",
                "op": "eq",
                "value": "India"
              }
            ]
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Commodity made abroad and packed in India lacks Indian packer/importer name and address.",
      "evidence_facts": [
        "packer",
        "importer"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R10-1-002",
      "version": 1,
      "status": "active",
      "title": "Packages <=5 cc carry an identifying mark of manufacturer/packer/importer",
      "category": "MANDATORY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "10(1) first proviso, 12(7)",
        "pdf_page": 11,
        "text_excerpt": "for packages of capacity 5 cubic cm or less, it shall be a sufficient compliance ... if a mark or inscription which would enable the consumer to identify the manufacturer or packer or the importer ... is made"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "macro": "SMALL_PACKAGE_5CC"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "any": [
          {
            "fact": "manufacturer.identifying_mark",
            "op": "exists"
          },
          {
            "fact": "manufacturer.name",
            "op": "exists"
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Small package (<=5 cc) has no mark identifying the manufacturer/packer/importer.",
      "evidence_facts": [
        "manufacturer.identifying_mark"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R10-2-001",
      "version": 1,
      "status": "active",
      "title": "Party name is the actual corporate / registered business name",
      "category": "MANDATORY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "10(2)",
        "pdf_page": 11,
        "text_excerpt": "The name of the manufacturer or packer or importer shall be the actual corporate name, or if not incorporated, the name under which the business is conducted"
      },
      "verification_mode": "EXTERNAL_LOOKUP",
      "severity": "MEDIUM",
      "applies_when": {
        "macro": "RETAIL_SCOPE"
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        },
        {
          "exemption_ref": "6(1)(a) Expl. III / 6(1)(d) 1st proviso",
          "when": {
            "fact": "product.tags",
            "op": "contains",
            "value": "food"
          },
          "reason": "Food packages: requirement governed by food law (PFA Act 1954 in the text; now Food Safety and Standards Act, 2006 and its labelling regulations). Route to FSS rule pack."
        }
      ],
      "check": {
        "fact": "registry.corporate_name_matches",
        "op": "eq",
        "value": true
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Declared name does not match the registered corporate/business name.",
      "evidence_facts": [
        "manufacturer.name"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT",
      "notes": "Needs MCA / LM registration lookup; without it the rule returns REQUIRES_VERIFICATION."
    },
    {
      "rule_id": "LMPC-R6-1a-EXPL1",
      "version": 1,
      "status": "active",
      "title": "Name without 'manufactured by'/'packed by' is presumed to be the manufacturer",
      "category": "LIABILITY_INFERENCE",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "6(1)(a) Explanation I & II",
        "pdf_page": 5,
        "text_excerpt": "If any name and address of a company is mentioned on the label without any qualifying words 'manufactured by' or 'packed by', it shall be presumed that such name and address shall be that of the manufacturer"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "INFO",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "manufacturer.name",
            "op": "exists"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fact": "manufacturer.role_qualified",
        "op": "eq",
        "value": true
      },
      "outcome_on_fail": "OBSERVATION",
      "fail_message": "No 'Manufactured by'/'Packed by'/'Marketed by' qualifier — the first named party is presumed manufacturer for liability.",
      "evidence_facts": [
        "manufacturer.name"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R6-1b-001",
      "version": 1,
      "status": "active",
      "title": "Common or generic name of the commodity declared",
      "category": "MANDATORY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "6(1)(b)",
        "pdf_page": 5,
        "text_excerpt": "The common or generic names of the commodity contained in the package"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "macro": "RETAIL_SCOPE"
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fact": "product.common_name",
        "op": "exists"
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Common/generic name of the commodity was not detected.",
      "evidence_facts": [
        "product.common_name"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R6-1b-002",
      "version": 1,
      "status": "active",
      "title": "Multi-product package names each product with its number or quantity",
      "category": "MANDATORY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "6(1)(b)",
        "pdf_page": 5,
        "text_excerpt": "in case of packages with more than one product, the name and number or quantity of each product shall be mentioned"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "package.is_multi_product",
            "op": "eq",
            "value": true,
            "absent_as": false
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "all": [
          {
            "fact": "package.components",
            "op": "exists"
          },
          {
            "each": "package.components",
            "require": {
              "all": [
                {
                  "fact": "$item.name",
                  "op": "exists"
                },
                {
                  "fact": "$item.quantity",
                  "op": "exists"
                }
              ]
            }
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Multi-product package does not state name and number/quantity of each product.",
      "evidence_facts": [
        "package.components"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R6-1c-001",
      "version": 1,
      "status": "active",
      "title": "Net quantity declared in standard unit or by number",
      "category": "QUANTITY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "6(1)(c)",
        "pdf_page": 5,
        "text_excerpt": "The net quantity, in terms of the standard unit of weight or measure ... or ... the number of the commodity contained in the package"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "CRITICAL",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "not": {
              "macro": "SMALL_PACKAGE_5CC"
            }
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "all": [
          {
            "fact": "net_quantity.value",
            "op": "exists"
          },
          {
            "fact": "net_quantity.unit",
            "op": "exists"
          },
          {
            "fact": "net_quantity.dimension",
            "op": "in",
            "value": [
              "mass",
              "volume",
              "length",
              "area",
              "number"
            ]
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Net quantity declaration not detected or not in a recognised standard unit.",
      "evidence_facts": [
        "net_quantity"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R12-7-001",
      "version": 1,
      "status": "active",
      "title": "Packages <=5 cc: quantity on tag/card/tape that cannot be removed without opening",
      "category": "QUANTITY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "12(7)",
        "pdf_page": 13,
        "text_excerpt": "the declaration of quantity shall be made on a tag, card, tape, or any other similar device affixed to the container in such a manner that it cannot be removed without opening the container"
      },
      "verification_mode": "MANUAL_INSPECTION",
      "severity": "MEDIUM",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "macro": "SMALL_PACKAGE_5CC"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "all": [
          {
            "fact": "net_quantity.value",
            "op": "exists"
          },
          {
            "fact": "label.quantity_tag_tamper_evident",
            "op": "eq",
            "value": true
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Quantity on <=5 cc package is missing or not on a tamper-evident tag/card/tape.",
      "evidence_facts": [
        "net_quantity"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R11-2-001",
      "version": 1,
      "status": "active",
      "title": "'When packed' qualifier used only for Third Schedule commodities",
      "category": "QUANTITY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "11(2)-(4) + Third Schedule",
        "pdf_page": 12,
        "text_excerpt": "the declaration of quantity on such package shall not be qualified by the words 'when packed' or the like ... [except] as specified in the Third Schedule"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "MEDIUM",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "net_quantity.text",
            "op": "exists"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "any": [
          {
            "not": {
              "fact": "net_quantity.text",
              "op": "matches_regex",
              "value": "(?i)when\\s+packed|at\\s+the\\s+time\\s+of\\s+packing"
            }
          },
          {
            "fact": "product.tags",
            "op": "contains_any",
            "value": [
              "soap",
              "lotion",
              "cream_non_dairy"
            ]
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Quantity is qualified by 'when packed' but the commodity is not in the Third Schedule (soaps, lotions, non-dairy cream).",
      "evidence_facts": [
        "net_quantity.text"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R12-2-001",
      "version": 1,
      "status": "active",
      "title": "Quantity expressed in the correct kind of unit (mass/volume/length/area/number)",
      "category": "QUANTITY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "12(2) + Fourth Schedule",
        "pdf_page": 12,
        "text_excerpt": "the declaration of quantity shall be in terms of the unit of (a) mass, if the commodity is solid, semi-solid, viscous or a mixture of solid and liquid; ... (d) volume, if the commodity is liquid"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "MEDIUM",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "net_quantity.dimension",
            "op": "exists"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fn": "unit_dimension_allowed",
        "args": {}
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Quantity is declared in a unit type not permitted for this commodity (Rule 12(2) / Fourth Schedule).",
      "evidence_facts": [
        "net_quantity",
        "product.physical_state"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R12-6-001",
      "version": 1,
      "status": "active",
      "title": "Quantity declaration has no misleading qualifiers ('about', 'minimum', 'approx.' ...)",
      "category": "QUANTITY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "12(6)",
        "pdf_page": 13,
        "text_excerpt": "words or expressions like-'minimum', 'not less than', 'average', 'about', approximately' or other words of a similar nature"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "net_quantity.text",
            "op": "exists"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fn": "no_misleading_quantity_terms",
        "args": {
          "table_version": "2011-04-01"
        }
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Net quantity declaration contains a misleading qualifier.",
      "evidence_facts": [
        "net_quantity.text"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": "2012-06-30",
      "amendment_status": "AMENDED_IN_TEXT"
    },
    {
      "rule_id": "LMPC-R12-6-001",
      "version": 2,
      "status": "active",
      "title": "Quantity declaration has no word of any sort that may mislead as to quantity",
      "category": "QUANTITY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "12(6) as amended",
        "pdf_page": 13,
        "text_excerpt": "The declaration of quantity under these Rules shall not contain any word or expression of any sort, whatsoever, which tends to create or likely to create an exaggerated, misleading or inadequate expression"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "net_quantity.text",
            "op": "exists"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fn": "no_misleading_quantity_terms",
        "args": {
          "table_version": "2012-07-01"
        }
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Net quantity declaration contains a word that may mislead as to quantity.",
      "evidence_facts": [
        "net_quantity.text"
      ],
      "threshold_source": "LAW",
      "effective_from": "2012-07-01",
      "effective_to": null,
      "amendment_status": "AMENDED_BY_GSR_748E_2011",
      "notes": "Known terms -> NON_COMPLIANT; any other unexplained word adjacent to the quantity -> REQUIRES_VERIFICATION."
    },
    {
      "rule_id": "LMPC-R13-2-001",
      "version": 1,
      "status": "active",
      "title": "Correct unit for the magnitude (g below 1 kg, kg from 1 kg; ml/l; cm/m; dm2/m2)",
      "category": "QUANTITY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "13(2), 13(3)",
        "pdf_page": 13,
        "text_excerpt": "When expressing a quantity less than (a) one kilogram, the unit of weight shall be the gram ... equal to or more than (a) one kilogram, the unit of weight shall be the kilogram"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "LOW",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "net_quantity.dimension",
            "op": "in",
            "value": [
              "mass",
              "volume",
              "length",
              "area"
            ]
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fn": "unit_convention_ok",
        "args": {}
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Unit does not follow Rule 13 conventions (e.g. '1500 g' should be '1.5 kg'; '0.5 kg' should be '500 g').",
      "evidence_facts": [
        "net_quantity"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R13-4-001",
      "version": 1,
      "status": "active",
      "title": "No 'dozen', 'score', 'gross' or 'great gross'",
      "category": "QUANTITY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "13(4)",
        "pdf_page": 14,
        "text_excerpt": "No number called the dozen, score, gross, great gross or the like shall be specified or indicated on any package."
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "MEDIUM",
      "applies_when": {
        "macro": "RETAIL_SCOPE"
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "not": {
          "fact": "label.full_text",
          "op": "matches_regex",
          "value": "(?i)\\b(dozen|score|great\\s+gross|gross(?!\\s*(wt|weight)))\\b"
        }
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Package uses dozen/score/gross style numbers.",
      "evidence_facts": [
        "label.full_text"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT",
      "notes": "Regex ignores 'gross wt/weight'. 'score' may appear in marketing copy — expect some false positives; restrict to declaration panel text in production."
    },
    {
      "rule_id": "LMPC-R13-5-001",
      "version": 1,
      "status": "active",
      "title": "Net quantity uses SI units only",
      "category": "QUANTITY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "13(5)(i)",
        "pdf_page": 14,
        "text_excerpt": "No system of units other than the International System of Units shall be used in furnishing the net quantity"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "MEDIUM",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "net_quantity.text",
            "op": "exists"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fn": "si_units_only",
        "args": {}
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Net quantity declaration uses non-SI units (oz, lb, fl oz, inch ...).",
      "evidence_facts": [
        "net_quantity.text"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R13-5-002",
      "version": 1,
      "status": "active",
      "title": "Items sold by number use symbol N or U",
      "category": "QUANTITY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "13(5)(ii)",
        "pdf_page": 14,
        "text_excerpt": "For items sold by number the symbol should be N or U."
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "LOW",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "net_quantity.dimension",
            "op": "eq",
            "value": "number"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fact": "net_quantity.unit",
        "op": "in",
        "value": [
          "N",
          "U"
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Count declared without the N or U symbol.",
      "evidence_facts": [
        "net_quantity"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AMENDED_LATER_VERIFY",
      "notes": "Later amendment reportedly allows number/unit/piece/pair/set etc. Add version 2 once the Gazette date is confirmed."
    },
    {
      "rule_id": "LMPC-R6-1d-001",
      "version": 1,
      "status": "active",
      "title": "Month and year of manufacture / pre-packing / import declared",
      "category": "DATE_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "6(1)(d)",
        "pdf_page": 5,
        "text_excerpt": "The month and year in which the commodity is manufactured or pre-packed or imported shall be mentioned in the package."
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "macro": "RETAIL_SCOPE"
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        },
        {
          "exemption_ref": "6(1)(a) Expl. III / 6(1)(d) 1st proviso",
          "when": {
            "fact": "product.tags",
            "op": "contains",
            "value": "food"
          },
          "reason": "Food packages: requirement governed by food law (PFA Act 1954 in the text; now Food Safety and Standards Act, 2006 and its labelling regulations). Route to FSS rule pack."
        },
        {
          "exemption_ref": "6(1)(d) 2nd proviso",
          "when": {
            "fact": "product.tags",
            "op": "contains",
            "value": "seeds_certified"
          },
          "reason": "Seeds labelled and certified under the Seeds Act, 1966."
        },
        {
          "exemption_ref": "6(1)(d) 4th proviso",
          "when": {
            "fact": "product.tags",
            "op": "contains",
            "value": "cosmetic"
          },
          "reason": "Cosmetics: Drugs and Cosmetics Rules, 1945 apply."
        },
        {
          "exemption_ref": "6(1)(g)(A)(i)",
          "when": {
            "fact": "product.tags",
            "op": "contains_any",
            "value": [
              "bidi",
              "incense_sticks"
            ]
          },
          "reason": "Bidis and incense sticks exempt from month/year declaration."
        },
        {
          "exemption_ref": "6(1)(g)(A)(ii)",
          "when": {
            "fact": "product.tags",
            "op": "contains",
            "value": "lpg_domestic_psu_14_2_or_5kg"
          },
          "reason": "Domestic LPG cylinders 14.2 kg / 5 kg bottled by a PSU."
        }
      ],
      "check": {
        "all": [
          {
            "fact": "date_of_manufacture.month",
            "op": "exists"
          },
          {
            "fact": "date_of_manufacture.year",
            "op": "exists"
          },
          {
            "fact": "date_of_manufacture.month",
            "op": "between",
            "value": [
              1,
              12
            ]
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Month and year of manufacture/pre-packing/import not detected.",
      "evidence_facts": [
        "date_of_manufacture"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AMENDED_LATER_VERIFY",
      "notes": "Later amendments reportedly changed which date must be declared (manufacture vs import) — add version 2 after verification."
    },
    {
      "rule_id": "LMPC-R6-1d-002",
      "version": 1,
      "status": "active",
      "title": "Month/year not applied by rubber stamp (proviso permitting it withdrawn)",
      "category": "DATE_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "6(1)(d) 3rd proviso (withdrawn)",
        "pdf_page": 6,
        "text_excerpt": "a manufacturer may indicate the month and year using a rubber stamp without overwriting. * Provisio will stand withdrawn wef 01.07.2012"
      },
      "verification_mode": "VISION_AUTOMATED",
      "severity": "LOW",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "date_of_manufacture.month",
            "op": "exists"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        },
        {
          "exemption_ref": "6(1)(a) Expl. III / 6(1)(d) 1st proviso",
          "when": {
            "fact": "product.tags",
            "op": "contains",
            "value": "food"
          },
          "reason": "Food packages: requirement governed by food law (PFA Act 1954 in the text; now Food Safety and Standards Act, 2006 and its labelling regulations). Route to FSS rule pack."
        },
        {
          "exemption_ref": "6(1)(d) 2nd proviso",
          "when": {
            "fact": "product.tags",
            "op": "contains",
            "value": "seeds_certified"
          },
          "reason": "Seeds labelled and certified under the Seeds Act, 1966."
        },
        {
          "exemption_ref": "6(1)(d) 4th proviso",
          "when": {
            "fact": "product.tags",
            "op": "contains",
            "value": "cosmetic"
          },
          "reason": "Cosmetics: Drugs and Cosmetics Rules, 1945 apply."
        },
        {
          "exemption_ref": "6(1)(g)(A)(i)",
          "when": {
            "fact": "product.tags",
            "op": "contains_any",
            "value": [
              "bidi",
              "incense_sticks"
            ]
          },
          "reason": "Bidis and incense sticks exempt from month/year declaration."
        },
        {
          "exemption_ref": "6(1)(g)(A)(ii)",
          "when": {
            "fact": "product.tags",
            "op": "contains",
            "value": "lpg_domestic_psu_14_2_or_5kg"
          },
          "reason": "Domestic LPG cylinders 14.2 kg / 5 kg bottled by a PSU."
        }
      ],
      "check": {
        "fact": "date_of_manufacture.print_method",
        "op": "ne",
        "value": "rubber_stamp"
      },
      "outcome_on_fail": "REQUIRES_VERIFICATION",
      "fail_message": "Date appears to be rubber-stamped; express permission for this was withdrawn from 01.07.2012.",
      "evidence_facts": [
        "date_of_manufacture"
      ],
      "threshold_source": "LAW",
      "effective_from": "2012-07-01",
      "effective_to": null,
      "amendment_status": "INTERPRETATION_FLAG",
      "notes": "Withdrawal of a permissive proviso is not an explicit prohibition — so the engine flags for officer review rather than failing."
    },
    {
      "rule_id": "LMPC-R6-1e-001",
      "version": 1,
      "status": "active",
      "title": "Retail sale price (MRP) declared",
      "category": "PRICE_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "6(1)(e)",
        "pdf_page": 6,
        "text_excerpt": "the retail sale price of the package"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "CRITICAL",
      "applies_when": {
        "macro": "RETAIL_SCOPE"
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        },
        {
          "exemption_ref": "6(1)(g)(C)(i)",
          "when": {
            "fact": "product.tags",
            "op": "contains",
            "value": "bidi"
          },
          "reason": "No retail sale price required on bidi packages."
        },
        {
          "exemption_ref": "6(1)(g)(C)(ii)",
          "when": {
            "fact": "product.tags",
            "op": "contains",
            "value": "lpg_domestic_apm"
          },
          "reason": "Domestic LPG cylinder under Administered Price Mechanism."
        },
        {
          "exemption_ref": "6(1)(e) proviso",
          "when": {
            "all": [
              {
                "fact": "product.tags",
                "op": "contains",
                "value": "alcoholic_beverage"
              },
              {
                "fact": "other_law.state_excise_prescribes_rsp",
                "op": "eq",
                "value": true
              }
            ]
          },
          "reason": "Alcoholic beverages: State Excise law governs RSP where it provides for it."
        }
      ],
      "check": {
        "all": [
          {
            "fact": "mrp.value",
            "op": "exists"
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Retail sale price (MRP) not detected.",
      "evidence_facts": [
        "mrp"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT",
      "notes": "For alcoholic beverages with other_law.state_excise_prescribes_rsp unknown, the exemption evaluates UNKNOWN -> a missing MRP returns REQUIRES_VERIFICATION instead of NON_COMPLIANT."
    },
    {
      "rule_id": "LMPC-R2m-001",
      "version": 1,
      "status": "active",
      "title": "MRP printed in the prescribed form ('MRP Rs ... inclusive of all taxes')",
      "category": "PRICE_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "2(m), 8(2)",
        "pdf_page": 3,
        "text_excerpt": "'Maximum or Max. retail price Rs/ .......inclusive of all taxes or in the form MRP Rs/ .........incl., of all taxes"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "MEDIUM",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "mrp.text",
            "op": "exists"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        },
        {
          "exemption_ref": "6(1)(g)(C)(i)",
          "when": {
            "fact": "product.tags",
            "op": "contains",
            "value": "bidi"
          },
          "reason": "No retail sale price required on bidi packages."
        },
        {
          "exemption_ref": "6(1)(g)(C)(ii)",
          "when": {
            "fact": "product.tags",
            "op": "contains",
            "value": "lpg_domestic_apm"
          },
          "reason": "Domestic LPG cylinder under Administered Price Mechanism."
        },
        {
          "exemption_ref": "6(1)(e) proviso",
          "when": {
            "all": [
              {
                "fact": "product.tags",
                "op": "contains",
                "value": "alcoholic_beverage"
              },
              {
                "fact": "other_law.state_excise_prescribes_rsp",
                "op": "eq",
                "value": true
              }
            ]
          },
          "reason": "Alcoholic beverages: State Excise law governs RSP where it provides for it."
        }
      ],
      "check": {
        "any": [
          {
            "fn": "mrp_format_ok",
            "args": {}
          },
          {
            "all": [
              {
                "fact": "product.tags",
                "op": "contains",
                "value": "soft_drink_returnable_bottle"
              },
              {
                "fact": "mrp.on_crown_cap_or_bottle",
                "op": "eq",
                "value": true,
                "absent_as": false
              },
              {
                "fn": "mrp_format_ok",
                "args": {
                  "returnable": true
                }
              }
            ]
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "MRP is not in the prescribed form (missing 'inclusive of all taxes' or MRP/Rs wording).",
      "evidence_facts": [
        "mrp.text"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AMENDED_LATER_VERIFY",
      "notes": "Rule 8(2): returnable soft-drink bottles may show just 'MRP Rs....' on crown cap/bottle. Currency symbol ₹/INR accepted as policy."
    },
    {
      "rule_id": "LMPC-R2m-002",
      "version": 1,
      "status": "active",
      "title": "MRP rounded as prescribed (paise part only 00 or 50)",
      "category": "PRICE_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "2(m)",
        "pdf_page": 3,
        "text_excerpt": "fraction of less than fifty paisa to be rounded off to the preceding rupees and fraction of above 50 paise and up to 95 paise to the rounded off to fifty paise"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "LOW",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "mrp.value",
            "op": "exists"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        },
        {
          "exemption_ref": "6(1)(g)(C)(i)",
          "when": {
            "fact": "product.tags",
            "op": "contains",
            "value": "bidi"
          },
          "reason": "No retail sale price required on bidi packages."
        },
        {
          "exemption_ref": "6(1)(g)(C)(ii)",
          "when": {
            "fact": "product.tags",
            "op": "contains",
            "value": "lpg_domestic_apm"
          },
          "reason": "Domestic LPG cylinder under Administered Price Mechanism."
        },
        {
          "exemption_ref": "6(1)(e) proviso",
          "when": {
            "all": [
              {
                "fact": "product.tags",
                "op": "contains",
                "value": "alcoholic_beverage"
              },
              {
                "fact": "other_law.state_excise_prescribes_rsp",
                "op": "eq",
                "value": true
              }
            ]
          },
          "reason": "Alcoholic beverages: State Excise law governs RSP where it provides for it."
        }
      ],
      "check": {
        "fn": "mrp_rounding_ok",
        "args": {}
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "MRP paise part is not rounded to 00 or 50 as required by Rule 2(m).",
      "evidence_facts": [
        "mrp.value"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AMENDED_LATER_VERIFY",
      "notes": "Text is silent on fractions above 95 paise; engine treats .00 and .50 as the only valid endings."
    },
    {
      "rule_id": "LMPC-R6-3-001",
      "version": 1,
      "status": "active",
      "title": "No sticker used to alter or make a mandatory declaration",
      "category": "LABEL_INTEGRITY",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "6(3)",
        "pdf_page": 7,
        "text_excerpt": "It shall not be permissible to affix individual stickers on the package for altering or making declaration required under these rules"
      },
      "verification_mode": "VISION_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "label.stickers",
            "op": "exists"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "each": "label.stickers",
        "require": {
          "any": [
            {
              "fact": "$item.covers_mandatory_declaration",
              "op": "eq",
              "value": false
            },
            {
              "fact": "$item.type",
              "op": "eq",
              "value": "mrp_reduction"
            }
          ]
        }
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "A sticker is used to make or alter a mandatory declaration.",
      "evidence_facts": [
        "label.stickers"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R6-3-002",
      "version": 1,
      "status": "active",
      "title": "MRP-reduction sticker shows a LOWER MRP and does not cover the original MRP",
      "category": "LABEL_INTEGRITY",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "6(3) proviso",
        "pdf_page": 7,
        "text_excerpt": "for reducing the Maximum Retail Price (MRP), a sticker with the revised lower MRP (inclusive of all taxes) may be affixed and the same shall not cover the MRP declaration made by the manufacturer"
      },
      "verification_mode": "VISION_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fn": "has_sticker_type",
            "args": {
              "type": "mrp_reduction"
            }
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fn": "mrp_reduction_stickers_ok",
        "args": {}
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "MRP sticker is higher than the printed MRP or hides the original MRP.",
      "evidence_facts": [
        "label.stickers",
        "mrp"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R18-5-001",
      "version": 1,
      "status": "active",
      "title": "Printed MRP not obliterated, smudged or altered",
      "category": "LABEL_INTEGRITY",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "18(5), 18(6)",
        "pdf_page": 17,
        "text_excerpt": "No wholesale dealer or retail dealer or other person shall obliterate, smudge or alter the retail sale price"
      },
      "verification_mode": "VISION_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "mrp.text",
            "op": "exists"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fact": "mrp.tamper_detected",
        "op": "eq",
        "value": false
      },
      "outcome_on_fail": "REQUIRES_VERIFICATION",
      "fail_message": "MRP area shows signs of obliteration/alteration.",
      "evidence_facts": [
        "mrp"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT",
      "notes": "Vision tamper signal is probabilistic -> officer confirms."
    },
    {
      "rule_id": "LMPC-R18-2-001",
      "version": 1,
      "status": "active",
      "title": "Sale not above retail sale price",
      "category": "TRADE_PRACTICE",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "18(2)",
        "pdf_page": 16,
        "text_excerpt": "No retail dealer or other person ... shall make any sale of any commodity in packed form at a price exceeding the retail sale price"
      },
      "verification_mode": "MANUAL_INPUT",
      "severity": "CRITICAL",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "transaction.selling_price",
            "op": "exists"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fn": "selling_price_within_mrp",
        "args": {}
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Commodity sold above the MRP.",
      "evidence_facts": [
        "transaction.selling_price",
        "mrp.value"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R6-1f-001",
      "version": 1,
      "status": "active",
      "title": "Dimensions declared where size of the commodity is relevant",
      "category": "DIMENSION_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "6(1)(f), 12(4), 15",
        "pdf_page": 6,
        "text_excerpt": "Where the sizes of the commodity contained in the package are relevant, the dimensions of the commodity ... shall be mentioned"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "MEDIUM",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "product.tags",
            "op": "contains_any",
            "value": [
              "size_relevant",
              "price_depends_on_dimensions"
            ]
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fact": "dimensions.text",
        "op": "exists"
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Size-relevant commodity without dimension declaration.",
      "evidence_facts": [
        "dimensions"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT",
      "notes": "Whether size is 'relevant' is a classification decision — keep it as an explicit tag set by the classifier or officer."
    },
    {
      "rule_id": "LMPC-R14-001",
      "version": 1,
      "status": "active",
      "title": "Textile goods declare number and finished dimensions",
      "category": "DIMENSION_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "14",
        "pdf_page": 14,
        "text_excerpt": "Where a package contains commodities like bed-sheets, hemmed fabric materials, dhoties, sarees, napkins, pillow-covers, towels, table cloths ... the number and the dimensions of finished size ... shall also be declared"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fn": "has_any_tag_from_table",
            "args": {
              "table": "rule14_textile_commodities"
            }
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "all": [
          {
            "fact": "dimensions.item_count",
            "op": "exists"
          },
          {
            "fact": "dimensions.text",
            "op": "exists"
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Textile package without number of pieces and finished dimensions.",
      "evidence_facts": [
        "dimensions"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R14-002",
      "version": 1,
      "status": "active",
      "title": "Textile set with pieces of different sizes declares dimensions and price of each piece",
      "category": "DIMENSION_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "14 first proviso",
        "pdf_page": 14,
        "text_excerpt": "where the package contains more than one piece of different dimensions, the package shall also contain a declaration as to the dimensions and the retail sale price of each such piece"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fn": "has_any_tag_from_table",
            "args": {
              "table": "rule14_textile_commodities"
            }
          },
          {
            "fact": "dimensions.pieces_differ",
            "op": "eq",
            "value": true,
            "absent_as": false
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "all": [
          {
            "fact": "dimensions.pieces",
            "op": "exists"
          },
          {
            "each": "dimensions.pieces",
            "require": {
              "all": [
                {
                  "fact": "$item.dimensions",
                  "op": "exists"
                },
                {
                  "fact": "$item.rsp",
                  "op": "exists"
                }
              ]
            }
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Mixed-size textile set does not state dimensions and price for each piece.",
      "evidence_facts": [
        "dimensions.pieces"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R14-003",
      "version": 1,
      "status": "active",
      "title": "Each individual textile piece marked with dimensions and price",
      "category": "DIMENSION_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "14 second proviso",
        "pdf_page": 14,
        "text_excerpt": "the dimensions of the commodities and the sale price thereof shall also be marked on each individual piece"
      },
      "verification_mode": "MANUAL_INSPECTION",
      "severity": "MEDIUM",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fn": "has_any_tag_from_table",
            "args": {
              "table": "rule14_textile_commodities"
            }
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fact": "inspection.each_piece_marked",
        "op": "eq",
        "value": true
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Individual pieces are not marked with dimensions and price.",
      "evidence_facts": [],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R16-001",
      "version": 1,
      "status": "active",
      "title": "Sheet products declare number of usable sheets and sheet dimensions",
      "category": "DIMENSION_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "16",
        "pdf_page": 15,
        "text_excerpt": "In the case of a package containing sheets like aluminum foil, facial tissues, waxed paper, toilet paper ... a statement as to the number of usable sheets ... and the dimensions of each such sheet"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fn": "has_any_tag_from_table",
            "args": {
              "table": "rule16_sheet_commodities"
            }
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "all": [
          {
            "fact": "sheets.count",
            "op": "exists"
          },
          {
            "fact": "sheets.dimensions",
            "op": "exists"
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Sheet product without number of usable sheets and dimensions of each sheet.",
      "evidence_facts": [
        "sheets"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R17-001",
      "version": 1,
      "status": "active",
      "title": "Container-type commodities declare count followed by dimensions",
      "category": "DIMENSION_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "17(i)-(iii)",
        "pdf_page": 15,
        "text_excerpt": "for bag-type commodities, the number of bags ... followed by linear dimensions; ... square, oblong ... length, width, and if required, depth; ... circular ... diameter"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "MEDIUM",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "product.tags",
            "op": "contains_any",
            "value": [
              "container_bag",
              "container_rectangular",
              "container_round"
            ]
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fn": "container_declaration_ok",
        "args": {}
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Container-type commodity lacks count and the dimensions required for its shape.",
      "evidence_facts": [
        "containers"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R17-002",
      "version": 1,
      "status": "active",
      "title": "Capacity claims of containers included in the quantity declaration",
      "category": "DIMENSION_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "17(iv)",
        "pdf_page": 15,
        "text_excerpt": "when the use of a container is related by label references ... to the capability of the container to hold a specific quantity ... such references shall be included in the declaration of quantity"
      },
      "verification_mode": "MANUAL_INSPECTION",
      "severity": "LOW",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "containers.label_mentions_capacity",
            "op": "eq",
            "value": true,
            "absent_as": false
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fact": "containers.capacity_in_quantity_declaration",
        "op": "eq",
        "value": true
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Capacity reference not included in the quantity declaration.",
      "evidence_facts": [
        "containers"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R6-2-001",
      "version": 1,
      "status": "active",
      "title": "Consumer complaint contact: name, address and telephone number",
      "category": "CONSUMER_CARE",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "6(2)",
        "pdf_page": 7,
        "text_excerpt": "Every package shall bear the name, address, telephone number, e mail address, if available, of the person who can be or the office which can be, contacted, in case of consumer complaints."
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "macro": "RETAIL_SCOPE"
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "all": [
          {
            "any": [
              {
                "fact": "consumer_care.name",
                "op": "exists"
              },
              {
                "fact": "consumer_care.designation",
                "op": "exists"
              }
            ]
          },
          {
            "fact": "consumer_care.address",
            "op": "exists"
          },
          {
            "fact": "consumer_care.phone",
            "op": "matches_regex",
            "value": "^[+0-9()\\-\\s]{8,20}$"
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Consumer-care contact (name/office, address and telephone) not fully declared.",
      "evidence_facts": [
        "consumer_care"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AMENDED_LATER_VERIFY",
      "notes": "2011 text read as: e-mail optional ('if available'). Later amendment reportedly made e-mail mandatory — see draft LMPC-R6-2-001 v2."
    },
    {
      "rule_id": "LMPC-R6-2-001",
      "version": 2,
      "status": "draft",
      "title": "Consumer complaint contact incl. e-mail address",
      "category": "CONSUMER_CARE",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "6(2) as amended",
        "pdf_page": 7,
        "text_excerpt": "[amended text to be pasted from Gazette]"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "macro": "RETAIL_SCOPE"
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "all": [
          {
            "any": [
              {
                "fact": "consumer_care.name",
                "op": "exists"
              },
              {
                "fact": "consumer_care.designation",
                "op": "exists"
              }
            ]
          },
          {
            "fact": "consumer_care.address",
            "op": "exists"
          },
          {
            "fact": "consumer_care.phone",
            "op": "matches_regex",
            "value": "^[+0-9()\\-\\s]{8,20}$"
          },
          {
            "fact": "consumer_care.email",
            "op": "matches_regex",
            "value": "^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$"
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Consumer-care contact incomplete (name/office, address, telephone, e-mail).",
      "evidence_facts": [
        "consumer_care"
      ],
      "threshold_source": "LAW",
      "effective_from": "2018-01-01",
      "effective_to": null,
      "amendment_status": "DRAFT_PENDING_GAZETTE_VERIFICATION"
    },
    {
      "rule_id": "LMPC-R6-5-001",
      "version": 1,
      "status": "active",
      "title": "Multi-unit single commodity: declarations on main package with info about accompanying packages",
      "category": "MANDATORY_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "6(5)",
        "pdf_page": 7,
        "text_excerpt": "the declaration ... shall appear on the main package and such package shall also carry information about the other accompanying packages"
      },
      "verification_mode": "MANUAL_INSPECTION",
      "severity": "MEDIUM",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "package.is_component_set",
            "op": "eq",
            "value": true,
            "absent_as": false
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "any": [
          {
            "fact": "package.main_package_lists_components",
            "op": "eq",
            "value": true
          },
          {
            "fact": "package.each_component_labelled_and_main_intimates",
            "op": "eq",
            "value": true
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Component set does not carry required declarations/intimation on the main package.",
      "evidence_facts": [],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R7-2-001",
      "version": 1,
      "status": "active",
      "title": "Numeral height meets Table-I (quantity by weight/volume)",
      "category": "LEGIBILITY",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "7(2)(i) Table-I",
        "pdf_page": 8,
        "text_excerpt": "[Table summary] Up to 200 g/ml: 1 mm (2 mm if blown/embossed); above 200 up to 500: 2 mm (4); above 500: 4 mm (6)"
      },
      "verification_mode": "MEASUREMENT_REQUIRED",
      "severity": "MEDIUM",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "net_quantity.dimension",
            "op": "in",
            "value": [
              "mass",
              "volume"
            ]
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        },
        {
          "exemption_ref": "7(4)",
          "when": {
            "fact": "other_law.governs_label_size",
            "op": "eq",
            "value": true,
            "absent_as": false
          },
          "reason": "Same information required by another law (e.g. food, drugs, cosmetics, medical devices) — Rule 7(1)-(3) not applied."
        }
      ],
      "check": {
        "fn": "numeral_height_ok",
        "args": {
          "table": "rule7_table1_numeral_height_weight_volume"
        }
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Numerals in the declaration are smaller than the Table-I minimum.",
      "evidence_facts": [
        "label.numeral_height_mm"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT",
      "notes": "Needs physical scale: derive mm from a known package dimension or a reference card in the photo. Without scale -> REQUIRES_VERIFICATION. Table amended later — verify."
    },
    {
      "rule_id": "LMPC-R7-2-002",
      "version": 1,
      "status": "active",
      "title": "Numeral height meets Table-II (quantity by length/area/number)",
      "category": "LEGIBILITY",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "7(2)(ii) Table-II",
        "pdf_page": 9,
        "text_excerpt": "[Table summary] PDP up to 100 cm2: 1 mm (2); above 100 up to 500: 2 (4); above 500 up to 2500: 4 (6); above 2500: 6 (6)"
      },
      "verification_mode": "MEASUREMENT_REQUIRED",
      "severity": "MEDIUM",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "net_quantity.dimension",
            "op": "in",
            "value": [
              "length",
              "area",
              "number"
            ]
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        },
        {
          "exemption_ref": "7(4)",
          "when": {
            "fact": "other_law.governs_label_size",
            "op": "eq",
            "value": true,
            "absent_as": false
          },
          "reason": "Same information required by another law (e.g. food, drugs, cosmetics, medical devices) — Rule 7(1)-(3) not applied."
        }
      ],
      "check": {
        "fn": "numeral_height_ok",
        "args": {
          "table": "rule7_table2_numeral_height_length_area_number"
        }
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Numerals in the declaration are smaller than the Table-II minimum.",
      "evidence_facts": [
        "label.numeral_height_mm",
        "label.pdp_area_cm2"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R7-3-001",
      "version": 1,
      "status": "active",
      "title": "Letter height >= 1 mm (>= 2 mm if blown/embossed) and width >= 1/3 height",
      "category": "LEGIBILITY",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "7(3)",
        "pdf_page": 8,
        "text_excerpt": "The height of letters in the declaration shall not be less than 1 mm height and when blown, formed, molded, embossed or perforated, the height of letters shall not be less than 2 mm. Provided that the width of the letter or numeral shall not be less than one third of its height"
      },
      "verification_mode": "MEASUREMENT_REQUIRED",
      "severity": "LOW",
      "applies_when": {
        "macro": "RETAIL_SCOPE"
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        },
        {
          "exemption_ref": "7(4)",
          "when": {
            "fact": "other_law.governs_label_size",
            "op": "eq",
            "value": true,
            "absent_as": false
          },
          "reason": "Same information required by another law (e.g. food, drugs, cosmetics, medical devices) — Rule 7(1)-(3) not applied."
        }
      ],
      "check": {
        "fn": "letter_size_ok",
        "args": {}
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Declaration letters are smaller/narrower than Rule 7(3) allows.",
      "evidence_facts": [
        "label.min_letter_height_mm",
        "label.min_letter_width_ratio"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R8-1-001",
      "version": 1,
      "status": "active",
      "title": "All declarations appear on the principal display panel",
      "category": "PLACEMENT",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "8(1), 2(h)",
        "pdf_page": 9,
        "text_excerpt": "Every declaration required to be made under these rules shall appear on the principal display panel."
      },
      "verification_mode": "VISION_AUTOMATED",
      "severity": "MEDIUM",
      "applies_when": {
        "macro": "RETAIL_SCOPE"
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fact": "label.all_declarations_grouped_on_pdp",
        "op": "eq",
        "value": true
      },
      "outcome_on_fail": "REQUIRES_VERIFICATION",
      "fail_message": "Mandatory declarations appear scattered outside the principal display panel.",
      "evidence_facts": [
        "label.layout"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT",
      "notes": "PDP may be grouped at one place, or pre-printed info in one place and online-printed info (date, batch) in another (Rule 2(h))."
    },
    {
      "rule_id": "LMPC-R8-1-002",
      "version": 1,
      "status": "active",
      "title": "Clear space around the quantity declaration",
      "category": "PLACEMENT",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "8(1) proviso",
        "pdf_page": 9,
        "text_excerpt": "free from printed information (a) above and below by a space equal to at least the height of the numeral ... (b) to the left and right by a space at least twice the height of numeral"
      },
      "verification_mode": "VISION_AUTOMATED",
      "severity": "LOW",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "net_quantity.value",
            "op": "exists"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fn": "quantity_clear_space_ok",
        "args": {}
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Other printed matter is too close to the net quantity declaration.",
      "evidence_facts": [
        "net_quantity.clearance"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT",
      "notes": "Scale-invariant — computed from bounding boxes as a ratio to numeral height."
    },
    {
      "rule_id": "LMPC-R9-1a-001",
      "version": 1,
      "status": "active",
      "title": "Declarations legible and prominent",
      "category": "LEGIBILITY",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "9(1)(a), 9(1) proviso (b)",
        "pdf_page": 10,
        "text_excerpt": "Every declaration ... shall be (a) legible and prominent"
      },
      "verification_mode": "VISION_AUTOMATED",
      "severity": "MEDIUM",
      "applies_when": {
        "macro": "RETAIL_SCOPE"
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fact": "label.min_declaration_ocr_confidence",
        "op": "gte",
        "value": {
          "policy": "min_ocr_confidence_for_legible"
        }
      },
      "outcome_on_fail": "REQUIRES_VERIFICATION",
      "fail_message": "Some mandatory declarations are hard to read (low OCR confidence) — officer to confirm legibility.",
      "evidence_facts": [
        "label.min_declaration_ocr_confidence"
      ],
      "threshold_source": "ENGINEERING_POLICY",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT",
      "notes": "OCR confidence is only a proxy for legibility; the law gives no number."
    },
    {
      "rule_id": "LMPC-R9-1b-001",
      "version": 1,
      "status": "active",
      "title": "MRP and net-quantity numerals in a colour contrasting with the background",
      "category": "LEGIBILITY",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "9(1)(b)",
        "pdf_page": 10,
        "text_excerpt": "numerals of the retail sale price and net quantity declaration shall be printed ... in a colour that contrasts conspicuously with the background"
      },
      "verification_mode": "VISION_AUTOMATED",
      "severity": "MEDIUM",
      "applies_when": {
        "macro": "RETAIL_SCOPE"
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        },
        {
          "exemption_ref": "9(1) proviso (a)",
          "when": {
            "fact": "label.is_blown_formed_moulded_on_glass_or_plastic",
            "op": "eq",
            "value": true,
            "absent_as": false
          },
          "reason": "Blown/formed/moulded on glass or plastic."
        }
      ],
      "check": {
        "all": [
          {
            "fact": "mrp.contrast_ratio",
            "op": "gte",
            "value": {
              "policy": "min_contrast_ratio_for_conspicuous"
            }
          },
          {
            "fact": "net_quantity.contrast_ratio",
            "op": "gte",
            "value": {
              "policy": "min_contrast_ratio_for_conspicuous"
            }
          }
        ]
      },
      "outcome_on_fail": "REQUIRES_VERIFICATION",
      "fail_message": "MRP/net-quantity numerals have low colour contrast against the background.",
      "evidence_facts": [
        "mrp",
        "net_quantity"
      ],
      "threshold_source": "ENGINEERING_POLICY",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R9-2-001",
      "version": 1,
      "status": "active",
      "title": "No declaration that must be read through a liquid",
      "category": "PLACEMENT",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "9(2)",
        "pdf_page": 10,
        "text_excerpt": "No declaration shall be made so as to require it to be read through any liquid commodity contained in the package."
      },
      "verification_mode": "MANUAL_INSPECTION",
      "severity": "LOW",
      "applies_when": {
        "macro": "RETAIL_SCOPE"
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fact": "label.read_through_liquid",
        "op": "eq",
        "value": false
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "A declaration can only be read through the liquid contents.",
      "evidence_facts": [],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R9-3-001",
      "version": 1,
      "status": "active",
      "title": "Outer container/wrapper repeats all declarations unless transparent",
      "category": "PLACEMENT",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "9(3)",
        "pdf_page": 10,
        "text_excerpt": "Where a package is provided with an outside container or wrapper such container or wrapper shall also contain all the declarations ... except where such container or wrapper itself is transparent"
      },
      "verification_mode": "MANUAL_INSPECTION",
      "severity": "MEDIUM",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "package.has_outer_wrapper",
            "op": "eq",
            "value": true,
            "absent_as": false
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "any": [
          {
            "fact": "package.outer_wrapper_has_all_declarations",
            "op": "eq",
            "value": true
          },
          {
            "fact": "package.outer_wrapper_transparent_and_readable",
            "op": "eq",
            "value": true
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Outer wrapper hides declarations and does not repeat them.",
      "evidence_facts": [],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R9-4-001",
      "version": 1,
      "status": "active",
      "title": "Declarations in English or Hindi (Devanagari)",
      "category": "LANGUAGE",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "9(4)",
        "pdf_page": 10,
        "text_excerpt": "The particulars of the declarations ... shall either be in Hindi in Devnagri script or in English"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "macro": "RETAIL_SCOPE"
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fact": "label.declaration_languages",
        "op": "contains_any",
        "value": [
          "en",
          "hi-Deva"
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Mandatory declarations are not in English or Hindi (Devanagari).",
      "evidence_facts": [
        "label.declaration_languages"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R21-2-001",
      "version": 1,
      "status": "active",
      "title": "Single package: deficiency in net quantity within maximum permissible error",
      "category": "NET_CONTENT",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "21(2)-(3), 22, First Schedule",
        "pdf_page": 21,
        "text_excerpt": "whether the deficiency is more than the maximum permissible error in relation to that commodity"
      },
      "verification_mode": "MEASUREMENT_REQUIRED",
      "severity": "CRITICAL",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "measurement.actual_net_quantity_base",
            "op": "exists"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fn": "single_package_within_mpe",
        "args": {}
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Measured net quantity is short of the declared quantity by more than the MPE.",
      "evidence_facts": [
        "measurement.actual_net_quantity_base",
        "net_quantity"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT",
      "notes": "21(3) proviso: if 'when packed' and shortage due to environment, no punitive action against dealer -> REQUIRES_VERIFICATION."
    },
    {
      "rule_id": "LMPC-R19-6-001",
      "version": 1,
      "status": "active",
      "title": "Lot approval: sample average >= declared and no sample short beyond MPE",
      "category": "NET_CONTENT",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "19(6), Fifth & Sixth Schedule",
        "pdf_page": 19,
        "text_excerpt": "the statistical average of the net quantity ... is equal to, or more than, the quantity declared ... the extent of error in deficiency in none of such sample packages exceeds the maximum permissible error"
      },
      "verification_mode": "MEASUREMENT_REQUIRED",
      "severity": "CRITICAL",
      "applies_when": {
        "all": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "fact": "measurement.sample_net_quantities_base",
            "op": "exists"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fn": "lot_test_ok",
        "args": {}
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Lot fails: average below declared quantity or a sample short beyond MPE (or sample size below Fifth Schedule).",
      "evidence_facts": [
        "measurement.sample_net_quantities_base",
        "measurement.lot_size"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R23-001",
      "version": 1,
      "status": "active",
      "title": "Package is not deceptive (no exaggerated impression of quantity)",
      "category": "NET_CONTENT",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "23 Explanation",
        "pdf_page": 22,
        "text_excerpt": "'deceptive package' means a package which is so designed as to deliberately given to the consumer an exaggerated or misleading impression as to the quantity"
      },
      "verification_mode": "MANUAL_INSPECTION",
      "severity": "HIGH",
      "applies_when": {
        "macro": "RETAIL_SCOPE"
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fact": "inspection.deceptive_package",
        "op": "eq",
        "value": false
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Package design gives a misleading impression of quantity (slack fill) without protection/machine justification.",
      "evidence_facts": [],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R24-a-001",
      "version": 1,
      "status": "active",
      "title": "Wholesale package: name and address of manufacturer/importer/packer",
      "category": "WHOLESALE",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "24(a)",
        "pdf_page": 23,
        "text_excerpt": "The name and address of the manufacturer or importer or where the manufacturer or importer is not the packer, of the packer"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "all": [
          {
            "fact": "package.level",
            "op": "eq",
            "value": "wholesale"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "24 proviso",
          "when": {
            "fact": "other_law.wholesale_declaration_required",
            "op": "eq",
            "value": true,
            "absent_as": false
          },
          "reason": "Similar declaration required by another law."
        }
      ],
      "check": {
        "any": [
          {
            "all": [
              {
                "fact": "manufacturer.name",
                "op": "exists"
              },
              {
                "fact": "manufacturer.address.text",
                "op": "exists"
              }
            ]
          },
          {
            "all": [
              {
                "fact": "importer.name",
                "op": "exists"
              },
              {
                "fact": "importer.address.text",
                "op": "exists"
              }
            ]
          },
          {
            "all": [
              {
                "fact": "packer.name",
                "op": "exists"
              },
              {
                "fact": "packer.address.text",
                "op": "exists"
              }
            ]
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Wholesale package lacks name and address of manufacturer/importer/packer.",
      "evidence_facts": [
        "manufacturer",
        "importer",
        "packer"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R24-b-001",
      "version": 1,
      "status": "active",
      "title": "Wholesale package: identity of the commodity",
      "category": "WHOLESALE",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "24(b)",
        "pdf_page": 23,
        "text_excerpt": "the identity of the commodity contained in the package"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "all": [
          {
            "fact": "package.level",
            "op": "eq",
            "value": "wholesale"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "24 proviso",
          "when": {
            "fact": "other_law.wholesale_declaration_required",
            "op": "eq",
            "value": true,
            "absent_as": false
          },
          "reason": "Similar declaration required by another law."
        }
      ],
      "check": {
        "fact": "product.common_name",
        "op": "exists"
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Wholesale package does not identify the commodity.",
      "evidence_facts": [
        "product.common_name"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R24-c-001",
      "version": 1,
      "status": "active",
      "title": "Wholesale package: number of retail packages or net quantity",
      "category": "WHOLESALE",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "24(c)",
        "pdf_page": 23,
        "text_excerpt": "the total number of retail package contained in such wholesale package or the net quantity"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "all": [
          {
            "fact": "package.level",
            "op": "eq",
            "value": "wholesale"
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "24 proviso",
          "when": {
            "fact": "other_law.wholesale_declaration_required",
            "op": "eq",
            "value": true,
            "absent_as": false
          },
          "reason": "Similar declaration required by another law."
        }
      ],
      "check": {
        "any": [
          {
            "fact": "package.retail_package_count",
            "op": "exists"
          },
          {
            "fact": "net_quantity.value",
            "op": "exists"
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Wholesale package states neither number of retail packs nor net quantity.",
      "evidence_facts": [
        "package.retail_package_count",
        "net_quantity"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-R25-001",
      "version": 1,
      "status": "active",
      "title": "Export package sold in India is re-packed/re-labelled per Chapter II",
      "category": "EXPORT",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "25",
        "pdf_page": 23,
        "text_excerpt": "An export package shall not be sold in India unless the manufacturer or packer has re-packed or relabeled the commodity in accordance with the provisions contained in Chapter II"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "CRITICAL",
      "applies_when": {
        "all": [
          {
            "fact": "package.level",
            "op": "eq",
            "value": "export"
          },
          {
            "fact": "package.offered_for_sale_in_india",
            "op": "eq",
            "value": true
          }
        ]
      },
      "exempt_when": [],
      "check": {
        "fact": "package.relabelled_for_india",
        "op": "eq",
        "value": true
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Export package offered for sale in India without Indian re-labelling.",
      "evidence_facts": [],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT",
      "notes": "If relabelled, re-run the inspection with package.level = retail."
    },
    {
      "rule_id": "LMPC-R27-001",
      "version": 1,
      "status": "active",
      "title": "Manufacturer / packer / importer registered with Director or Controller",
      "category": "REGISTRATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "27",
        "pdf_page": 24,
        "text_excerpt": "Every individual, firm ... who or which pre-packs or imports any commodity for sale ... shall make an application ... for the registration"
      },
      "verification_mode": "EXTERNAL_LOOKUP",
      "severity": "HIGH",
      "applies_when": {
        "any": [
          {
            "macro": "RETAIL_SCOPE"
          },
          {
            "all": [
              {
                "fact": "package.level",
                "op": "eq",
                "value": "wholesale"
              }
            ]
          }
        ]
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        }
      ],
      "check": {
        "fact": "registry.packer_or_importer_registered",
        "op": "eq",
        "value": true
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "No Legal Metrology registration found for the packer/importer.",
      "evidence_facts": [
        "manufacturer.name"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT",
      "notes": "Needs registry lookup (state LM portals). Penalty under Rule 32(1)."
    },
    {
      "rule_id": "LMPC-R31-001",
      "version": 1,
      "status": "active",
      "title": "Advertisement mentioning RSP also states net quantity in the same font size",
      "category": "ADVERTISEMENT",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "31",
        "pdf_page": 26,
        "text_excerpt": "Any advertisement mentioning the retail sale price ... shall contain a declaration as to the net quantity ... The font size of the net quantity ... shall be same as that of retail sale price."
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "MEDIUM",
      "applies_when": {
        "all": [
          {
            "fact": "inspection.input_type",
            "op": "eq",
            "value": "advertisement",
            "absent_as": false
          },
          {
            "fact": "ad.mentions_rsp",
            "op": "eq",
            "value": true
          }
        ]
      },
      "exempt_when": [],
      "check": {
        "all": [
          {
            "fact": "ad.net_quantity_text",
            "op": "exists"
          },
          {
            "fn": "ad_font_sizes_match",
            "args": {}
          }
        ]
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Advertisement shows price without net quantity in the same font size.",
      "evidence_facts": [
        "ad"
      ],
      "threshold_source": "LAW",
      "effective_from": "2011-04-01",
      "effective_to": null,
      "amendment_status": "AS_PER_2011_TEXT"
    },
    {
      "rule_id": "LMPC-USP-001",
      "version": 1,
      "status": "draft",
      "title": "Unit sale price declared (per g/kg, ml/l, cm/m or per unit)",
      "category": "PRICE_DECLARATION",
      "provision": {
        "source": "LMPC Rules 2011",
        "rule": "6(1) as amended (unit sale price)",
        "pdf_page": null,
        "text_excerpt": "[amended text to be pasted from Gazette]"
      },
      "verification_mode": "LABEL_AUTOMATED",
      "severity": "HIGH",
      "applies_when": {
        "macro": "RETAIL_SCOPE"
      },
      "exempt_when": [
        {
          "exemption_ref": "Rule 26",
          "when": {
            "macro": "RULE26_EXEMPT"
          },
          "reason": "Exempt from the Rules under Rule 26 (<=10 g/ml, restaurant fast food, DPCO drugs, farm produce >50 kg)."
        },
        {
          "exemption_ref": "amended proviso",
          "when": {
            "fact": "product.tags",
            "op": "contains",
            "value": "alcoholic_beverage"
          },
          "reason": "Alcoholic beverages under State Excise law (reported)."
        },
        {
          "exemption_ref": "amended proviso",
          "when": {
            "fn": "usp_equals_rsp",
            "args": {}
          },
          "reason": "Retail sale price equals unit sale price (reported)."
        }
      ],
      "check": {
        "fn": "unit_sale_price_ok",
        "args": {}
      },
      "outcome_on_fail": "NON_COMPLIANT",
      "fail_message": "Unit sale price not declared or not in the prescribed unit.",
      "evidence_facts": [
        "unit_sale_price",
        "mrp",
        "net_quantity"
      ],
      "threshold_source": "LAW",
      "effective_from": "2022-04-01",
      "effective_to": null,
      "amendment_status": "DRAFT_PENDING_GAZETTE_VERIFICATION",
      "notes": "Secondary sources describe per-1 g / per-1 ml etc. below 1 kg/l and per-kg/l at or above, rounded to 2 decimals; enforcement dates reported as 2022, 2023 and 2024 in different sources. Activate only after confirming the Gazette text."
    }
  ],
  "coverage_not_rules": [
    {
      "provision": "1, 2, 34",
      "reason": "Title, definitions, repeal — definitions feed the fact vocabulary (retail package, PDP, RSP, wholesale package)."
    },
    {
      "provision": "3",
      "reason": "Implemented as macro RETAIL_SCOPE (gate for every Chapter II rule)."
    },
    {
      "provision": "6(1)(g)(B), 6(6)",
      "reason": "Use of unexhausted packaging material — time-bound transitional permissions; not verifiable from a label."
    },
    {
      "provision": "6(4)",
      "reason": "Permissive (stickers allowed for non-mandatory declarations) — no violation possible."
    },
    {
      "provision": "7(1)",
      "reason": "Permissive (card/tape PDP for <=5 cc)."
    },
    {
      "provision": "11(1), 11(3)",
      "reason": "Net quantity excludes wrapper / accounts for negligible variation — tested physically via LMPC-R21-2-001 / LMPC-R19-6-001."
    },
    {
      "provision": "12(1), 12(3), 12(5)",
      "reason": "General or optional (additional number declaration allowed; extra info on same panel) — covered by LMPC-R8-1-001."
    },
    {
      "provision": "18(1)",
      "reason": "Dealer may not sell non-compliant packages — the consequence of any NON_COMPLIANT result, not a separate check."
    },
    {
      "provision": "18(3), 18(4)",
      "reason": "Revised price after tax change — needs price circulars/newspaper notices; out of label scope."
    },
    {
      "provision": "18(7)",
      "reason": "Retailer must keep a class III electronic weighing machine — premises inspection checklist item."
    },
    {
      "provision": "19(1)-(5), 19(7)-(8), 20, 21(1), 21(4)-(5), 22(2)-(3)",
      "reason": "Inspection procedure & powers of officers — workflow in the app, not compliance rules."
    },
    {
      "provision": "23(2)",
      "reason": "Disposal of perishable seized goods — procedure."
    },
    {
      "provision": "28-30",
      "reason": "Registration admin; 28 used as exemption on LMPC-R6-1a-002."
    },
    {
      "provision": "32",
      "reason": "Penalty — reference table rule32_penalties, attached to violations in the report."
    },
    {
      "provision": "33",
      "reason": "Central Government power to relax — handled as a per-manufacturer override record, not a rule."
    },
    {
      "provision": "Fifth, Sixth Schedule",
      "reason": "Sampling and test method — used inside LMPC-R19-6-001 and as officer SOP."
    },
    {
      "provision": "Seventh Schedule (Forms A/B)",
      "reason": "Data sheet format — generate from inspection record for the report."
    }
  ],
  "amendment_register": [
    {
      "notification": "GSR 748(E), 24.10.2011",
      "status": "IN_UPLOADED_PDF",
      "changes": [
        "Rule 5 proviso withdrawn w.e.f. 01.07.2012",
        "6(1)(d) rubber-stamp proviso withdrawn",
        "12(6) broadened",
        "19(8) wording",
        "26(a) proviso withdrawn",
        "Fourth Schedule ice cream: volume -> weight"
      ],
      "encoded_as": [
        "LMPC-R5-002 effective_to",
        "LMPC-R6-1d-002",
        "LMPC-R12-6-001 v2",
        "fourth_schedule entries"
      ]
    },
    {
      "notification": "GSR 629(E), 23.06.2017 (in force 01.01.2018)",
      "status": "NOT_IN_PDF_VERIFY",
      "reported_changes": [
        "Country of origin/manufacture/assembly for imported goods",
        "'Best before'/'use by' declaration for commodities that become unfit",
        "Consumer-care details strengthened",
        "E-commerce entities to display declarations",
        "Principal display panel size and font tables revised",
        "Institutional/industrial consumer definitions tightened",
        "Penalty amounts revised"
      ]
    },
    {
      "notification": "2021 amendment (in force 01.04.2022, per secondary sources)",
      "status": "NOT_IN_PDF_VERIFY",
      "reported_changes": [
        "Rule 5 & Second Schedule omitted",
        "Unit sale price introduced",
        "MRP in Indian currency inclusive of all taxes",
        "Date of manufacture wording changed",
        "Count symbols expanded (number/unit/piece/pair/set)"
      ]
    },
    {
      "notification": "2022 amendments",
      "status": "NOT_IN_PDF_VERIFY",
      "reported_changes": [
        "Imported packages: month/year of import",
        "Unit sale price commencement deferred"
      ]
    },
    {
      "notification": "2023 amendment (in force 01.01.2024, per secondary sources)",
      "status": "NOT_IN_PDF_VERIFY",
      "reported_changes": [
        "'Combination package' and 'group package' definitions",
        "Spare parts proviso",
        "Rule 26 e-commerce loose commodities exemption"
      ]
    },
    {
      "notification": "2025 amendment (Oct 2025, per secondary sources)",
      "status": "NOT_IN_PDF_VERIFY",
      "reported_changes": [
        "Medical devices: Medical Devices Rules, 2017 prevail for label font size/dimensions and PDP"
      ]
    }
  ]
}