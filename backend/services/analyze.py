from schemas.analyze import AnalyzeResponse

from ml.inference import TriageInference

def process_text(content: str, inference_model: TriageInference) -> AnalyzeResponse:
    result = inference_model.predict(content, top_k=5)
    return AnalyzeResponse(
        triage=result["triage"]["label"],
        triage_confidence=result["triage"]["confidence"],
        priority=result["priority"]["label"],
        priority_confidence=result["priority"]["confidence"],
        risk=result["risk"]["label"],
        risk_confidence=result["risk"]["confidence"],
        should_process=str(result["should_process"]["label"]).lower(),
        should_process_confidence=result["should_process"]["confidence"],
        shap_indices=result["shap_indices"],
    )


