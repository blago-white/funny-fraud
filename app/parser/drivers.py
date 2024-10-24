from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service

from fake_useragent import UserAgent

from .proxies.services import ProxiesService


class WebDriversService:
    def __init__(self, default_driver: Chrome = Chrome,
                 default_opts_class: ChromeOptions = ChromeOptions,
                 agent_service: UserAgent = UserAgent(
                     os=["windows", "macos", "linux"],
                     platforms=["pc"]
                 ),
                 proxy_service: ProxiesService = ProxiesService(),
                 driver_path: str = "C:\\Users\\abram\\"
                                    ".cache\\selenium\\chromedriver\\"
                                    "win64\\129.0.6668.100\\"
                                    "chromedriver.exe"):
        self._default_driver = default_driver
        self._default_opts_class = default_opts_class
        self._agent_service = agent_service
        self._driver_path = driver_path
        self._proxy_service = proxy_service

    async def get(self, proxy: str = None) -> Chrome:
        agent = self._get_agent()

        return self._get_driver(
            opts=await self._get_opts(
                agent=agent,
                headless=False,
                proxy=proxy
            ),
            agent=agent
        )

    def _get_driver(self, opts: ChromeOptions, agent: str):
        driver = self._default_driver(service=Service(
            executable_path=self._driver_path
        ), options=opts)

        driver.execute_cdp_cmd('Network.setUserAgentOverride',
                               {"userAgent": agent})

        return driver

    def _get_agent(self) -> str:
        return self._agent_service.random

    async def _get_opts(self, agent: str,
                        headless: bool = True,
                        proxy: str = None):
        opts = self._default_opts_class()

        opts.add_argument("--window-size=2200,1000")

        # if not proxy:
        #     proxy = self._proxy_service.buy_proxy(count=1)

        # opts.add_argument(f"--proxy={proxy}")

        if headless:
            opts.add_argument("--headless")

        opts.add_argument(f"user-agent={agent}")

        return opts
