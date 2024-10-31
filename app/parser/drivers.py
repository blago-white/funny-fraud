from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver
from fake_useragent import UserAgent

from .proxies.services import ProxiesService


class WebDriversService:
    def __init__(
            self, default_driver: webdriver.Chrome = webdriver.Chrome,
            default_opts_class: ChromeOptions = ChromeOptions,
            agent_service: UserAgent = UserAgent(
                os=["windows", "macos", "linux"],
                platforms=["pc"]
            ),
            proxy_service: ProxiesService = ProxiesService(),
            driver_path: str = "C:\\chromedriver.exe"):
        self._default_driver = default_driver
        self._default_opts_class = default_opts_class
        self._agent_service = agent_service
        self._driver_path = driver_path
        self._proxy_service = proxy_service

    async def get(self, proxy: str = None) -> webdriver.Chrome:
        agent = self._get_agent()

        return self._get_driver(
            opts=await self._get_opts(
                agent=agent,
                headless=False,
            ),
            agent=agent,
            proxy=proxy
        )

    def _get_driver(self, opts: ChromeOptions, agent: str, proxy: str = None):
        if not proxy:
            return Chrome(
                service=Service(
                    executable_path=self._driver_path
                ),
                options=opts,
            )

        driver = self._default_driver(
            service=Service(
                executable_path=self._driver_path
            ),
            options=opts,
            seleniumwire_options={
                "proxy": {
                    "http": "http://" + proxy,
                    "https": "http://" + proxy,
                    "no_proxy": "localhost,127.0.0.1"
                }
            }
        )

        driver.execute_cdp_cmd('Network.setUserAgentOverride',
                               {"userAgent": agent})

        return driver

    def _get_agent(self) -> str:
        return self._agent_service.random

    async def _get_opts(
            self, agent: str,
            headless: bool = True):
        opts = self._default_opts_class()

        opts.add_argument("--window-size=2200,1000")

        # if proxy:
        #     opts.add_argument(f"--proxy={proxy}")
        #     opts.add_argument(f"--proxy-server={proxy}")

        if headless:
            opts.add_argument("--headless")

        opts.add_argument(f"user-agent={agent}")

        return opts
