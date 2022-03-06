import json

from django.conf import settings


class PlatformType:
    AASAANJOBS = 0
    OLX_PEOPLE = 1


class PlatformBucket:
    AASAANJOBS = 'aasaanjobs'
    OLX_PEOPLE = 'olx-people'


class MobilePushClient:
    CANDIDATE_ANDROID_MOBILE = 0
    CANDIDATE_MOBILE_WEB = 1
    STAFFING_ANDROID_MY_HR_APP = 2
    STAFFING_IOS_MY_HR_APP = 3


MOBILE_NUMBER_REGEX = '^[6-9]\d{9}$'


# class ElasticIndex:
#     def __init__(
#             self,
#             index_prefix,
#             doc_type,
#             data_function=None,
#             mapping=None,
#             setting=settings.ES_ENV
#     ):
#         self.index = ''.join([index_prefix, setting])
#         self.doc_type = doc_type
#         if mapping:
#             self.mapping = '{}/{}'.format(settings.BASE_DIR, mapping)
#         else:
#             self.mapping = None
#         if data_function:
#             self.data_function = data_function
#
#     def get_mapping(self):
#         if not self.mapping:
#             raise ValueError('No mapping provided')
#         with open(self.mapping, 'r') as fp:
#             content = json.load(fp)
#         return content
#
#
# # Elasticsearch index settings
# ES_ORGANIZATION = ElasticIndex('organizations', 'organization', setting=settings.ROOT_API_ES_ENV)
# ES_EMPLOYEE = ElasticIndex('staffing_employee', 'employee', setting=settings.ROOT_API_ES_ENV)
# ES_CANDIDATE = ElasticIndex('candidates', 'candidate', setting=settings.ROOT_API_ES_ENV)
#
# # Fields which correspond to a Mobile Number (field_name: Whether to Hash)
# SEARCH_MOBILE_FIELDS = {
#     ES_EMPLOYEE: {
#         'mobile_hash': True,
#         'alternate_mobile_hash': True
#     },
# }
#
# SEARCH_CROSS_FIELDS = {
#     ES_EMPLOYEE: ['first_name', 'last_name'],
# }
#
# SEARCH_FIELDS = {
#     ES_EMPLOYEE: [
#         'employee_code', 'client_employee_id'
#     ]
# }
