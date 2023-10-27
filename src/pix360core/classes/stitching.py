from ..models import File
from ..classes import StitchingError

from django.core.files.base import ContentFile

from typing import List, Optional, Tuple
from pathlib import Path

import PIL.Image

import tempfile
import subprocess
import io
import logging
import time

class BaseStitcher:
    """Base class for stitcher modules
    """

    CUBEMAP_ORDER = ["back", "right", "front", "left", "up", "down"]

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger("pix360")

    def cubemap_to_equirectangular(self, files: List[File], rotation: Tuple[int, int, int] = (0, 0, 0)) -> File:
        """Stitch a cubemap into an equirectangular image

        Args:
            files (List[File]): List of 6 files representing the 6 faces of the cubemap [back, right, front, left, up, down].
            rotation (Tuple[int, int, int], optional): Rotation of the cubemap on x, y and z axes in degrees. Defaults to (0, 0, 0).

        Raises:
            NotImplementedError: If the method is not implemented in a module
            StitchingError: If the stitching failed

        Returns:
            File: File object containing the stitched image
        """
        raise NotImplementedError

    def stitch(self, files: List[List[File]]) -> File:
        """Stitch a list of images together

        The input is a list of lists of images.
        Each list of images is stitched into one line horizontally.
        The resulting lines are then stitched together vertically.

        Args:
            files (List[List[File]]): List of lists of files to stitch together

        Raises:
            NotImplementedError: If the method is not implemented in a module
            StitchingError: If the stitching failed

        Returns:
            File: File object containing the stitched image
        """
        raise NotImplementedError

    def multistitch(self, tiles: List[List[List[File]]]) -> List[File]:
        """Stitch a list of lists of images together

        The input is a list of lists of lists of images.
        Each list of lists of images is stitched into one line horizontally.
        The resulting lines are then stitched together vertically.
        This is repeated for each list of lists of images.

        Args:
            tiles (List[List[List[File]]]): List of lists of lists of files to stitch together

        Raises:
            NotImplementedError: If the method is not implemented in a module
            StitchingError: If the stitching failed

        Returns:
            List[File]: List of File objects containing the stitched images
        """
        result = []

        for tile in tiles:
            result.append(self.stitch(tile))

        return result

class BlenderStitcher(BaseStitcher):
    """Stitcher module using Blender to stitch images
    """
    def __init__(self, cube2sphere_path: Optional[str] = None):
        """Initialize the BlenderStitcher

        Args:
            cube2sphere_path (Optional[str], optional): Path to the cube2sphere binary. Defaults to None, which will try to find the binary in the PATH.
        """
        super().__init__()
        self.cube2sphere_path = cube2sphere_path or "cube2sphere"

    def cubemap_to_equirectangular(self, files: List[File], rotation: Tuple[int, int, int] = (0, 0, 0)) -> File:
        """Stitch a cubemap into an equirectangular image

        Args:
            files (List[File]): List of 6 files representing the 6 faces of the cubemap [back, right, front, left, up, down].

        Raises:
            StitchingError: If the stitching failed
            ValueError: If the number of provided input files is not 6

        Returns:
            File: File object containing the stitched image
        """
        
        if len(files) != 6:
            raise ValueError("Exactly 6 files are required!")

        with tempfile.TemporaryDirectory() as tempdir:
            for i, file in enumerate(files):
                with (Path(tempdir) / f"{self.CUBEMAP_ORDER[i]}.png").open("wb") as f:
                    f.write(file.file.read())

            height = PIL.Image.open(files[0].file).height * 2
            width = PIL.Image.open(files[0].file).width * 4

            command = [
                self.cube2sphere_path,
                "front.png",
                "back.png",
                "right.png",
                "left.png",
                "up.png",
                "down.png",
                "-R", str(rotation[0]), str(rotation[1]), str(rotation[2]),
                "-o", "out",
                "-f", "png",
                "-r", str(width), str(height),
                ]

            result = subprocess.run(command, cwd=tempdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode != 0:
                self.logger.error(command)
                self.logger.error(result.stderr.decode("utf-8"))
                self.logger.error(result.stdout.decode("utf-8"))
                self.logger.debug(tempdir)
                time.sleep(600)
                raise StitchingError(f"cube2sphere stitching failed for conversion {files[0].conversion.id}")

            with (Path(tempdir) / "out0001.png").open("rb") as f:
                result = File.objects.create(conversion=files[0].conversion, file=ContentFile(f.read(), name="result.png"), mime_type="image/png")

            return result

class PILStitcher(BaseStitcher):
    """Stitcher module using PIL to stitch images
    """
    def cubemap_to_equirectangular(self, files: List[File], rotation: Tuple[int, int, int] = (0, 0, 0)) -> File:
        '''Stitch a cubemap into an equirectangular image

        This method does not use Blender, but instead uses PIL to stitch the images together.
        This algorithm is not thoroughly tested and may not work correctly.

        Args:
            files (List[File]): List of 6 files representing the 6 faces of the cubemap [back, right, front, left, up, down]
            rotation (Tuple[int, int, int], optional): Not supported by this stitcher. Defaults to (0, 0, 0).

        Raises:
            StitchingError: If the stitching failed

        Returns:
            File: File object containing the stitched image
        '''

        if len(files) != 6:
            raise ValueError("Exactly 6 files are required!")

        back, right, front, left, top, bottom = [PIL.Image.open(f.file) for f in files]

        dim = left.size[0]

        raw = []

        t_width = dim * 4
        t_height = dim * 2

        for y in range(t_height):
            v = 1.0 - (float(y) / t_height)
            phi = v * math.pi

            for x in range(t_width):
                u = float(x) / t_width
                theta = u * math.pi * 2

                x = math.cos(theta) * math.sin(phi)
                y = math.sin(theta) * math.sin(phi)
                z = math.cos(phi)

                a = max(abs(x), abs(y), abs(z))

                xx = x / a
                yy = y / a
                zz = z / a

                if yy == -1:
                    currx = int(((-1 * math.tan(math.atan(x / y)) + 1.0) / 2.0) * dim)
                    ystore = int(((-1 * math.tan(math.atan(z / y)) + 1.0) / 2.0) * (dim - 1))
                    part = left

                elif xx == 1:
                    currx = int(((math.tan(math.atan(y / x)) + 1.0) / 2.0) * dim)
                    ystore = int(((math.tan(math.atan(z / x)) + 1.0) / 2.0) * dim)
                    part = front

                elif yy == 1:
                    currx = int(((-1 * math.tan(math.atan(x / y)) + 1.0) / 2.0) * dim)
                    ystore = int(((math.tan(math.atan(z / y)) + 1.0) / 2.0) * (dim - 1))
                    part = right

                elif xx == -1:
                    currx = int(((math.tan(math.atan(y / x)) + 1.0) / 2.0) * dim)
                    ystore = int(((-1 * math.tan(math.atan(z / x)) + 1.0) / 2.0) * (dim - 1))
                    part = back

                elif zz == 1:
                    currx = int(((math.tan(math.atan(y / z)) + 1.0) / 2.0) * dim)
                    ystore = int(((-1 * math.tan(math.atan(x / z)) + 1.0) / 2.0) * (dim - 1))
                    part = bottom

                else:
                    currx = int(((-1 * math.tan(math.atan(y / z)) + 1.0) / 2.0) * dim)
                    ystore = int(((-1 * math.tan(math.atan(x / z)) + 1.0) / 2.0) * (dim - 1))
                    part = top

                curry = (dim - 1) if ystore > (dim - 1) else ystore

                if curry > (dim - 1):
                    curry = dim - 1

                if currx > (dim - 1):
                    currx = dim - 1

                raw.append(part.getpixel((currx, curry)))

        bio = io.BytesIO()
        PIL.Image.frombytes("RGB", (t_width, t_height), bytes(raw)).save(bio, "PNG")
        bio.seek(0)

        result = File.objects.create(conversion=files[0].conversion, file=ContentFile(output, name="result.png", mime_type="image/png"))

        return result

    def stitch(self, files: List[List[File]]) -> File:
        """Stitch a list of images together

        The input is a list of lists of images.
        Each list of images is stitched into one line horizontally.
        The resulting lines are then stitched together vertically.

        Args:
            files (List[List[File]]): List of lists of files to stitch together

        Raises:
            StitchingError: If the stitching failed

        Returns:
            File: File object containing the stitched image
        """
        if len(files) == 0:
            raise StitchingError("No files to stitch!")

        if len(files[0]) == 0:
            raise StitchingError("No files to stitch!")

        image_files = [[PIL.Image.open(f.file) for f in line] for line in files]

        width = image_files[0][0].width
        height = image_files[0][0].height

        for line in image_files:
            if len(line) != len(files[0]):
                raise ValueError("All lines must have the same length!")

            for file in line:
                if file.width != width or file.height != height:
                    raise ValueError("All files must have the same dimensions!")

        result = PIL.Image.new("RGB", (width * len(files[0]), height * len(files)))

        for y, line in enumerate(image_files):
            for x, file in enumerate(line):
                result.paste(file, (x * width, y * height))

        bio = io.BytesIO()
        result.save(bio, "PNG")
        bio.seek(0)

        result_file = File.objects.create(conversion=files[0][0].conversion, file=ContentFile(bio.read(), name="result.png"), mime_type="image/png")
        return result_file



DEFAULT_CUBEMAP_TO_EQUIRECTANGULAR_STITCHER = BlenderStitcher
DEFAULT_STITCHER = PILStitcher