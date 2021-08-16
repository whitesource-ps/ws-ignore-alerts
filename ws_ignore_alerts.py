import argparse
import logging
import os
import shutil
import sys
from configparser import ConfigParser

from ws_sdk import ws_constants
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
AGENT_NAME = "ignore-alerts"
AGENT_VERSION = "0.1.6"


class Configuration:
    def __init__(self):
        config = ConfigParser()
        config.optionxform = str
        config.read('./config/params.config')
        # WS Settings
        self.url = config.get('DEFAULT', 'wsUrl')
        self.user_key = config.get('DEFAULT', 'userKey')
        self.org_token = config.get('DEFAULT', 'orgToken')
        self.product_token = config.get('DEFAULT', 'productToken')
        self.baseline_project_token = config.get('DEFAULT', 'baselineProjectToken', fallback=False)
        self.dest_project_name = config.get('DEFAULT', 'destProjectName', fallback=False)
        self.dest_project_version = config.get('DEFAULT', 'destProjectVersion', fallback=False)


class ArgumentsParser:
    def __init__(self):
        """

        :return:
        """
        parser = argparse.ArgumentParser(description="Arguments parser")
        parser.add_argument("-u", "--url", help="WS url", dest='url', required=False)
        parser.add_argument("-k", "--userKey", help="WS User Key", dest='user_key', required=False)
        parser.add_argument("-o", "--orgToken", help="WS Org Token", dest='org_token', required=False)
        parser.add_argument("-p", "--productToken", help="WS Product Token", dest='product_token', required=False)
        parser.add_argument("-b", "--baselineProjectToken", help="WS Baseline project token",
                            dest='baseline_project_token', required=False)
        parser.add_argument("-n", "--destProjectName", help="WS Destination Project Name",
                            dest='dest_project_name', required=False)
        parser.add_argument("-v", "--destProjectVersion", help="WS Destination Project Version",
                            dest='dest_project_version', required=False)
        self.args = parser.parse_args()


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
    if len(args) >= 8:
        parser = ArgumentsParser()
        config = parser.args
    else:
        config = Configuration()
    creating_folder_and_log_file()
    init_logger()

    logger.info("Starting")

    conn = WS(url=config.url,
              user_key=config.user_key,
              token=config.product_token,
              token_type=ws_constants.PRODUCT,
              tool_details=("ps-"+AGENT_NAME, AGENT_VERSION))

    # default for the source project token is a baseline_project_token provided by user
    config_dest_project_name = config.dest_project_name
    config_baseline_project_token = config.baseline_project_token
    if config_baseline_project_token and config_dest_project_name:
        if config.dest_project_version:
            config_dest_project_name = f"{config_dest_project_name} - {config.dest_project_version}"
        try:
            source_project_token = config_baseline_project_token
            dest_projects_by_project_name = conn.get_scopes(name=config_dest_project_name)
        except Exception:
            logging.exception("The destination project hasn't been found")
            exit(1)
        if len(dest_projects_by_project_name) == 1:
            dest_project_token = dest_projects_by_project_name[0].get(TOKEN)
        else:
            raise ProcessLookupError(f"There are more than one project with the same name {config_dest_project_name}")

    else:
        try:
            source_project, destination_project = get_source_and_destination_projects(conn, config)
        except Exception as err:
            logging.error(err)
            exit(1)
        source_project_token = source_project.get(TOKEN)
        dest_project_token = destination_project.get(TOKEN)

    logging.info('Fetching all ignored alerts from the source/baseline project')
    source_ignored_alerts_list = conn.get_alerts(token=source_project_token, ignored=True)

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

    ignore_alerts(lib_to_ignore_from_source_dict, destination_alerts_dict, conn, config)


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
             Two last projects of the certain product.
    """
    logging.debug('Getting all projects and sort them')
    all_projects = conn.get_projects()
    if len(all_projects) >= 2:
        all_projects.sort(key=lambda x: x['lastUpdatedDate'])
        logging.debug('Find last (new) and penultimate projects')
        source_project = all_projects[-2]
        destination_project = all_projects[-1]
    else:
        raise ProcessLookupError("There are no enough projects in the product. Should be minimum 2.")

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


def ignore_alerts(lib_to_ignore_from_source_dict, destination_alerts_dict, conn, config):
    """

    :rtype: object
    """
    print_header('Ignore alerts in the new project')

    response = None
    for key, value in lib_to_ignore_from_source_dict.items():
        if key in destination_alerts_dict.keys():
            value_dest = destination_alerts_dict.get(key)
            try:
                conn.token = config.org_token
                conn.token_type = ws_constants.ORGANIZATION
                response = conn.set_alerts_status(alert_uuids=value_dest.get('alertUuid'),
                                                  status="Ignored",
                                                  comments="automatically ignored by WS utility")
                if "Successfully set the alert's status" not in response.values():
                    logger.error(response)
                    return
            except:
                logger.error(response)
                return
            print_to_log(key, value_dest)

    if response:
        logger.info('Ignoring alerts has successfully finished')
    else:
        logger.info('There are no alerts to ignore')


def print_to_log(key, value_dest):
    """

    :param key:
    :param value_dest:
    """
    string_buffer = "{0} alert has been automatically ignored. Library: {1}". \
        format(key[0], value_dest.get('library').get('filename'))
    if key[0] == "SECURITY_VULNERABILITY":
        string_buffer += ", vulnerability:  {0}".format(key[1])
    logger.info(string_buffer)


if __name__ == '__main__':
    main()
