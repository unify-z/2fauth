from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import rtoml
from loguru import logger

class ConfigFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        logger.warning(f"Configuration file {event.src_path} has been modified, reloading...")
        config_manager.load_config()


class ConfigManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.load_config()
        event_handler = ConfigFileHandler()
        observer = Observer()
        observer.schedule(event_handler, path="./config", recursive=False)
        observer.start()
    
    def set(self, key: str, value):
        self.config[key] = value
        try:
            with open(self.config_path, 'w') as f:
                rtoml.dump(self.config, f)
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")

    def get(self,key: str,default=None):
        current = self.config
        parts = key.split('.')
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current

    def load_config(self):
        with open(self.config_path, 'r') as f:
            config = rtoml.load(f)
        logger.info(f"Loading config from {self.config_path}")
        return config
    
    def __repr__(self) -> str:
        return f"ConfigManager(config_path={self.config_path}, config={self.config})"


config_manager = ConfigManager('./config/config.toml')        