from urllib.request import Request, urlopen

from .exceptions import DownloadError

import logging

USER_AGENT = 'Mozilla/5.0 (compatible; Pix360/dev; +https://kumig.it/kumisystems/pix360)'

class HTTPRequest(Request):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.logger = logging.getLogger("pix360")

        self.headers['User-Agent'] = USER_AGENT

    def open(self, retries=3, timeout=10, *args, **kwargs):
        self.logger.debug(f"Opening {self.full_url}")
        for i in range(retries):
            try:
                return urlopen(self, timeout=timeout, *args, **kwargs)
            except Exception as e:
                self.logger.warn(f"Error while opening {self.full_url}: {e}")
                if i == retries - 1:
                    raise DownloadError(f"Error downloading file from {self.full_url}") from e
