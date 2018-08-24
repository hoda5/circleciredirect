
import webapp2
import json
import logging
from google.appengine.api import urlfetch

# https://circleredirect.appspot.com


# send_api
# http://localhost:7001/api/v1.1/project/github/hoda5/workspace/tree/master?u=hoda5&p=workspace&b=master&a=0&t=874a579716b1ea0f6b6bace02bf96cf9bad55478
# http://localhost:7001/$USERNAME/$PROJECT/$BRANCH/$LASTBUILD?u=hoda5&p=workspace&b=master&a=0&t=874a579716b1ea0f6b6bace02bf96cf9bad55478

# redirect
# http://localhost:7001/tmp/artefatos/coverage/index.html?u=hoda5&p=workspace&b=master&a=1&t=874a579716b1ea0f6b6bace02bf96cf9bad55478
# proxify
# http://localhost:7001/tmp/artefatos/coverage/index.html?u=hoda5&p=workspace&b=master&a=2&t=874a579716b1ea0f6b6bace02bf96cf9bad55478

# https://circleci.com/api/v1.1/project/github/hoda5/workspace/tree/master?circle-token=874a579716b1ea0f6b6bace02bf96cf9bad55478
# /project/:vcs-type/:username/:project/:build_num/artifacts

class MainPage(webapp2.RequestHandler):
    def get(self):

        self.error=False

        try:
            self.path = self.request.path
            self.user_name = self.request.GET['u']
            self.project = self.request.GET['p']
            self.branch = self.request.GET['b']
            self.token = self.request.GET['t']
            self.redir_artifact = self.request.GET['a'] == "1"
            self.proxy_artifact = self.request.GET['a'] == "2"

            self.path = self.path.replace("$USERNAME", self.user_name)        
            self.path = self.path.replace("$PROJECT", self.project)
            self.path = self.path.replace("$BRANCH", self.branch)
            self.path = self.path.replace("$TOKEN", self.token)

            self.parse_build_num()
            if self.redir_artifact:
              return self.redirect_to_artifact()

            if self.proxy_artifact:
              return self.proxify_artifact()
            
            self.send_api()

            # self.response.write(self.artifact_root)
           
        
            # if result.status_code == 200:
            #     p_status = json.loads(result.content)
            #     p_status0 = p_status[0]
            #     last_build_num = p_status0.get("build_num")

            #     path = path.replace("$USERNAME", user_name)        
            #     path = path.replace("$PROJECT", project)
            #     path = path.replace("$BRANCH", branch)
            #     path = path.replace("$TOKEN", token)
            #     path = path.replace("$LASTBUILD", token)

            #     url = 'https://circleci.com/' + path + user_name + "/" + project + "/tree/" + branch + "?circle-token=" + token
            #     # self.response.write(url)
            #     self.response.write(result.content)
            #     # result = urlfetch.fetch(url)
            #     # if result.status_code == 200:
            #     #     self.response.headers = result.headers
            #     #     self.response.write(result.content)
            #     # else:
            #     #     self.response.status_code = result.status_code
            # else:
            #     self.response.status_code = result.status_code


        except urlfetch.Error:
            logging.exception('Caught exception fetching url')

    def parse_build_num(self):
        url = 'https://circleci.com/api/v1.1/project/github/' + self.user_name + "/" + self.project + "/tree/" + self.branch + "?circle-token=" + self.token
        headers = {'Accept': 'text/plain'}
        result = urlfetch.fetch(
                url=url,
                headers=headers)
        if result.status_code == 200:
            p_status = json.loads(result.content)
            p_status0 = p_status[0]
            self.last_build_num = str(p_status0.get("build_num"))

            self.path = self.path.replace("$LASTBUILD", self.last_build_num)

        else:
            self.error = result.status_code

    def parse_artifact(self):
        url = 'https://circleci.com/api/v1.1/project/github/' + self.user_name + "/" + self.project + "/" + self.last_build_num + "/artifacts?circle-token=" + self.token
        headers = {'Accept': 'text/plain'}
        result = urlfetch.fetch(
                url=url,
                headers=headers)
        if result.status_code == 200:
            self.artifacts = json.loads(result.content)
            artifact1 = self.artifacts[0]
            self.artifact_root = artifact1.get("url").replace("/"+artifact1.get("path"), "")

        else:
            self.error = result.status_code

    def send_api(self):
        url = 'https://circleci.com/' + self.path + "?circle-token=" + self.token
        headers = {'Accept': 'text/plain'}
        result = urlfetch.fetch(
                url=url,
                headers=headers)
        self.response.headers = result.headers
        self.response.write(result.content)

    def redirect_to_artifact(self):
        self.parse_artifact()
        url = self.artifact_root + self.path
        self.response.headers['Location'] = str(url)
        self.response.status_int = 307

    def proxify_artifact(self):
        self.parse_artifact()
        url = self.artifact_root + self.path + "?circle-token=" + self.token
        headers = {'Accept': '*/*'}
        result = urlfetch.fetch(
                url=url,
                validate_certificate=True,
                headers=headers)
        # self.response.write(url)        
        self.response.headers = result.headers
        self.response.write(result.content)

app = webapp2.WSGIApplication([
    (r'.*', MainPage),
], debug=True)


