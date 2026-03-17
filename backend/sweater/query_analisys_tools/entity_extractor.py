from gliner import GLiNER

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = GLiNER.from_pretrained("nvidia/gliner-pii")
    return _model


def extract_entities(text, labels=None):
    """Extract named entities from text using GLiNER.

    Currently supports 'metric' labels; more will be added over time.
    Returns a list of dicts with 'text', 'label', 'start', 'end', 'score'.
    """
    if labels is None:
        labels = ["metric"]
    model = _get_model()
    return model.predict_entities(text, labels, threshold=0.3)
