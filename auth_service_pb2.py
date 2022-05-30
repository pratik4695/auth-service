# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: auth_service.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12\x61uth_service.proto\x12\x0c\x61uth_service\"\x07\n\x05\x45mpty\"6\n\x0f\x42ooleanResponse\x12#\n\x07success\x18\x01 \x01(\x0e\x32\x12.auth_service.Bool\"\x83\x01\n\x08UserBlob\x12\n\n\x02id\x18\x01 \x01(\t\x12\x12\n\nfirst_name\x18\x02 \x01(\t\x12\x11\n\tlast_name\x18\x03 \x01(\t\x12\x11\n\tuser_type\x18\x04 \x01(\t\x12\x11\n\tentity_id\x18\x05 \x01(\t\x12\x0c\n\x04name\x18\x06 \x01(\t\x12\x10\n\x08platform\x18\x07 \x01(\t\"I\n\tAuthToken\x12\x14\n\x0c\x61\x63\x63\x65ss_token\x18\x01 \x01(\t\x12\x15\n\rrefresh_token\x18\x02 \x01(\t\x12\x0f\n\x07\x65xpires\x18\x03 \x01(\x03\"\xaa\x01\n\x08Userdata\x12\n\n\x02id\x18\x01 \x01(\t\x12\x12\n\nfirst_name\x18\x02 \x01(\t\x12\x11\n\tlast_name\x18\x03 \x01(\t\x12\x11\n\tuser_type\x18\x04 \x01(\t\x12\r\n\x05\x65mail\x18\x05 \x01(\t\x12\x0e\n\x06mobile\x18\x06 \x01(\t\x12\x0f\n\x07\x63reated\x18\x07 \x01(\x03\x12\x10\n\x08username\x18\x08 \x01(\t\x12\x16\n\x0euser_full_name\x18\t \x01(\t\"a\n\x11UserLoginResponse\x12&\n\x05token\x18\x01 \x01(\x0b\x32\x17.auth_service.AuthToken\x12$\n\x04user\x18\x02 \x01(\x0b\x32\x16.auth_service.Userdata\"8\n\x15UserLoginWithPassword\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\"\x88\x02\n\x11RegisterUserInput\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\x12\n\nfirst_name\x18\x02 \x01(\t\x12\x11\n\tlast_name\x18\x03 \x01(\t\x12\x11\n\tuser_type\x18\x04 \x01(\t\x12\x0e\n\x06mobile\x18\x05 \x01(\t\x12\x10\n\x08username\x18\x06 \x01(\t\x12\x10\n\x08password\x18\x07 \x01(\t\x12\x13\n\x0bre_password\x18\x08 \x01(\t\x12\x15\n\rdate_of_birth\x18\t \x01(\t\x12\x0e\n\x06gender\x18\n \x01(\t\x12\x16\n\x0euser_full_name\x18\x0b \x01(\t\x12\"\n\x06is_app\x18\x0c \x01(\x0e\x32\x12.auth_service.Bool\"\x1d\n\x0bMobileInput\x12\x0e\n\x06mobile\x18\x01 \x01(\t\"5\n\x16ValidateMobileOTPInput\x12\x0e\n\x06mobile\x18\x01 \x01(\t\x12\x0b\n\x03otp\x18\x02 \x01(\t\"\xb2\x01\n\x0cUserListData\x12\n\n\x02id\x18\x01 \x01(\t\x12\x12\n\nfirst_name\x18\x02 \x01(\t\x12\x11\n\tlast_name\x18\x03 \x01(\t\x12\x11\n\tuser_type\x18\x04 \x01(\t\x12\r\n\x05\x65mail\x18\x05 \x01(\t\x12\x0e\n\x06mobile\x18\x06 \x01(\t\x12\x10\n\x08username\x18\x08 \x01(\t\x12\x15\n\rdate_of_birth\x18\t \x01(\t\x12\x14\n\x0c\x61\x63\x63\x65ss_token\x18\n \x01(\t\" \n\x10GetUserListInput\x12\x0c\n\x04page\x18\x01 \x01(\x05\"\xa2\x01\n\x10UserListResponse\x12)\n\x05users\x18\x01 \x03(\x0b\x32\x1a.auth_service.UserListData\x12\x10\n\x08per_page\x18\x02 \x01(\x05\x12\x0f\n\x07orphans\x18\x03 \x01(\x05\x12\x1e\n\x16\x61llow_empty_first_page\x18\x04 \x01(\x05\x12\r\n\x05\x63ount\x18\x05 \x01(\x05\x12\x11\n\tnum_pages\x18\x06 \x01(\x05\"\x9d\x01\n\rUserEditInput\x12\n\n\x02id\x18\x01 \x01(\t\x12\x12\n\nfirst_name\x18\x02 \x01(\t\x12\x11\n\tlast_name\x18\x03 \x01(\t\x12\x11\n\tuser_type\x18\x04 \x01(\t\x12\r\n\x05\x65mail\x18\x05 \x01(\t\x12\x0e\n\x06mobile\x18\x06 \x01(\t\x12\x10\n\x08username\x18\x07 \x01(\t\x12\x15\n\rdate_of_birth\x18\x08 \x01(\t\"w\n\x11UserShortResponse\x12\n\n\x02id\x18\x01 \x01(\t\x12\x12\n\nfirst_name\x18\x02 \x01(\t\x12\x11\n\tlast_name\x18\x03 \x01(\t\x12\r\n\x05\x65mail\x18\x04 \x01(\t\x12\x0e\n\x06mobile\x18\x05 \x01(\t\x12\x10\n\x08username\x18\x06 \x01(\t\"Z\n\x13UserMinimumResponse\x12\n\n\x02id\x18\x01 \x01(\t\x12\x12\n\nfirst_name\x18\x02 \x01(\t\x12\x11\n\tlast_name\x18\x03 \x01(\t\x12\x10\n\x08username\x18\x06 \x01(\t\"a\n\x0eStatusResponse\x12\x15\n\rerror_message\x18\x01 \x01(\t\x12\x13\n\x0bstatus_code\x18\x02 \x01(\x05\x12#\n\x07success\x18\x03 \x01(\x0e\x32\x12.auth_service.Bool\"t\n\x15\x41uthorisationResponse\x12-\n\x04user\x18\x01 \x01(\x0b\x32\x1f.auth_service.UserShortResponse\x12,\n\x06status\x18\x02 \x01(\x0b\x32\x1c.auth_service.StatusResponse\"#\n\x12\x41uthorisationInput\x12\r\n\x05token\x18\x01 \x01(\t\"&\n\x15GetUserIDsDetailInput\x12\r\n\x05users\x18\x01 \x03(\t\"L\n\x18GetUserIDsDetailResponse\x12\x30\n\x05users\x18\x01 \x03(\x0b\x32!.auth_service.UserMinimumResponse\"\x96\x01\n\x19ValidateMobileOTPResponse\x12+\n\x0fis_current_user\x18\x01 \x01(\x0e\x32\x12.auth_service.Bool\x12&\n\x05token\x18\x02 \x01(\x0b\x32\x17.auth_service.AuthToken\x12$\n\x04user\x18\x03 \x01(\x0b\x32\x16.auth_service.Userdata\"C\n\x14NewMobileOTPResponse\x12+\n\x0fis_current_user\x18\x01 \x01(\x0e\x32\x12.auth_service.Bool*%\n\x04\x42ool\x12\x08\n\x04NULL\x10\x00\x12\x08\n\x04TRUE\x10\x01\x12\t\n\x05\x46\x41LSE\x10\x02\x32\xc4\x05\n\x0b\x41uthService\x12P\n\x0cRegisterUser\x12\x1f.auth_service.RegisterUserInput\x1a\x1f.auth_service.UserLoginResponse\x12Q\n\tLoginUser\x12#.auth_service.UserLoginWithPassword\x1a\x1f.auth_service.UserLoginResponse\x12M\n\x11GenerateMobileOTP\x12\x19.auth_service.MobileInput\x1a\x1d.auth_service.BooleanResponse\x12\x62\n\x11ValidateMobileOTP\x12$.auth_service.ValidateMobileOTPInput\x1a\'.auth_service.ValidateMobileOTPResponse\x12M\n\x0bGetUserList\x12\x1e.auth_service.GetUserListInput\x1a\x1e.auth_service.UserListResponse\x12L\n\x0e\x45\x64itUserDetail\x12\x1b.auth_service.UserEditInput\x1a\x1d.auth_service.BooleanResponse\x12_\n\x16\x41uthenticateUserViaJWT\x12 .auth_service.AuthorisationInput\x1a#.auth_service.AuthorisationResponse\x12_\n\x10GetUserIDsDetail\x12#.auth_service.GetUserIDsDetailInput\x1a&.auth_service.GetUserIDsDetailResponseb\x06proto3')

_BOOL = DESCRIPTOR.enum_types_by_name['Bool']
Bool = enum_type_wrapper.EnumTypeWrapper(_BOOL)
NULL = 0
TRUE = 1
FALSE = 2


_EMPTY = DESCRIPTOR.message_types_by_name['Empty']
_BOOLEANRESPONSE = DESCRIPTOR.message_types_by_name['BooleanResponse']
_USERBLOB = DESCRIPTOR.message_types_by_name['UserBlob']
_AUTHTOKEN = DESCRIPTOR.message_types_by_name['AuthToken']
_USERDATA = DESCRIPTOR.message_types_by_name['Userdata']
_USERLOGINRESPONSE = DESCRIPTOR.message_types_by_name['UserLoginResponse']
_USERLOGINWITHPASSWORD = DESCRIPTOR.message_types_by_name['UserLoginWithPassword']
_REGISTERUSERINPUT = DESCRIPTOR.message_types_by_name['RegisterUserInput']
_MOBILEINPUT = DESCRIPTOR.message_types_by_name['MobileInput']
_VALIDATEMOBILEOTPINPUT = DESCRIPTOR.message_types_by_name['ValidateMobileOTPInput']
_USERLISTDATA = DESCRIPTOR.message_types_by_name['UserListData']
_GETUSERLISTINPUT = DESCRIPTOR.message_types_by_name['GetUserListInput']
_USERLISTRESPONSE = DESCRIPTOR.message_types_by_name['UserListResponse']
_USEREDITINPUT = DESCRIPTOR.message_types_by_name['UserEditInput']
_USERSHORTRESPONSE = DESCRIPTOR.message_types_by_name['UserShortResponse']
_USERMINIMUMRESPONSE = DESCRIPTOR.message_types_by_name['UserMinimumResponse']
_STATUSRESPONSE = DESCRIPTOR.message_types_by_name['StatusResponse']
_AUTHORISATIONRESPONSE = DESCRIPTOR.message_types_by_name['AuthorisationResponse']
_AUTHORISATIONINPUT = DESCRIPTOR.message_types_by_name['AuthorisationInput']
_GETUSERIDSDETAILINPUT = DESCRIPTOR.message_types_by_name['GetUserIDsDetailInput']
_GETUSERIDSDETAILRESPONSE = DESCRIPTOR.message_types_by_name['GetUserIDsDetailResponse']
_VALIDATEMOBILEOTPRESPONSE = DESCRIPTOR.message_types_by_name['ValidateMobileOTPResponse']
_NEWMOBILEOTPRESPONSE = DESCRIPTOR.message_types_by_name['NewMobileOTPResponse']
Empty = _reflection.GeneratedProtocolMessageType('Empty', (_message.Message,), {
  'DESCRIPTOR' : _EMPTY,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.Empty)
  })
_sym_db.RegisterMessage(Empty)

BooleanResponse = _reflection.GeneratedProtocolMessageType('BooleanResponse', (_message.Message,), {
  'DESCRIPTOR' : _BOOLEANRESPONSE,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.BooleanResponse)
  })
_sym_db.RegisterMessage(BooleanResponse)

UserBlob = _reflection.GeneratedProtocolMessageType('UserBlob', (_message.Message,), {
  'DESCRIPTOR' : _USERBLOB,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.UserBlob)
  })
_sym_db.RegisterMessage(UserBlob)

AuthToken = _reflection.GeneratedProtocolMessageType('AuthToken', (_message.Message,), {
  'DESCRIPTOR' : _AUTHTOKEN,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.AuthToken)
  })
_sym_db.RegisterMessage(AuthToken)

Userdata = _reflection.GeneratedProtocolMessageType('Userdata', (_message.Message,), {
  'DESCRIPTOR' : _USERDATA,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.Userdata)
  })
_sym_db.RegisterMessage(Userdata)

UserLoginResponse = _reflection.GeneratedProtocolMessageType('UserLoginResponse', (_message.Message,), {
  'DESCRIPTOR' : _USERLOGINRESPONSE,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.UserLoginResponse)
  })
_sym_db.RegisterMessage(UserLoginResponse)

UserLoginWithPassword = _reflection.GeneratedProtocolMessageType('UserLoginWithPassword', (_message.Message,), {
  'DESCRIPTOR' : _USERLOGINWITHPASSWORD,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.UserLoginWithPassword)
  })
_sym_db.RegisterMessage(UserLoginWithPassword)

RegisterUserInput = _reflection.GeneratedProtocolMessageType('RegisterUserInput', (_message.Message,), {
  'DESCRIPTOR' : _REGISTERUSERINPUT,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.RegisterUserInput)
  })
_sym_db.RegisterMessage(RegisterUserInput)

MobileInput = _reflection.GeneratedProtocolMessageType('MobileInput', (_message.Message,), {
  'DESCRIPTOR' : _MOBILEINPUT,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.MobileInput)
  })
_sym_db.RegisterMessage(MobileInput)

ValidateMobileOTPInput = _reflection.GeneratedProtocolMessageType('ValidateMobileOTPInput', (_message.Message,), {
  'DESCRIPTOR' : _VALIDATEMOBILEOTPINPUT,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.ValidateMobileOTPInput)
  })
_sym_db.RegisterMessage(ValidateMobileOTPInput)

UserListData = _reflection.GeneratedProtocolMessageType('UserListData', (_message.Message,), {
  'DESCRIPTOR' : _USERLISTDATA,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.UserListData)
  })
_sym_db.RegisterMessage(UserListData)

GetUserListInput = _reflection.GeneratedProtocolMessageType('GetUserListInput', (_message.Message,), {
  'DESCRIPTOR' : _GETUSERLISTINPUT,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.GetUserListInput)
  })
_sym_db.RegisterMessage(GetUserListInput)

UserListResponse = _reflection.GeneratedProtocolMessageType('UserListResponse', (_message.Message,), {
  'DESCRIPTOR' : _USERLISTRESPONSE,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.UserListResponse)
  })
_sym_db.RegisterMessage(UserListResponse)

UserEditInput = _reflection.GeneratedProtocolMessageType('UserEditInput', (_message.Message,), {
  'DESCRIPTOR' : _USEREDITINPUT,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.UserEditInput)
  })
_sym_db.RegisterMessage(UserEditInput)

UserShortResponse = _reflection.GeneratedProtocolMessageType('UserShortResponse', (_message.Message,), {
  'DESCRIPTOR' : _USERSHORTRESPONSE,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.UserShortResponse)
  })
_sym_db.RegisterMessage(UserShortResponse)

UserMinimumResponse = _reflection.GeneratedProtocolMessageType('UserMinimumResponse', (_message.Message,), {
  'DESCRIPTOR' : _USERMINIMUMRESPONSE,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.UserMinimumResponse)
  })
_sym_db.RegisterMessage(UserMinimumResponse)

StatusResponse = _reflection.GeneratedProtocolMessageType('StatusResponse', (_message.Message,), {
  'DESCRIPTOR' : _STATUSRESPONSE,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.StatusResponse)
  })
_sym_db.RegisterMessage(StatusResponse)

AuthorisationResponse = _reflection.GeneratedProtocolMessageType('AuthorisationResponse', (_message.Message,), {
  'DESCRIPTOR' : _AUTHORISATIONRESPONSE,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.AuthorisationResponse)
  })
_sym_db.RegisterMessage(AuthorisationResponse)

AuthorisationInput = _reflection.GeneratedProtocolMessageType('AuthorisationInput', (_message.Message,), {
  'DESCRIPTOR' : _AUTHORISATIONINPUT,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.AuthorisationInput)
  })
_sym_db.RegisterMessage(AuthorisationInput)

GetUserIDsDetailInput = _reflection.GeneratedProtocolMessageType('GetUserIDsDetailInput', (_message.Message,), {
  'DESCRIPTOR' : _GETUSERIDSDETAILINPUT,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.GetUserIDsDetailInput)
  })
_sym_db.RegisterMessage(GetUserIDsDetailInput)

GetUserIDsDetailResponse = _reflection.GeneratedProtocolMessageType('GetUserIDsDetailResponse', (_message.Message,), {
  'DESCRIPTOR' : _GETUSERIDSDETAILRESPONSE,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.GetUserIDsDetailResponse)
  })
_sym_db.RegisterMessage(GetUserIDsDetailResponse)

ValidateMobileOTPResponse = _reflection.GeneratedProtocolMessageType('ValidateMobileOTPResponse', (_message.Message,), {
  'DESCRIPTOR' : _VALIDATEMOBILEOTPRESPONSE,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.ValidateMobileOTPResponse)
  })
_sym_db.RegisterMessage(ValidateMobileOTPResponse)

NewMobileOTPResponse = _reflection.GeneratedProtocolMessageType('NewMobileOTPResponse', (_message.Message,), {
  'DESCRIPTOR' : _NEWMOBILEOTPRESPONSE,
  '__module__' : 'auth_service_pb2'
  # @@protoc_insertion_point(class_scope:auth_service.NewMobileOTPResponse)
  })
_sym_db.RegisterMessage(NewMobileOTPResponse)

_AUTHSERVICE = DESCRIPTOR.services_by_name['AuthService']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _BOOL._serialized_start=2340
  _BOOL._serialized_end=2377
  _EMPTY._serialized_start=36
  _EMPTY._serialized_end=43
  _BOOLEANRESPONSE._serialized_start=45
  _BOOLEANRESPONSE._serialized_end=99
  _USERBLOB._serialized_start=102
  _USERBLOB._serialized_end=233
  _AUTHTOKEN._serialized_start=235
  _AUTHTOKEN._serialized_end=308
  _USERDATA._serialized_start=311
  _USERDATA._serialized_end=481
  _USERLOGINRESPONSE._serialized_start=483
  _USERLOGINRESPONSE._serialized_end=580
  _USERLOGINWITHPASSWORD._serialized_start=582
  _USERLOGINWITHPASSWORD._serialized_end=638
  _REGISTERUSERINPUT._serialized_start=641
  _REGISTERUSERINPUT._serialized_end=905
  _MOBILEINPUT._serialized_start=907
  _MOBILEINPUT._serialized_end=936
  _VALIDATEMOBILEOTPINPUT._serialized_start=938
  _VALIDATEMOBILEOTPINPUT._serialized_end=991
  _USERLISTDATA._serialized_start=994
  _USERLISTDATA._serialized_end=1172
  _GETUSERLISTINPUT._serialized_start=1174
  _GETUSERLISTINPUT._serialized_end=1206
  _USERLISTRESPONSE._serialized_start=1209
  _USERLISTRESPONSE._serialized_end=1371
  _USEREDITINPUT._serialized_start=1374
  _USEREDITINPUT._serialized_end=1531
  _USERSHORTRESPONSE._serialized_start=1533
  _USERSHORTRESPONSE._serialized_end=1652
  _USERMINIMUMRESPONSE._serialized_start=1654
  _USERMINIMUMRESPONSE._serialized_end=1744
  _STATUSRESPONSE._serialized_start=1746
  _STATUSRESPONSE._serialized_end=1843
  _AUTHORISATIONRESPONSE._serialized_start=1845
  _AUTHORISATIONRESPONSE._serialized_end=1961
  _AUTHORISATIONINPUT._serialized_start=1963
  _AUTHORISATIONINPUT._serialized_end=1998
  _GETUSERIDSDETAILINPUT._serialized_start=2000
  _GETUSERIDSDETAILINPUT._serialized_end=2038
  _GETUSERIDSDETAILRESPONSE._serialized_start=2040
  _GETUSERIDSDETAILRESPONSE._serialized_end=2116
  _VALIDATEMOBILEOTPRESPONSE._serialized_start=2119
  _VALIDATEMOBILEOTPRESPONSE._serialized_end=2269
  _NEWMOBILEOTPRESPONSE._serialized_start=2271
  _NEWMOBILEOTPRESPONSE._serialized_end=2338
  _AUTHSERVICE._serialized_start=2380
  _AUTHSERVICE._serialized_end=3088
# @@protoc_insertion_point(module_scope)
