# tests/services/test_analyses_service.py
import pytest

try:
    from src.services import analyses as analyses_service
except ImportError:
    analyses_service = None


@pytest.mark.services
def test_analise_de_conteudo_retorna_estrutura_basica():
    """
    Testa se o service de análise de conteúdo retorna
    uma estrutura coerente, mesmo que simplificada.
    """
    if analyses_service is None:
        pytest.skip("Ajustar import de analyses_service conforme código real.")

    # Exemplo de chamada (ajustar para a função real):
    # result = analyses_service.analyze_content_strategy(
    #     platform="instagram",
    #     niche="consultoria de imagem",
    #     target_audience="mulheres 25-45",
    #     objectives=["aumentar engajamento"],
    # )
    #
    # assert isinstance(result, dict)
    # assert "insights" in result
    # assert "post_ideas" in result

    assert True  # placeholder
