from typing import List, Tuple, Optional

from pix360core.classes.modules import DownloaderModule

import importlib.metadata

class Loader:
    def __init__(self):
        self.downloaders = self.__class__.load_downloaders()

    def resolve_downloader_identifier(self, identifier: str) -> Optional[DownloaderModule]:
        """A function to resolve a downloader identifier to a downloader name.

        Args:
            identifier (str): The downloader identifier

        Returns:
            str: The downloader name
        """

        for downloader in self.downloaders:
            if downloader.identifier == identifier:
                return downloader

        return None

    def find_downloader(self, url: str) -> List[Tuple[DownloaderModule, int]]:
        """A function to find the downloader(s) that can handle a given URL.

        Args:
            url (str): The URL to test

        Returns:
            List[Tuple[DownloaderModule, int]]: A list of tuples containing the downloader and the certainty level
        """

        downloaders = []

        for downloader in self.downloaders:
            downloader = downloader()
            try:
                certainty = downloader.test_url(url)
            except Exception as e:
                raise Exception(f"Error while testing URL with {downloader.identifier}: {e}") from e
            if certainty != DownloaderModule.CERTAINTY_UNSUPPORTED:
                downloaders.append((downloader, certainty))

        return downloaders

    @staticmethod
    def load_downloaders() -> List:
        """A function to find all downloaders installed, implementing the
        pix360downloader entry point.

        Returns: List of imported installed downloaders
        """

        downloaders = []

        for entry_point in importlib.metadata.entry_points().get("pix360downloader", []):
            try:
                downloaders.append(entry_point.load())
            except:
                print(f"Something went wrong trying to import {entry_point}")

        return downloaders