from logging.handlers import TimedRotatingFileHandler
from module.ardu import *
from datetime import datetime
import multiprocessing as mp
import logging, os

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_error = "%(asctime)s - [%(levelname)s] %(message)s (%(filename)s:%(lineno)d)"
    format = "%(asctime)s - [%(levelname)s] %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format_error + reset,
        logging.CRITICAL: bold_red + format_error + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def set_logger() -> logging.Logger:
    current_dir = os.path.dirname(os.path.realpath(__file__))
    log_dir = '{}/logs'.format(current_dir)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logger = logging.getLogger(('main' if __name__ == '__main__' else __name__).upper())
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] %(message)s')
    
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    file_handler = TimedRotatingFileHandler(
        log_dir+'/log',
        when='midnight',
        encoding='utf8'
    )
    file_handler.setLevel(logging.CRITICAL)
    file_handler.suffix = '%Y-%m-%d'
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info('Logger Initialization Sequence Complete')
    return logger


def set_local_folder():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = '{}/data'.format(current_dir)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)


def main():
    logger = set_logger()
    set_local_folder()
    ardu = Arduino(logger=logger)
    ardu.initUploadCompletionStatus()
    reset_count = 0
    while True:
        ardu.control_serial_port('open')
        ardu.read_data()
        ardu.save_local()
        reset_count += 1
        if ardu.isUploadCompleteCheck(): # 만약에 시간까지 고려해야한다면 여기에 시간 조건을 더하면 될 것 같다.
            p = mp.Pool(mp.cpu_count())
            p.apply_async(ardu.upload_thingspeak)
            p.close()
            reset_count -= 1
        ardu.control_serial_port('close')
        if reset_count > 120:
            try:
                p.terminate()
                reset_count = 0
                ardu.initUploadCompletionStatus()
                logger.warning('upload procedure has been \'RESET\' due to module did not respond.')
                # 여기서도 단순히 프로세스 종료가 아니라 (혹은 errcount따로 받아서) 1. 아두이노 리셋 / 센서 초기화, 2. CATM1 모듈 초기화
            except:
                logger.critical('Unexpected Error Ocurred!')
                # Process Reset Code Required
    # 파이썬 코드를 하나 더 만들어서 라즈베리파이 전체 재부팅 혹은 시스템 제어를 받는 건 어떨까 | 서버로 로그 보내주는것도 만들어보면 어떨까



if __name__ == '__main__':
    main()