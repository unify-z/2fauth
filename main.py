import app
from config.config_manager import config_manager
import logging

def main():
    web_server_cfg = app.WebServerConfig(host=str(config_manager.get("server.host", "0.0.0.0")),port=int(config_manager.get("server.port", 8000)),enable_access_log=config_manager.get("server.access_log"),uvicorn_log_level=config_manager.get("server.uvicorn_log_level")) # type: ignore
    web_server = app.WebServer(web_server_cfg)
    web_server.run()


if __name__ == "__main__":
    main()
