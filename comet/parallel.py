from multiprocessing import Pool
from functools import partial
import multiprocessing
from .terraform import T
import os
import re

COMET_PATH = '.comet'


def execute(tf_jobs, command, extra_args):
    if not os.path.exists(COMET_PATH):
        os.makedirs(COMET_PATH)

    for job in tf_jobs:
        job['extra_args'] = extra_args
        job['path'] = os.path.abspath('') + '/' + COMET_PATH + '/' + \
            job['job_name'] + '/' + job['region'] + '/' + job['workspace']

        # Full directory not created here. Symlink of working directory created
        # in terraform init
        job_dir = os.path.abspath('') + '/' + COMET_PATH + '/' + \
            job['job_name'] + '/' + job['region'] + '/' + job['workspace']
        if not os.path.exists(job_dir):
            os.makedirs(job_dir)

    p = Pool(int(os.environ.get('MAX_PARALLEL')))

    cmd = partial(run_terraform, command)
    results = p.map(cmd, tf_jobs)

    for result in results:
        print(result)


def run_terraform(cmd, job):
    t = T(job)

    result = '=' * 100 + '\n'
    result += 'Job Name: \t\t\t%s\n' % job['job_name']
    result += 'Region: \t\t\t%s\n' % job['region']
    result += 'Workspace: \t\t\t%s\n\n' % job['workspace']

    if cmd == 'init':
        code, stdout, stderr = t.init()

    if cmd == 'plan':
        code, stdout, stderr = t.plan()

    if cmd == 'apply':
        code, stdout, stderr = t.apply()

    if cmd == 'destroy':
        code, stdout, stderr = t.destroy()

    result += stdout
    result += stderr
    result += '=' * 100 + '\n'

    return result
