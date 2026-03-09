from gliner import GLiNER
# 1. Define our new text
def query_separator(text, labels = ["metric", "brand"]):
    model = GLiNER.from_pretrained("nvidia/gliner-pii")
    entities = model.predict_entities(text, labels, threshold=0.5)
    return entities