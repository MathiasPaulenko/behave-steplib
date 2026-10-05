"""E2E test: run a real behave process against steplib-registered steps.

Unlike ``test_api_feature.py`` (which calls step functions directly), this
exercises the full pipeline: ``load()`` → behave step registration →
pattern matching (including es/pt translations) → step execution, using a
mock HTTP client injected from ``environment.py``.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

_ENVIRONMENT_PY = textwrap.dedent(
    '''
    """behave environment for the e2e test."""

    from steplib.behave import load
    from steplib.modules.api.client import Response
    from steplib.modules.api.context import ApiContext


    class MockHTTPClient:
        """Return a canned response for every request."""

        def request(self, method, url, **kwargs):
            return Response(
                status=200,
                headers={"Content-Type": "application/json"},
                body=b'{"users": [{"name": "Ada"}]}',
                elapsed_ms=1.0,
            )


    def before_all(context):
        context.steplib = load(context, "steplib.modules.api.steps")


    def before_scenario(context, scenario):
        context.steplib.api = ApiContext(client=MockHTTPClient())
    '''
)

_FEATURE_EN = textwrap.dedent(
    """\
    Feature: API health check

      Scenario: GET users returns 200
        Given the API base url is "https://api.example.com"
        When I send a GET request to "/users"
        Then the response status is 200
        And the response body is valid JSON
        And the JSON path "$.users[0].name" equals "Ada"
    """
)

_FEATURE_ES = textwrap.dedent(
    """\
    # language: es
    Característica: Chequeo de API

      Escenario: GET usuarios devuelve 200
        Dado la url base de la API es "https://api.example.com"
        Cuando envío una petición GET a "/users"
        Entonces el estado de la respuesta es 200
        Y el cuerpo de la respuesta es JSON válido
    """
)


def test_behave_run(tmp_path: Path) -> None:
    """A real behave run resolves steplib steps in English and Spanish."""
    features = tmp_path / "features"
    (features / "steps").mkdir(parents=True)
    (features / "environment.py").write_text(_ENVIRONMENT_PY, encoding="utf-8")
    (features / "api.feature").write_text(_FEATURE_EN, encoding="utf-8")
    (features / "api_es.feature").write_text(_FEATURE_ES, encoding="utf-8")

    repo_root = Path(__file__).resolve().parents[3]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root) + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [sys.executable, "-m", "behave", "-f", "progress"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
        check=False,
    )
    assert result.returncode == 0, (
        f"behave exited with {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
