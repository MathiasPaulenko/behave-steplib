"""Regression tests for Web module bugs found in the audit."""

from __future__ import annotations

import pytest

from steplib.modules.web.context import WebContext


class TestNavigateSchemeCase:
    """Absolute URLs must be detected case-insensitively."""

    def test_uppercase_scheme_is_absolute(self):
        from steplib.modules.web.actions import web_navigate

        class FakeDriver:
            def __init__(self) -> None:
                self.urls: list[str] = []

            def get(self, url: str) -> None:
                self.urls.append(url)

        driver = FakeDriver()
        web_ctx = WebContext(driver=driver, base_url="https://base.test")  # type: ignore[arg-type]
        web_navigate(web_ctx, "HTTPS://EXAMPLE.TEST/x")
        assert driver.urls == ["HTTPS://EXAMPLE.TEST/x"]


class TestSeleniumByResolution:
    """Locator strategy names must map to selenium By attributes."""

    def _driver(self):
        from types import SimpleNamespace

        from steplib.modules.web.client import SeleniumDriver

        class FakeBy:
            ID = "id"
            NAME = "name"
            XPATH = "xpath"
            CSS_SELECTOR = "css selector"
            CLASS_NAME = "class name"
            TAG_NAME = "tag name"
            LINK_TEXT = "link text"
            PARTIAL_LINK_TEXT = "partial link text"

        driver = SeleniumDriver.__new__(SeleniumDriver)
        driver._By = FakeBy
        driver._driver = SimpleNamespace(
            find_element=lambda by, value: (by, value),
        )
        return driver

    def test_spaced_alias_resolves(self):
        driver = self._driver()
        assert driver.find_element("css selector", "#x") == ("css selector", "#x")

    def test_short_alias_resolves(self):
        driver = self._driver()
        assert driver.find_element("css", "#x") == ("css selector", "#x")
        assert driver.find_element("class", ".y") == ("class name", ".y")
        assert driver.find_element("tag", "div") == ("tag name", "div")

    def test_underscore_names_still_work(self):
        driver = self._driver()
        assert driver.find_element("css_selector", "#x") == ("css selector", "#x")
        assert driver.find_element("id", "x") == ("id", "x")

    def test_unknown_strategy_raises_clear_error(self):
        driver = self._driver()
        try:
            driver.find_element("bogus", "x")
        except ValueError as exc:
            assert "bogus" in str(exc)
        else:
            raise AssertionError("expected ValueError")


class TestWebCleanupResilience:
    """driver.quit() failure must still null the driver reference."""

    def test_cleanup_nulls_driver_even_when_quit_fails(self):
        class BadDriver:
            def quit(self) -> None:
                raise RuntimeError("quit failed")

        web_ctx = WebContext(driver=BadDriver())  # type: ignore[arg-type]
        with pytest.raises(RuntimeError):
            web_ctx.cleanup()
        assert web_ctx.driver is None
