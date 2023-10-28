import subprocess
import sys

def install(package):
    #Allows you to install external python packages inside blender.
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    ##Example usage: install('pandas')


required_packages= ["matplotlib","pandas","klayout","tornado","psutil","keyboard"]

for package in required_packages:
	install(package)