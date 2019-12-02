from api.stores.group import *
from api.stores.user import User, GroupMapping, UserStatus, LinkedAccount, LinkedAccountType
from api.stores.employee import Employee, SupportedRoles, GroupStatus
from tornado.gen import *
from api.core.user import UserHelper
from api.models.base import BaseModel
from api.core.group import GroupHelper
import uuid
import datetime

class GroupModel(BaseModel):
    @coroutine
    def create_group(self, groupDict, userId=None, type=None):
        if not userId:
            userId = self._user.UserId
        group = Group()
        group.Name = groupDict.get(CreateGroupRequestParams.Name)
        group.Type = groupDict.get(CreateGroupRequestParams.Type)
        group.OwnerId = userId
        # membermappings = [self._gh.create_member_mapping(userId, [SupportedRoles.Admin])]
        # group.MemberMappings = membermappings
        group.set_value(group.PropertyNames.CreatedTimeStamp, datetime.datetime.now())
        group.set_value(group.PropertyNames.UpdatedTimeStamp, datetime.datetime.now())
        group.Id = uuid.uuid4()
        yield self._gh.create_group_for_user(group.datadict)
        yield self.create_employee_profile(userId, group.Id, SupportedRoles.Admin)

    #
    # @coroutine
    # def create_employee(self, employeeDict, addedby=None):
    #     # create member mapping for employee
    #     employeeId = employeeDict.get('employee')
    #     membermappings = [self._gh.create_member_mapping(userId, [SupportedRoles.Admin])]
    #
    # Pharmaceutical distributor is a kind of group that don't have link to Pharmacy company only reverse link


    @coroutine
    def create_pharmaceutical_distributor(self, **kwargs):
        group = self.create_group(kwargs, self._user.UserId, GroupType.PharmaDistributor)
        raise Return(group)

    @coroutine
    def create_employee_profile(self, userId, groupId, role):
        employee = Employee()
        employee.Id = uuid.uuid4()
        employee.UserId = userId
        employee.GroupId = groupId
        employee.Role = role
        if role == SupportedRoles.Admin:
            employee.Status = GroupStatus.Joined
        else:
            employee.Status = GroupStatus.Invited
        employee.CreatedTimeStamp = datetime.datetime.utcnow()
        employee.UpdatedTimeStamp = datetime.datetime.utcnow()
        yield self._uh.save_user(employee.datadict)


    # Dummy team for employees
    @coroutine
    def create_employee_team(self, **kwargs):
        group = self.create_group(kwargs, self._user.UserId, GroupType.EmployeeTeam)
        raise Return(group)

    def populate_group_response(self, group):
        returning_dict = {}
        returning_dict[GroupResponse.Name] = group.Name
        returning_dict[GroupResponse.Id] = str(group.Id)
        returning_dict[GroupResponse.MemberCount] = len(group.MemberMappings)
        return returning_dict

    @coroutine
    def create_invited_state_user(self, invitedDict, groupId):
        employee = User()
        employee.Name = invitedDict.get(CreateEmployeeRequestParams.Name)
        employee.Phone = invitedDict.get(CreateEmployeeRequestParams.Phone)
        employee.UserId = uuid.uuid4()
        account = LinkedAccount()
        password = yield self.get_hashed_password(invitedDict.get(CreateEmployeeRequestParams.Password))
        account.AccountName = employee.Phone
        account.AccountHash = password.get('hash')
        account.AccountType = LinkedAccountType.Native
        employee.Status = UserStatus.Invited
        employee.EmailValidated = False
        employee.CreatedTimeStamp = datetime.datetime.now()
        employee.UpdatedTimeStamp = datetime.datetime.now()
        yield self._uh.save_user(employee.datadict)
        raise Return(employee)

    @coroutine
    def get_groups_where_user_is_owner(self, userId):
        if not userId:
            userId = self._user.UserId
        try:
            (groups) = yield self._gh.get_groups_where_user_is_owner(userId)
            groupsToReturn = list(map(lambda x: self.populate_group_response(x), groups))

        except Exception as e:
            raise Return((False, str(e)))
        else:
            raise Return((True, groupsToReturn))

    # @coroutine
    # def create_unique_invitation_code(self):
    #     invitation_codes = yield self._uh.get_all_invitation_codes()

    @coroutine
    def create_employee(self, groupId, employeeDict):
        """
            Employee added by admin.
            This method takes input from admin and creates user profile and
            creates membermapping for corresponding group.
            employeeDict should contain
            name,
            designation
            emailid
            :return:
        """
        if not isinstance(groupId, uuid.UUID):
            groupId = uuid.UUID(groupId)
        if not (employeeDict and  groupId):
            raise NotImplementedError()
        employee = yield self.create_invited_state_user(employeeDict, groupId)
        yield self.create_employee_profile(employee.UserId, groupId, SupportedRoles.SalesRep)
        raise Return({'status':'success'})







