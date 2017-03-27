from .routes import _Routes

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

import os
import logging
import requests

VALID_PROJECT_ROLES = ["Contributor", "ResultsConsumer",
                       "LauncherUser", "ProjectImporter"]


class Domino:
    def __init__(self, project, api_key=None, host=None):
        self._configure_logging()

        if host is not None:
            host = host
        elif 'DOMINO_API_HOST' in os.environ:
            host = os.environ['DOMINO_API_HOST']
        else:
            raise Exception("Host must be provided, either via the \
                constructor value or through DOMINO_API_HOST environment \
                variable.")

        self._logger.info('Initializing Domino API with host ' + host)

        owner_username = project.split("/")[0]
        project_name = project.split("/")[1]
        self._routes = _Routes(host, owner_username, project_name)

        if api_key is not None:
            self._api_key = api_key
        elif 'DOMINO_USER_API_KEY' in os.environ:
            self._api_key = os.environ['DOMINO_USER_API_KEY']
        else:
            raise Exception("API key must be provided, either via the \
                constructor value or through DOMINO_USER_API_KEY environment \
                variable.")

        # Get version
        self._version = str(self.deployment_version().get("version"))

    def _configure_logging(self):
        logging.basicConfig(level=logging.INFO)
        self._logger = logging.getLogger(__name__)

    def runs_list(self):
        url = self._routes.runs_list()
        return self._get(url)

    def runs_start(self, command, isDirect=False, commitId=None, title=None,
                   tier=None, publishApiEndpoint=None):

        url = self._routes.runs_start()

        request = {
            "command": command,
            "isDirect": isDirect,
            "commitId": commitId,
            "title": title,
            "tier": tier,
            "publishApiEndpoint": publishApiEndpoint
        }

        response = requests.post(url, auth=('', self._api_key), json=request)
        return response.json()

    def runs_status(self, runId):
        url = self._routes.runs_status(runId)
        return self._get(url)

    def files_list(self, commitId, path='/'):
        url = self._routes.files_list(commitId, path)
        return self._get(url)

    def files_upload(self, path, file):
        url = self._routes.files_upload(path)
        return self._put_file(url, file)

    def blobs_get(self, key):
        url = self._routes.blobs_get(key)
        return self._open_url(url)

    def endpoint_state(self):
        url = self._routes.endpoint_state()
        return self._get(url)

    def endpoint_unpublish(self):
        url = self._routes.endpoint()
        response = requests.delete(url, auth=('', self._api_key))
        return response

    def endpoint_publish(self, file, function, commitId):
        url = self._routes.endpoint_publish()

        request = {
            "commitId": commitId,
            "bindingDefinition": {
                "file": file,
                "function": function
            }
        }

        response = requests.post(url, auth=('', self._api_key), json=request)
        return response

    def deployment_version(self):
        url = self._routes.deployment_version()
        return self._get(url)

    def project_create(self, owner_username, project_name):
        self.requires_at_least("1.53.0.0")
        url = self._routes.project_create()
        request = {
            'owner': owner_username,
            'name': project_name
        }
        response = requests.post(url, auth=('', self._api_key), data=request,
                                 allow_redirects=False)

        disposition = parse_play_flash_cookie(response)
        if disposition.get("error"):
            raise Exception(disposition.get("message"))
        else:
            return disposition

    def collaborators_get(self):
        self.requires_at_least("1.53.0.0")
        url = self._routes.collaborators_get()
        return self._get(url)

    def collaborators_add(self, usernameOrEmail, message=""):
        self.requires_at_least("1.53.0.0")
        url = self._routes.collaborators_add()
        request = {
            'collaboratorUsernameOrEmail': usernameOrEmail,
            'welcomeMessage': message
        }
        response = requests.post(url, auth=('', self._api_key), data=request,
                                 allow_redirects=False)
        disposition = parse_play_flash_cookie(response)

        if disposition.get("error"):
            raise Exception(disposition.get("message"))
        else:
            return disposition

    def collaborators_change_role(self, username, newRole):
        self.requires_at_least("1.53.0.0")

        # Validate the given role is valid
        if newRole not in VALID_PROJECT_ROLES:
            raise Exception("Invalid role. Choices are: {}".format(
                            ', '.join(VALID_PROJECT_ROLES)))

        url = self._routes.collaborators_change_role()
        request = {
            'collaboratorUsername': username,
            'projectRole': newRole
        }
        response = requests.post(url, auth=('', self._api_key), data=request)
        disposition = parse_http_status_code_dispoition(response)

        if disposition.get("error"):
            raise Exception(disposition.get("message"))
        else:
            return disposition

    # Helper methods
    def _get(self, url):
        return requests.get(url, auth=('', self._api_key)).json()

    def _put_file(self, url, file):
        files = {'file': file}
        return requests.put(url, files=files, auth=('', self._api_key))

    def _open_url(self, url):
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, self._routes.host, '', self._api_key)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        return opener.open(url)

    def requires_at_least(self, at_least_version):
        if at_least_version > self._version:
            raise Exception("You need at least version {} but your deployment \
                            seems to be running {}".format(
                            at_least_version, self._version))


def parse_play_flash_cookie(response):
    flash_cookie = response.cookies['PLAY_FLASH']
    messageType, message = flash_cookie.split("=")
    # Format message into user friendly string
    message = urllib2.unquote(message).replace("+", " ")
    # Discern error disposition
    if(messageType == "dominoFlashError"):
        error = True
    else:
        error = False
    return dict(messageType=messageType, message=message, error=error)


def parse_http_status_code_dispoition(response):
    if response.status_code == 200:
        error = False
        messageType = "dominoFlashMessage"
    else:
        error = True
        messageType = "dominoFlashError"
    return dict(messageType=messageType, message=response.content, error=error)
