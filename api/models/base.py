from api.core.user import UserHelper
from api.core.group import GroupHelper
from tornado.gen import coroutine, Return
import bcrypt

class BaseModel(object):
    def __init__(self, **kwargs):
        if not kwargs.get('db'):
            raise ValueError('db should be present')
        self._user = None
        if kwargs.get('user'):
            self._user = kwargs.get('user')
        self.db = kwargs.get('db')

        if self._user:
            self._gh = GroupHelper(**kwargs)
            self._uh = UserHelper(**kwargs)
        elif self.db:
            self._gh = GroupHelper(db=self.db)
            self._uh = UserHelper(db=self.db)

    @coroutine
    def get_hashed_password(self, plain_text_password:str):
        if not plain_text_password:
            raise NotImplementedError()
        raise Return({'hash':bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt(12))})

    @coroutine
    def check_hashed_password(self, text_password, hashed_password):
        raise Return(bcrypt.checkpw(text_password.encode('utf-8'), hashed_password))
