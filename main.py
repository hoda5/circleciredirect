# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import webapp2
import json
from google.appengine.api import urlfetch

# http://localhost:7001/$USERNAME/$PROJECT/$BRANCH/$LASTBUILD?u=hoda5&p=workspace&b=master&a=0&t=874a579716b1ea0f6b6bace02bf96cf9bad55478
# http://localhost:7001/tmp/artefatos/coverage/index.html?u=hoda5&p=workspace&b=master&a=1&t=874a579716b1ea0f6b6bace02bf96cf9bad55478
# http://localhost:7001/tmp/artefatos/coverage/index.html?u=hoda5&p=workspace&b=master&a=1&t=874a579716b1ea0f6b6bace02bf96cf9bad55478
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
            self.is_artifact = self.request.GET['a'] == "1"

            self.path = self.path.replace("$USERNAME", self.user_name)        
            self.path = self.path.replace("$PROJECT", self.project)
            self.path = self.path.replace("$BRANCH", self.branch)
            self.path = self.path.replace("$TOKEN", self.token)

            self.parse_build_num()
            self.parse_artifact()
            if self.is_artifact:
              self.send_artficat()
            else:
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
        if not self.is_artifact:
           return
        url = 'https://circleci.com/api/v1.1/project/github/' + self.user_name + "/" + self.project + "/" + self.last_build_num + "/artifacts?circle-token=" + self.token
        headers = {'Accept': 'text/plain'}
        result = urlfetch.fetch(
                url=url,
                headers=headers)
        if result.status_code == 200:
            self.artifacts = json.loads(result.content)
            artifact1 = self.artifacts[0]
            self.artifact_root = artifact1.get("url").replace(artifact1.get("path"), "")

        else:
            self.error = result.status_code

    def send_api(self):
        url = 'https://circleci.com/' + self.path
        headers = {'Accept': 'text/plain'}
        result = urlfetch.fetch(
                url=url,
                headers=headers)
        self.response.headers = result.headers
        self.response.write(result.content)

    def send_artficat(self):
        url = self.artifact_root + self.path
        url = url.replace("//", "/")
        self.response.headers['Location'] = str(url)
        self.response.status_int = 307

app = webapp2.WSGIApplication([
    (r'.*', MainPage),
], debug=True)


