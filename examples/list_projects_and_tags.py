from domino import Domino
import os

domino = Domino("marks/quick-start",
                api_key=os.environ['RC_DOMINO_USER_API_KEY'],
                host=os.environ['RC_DOMINO_API_HOST'])

projects = domino.projects_list()
print(projects)

metadata = domino.project_metadata("marks", "fromapi3")
print("Project tags:")
print(metadata.get("tagIds", []))
