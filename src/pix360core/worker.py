from .loader import Loader
from .models import Conversion, File, ConversionStatus
from .classes import ConversionError

from django.conf import settings

import multiprocessing
import logging
import time
import traceback

class Worker(multiprocessing.Process):
    def __init__(self):
        super().__init__()
        self.loader = Loader()
        self.logger = logging.getLogger("pix360")

        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(handler)

        if settings.DEBUG:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    def process_conversion(self, conversion: Conversion) -> File:
        """Process a conversion

        Args:
            conversion (Conversion): Conversion to process

        Returns:
            File: Result of the conversion

        Raises:
            ConversionError: If the conversion is invalid
            DownloadError: If the download fails
            StitchingError: If the stitching fails
        """
        
        if conversion.downloader:
            downloader = self.loader.resolve_downloader_identifier(conversion.downloader)
            if not downloader:
                raise ConversionError("Downloader not found")
        else:
            downloaders = self.loader.find_downloader(conversion.url)
            if len(downloaders) > 0:
                downloaders.sort(key=lambda x: x[1], reverse=True)
                downloader = downloaders[0][0]
                conversion.downloader = downloader.identifier
                conversion.save()
            else:
                raise ConversionError("No downloader found")
        
        result = downloader.process_conversion(conversion)
        result.conversion = conversion
        result.is_result = True
        result.save()

        return result

    def run(self):
        """Run the worker
        """
        while True:
            try:
                conversion = Conversion.objects.filter(status=ConversionStatus.PENDING).first()
                
                if conversion:
                    conversion.status = ConversionStatus.PROCESSING
                    conversion.save()
                    self.logger.info(f"Processing conversion {conversion.id}")
                
                    try:
                        result = self.process_conversion(conversion)
                        result.is_result = True
                        result.save()
                        conversion.status = ConversionStatus.DONE
                        conversion.save()
                        self.logger.info(f"Conversion {conversion.id} done")
                    except Exception as e:
                        conversion.status = ConversionStatus.FAILED
                        conversion.log = traceback.format_exc()
                        conversion.save()
                        self.logger.error(f"Conversion {conversion.id} failed: {e}")
                        self.logger.debug(traceback.format_exc())

                else:
                    self.logger.debug("No conversion to process")
                    time.sleep(1)

            except Exception as e:
                self.logger.error(f"Worker error: {e}")