import argparse
import logging
import os
import shutil
import sys
from configparser import ConfigParser
from dataclasses import dataclass

from ws_sdk import ws_constants,ws_utilities, WS

from ws_ignore_alerts._version import __description__, __tool_name__, __version__

LOG_DIR = 'logs'
LOG_FILE_WITH_PATH = LOG_DIR + '/ws-ignore-alerts.log'
TOKEN = 'token'
logger = logging.getLogger()

url = None
user_key = None
org_token = None
product_token = None


def parse_config():
    @dataclass
    class Config:
        url: str
        user_key: str
        org_token: str
        product_token: str
        baseline_project_token: str
        dest_project_name: str
        dest_project_version: str
        dest_project_token: str
        dest_product_token: str
        whitelist: str

    if len(sys.argv) < 3:
        maybe_config_file = True
    if len(sys.argv) == 1:
        conf_file = "../params.config"
    elif not sys.argv[1].startswith('-'):
        conf_file = sys.argv[1]
    else:
        maybe_config_file = False

    if maybe_config_file:                             # Covers no conf file or only conf file
        if os.path.exists(conf_file):
            logger.info(f"loading configuration from file: {conf_file}")
            config = ConfigParser()
            config.optionxform = str
            # if os.path.exists(conf_file):
            #     logger.info(f"loading configuration from file: {conf_file}")
            config.read(conf_file)
            conf = Config(

                url = config.get('DEFAULT', 'wsUrl'),
                user_key = config.get('DEFAULT', 'userKey'),
                org_token = config.get('DEFAULT', 'orgToken'),
                product_token = config.get('DEFAULT', 'productToken'),
                baseline_project_token = config.get('DEFAULT', 'baselineProjectToken', fallback=False),
                dest_project_name = config.get('DEFAULT', 'destProjectName', fallback=False),
                dest_project_version = config.get('DEFAULT', 'destProjectVersion', fallback=False),
                dest_project_token = config.get('DEFAULT', 'destProjectToken', fallback=False),
                dest_product_token = config.get('DEFAULT', 'destProductToken', fallback=False),
                whitelist = config.get('DEFAULT', 'whitelist', fallback=False)
            )
        else:
            logger.error(f"No configuration file found at: {conf_file}")
            raise FileNotFoundError
    else:
        parser = argparse.ArgumentParser(description=__description__)
        parser.add_argument('-u', '--url', help='WS url', dest='url', required=False)
        parser.add_argument('-k', '--userKey', help='WS User Key', dest='user_key', required=False)
        parser.add_argument('-o', '--orgToken', help='WS Org Token', dest='org_token', required=False)
        parser.add_argument('-p', '--productToken', help='WS Product Token', dest='product_token', required=False)
        parser.add_argument('-b', '--baselineProjectToken', help='WS Baseline project token',dest='baseline_project_token', required=False)
        parser.add_argument('-n', '--destProjectName', help='WS Destination Project Name', dest='dest_project_name', required=False)
        parser.add_argument('-v', '--destProjectVersion', help='WS Destination Project Version',dest='dest_project_version', required=False)
        parser.add_argument('-t', '--destProjectToken', help='WS Destination Project Token',dest='dest_project_token', required=False)
        parser.add_argument('-d', '--destProductToken', help='WS Destination Product Token',dest='dest_product_token', required=False)
        parser.add_argument('-w', '--whitelist', help='CVE white list file',dest='whitelist', required=False)
        conf = parser.parse_args()

    return conf


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
    global cve_whitelist

    try:
        config = parse_config()
    except FileNotFoundError:
        exit(-1)
    creating_folder_and_log_file()
    init_logger()

    logger.info('Starting')
    cve_whitelist = []
    if config.whitelist:
        try:
            with open(config.whitelist, 'r') as file:
                cve_whitelist = [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            #logger.error(f"File '{config.whitelist}' not found.")
            cve_whitelist = config.whitelist.split(",")

    conn = WS(url=config.url,
              user_key=config.user_key,
              token=config.product_token,
              token_type=ws_constants.PRODUCT,
              tool_details=(f"ps-{__tool_name__.replace('_', '-')}", __version__))

    config_dest_project_name = config.dest_project_name
    config_baseline_project_token = config.baseline_project_token
    if config_baseline_project_token:
        source_project_token = config_baseline_project_token
        # getting tokens when destination project and source/baseline projects are provided by the user
        if config.dest_project_token:
            dest_project_token = config.dest_project_token
        # else looking for a destination project token by project name (version) that has been provided by the user
        elif config_dest_project_name:
            if config.dest_project_version:
                config_dest_project_name = f"{config_dest_project_name} - {config.dest_project_version}"
            try:
                if config.dest_product_token:
                    conn.token = config.dest_product_token
                dest_projects_by_project_name = conn.get_scopes(name=config_dest_project_name, scope_type="project")
            except Exception as err:
                logging.exception(err)
                exit(1)
            if len(dest_projects_by_project_name) == 1:
                dest_project_token = dest_projects_by_project_name[0].get(TOKEN)
            elif len(dest_projects_by_project_name) == 0:
                raise ProcessLookupError(f"Project {config_dest_project_name} hasn't been found in this product. "
                                         f"Please check the provided destination project name and try again")
            else:
                raise ProcessLookupError(f"There are more than one project with the same name {config_dest_project_name}")

    # else if nothing has been provided by the user, the destination is the latest project and source/baseline
    # is one before the latest project
    elif not config_baseline_project_token and not config.dest_project_token and not config_dest_project_name:
        try:
            source_project, destination_project = get_source_and_destination_projects(conn, config)
        except Exception as err:
            logging.error(err)
            exit(1)
        source_project_token = source_project.get(TOKEN)
        dest_project_token = destination_project.get(TOKEN)

    else:
        logging.exception(f"One or more parameters are missing in the config file. In the event when baseline "
                          f"project is provided, a destination project token or destination project name (version)"
                          f" should be provided as well.")
        exit(1)

    logging.info(f'Getting all ignored alerts from the source/baseline project (token={source_project_token})')
    conn.token = config.product_token
    source_ignored_alerts_list = conn.get_alerts(token=source_project_token, ignored=True)
    logging.info(f'total: {len(source_ignored_alerts_list)}')

    logging.info(f'Getting all alerts from the destination project (token={dest_project_token})')
    if config.dest_product_token:
        conn.token = config.dest_product_token
    dest_all_alerts_list = conn.get_alerts(token=dest_project_token)
    logging.info(f'total: {len(dest_all_alerts_list)}')

    libs_to_ignore_from_source_list = get_libs_to_ignore_from_source_list(source_ignored_alerts_list)

    destination_alerts_dict = ws_utilities.convert_dict_list_to_dict(lst=dest_all_alerts_list,
                                                                     key_desc=('type',
                                                                               {'vulnerability': 'name'},
                                                                               {'library': 'keyUuid'}))

    lib_to_ignore_from_source_dict = ws_utilities.convert_dict_list_to_dict(lst=libs_to_ignore_from_source_list,
                                                                            key_desc=('type',
                                                                                      'vulnerability_name',
                                                                                      'lib_keyUuid'))

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
    :return: the Source is a project the ignored alerts are pulled from and
             the Destination is a project where the alerts will be ignored.
             Default values:
                - destination project is a recent project of the certain product
                - source project is one before the recent (penultimate) project of the same product
    """
    logging.info('Getting all projects and sort them')
    all_projects = conn.get_projects()
    if len(all_projects) >= 2:
        all_projects.sort(key=lambda x: x['lastUpdatedDate'])
        logging.info('Find both destination and source projects')
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
            'vulnerability_name': vulnerability_name,
            'type': source_alert_dict.get('type'),
            'lib_keyUuid': source_alert_dict.get('library').get('keyUuid'),
            'alert_comment': source_alert_dict.get('comments')
        }
        libs_to_ignore_from_source_list.append(new_dict)

    return libs_to_ignore_from_source_list


def ignore_alerts(lib_to_ignore_from_source_dict, destination_alerts_dict, conn, config):
    """

    :rtype: object
    """
    print_header('Ignore alerts in the destination project')

    response = None
    exist_in_whitelist = [tup for tup in destination_alerts_dict if tup[1] in cve_whitelist]
    for value in exist_in_whitelist:
        try:
            conn.token = config.org_token
            conn.token_type = ws_constants.ORGANIZATION
            response = conn.set_alerts_status(alert_uuids=value[2],
                                              status="Ignored",
                                              comments='The CVE from white list '
                                                       '(automatically ignored by WS utility)')
            if "Successfully set the alert's status" not in response.values():
                logger.error(response)
                return
        except Exception as err:
            logging.exception(err)
            return
        logger.info(f"Alert for vulnerability {value[1]} has been automatically ignored.")

    for key, value in lib_to_ignore_from_source_dict.items():
        if key in destination_alerts_dict.keys():
            value_dest = destination_alerts_dict.get(key)
            value_source = lib_to_ignore_from_source_dict.get(key)
            try:
                conn.token = config.org_token
                conn.token_type = ws_constants.ORGANIZATION
                response = conn.set_alerts_status(alert_uuids=value_dest.get('alertUuid'),
                                                  status="Ignored",
                                                  comments=f'{value_source.get("alert_comment")} '
                                                           f'(automatically ignored by WS utility)')
                if "Successfully set the alert's status" not in response.values():
                    logger.error(response)
                    return
            except Exception as err:
                logging.exception(err)
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
