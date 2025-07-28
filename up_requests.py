# -*- coding: utf-8 -*-
import requests
import json

import up_config_manager
import up_logger_manager

"""
json 값을 api로 센서 보내기 위한 클래스 
"""

class apiRequestManager:

    def __init__(self):
        server_url = up_config_manager.ConfigManager().get_url()
        self.url = "http://"+server_url['host']+":"+server_url['port']+"/"
        print(self.url)
        self.headers = {"Content-Type": "application/json"}

    def send_sensor_data(self, url_type, sensor_id, sensor_type, sensor_value):
        data = {
            "id": sensor_id,
            "type": sensor_type,
            "value": sensor_value
        }

        try:
            response = requests.post(
                self.url+str(url_type),
                data=json.dumps(data),
                headers=self.headers,
                timeout=5
            )

            response.raise_for_status()  # HTTP 오류 발생 시 예외 처리
            return response.json()  # 응답이 JSON이면 파싱해서 반환

        except requests.exceptions.RequestException as e:
            print(f"[에러] 센서 전송 실패: {e}")
            return None


if __name__ == '__main__':
    log_manager = up_logger_manager.LoggerManager()

    info_logger = log_manager.get_logger('info')
    serial_logger = log_manager.get_logger('serial')

    urlManager = apiRequestManager()
    try:
        serial_logger.info('api request Test Start')

        res = urlManager.send_sensor_data("irrigation_sensor", "s001", "press", 123.1)
        serial_logger.info(f"api request Test Start,{res}")

    except Exception as E:
        print(E)