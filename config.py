"""Validates and Generates Array of Terraform Configs to Execute"""

import itertools
import os
import re
import pystache
import sys
import yaml
import logging
from jsonschema import validate

DEPS = 'depends_on'
NAME = 'name'
JOBS = 'jobs'
JOB = 'job'
SOURCE = 'source'
ACCOUNT_ID = 'account_id'
REGIONS = 'regions'
BACKEND = 'backend'
BUCKET = 'bucket'
KEY = 'key'
REGION = 'region'
ROLE_ARN = 'role_arn'
WORKSPACE = 'workspace'


class Config:
    """Validates and Generates Array of Terraform Configs to Execute"""

    def __init__(self, file_path):
        try:
            with open(file_path) as file:
                self.config = yaml.safe_load(file)
        except BaseException:
            sys.exit('Could not load configuration file %s' % file_path)

        self.validate_schema()

        self.workspaces = list(
            map(lambda w: Workspace(w), self.config['workspaces']))
        self.jobs = list(map(lambda j: Job(j), self.config[JOBS]))

        self.validate_sources()

    def validate_schema(self):
        schema = """
type: object
required:
  - jobs
  - backend
properties:
  backend:
    type: object
    required:
      - bucket
      - key
      - region
    properties:
      bucket:
        type: string
      key:
        type: string
      region:
        type: string

  jobs:
    type: array
    items:
      type: object
      properties:
        remote:
          type: object
          required:
            - bucket
            - key
            - region
      required:
        - source
        - name
"""

        try:
            validate(self.config, yaml.safe_load(schema))
        except Exception as e:
            sys.exit(e)

    def validate_sources(self):
        map(lambda j: j.validate_source(), self.jobs)

    def filter_jobs(self, job):
        if job:
            self.jobs = list(
                filter(
                    lambda j: j.name_matches_regex(job),
                    self.jobs))

    def filter_workspaces(self, workspace):
        if workspace:
            self.workspaces = list(
                filter(
                    lambda w: w.name_matches_regex(workspace),
                    self.workspaces))

    def filter_regions(self, region):
        if region:
            map(lambda w: w.filter_regions(region), self.workspaces)

    def filter_depends_on(self, dependency):
        if dependency:
            self.jobs = list(
                filter(
                    lambda j: j.has_dependency(dependency),
                    self.jobs))

    def get_terraform_jobs(self):
        terraform_jobs = []
        for job in self.jobs:
            terraform_job = TerraformJob(
                job, self.workspaces, self.config[BACKEND])
            terraform_jobs += terraform_job.render()
        return terraform_jobs


class Workspace:
    def __init__(self, workspace):
        self.name = workspace[NAME]
        self.account_id = workspace[ACCOUNT_ID]
        self.regions = workspace[REGIONS]

    def name_matches_regex(self, regex):
        return re.match(re.compile(regex), self.name)

    def filter_regions(self, region):
        self.regions = list(
            filter(
                lambda r: re.match(
                    re.compile(region),
                    r),
                self.regions))

    def get_name(self):
        return self.name

    def get_regions(self):
        return self.regions

    def get_account_id(self):
        return self.account_id


class Job:
    def __init__(self, job):
        self.name = job[NAME]
        self.source = job[SOURCE]
        self.depends_on = job[DEPS]

    def get_name(self):
        return self.name

    def get_source(self):
        return self.source

    def validate_source(self):
        if not os.path.exists(self.source):
            sys.exit('Could not find path %s' % self.source)

    def name_matches_regex(self, regex):
        return re.match(re.compile(regex), self.name)

    def has_dependency(self, dependency):
        return dependency in self.depends_on


class Backend:
    @staticmethod
    def render(backend, job):
        rendered = {}
        for key in backend.keys():
            rendered[key] = pystache.render(backend[key], job)

        return rendered


class TerraformJob:
    def __init__(self, job, workspaces, backend):
        self.job = job
        self.workspaces = workspaces
        self.backend = backend

    def render(self):
        tf_jobs = []
        for workspace in self.workspaces:
            cart_product = list(itertools.product(
                [workspace.get_name()],
                [workspace.get_account_id()],
                workspace.get_regions()))

            keys = ['workspace', 'account_id', 'region']
            for item in cart_product:
                job = dict(zip(keys, item))
                job['job_name'] = self.job.get_name()
                job['source'] = self.job.get_source()
                job['backend'] = Backend().render(self.backend, job)
                tf_jobs.append(job)

        return tf_jobs
