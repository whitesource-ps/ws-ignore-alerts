import argparse
import os
import shutil
import sys
import logging
from configparser import ConfigParser
from ws_sdk import ws_utilities
from ws_sdk.web import WS

LOG_DIR = 'logs'
LOG_FILE_WITH_PATH = LOG_DIR + '/ws-ignore-alerts.log'
TOKEN = "token"

logger = logging.getLogger()

url = ''
user_key = ''
org_token = ''
product_token = ''


class Configuration:
    def __init__(self):
        config = ConfigParser()
        config.optionxform = str
        config.read('./config/params.config')
        # WS Settings
        self.url = config.get('DEFAULT', 'WsUrl')
        self.user_key = config.get('DEFAULT', 'UserKey')
        self.org_token = config.get('DEFAULT', 'OrgToken')
        self.product_token = config.get('DEFAULT', 'ProductToken')


class ArgumentsParser:
    def __init__(self):
        """

        :return:
        """
        parser = argparse.ArgumentParser(description="Description for my parser")
        parser.add_argument("-u", required=False)
        parser.add_argument("-k", required=False)
        parser.add_argument("-o", required=False)
        parser.add_argument("-p", required=False)

        argument = parser.parse_args()
        if argument.u:
            self.url = argument.u
        if argument.k:
            self.user_key = argument.k
        if argument.o:
            self.org_token = argument.o
        if argument.p:
            self.product_token = argument.p


def init_logger():
    """
    Initializes loggers to include timestamps and set outputs

    :return:
    """
    logger = logging.getLogger()
    format_string = '[%(asctime)s] %(message)s'
    formatter = logging.Formatter(format_string)
    std_handler = logging.StreamHandler(sys.stdout)
    std_handler.setFormatter(formatter)
    std_handler.setLevel(logging.INFO)
    debug_handler = logging.FileHandler(LOG_FILE_WITH_PATH)
    debug_handler.setFormatter(formatter)
    debug_handler.setLevel(logging.DEBUG)
    logger.addHandler(std_handler)
    logger.addHandler(debug_handler)
    logger.setLevel(logging.DEBUG)


def main():

    print_header('WhiteSource - Ignore Future Alerts')

    args = sys.argv[1:]
    if len(args) == 8:
        config = ArgumentsParser()
    else:
        config = Configuration()
    creating_folder_and_log_file()
    init_logger()

    logger.info("Starting")

    conn = WS(url=config.url,
              user_key=config.user_key,
              token=config.org_token,
              timeout=300)

    source_project, destination_project = get_source_and_destination_projects(conn, config)

    source_project_token = source_project.get(TOKEN)
    logging.info('Fetching ignored alerts from the last project')
    source_ignored_alerts_list = conn.get_alerts(token=source_project_token, ignored=True)

    dest_project_token = destination_project.get(TOKEN)
    logging.info('Fetching all alerts from the new project')
    dest_all_alerts_list = conn.get_alerts(token=dest_project_token)

    libs_to_ignore_from_source_list = get_libs_to_ignore_from_source_list(source_ignored_alerts_list)

    destination_alerts_dict = ws_utilities.convert_dict_list_to_dict(lst=dest_all_alerts_list,
                                                                     key_desc=('type',
                                                                               {'vulnerability': 'name'},
                                                                               {'library': 'keyUuid'}))

    lib_to_ignore_from_source_dict = ws_utilities.convert_dict_list_to_dict(lst=libs_to_ignore_from_source_list,
                                                                            key_desc=('type',
                                                                                      'vulnerabilityName',
                                                                                      'libKeyUuid'))

    ignore_alerts(lib_to_ignore_from_source_dict, destination_alerts_dict, conn)


def print_header(hdr_txt: str):
    hdr_txt = ' {0} '.format(hdr_txt)
    hdr = '\n{0}\n{1}\n{0}'.format(('=' * len(hdr_txt)), hdr_txt)
    print(hdr)


def creating_folder_and_log_file():
    """
    Create empty directories for logs and scan results
    Directories from previous runs are deleted

    :return:
    """
    if os.path.exists(LOG_DIR):
        shutil.rmtree(LOG_DIR)
    os.makedirs(LOG_DIR, exist_ok=True)


def get_source_and_destination_projects(conn, config):
    """

    :param conn:
    :param config:
    :return: the source is a project for pulling ignored alerts and
             destination is a project where the alerts will be ignored.
             Two last projects of the product.
    """
    logging.debug('Getting all projects and sort them')
    all_projects = conn.get_projects(product_token=config.product_token)
    all_projects.sort(key=lambda x: x['lastUpdatedDate'])
    logging.debug('Find last (new) and penultimate projects')
    source_project = all_projects[-2]
    destination_project = all_projects[-1]

    return source_project, destination_project


def get_libs_to_ignore_from_source_list(source_ignored_alerts_list):
    """

    :param source_ignored_alerts_list:
    :return: list of dicts, each dict represents a key for future ignore
    """
    libs_to_ignore_from_source_list = []
    logging.debug('Creating a list of dicts. Each dict includes vulnerability name, type and lib')
    for source_alert_dict in source_ignored_alerts_list:
        vulnerability_name = ''
        if source_alert_dict.get('vulnerability'):
            vulnerability_name = source_alert_dict.get('vulnerability').get('name')
        new_dict = {
            'vulnerabilityName': vulnerability_name,
            'type': source_alert_dict.get('type'),
            'libKeyUuid': source_alert_dict.get('library').get('keyUuid'),
        }
        libs_to_ignore_from_source_list.append(new_dict)

    return libs_to_ignore_from_source_list


def ignore_alerts(lib_to_ignore_from_source_dict, destination_alerts_dict, conn):
    """

    :rtype: object
    """
    print_header('Ignore alerts in the new project')
    for key, value in lib_to_ignore_from_source_dict.items():
        if key in destination_alerts_dict.keys():
            value_dest = destination_alerts_dict.get(key)
            try:
                response = conn.set_alerts_status(alert_uuids=value_dest.get('alertUuid'),
                                                  status="Ignored",
                                                  comments="automatically ignored by WS utility")
                if "Successfully set the alert's status" not in response.values():
                    logger.info(response)
                    return
            except:
                logger.info(response)
            print_to_log(key, value_dest)
    logger.info('Ignoring alerts has successfully finished')


def print_to_log(key, value_dest):
    """

    :param key:
    :param value_dest:
    """
    string_buffer = "{0} alert has been automatically ignored. Library: {1}".\
        format(key[0], value_dest.get('library').get('filename'))
    if key[0] == "SECURITY_VULNERABILITY":
        string_buffer += ", vulnerability:  {0}".format(key[1])
    logger.info(string_buffer)


if __name__ == '__main__':
    main()





