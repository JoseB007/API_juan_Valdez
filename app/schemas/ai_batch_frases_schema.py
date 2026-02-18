AI_BATCH_FRASES_SCHEMA = {
    "type": "object",
    "properties": {
        "resultados": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "apellido": {"type": "string"},
                    "frases": {
                        "type": "array",
                        "minItems": 4,
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
                "required": ["apellido", "frases"]
            },
        },
    },
    "required": ["resultados"],
}
