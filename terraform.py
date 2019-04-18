from python_terraform import *
import os
import sys
import glob
import shutil


class T:
    def __init__(self, job):
        self.job = job
        self.custom_args = self.job['extra_args'] or ''
        self.t = Terraform(working_dir=self.job['path'])

    def init(self):
        self.copy_and_overwrite(
            os.path.abspath('') +
            '/' +
            self.job['source'],
            self.job['path'])

        code, stdout, stderr = self.t.init(backend_config=self.job['backend'])

        if os.path.exists(self.job['path'] + '/.terraform'):
            file_name = self.job['path'] + '/.terraform/environment'
            f = open(file_name, 'w')
            f.write(self.job['workspace'])
            f.close()

        return code, stdout, stderr

    def copy_and_overwrite(self, from_path, to_path):
        if os.path.exists(to_path):
            shutil.rmtree(to_path)
        shutil.copytree(from_path, to_path)

    def apply(self):
        return self.t.apply(
            self.custom_args,
            var={
                'region': self.job['region']},
            skip_plan=True)

    def plan(self):
        print('Running plan...')
        return self.t.plan(
            self.custom_args, var={
                'region': self.job['region']})

    def destroy(self):
        return self.t.destroy(
            var={
                'region': self.job['region']},
        )
