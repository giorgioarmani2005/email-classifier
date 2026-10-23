from schemas.analyze import AnalyzeResponse
import time

def process_text(content: str) -> AnalyzeResponse:
    # TODO: настоящую логику анализа
    time.sleep(3)  # имитация
    return AnalyzeResponse(
        result="MOCK",
        confidence=1
    )