class ConversionError(Exception):
    """Generic error that occurred while attempting to convert content
    """
    pass

class DownloadError(ConversionError):
    """Generic error that occurred while attempting to download content
    """
    pass

class StitchingError(ConversionError):
    """Generic error that occurred while attempting to stitch content
    """
    pass