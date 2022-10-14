from logging.handlers import TimedRotatingFileHandler
from module.ardu import *
from datetime import datetime
import multiprocessing as mp
import logging, os


def set_logger() -> logging.Logger:
    current_dir = os.path.dirname(os.path.realpath(__file__))
    log_dir = '{}/logs'.format(current_dir)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logger = logging.getLogger(('main' if __name__ == '__main__' else __name__).upper())
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] %(message)s')
    
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
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
    p = mp.Pool(mp.cpu_count)
    while True:
        ardu.control_serial_port('open')
        ardu.read_data()
        proc_save_local = p.apply_async(ardu.save_local)
        if ardu.isUploadCompleted: # 만약에 시간까지 고려해야한다면 여기에 시간 조건을 더하면 될 것 같다.
            proc_upload_ts = p.apply_async(ardu.upload_thingspeak)
        logger.debug("Function <save_local> returns successful endcode") if proc_save_local.get() else logger.debug("Function <save_local> returns error endcode")
        p.close()
        # ardu.save_local()
        # ardu.upload_thingspeak()
        ardu.control_serial_port('close')




if __name__ == '__main__':
    main()