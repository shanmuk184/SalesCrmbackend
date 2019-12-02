from tornado.gen import *
from .baseHandler import BaseHandler, BaseApiHandler
from api.models.group import GroupModel
import json
from tornado import web
from bson.json_util import dumps
from tornado_swirl.swagger import schema, restapi
@restapi('/api/user/groups')
class GroupsListHandler(BaseApiHandler):
    @web.authenticated
    @coroutine
    def get(self):
        model = GroupModel(user=self._user, db=self.db)
        (status, _) = yield model.get_groups_where_user_is_owner(self._user.UserId)
        if status:
            self.finish(dumps(_))
        else:
            self.set_status(400, _)
            self.finish()

@restapi('/api/group')
class GroupHandler(BaseHandler):
    @web.authenticated
    @coroutine
    def post(self):
        user = yield self.current_user
        model = GroupModel(user=user, db=self.db)
        try:
            yield model.create_group(self.args)
        except Exception as e:
            pass
        self.finish(json.dumps({'status': 'success'}))

@restapi('/api/(.*)/group')
class CreateEmloyeeHandler(BaseApiHandler):
    @coroutine
    def post(self, groupId):
        user = yield self.current_user
        model = GroupModel(user=user, db=self.db)
        # e=''
        employee = None
        try:
            employee = yield model.create_employee(groupId, self.args)
        except Exception as e:
            self.set_status(400, str(e))
            self.finish()
        self.write(employee)


