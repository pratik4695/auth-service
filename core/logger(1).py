import threading
from contextlib import ContextDecorator
from string import Template
from time import time


class LoggerMeta:
    obj_name = None
    obj_id = None
    trace_id = None
    iteration_id = None

    def log(self, message, print_type="INFO"):
        log_object_template = "[{obj_name}:{obj_id}]"
        log_trace_template = "[{trace_id}]"
        log_iteration_template = "[{iteration_id}]"
        log_template = "[{class_name}] $log_object_template $log_trace_template $log_iteration_template {message} {print_type}"
        if self.obj_id and self.obj_name:
            log_obj = log_object_template.format(obj_name=self.obj_name, obj_id=self.obj_id)
            log_template = Template(log_template).safe_substitute(log_object_template=log_obj)
        else:
            log_template = Template(log_template).safe_substitute(log_object_template='')
        if self.trace_id:
            log_trace_id = log_trace_template.format(trace_id=self.trace_id)
            log_template = Template(log_template).safe_substitute(log_trace_template=log_trace_id)
        else:
            log_template = Template(log_template).safe_substitute(log_trace_template='')
        if self.iteration_id:
            log_iteration_id = log_iteration_template.format(iteration_id=self.iteration_id)
            log_template = Template(log_template).safe_substitute(log_iteration_template=log_iteration_id)
        else:
            log_template = Template(log_template).safe_substitute(log_iteration_template='')
        log = log_template.format(class_name=self.__class__.__name__, message=message, print_type=print_type)
        print(log)

    def log_error(self, message):
        self.log(message, print_type="**ERROR**")

    def log_warn(self, message):
        self.log(message, print_type="*WARN*")


class GRPCLogger(ContextDecorator):
    def __init__(self, rpc_name, request_data):
        self.name = rpc_name
        self.request = request_data

    def __enter__(self):
        self.start_time = time()
        print(f'Received {self.name} on thread {threading.currentThread().ident} with data {self.request}')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time()
        run_time = self.end_time - self.start_time
        print(f'Execution {self.name} on thread {threading.currentThread().ident} took {run_time} seconds')
