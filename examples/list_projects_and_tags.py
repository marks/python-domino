from domino import Domino
import os

domino = Domino("marks/quick-start",
                api_key=os.environ['RC_DOMINO_USER_API_KEY'],
                host=os.environ['RC_DOMINO_API_HOST'])

projects = domino.projects_list()
print(projects)

metadata = domino.project_metadata("marks", "fromapi3")
tagIds = metadata.get("tagIds", [])
print("Project has {} tag(s):".format(len(tagIds)))
for tagId in tagIds:
    print(domino.tag_metadata(tagId))

all_tags = domino.tags_list()
print("All {} tags: ".format(len(all_tags)))
print(all_tags)
