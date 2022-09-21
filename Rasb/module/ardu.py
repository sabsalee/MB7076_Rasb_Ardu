from random import randint
from datetime import datetime
import logging
import serial
import socket

class Arduino():
    def __init__(self, logger: logging.Logger) -> None:

        self.logger = logger
        self.logger.info("Arduino Initialization Sequence Initiate")
        # DEFINE
        self.API_KEY: bytes = b"CRKG5DCWA6WDXEXP"
        self.FIELD: bytes = b"field3"
        self.read_datetime = None

        self.sensor_data: bytes = b'0'
        self.port = serial.Serial('/dev/cu.usbmodem1401', 57600) # for DEV
        # self.port = serial.Serial("/dev/ttyACM0", 57600)

    def read_data(self):
        try:
            self.sensor_data = self.port.readline().strip()
            self.read_datetime = datetime.now()
            self.logger.info(f'Data Successfully Transmit - {self.sensor_data.decode()}cm')
        except:
            self.logger.critical('Reading Sensor Data from Arduino Failed.')

    def save_local(self):
        try:
            with open(f'data/{self.read_datetime.strftime("%Y-%m-%d")}.txt', 'a') as f:
                __write_data = f"{self.read_datetime.strftime('%Y-%m-%d %H:%M:%S')} {self.sensor_data.decode()}cm\n"
                f.write(__write_data)
            self.logger.info('Data Saved in Local')
        except:
            self.logger.critical('Writing Local Data Failed')

    def upload_thingspeak(self):
        logger = self.logger
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            server_address = ('api.thingspeak.com', 80)
            self.logger.info('Connecting to {}, port: {}'.format(*server_address))
            sock.connect(server_address)
            logger.info('Socket Created.')

            try:
                req = b'GET /update'
                req += b"?api_key=" + self.API_KEY + b"&" + self.FIELD + b"=" + self.sensor_data
                req += b" HTTP/1.1\r\n"
                req += b"Host: api.thingspeak.com\r\n"
                req += b"Connection: close\r\n\r\n"

                self.logger.info('Sending - {!r}'.format(req))
                sock.sendall(req)
                self.logger.info('Sending Completed')
                res = sock.recv(2048)
                self.logger.info('Received {!r}'.format(res))
            except Exception as e:
                logger.critical(f'Sending Data to Thingspeak Failed. -> {e}')
            finally:
                self.logger.info('Closing socket.')
                sock.close()
        except:
            logger.critical('Creating Socket Failed.')