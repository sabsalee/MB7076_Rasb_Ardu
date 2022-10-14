from datetime import datetime
import logging
import serial
import socket
import pickle
# import requests

class Arduino():
    def __init__(self, logger: logging.Logger) -> None:

        self.logger = logger
        self.logger.info("Arduino Initialization Sequence Initiate")
        # DEFINE
        self.API_KEY: bytes = b"CRKG5DCWA6WDXEXP"
        self.FIELD: bytes = b"field3"
        self.read_datetime = None

        self.sensor_data: bytes = b'0'
        # self.port = serial.Serial('/dev/cu.usbmodem1401', 57600) # for DEV
        self.port = None
    def control_serial_port(self, opt):
        if opt == 'open':
            try:
                self.port = serial.Serial("/dev/ttyACM0", 57600)
                self.logger.info('Serial port opened.')
            except:
                self.logger.critical('Failed to open Serial port.')
        elif opt == 'close':    
            try:
                self.port.close()
                self.logger.info('Serial port closed.\n')
            except:
                self.logger.critical('Failed to close Serial port.\n')

    def read_data(self):
        try:
            self.sensor_data = self.port.readline().strip()
            self.read_datetime = datetime.now()
            self.logger.info(f'Data Successfully Transmit - {self.sensor_data.decode()}cm')
        except Exception as e:
            self.logger.critical(f'Reading Sensor Data from Arduino Failed. -> {e}')

    def save_local(self):
        try:
            with open(f'data/{self.read_datetime.strftime("%Y-%m-%d")}.txt', 'a') as f:
                __write_data = f"{self.read_datetime.strftime('%Y-%m-%d %H:%M:%S')} {self.sensor_data.decode()}cm\n"
                f.write(__write_data)
            self.logger.info('Data Saved in Local')
            return 1
        except Exception as e:
            self.logger.critical(f'Writing Local Data Failed -> {e}')
            return 0


    def initUploadCompletionStatus(self):
        with open('status.pkl', 'wb') as f:
            pickle.dump(True, f)
    
    def isUploadCompleteCheck(self):
        try:
            with open('status.pkl', 'rb') as f:
                status = pickle.load(f)
            return status
        except:
            with open('status.pkl', 'wb') as f:
                pickle.dump(True, f)
            return True
            
    def uploadCompletionStatusChange(self, status: bool):
        with open('status.pkl', 'wb') as f:
            pickle.dump(status, f)

    def upload_thingspeak(self):
        self.uploadCompletionStatusChange(False)
        logger = self.logger
        sensor_data = self.sensor_data
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            server_address = ('api.thingspeak.com', 80)
            self.logger.info('Connecting to {}, port: {}'.format(*server_address))
            sock.connect(server_address)
            logger.info('Socket Created.')

            try:
                req = b'GET /update'
                req += b"?api_key=" + self.API_KEY + b"&" + self.FIELD + b"=" + sensor_data
                req += b" HTTP/1.1\r\n"
                req += b"Host: api.thingspeak.com\r\n\r\n"
                req += b"Connection: close\r\n\r\n"

                self.logger.info('Sending - {!r}'.format(req))
                sock.send(req)
                self.logger.info('Sending Completed')
                res = sock.recv(12)
                self.logger.info('Received {!r}'.format(res))
            except Exception as e:
                logger.critical(f'Sending Data to Thingspeak Failed. -> {e}')
            finally:
                self.logger.info('Closing socket.')
                sock.close()
        except Exception as e:
            logger.critical(f'Creating Socket Failed. -> {e}')
        finally:
            self.uploadCompletionStatusChange(True)


    # def upload_thingspeak_by_requests(self):
    #     logger = self.logger
    #     try:
    #         logger.info(f'Sending Data to Thingspeak.')
    #         res = requests.get(f'http://api.thingspeak.com/update?api_key={self.API_KEY.decode()}&{self.FIELD.decode()}={self.sensor_data.decode()}')
    #         if res.status_code != 200:
    #             raise SendingToThingsspeakFailed(res.status_code)
    #         logger.info(f'Sending Completed.')
    #     except Exception as e:
    #         logger.critical(f'Sending Failed -> {e}')
            
class SendingToThingsspeakFailed(Exception):
    def __str__(self, code) -> str:
        return f'Not 200 received. errno is {code}'