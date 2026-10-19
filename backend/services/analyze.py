from schemas.analyze import AnalyzeResponse


async def process_text(content: str) -> AnalyzeResponse:
    # TODO: настоящую логику анализа обязатеьно в AIOTHRED иначе евент луп заблокируется
    return AnalyzeResponse(
        result="MOCK",
        confidence=1
    )