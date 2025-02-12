import logging
import logging.handlers
import os
import requests
from datetime import datetime,timedelta

# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "status.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)

# Environment variables
try:
    USERNAME = os.environ["USERNAME"]
    PASSWORD = os.environ["PASSWORD"]
    LESSONS = os.environ["LESSONS"]
except KeyError as e:
    logger.error(f"Missing environment variable: {str(e)}")
    exit(1)

def login_user_client(username: str, password: str) -> tuple[str, str]:
    url = "https://fitnessfactory.onvirtualgym.com/apiUsers.php?method=loginUserClient"
    payload = {
        "username": username,
        "password": password,
        "typeOS": 6,
        "deviceID": "derBq0jfQ8a7zRkWrOfd1o:APA91bFYmB4wMCTOzcvjC1sxz0HHkpfSFNEXc9ZlW72tBw_0EBtnBv-9Mdl6zkIcx5Q0lOb64kIQOLro4H4Ms0O_c_o2meHZ_pn5Xo-XbdcNcBEPK4Amz-g",
        "newVersion": 3,
        "appVersion": 313
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        data = response.json()
        token = data.get("token")
        num_socio = data.get("loginUserClient", [{}])[0].get("numSocio")
        return token, num_socio

    return None, None


def add_pre_reservation(token: str, num_socio: str, id_funcionarios_atividades_grupo: str) -> dict:
    url = "https://fitnessfactory.onvirtualgym.com/apiGroupClasses.php?method=addPreReservationOfClientToActivityGroupClasses"

    # Get current date and hour in the required format
    now = datetime.now()
    tomorrow = now + timedelta(days=1)  # Get tomorrow's date

    data_atividade = tomorrow.strftime("%Y-%m-%d")  # Tomorrow's date
    client_date_time = now.strftime("%Y-%m-%d %H")

    payload = {
        "fk_numSocio": num_socio,
        "data_atividade": data_atividade,
        "clientDateTime": client_date_time,
        "idFuncionariosAtividadesGrupo": id_funcionarios_atividades_grupo
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.json() if response.status_code == 200 else {"error": response.text}


if __name__ == "__main__":
    token, num_socio = login_user_client(USERNAME, PASSWORD)

    if not token or not num_socio:
        logger.error("Login failed. Check credentials.")
        exit(1)

    lesson_ids = LESSONS.split(",")  # Split the string into a list of IDs

    for lesson_id in lesson_ids:
        response = add_pre_reservation(token, num_socio, lesson_id.strip())
        logger.info(f'Pre-reservation finished: {response}')
