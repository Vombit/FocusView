"""Logger configuration"""
import logging


def setup_logger(name: str) -> logging.Logger:
    """Creates and configures a logger by module name"""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create file handler
        # file_handler = logging.FileHandler('app.log')  # , 'utf-8'
        # file_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Add formatter to handler
        console_handler.setFormatter(formatter)
        # file_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(console_handler)
        # logger.addHandler(file_handler)

    return logger
