AI_FRASES_SCHEMA = {
    "type": "object",
    "properties": {
        "frases": {
            "type": "array",
            "minItems": 0,
            "maxItems": 4,
            "items": {
                "type": "object",
                "properties": {
                    "categoria": {
                        "type": "string",
                        "enum": ["PERSONALIDAD", "SABORES"]
                    },
                    "texto": {"type": "string", "minLength": 15},
                },
                "required": ["categoria", "texto"]
            },
        },
    },
    "required": ["frases"],
}