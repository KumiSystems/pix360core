from .classes import HTTPRequest, InstallError

import json
import subprocess

class Installer:
    MODULES_JSON = "https://git.kumi/-/snippets/131/raw/main/modules.json"

    def __init__(self):
        self.available_modules = self.fetch_modules()

    def fetch_modules(self):
        request = HTTPRequest(self.MODULES_JSON).open()
        return json.loads(request.read().decode())

    def install_all(self):
        for module in self.available_modules:
            try:
                self.install_module(module)
            except InstallError as e:
                print(f"Error while installing module {module['name']}: {e}")

    def install_module(self, module):
        try:
            subprocess.run(["pip", "install", "-U", module["source"]], check=True)
        except Exception as e:
            raise InstallError(f"Error while installing module {module['name']}: {e}") from e

if __name__ == "__main__":
    installer = Installer()
    installer.install_all()