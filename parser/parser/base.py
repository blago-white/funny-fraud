from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement


class BaseParser:
    def add_banners_dropping_script(self):
        self._driver.execute_script("""
            function sleep(ms) {
                return new Promise(resolve => setTimeout(resolve, ms));
            }
            
            async function dropFloctoryWidget() {
                while (true) {
                    await sleep(5);
                    
                    if (document.getElementsByClassName("flocktory-widget-overlay").length > 0) {
                        document.getElementsByClassName("flocktory-widget-overlay")[0].remove();
                        
                        try {document.getElementsByClassName("flocktory-widget-overlay")[1].remove()} catch {}     
                    }
                } 
            }
            
            dropFloctoryWidget()
        """)

        self._driver.execute_script("""
            function sleep(ms) {
                return new Promise(resolve => setTimeout(resolve, ms));
            }
            
            async function dropLayers() {
                while (true) {
                    await sleep(5);
                    
                    if (document.getElementById("layers")) {
                        document.getElementById("layers").remove();
                    }
                } 
            }
            
            dropLayers()
        """)

    def _wait_for_element(
        self,
        by: str = By.ID,
        locator: str | None = None,
        timeout: float = 10,
    ) -> WebElement:
        return WebDriverWait(self._driver, timeout).until(expected_conditions.presence_of_element_located((by, locator)))

    def _make_js_click(self, element: WebElement) -> None:
        self._driver.execute_script('arguments[0].click();', element)
