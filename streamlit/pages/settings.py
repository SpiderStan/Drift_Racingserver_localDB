from typing import Set
import socket

from pydantic import BaseSettings

def gethostname():
    name = ""
    try:
        name = socket.gethostbyname("host.docker.internal")
    except:
        pass

    if name == "":
        name = socket.gethostname()
    return name


class Settings(BaseSettings):
    """Parameters to be loaded from Environment Variables in .env file"""

    # Database
    driftapi_path: str = "http://localhost:8000"
    hostname:str = gethostname()
    ip_address:str = "xxx.yyy.zzz.xyz"   # always set your local IP-Address here! (Windows cmd: ipconfig / Linux shell: ifconfig )

    class Config:
        env_prefix = "STREAMLIT_"
        env_file = ".env"
