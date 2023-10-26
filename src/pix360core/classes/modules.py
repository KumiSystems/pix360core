from ..models import File, Conversion

class BaseModule:
    """Base class for any type of modules supported by PIX360
    """
    name: str
    identifier: str


class DownloaderModule(BaseModule):
    """Base class for modules that handle downloading content from a URL
    """

    # Certainty levels for the test_url() method

    CERTAINTY_UNSUPPORTED = -100
    CERTAINTY_POSSIBLE = 0
    CERTAINTY_PROBABLE = 50
    CERTAINTY_CERTAIN = 100

    # Properties of the module

    name: str # Human-friendly name of the module
    identifier: str # Unique identifier for the module

    @classmethod
    def test_url(cls, url: str) -> int:
        """Test if URL is plausible for this module

        This should just match the URL against a regex or something like that,
        it is not intended to check whether the URL is valid and working, or
        whether it actually contains downloadable content.

        Args:
            url (str): URL to check for plausibility

        Raises:
            NotImplementedError: If the method is not implemented in a module

        Returns:
            int: Certainty level of the URL being supported by this module
                 See CERTAINTY_* constants for default values

        """
        raise NotImplementedError(f"Downloader Module {cls.__name__} does not implement test_url(url)!")

    def process_conversion(self, conversion: Conversion) -> File:
        """Attempt to download content for a conversion

        Args:
            conversion (Conversion): Conversion object to process

        Raises:
            DownloadError: If an error occurred while downloading content
            NotImplementedError: If the method is not implemented in a module

        Returns:
            File: Image or Video object containing the downloaded file
        """
        raise NotImplementedError(f"Downloader Module {self.__class__.__name__} does not implement process_url(url)!")