"""
g4py/g4dl.py
- Geant4 download and installation automation
"""

import os, platform, requests, subprocess, argparse, sys
from pathlib import Path
from bs4 import BeautifulSoup as bs4
from argparse import Namespace

# ---------------- Argument Parser ----------------
parser = argparse.ArgumentParser(
    description="Geant4 download and installation automation",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""Examples:
  ./g4dl
      Downloads and installs the latest Geant4 version.

  ./g4dl --version 11.2.1
      Downloads and installs Geant4 version 11.2.1.

  ./g4dl -V 10.7.3
      Downloads and installs Geant4 version 10.7.3.
"""
)

parser.add_argument(
    "-V", "--version",
    type=str,
    help="Specify Geant4 version (e.g., 11.2.1). Defaults to latest if not provided."
)

class Args(Namespace):
    version: str

args: Args = parser.parse_args()

subprocess.run(["echo", """'
-----------------------------------------------------------------------
        ___________________   _____    _______________________  
       /  _____/\_   _____/  /  _  \   \      \__    ___/  |  | 
      /   \  ___ |    __)_  /  /_\  \  /   |   \|    | /   |  |_
      \    \_\  \|        \/    |    \/    |    \    |/    `   /
       \______  /_______  /\____|__  /\____|__  /____|\____   | 
              \/        \/         \/         \/           |__| 

            ✨ GEANT4 INSTALLATION AUTOMATION PROGRAM

            AUTHOR: MOHAK KETAN PATIL

            This program downloads and installs the specified
            version of Geant4 from the official website.

-----------------------------------------------------------------------
'
"""])

absPath = Path().absolute()

"""
absPath <--
"""

# ---------------- Version Handling ----------------
if args.version:
    g4Version = args.version
else:
    g4homePage = requests.get("https://geant4.web.cern.ch").content
    g4homePageParsed = bs4(g4homePage, "html5lib")
    g4Version = g4homePageParsed.find(string="Latest: ").find_next_sibling("a").text
    user_input = input(f"Download latest Geant4 version {g4Version}? [y/n]: ").strip().lower()
    if user_input != 'y':
        print("❌ Aborted download.\n")
        sys.exit(0)
    print(f"Downloading latest version...\n")

# ---------------- Download Page ----------------
try:
    g4dlPage = requests.get(f"https://geant4.web.cern.ch/download/{g4Version}.html")
    g4dlPage.raise_for_status()
    g4dlPageParsed = bs4(g4dlPage.content, "html5lib")
except requests.exceptions.HTTPError:
    subprocess.run(["echo", f"❌ ERROR: Geant4 version {g4Version} not found on the official website.\n"])
    sys.exit(1)
except Exception:
    subprocess.run(["echo", f"❌ ERROR: Failed to fetch Geant4 version {g4Version}. Please check your network or version number.\n"])
    sys.exit(1)

# Download link for tar file of Geant4
g4tarLink = g4dlPageParsed.find(string="Download tar.gz").parent["href"]

# Download link for datasets of Geant4
g4datasetATags = g4dlPageParsed.find("h4", {"id": "datasets"}).find_next_sibling("p").find_all("a")

# Directory paths
g4_dir         = f"{absPath}/geant4-v{g4Version}"
g4_build_dir   = f"{absPath}/geant4-v{g4Version}-build"
g4_install_dir = f"{absPath}/geant4-v{g4Version}-install"
g4_tars_dir    = f"{absPath}/geant4-v{g4Version}-tars"
g4_data_dir    = f"{g4_install_dir}/share/Geant4/data"

if platform.system() == "Linux":
    subprocess.run("""
                        sudo apt install
                        cmake cmake-curses-gui gcc g++
                        qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools
                        libexpat1-dev libxmu-dev libmotif-dev
                   """
                   .split())

    g4tar = g4tarLink.split("/")[-1]
    if not os.path.exists(f"{g4_dir}.tar.gz"):
        subprocess.run(["wget", g4tarLink])
    if not os.path.exists(g4_dir):
        subprocess.run(["tar", "-xvf", f"{g4_dir}.tar.gz"])

if platform.system() == "Darwin":
    subprocess.run(["xcode-select", "--install"])
    subprocess.run("""
                        /bin/bash -c
                        \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"
                   """
                   .split())
    subprocess.run(["brew", "install", "--cask", "cmake"])
    subprocess.run(["brew", "install", "qt@5"])
    subprocess.run(["brew", "install", "xerces-c"])
    subprocess.run(["curl", "-OL", g4tarLink])
    subprocess.run(["tar", "-xvf", f"geant4-v{g4Version}.tar.gz"])

if platform.system() == "Windows":
    subprocess.run(["winget", "install", "kitware.cmake"])
    subprocess.run(["curl", g4tarLink, "-O", g4tarLink.split("/")[-1]])
    subprocess.run(["tar", "-x", g4tarLink.split("/")[-1]])

"""
absPath <--
    |____ g4
    |____ g4.tar.gz
"""

if not os.path.exists(g4_build_dir):
    os.makedirs(g4_build_dir)
os.chdir(g4_build_dir)

"""
absPath
    |____ g4
    |____ g4-build <--
    |____ g4.tar.gz
"""

subprocess.run(f"""
                    cmake
                    -DCMAKE_INSTALL_PREFIX={g4_install_dir}
                    {g4_dir}
                """
                .split())
subprocess.run(["make", f"-j{os.cpu_count() - 1}"])
subprocess.run(["make", "install"])

"""
absPath
    |____ g4
    |____ g4-build <--
    |____ g4-install
    |____ g4.tar.gz
"""

if not os.path.exists(g4_tars_dir):
    os.makedirs(g4_tars_dir)
os.chdir(g4_tars_dir)

"""
absPath
    |____ g4
    |____ g4-build
    |____ g4-install
    |____ g4-tars <--
    |____ g4.tar.gz
"""

for ATag in g4datasetATags:
    datasetLink = ATag["href"]
    dataset     = datasetLink.split("/")[-1]
    if not os.path.exists(f"{g4_tars_dir}/{dataset}"):
        subprocess.run(["wget", datasetLink])

"""
absPath
    |____ g4
    |____ g4-build
    |____ g4-install
    |____ g4-tars <--
            |____ g4ds0.tar.gz
            |____ g4ds1.tar.gz
            |____ ...
    |____ g4.tar.gz
"""

if not os.path.exists(g4_data_dir):
    os.makedirs(g4_data_dir)
os.chdir(g4_data_dir)

"""
absPath
    |____ g4
    |____ g4-build
    |____ g4-install
            |____ share
                    |____ Geant4
                            |____ data <--
    |____ g4-tars
            |____ g4ds0.tar.gz
            |____ g4ds1.tar.gz
            |____ ...
    |____ g4.tar.gz
"""

for dataset in os.listdir(g4_tars_dir):
    if dataset[:-7] not in os.listdir(g4_data_dir):
        subprocess.run(["tar", "-xvf", f"{g4_tars_dir}/{dataset}"])

"""
absPath
    |____ g4
    |____ g4-build
    |____ g4-install
            |____ share
                    |____ Geant4
                            |____ data <--
                                    |____ g4ds0
                                    |____ g4ds1
                                    |____ ...
    |____ g4-tars
            |____ g4ds0.tar.gz
            |____ g4ds1.tar.gz
            |____ ...
    |____ g4.tar.gz
"""

os.chdir(g4_build_dir)

"""
absPath
    |____ g4
    |____ g4-build <--
    |____ g4-install
    |____ g4-tars
    |____ g4.tar.gz
"""

subprocess.run(f"""
                    cmake
                    -DGEANT4_INSTALL_DATADIR={g4_install_dir}/share/Geant4/data
                    -DGEANT4_USE_QT=ON
                    .
                """
                .split())
subprocess.run(["make", f"-j{os.cpu_count() - 1}"])
subprocess.run(["make", "install"])

if platform.system() == "Linux":
    with open(os.path.join(os.path.expanduser('~'), '.bashrc'), "a") as bashrc:
        bashrc.write(f"source {g4_install_dir}/share/Geant4/geant4make/geant4make.sh")

if platform.system() == "Darwin":
    with open(os.path.join(os.path.expanduser('~'), '.zshrc'), "a") as zshrc:
        zshrc.write(f"source {g4_install_dir}/share/Geant4/geant4make/geant4make.sh")

subprocess.run(["echo", """'
-----------------------------------------------------------------------
        ___________________   _____    _______________________  
       /  _____/\_   _____/  /  _  \   \      \__    ___/  |  | 
      /   \  ___ |    __)_  /  /_\  \  /   |   \|    | /   |  |_
      \    \_\  \|        \/    |    \/    |    \    |/    `   /
       \______  /_______  /\____|__  /\____|__  /____|\____   | 
              \/        \/         \/         \/           |__| 

            ✅ GEANT4 INSTALLATION COMPLETED

            AUTHOR: MOHAK KETAN PATIL
            GITHUB: mohak300501/g4py

            Thank you for using this automation
            program to download and install GEANT4.

            [GEANT4 ASCII art generated from -
                https://patorjk.com/software/taag/]

-----------------------------------------------------------------------
'"""])
