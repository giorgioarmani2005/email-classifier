from schemas.analyze import AnalyzeResponse
import asyncio

async def process_text(content: str) -> AnalyzeResponse:
    # TODO: настоящую логику анализа обязатеьно в AIOTHRED иначе евент луп заблокируется
    await asyncio.sleep(3)  # имитация
    return AnalyzeResponse(
        result="MOCK",
        confidence=1
    )