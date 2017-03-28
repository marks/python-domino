class _Routes:
    def __init__(self, host, owner_username, project_name):
        self.host = host
        self._owner_username = owner_username
        self._project_name = project_name

    # Project URLs
    def _build_project_url(self):
        return self.host + '/v1/projects/' + \
            self._owner_username + '/' + self._project_name

    def runs_list(self):
        return self._build_project_url() + '/runs'

    def runs_start(self):
        return self._build_project_url() + '/runs'

    def runs_status(self, runId):
        return self._build_project_url() + '/runs/' + runId

    def files_list(self, commitId, path):
        return self._build_project_url() + '/files/' + commitId + '/' + path

    def files_upload(self, path):
        return self._build_project_url() + path

    def blobs_get(self, key):
        return self._build_project_url() + '/blobs/' + key

    def _build_old_project_url(self):
        # TODO refactor once these API endpoints are supported in REST API
        return self.host + '/' \
            + self._owner_username + '/' + self._project_name

    def collaborators_get(self):
        return self._build_old_project_url() + '/collaborators'

    def collaborators_add(self):
        return self._build_old_project_url() + '/addCollaborator'

    def collaborators_remove(self):
        return self._build_old_project_url() + '/removeCollaborator'

    def collaborators_change_role(self):
        return self._build_old_project_url() + '/changeCollaboratorProjectRole'

    # Endpoint URLs
    def _build_endpoint_url(self):
        return self.host + '/v1/' + \
            self._owner_username + '/' + self._project_name + '/endpoint'

    def endpoint(self):
        return self._build_endpoint_url()

    def endpoint_state(self):
        return self._build_endpoint_url() + '/state'

    def endpoint_publish(self):
        return self._build_endpoint_url() + '/publishRelease'

    # Miscellaneous URLs
    def deployment_version(self):
        return self.host + '/version'

    def project_create(self):
        return self.host + '/new'

    def projects_list(self):
        return self.host + '/project'

    def project_metadata(self, owner_username, project_name):
        # use instnatiated Domino owner/user if not specified
        if owner_username is None:
            owner_username = self._owner_username
        if project_name is None:
            project_name = self._project_name

        return self.host + '/project/' + owner_username + '/' + project_name
