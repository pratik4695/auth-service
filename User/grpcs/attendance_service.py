from django.conf import settings

from core.grpc.tasks import AttendanceGrpcTask
from core.helpers import RecognizeUserAPI


# TODO: This needs to be implemented for future use
class GetEmployeeOrganizationUsingAttendance(AttendanceGrpcTask):

    def __call__(self, *args, **kwargs):
        return {}
