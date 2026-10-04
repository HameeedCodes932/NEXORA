def dump_model(model):
    return model.model_dump() if hasattr(model, "model_dump") else model.dict()
