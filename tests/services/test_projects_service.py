# tests/services/test_projects_service.py
import pytest

# Ajuste o import conforme o código real:
# por exemplo: from src.services import projects as projects_service
try:
    from src.services import projects as projects_service
except ImportError:
    projects_service = None  # evita quebrar antes de você ajustar


@pytest.mark.services
def test_criar_projeto_modelo_basico():
    """
    Exemplo de teste unitário para o service de projetos.
    Aqui a ideia é testar a função que encapsula a lógica
    de criação de projeto (sem passar por FastAPI).
    """
    if projects_service is None:
        pytest.skip("Ajustar import de projects_service conforme código real.")

    # TODO: ajuste para o nome real da função e argumentos
    # Exemplo:
    # project = projects_service.create_project(
    #     name="Projeto Teste",
    #     platform="instagram",
    #     niche="moda",
    #     owner_id=1,
    # )
    #
    # assert project.name == "Projeto Teste"
    # assert project.platform == "instagram"
    assert True  # placeholder até você ligar com o service real
