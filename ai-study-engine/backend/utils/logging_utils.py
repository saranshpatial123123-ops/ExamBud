import logging
import sys

def get_logger(module_name: str) -> logging.Logger:
    """
    Returns a configured structured logger to streamline tracing across the distributed domains.
    """
    logger = logging.getLogger(module_name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        # Use stdout for production safety compatible with cloud execution wrappers
        handler = logging.StreamHandler(sys.stdout)
        
        # Consistent structured formatting
        formatter = logging.Formatter(
            '%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger
