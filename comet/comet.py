"""CLI Tool to run Terraform"""

import click
import json
import os
from .config import Config
from .parallel import execute
import logging
import multiprocessing
import sys


@click.group()
@click.option(
    '-c',
    '--config-file',
    default='comet.yml',
    help='Name of comet config file',
    show_default=True)
@click.option(
    '-d',
    '--depends-on',
    help='Run all jobs that have a depency matching a regex.')
@click.option('--debug', default=False, help='Enable debug output.')
@click.option(
    '-j',
    '--jobs',
    help='Filter jobs using a regular expression.')
@click.option(
    '-m',
    '--max-parallel',
    type=int,
    help='Maximum number of jobs to run in parallel (cannot be more than number of cores).')
@click.option('-r', '--region',
              help='Filter regions using regex.')
@click.option('-w', '--workspace',
              help='Filter workspaces using regex.')
@click.option('-v', is_flag=True, help="Enable debug logging")
@click.pass_context
def cli(
        ctx,
        config_file,
        debug,
        depends_on,
        jobs,
        region,
        workspace,
        v,
        max_parallel,
):
    """A program to manage and run multiple terraform configurations."""
    os.environ['LOGLEVEL'] = 'DEBUG' if v else 'CRITICAL'
    os.environ['MAX_PARALLEL'] = str(
        max_parallel or multiprocessing.cpu_count())

    ctx.obj = {}
    ctx.obj['WORKSPACE'] = workspace

    config = Config(config_file)
    config.filter_jobs(jobs)
    config.filter_depends_on(depends_on)
    config.filter_workspaces(workspace)
    config.filter_regions(region)
    ctx.obj['TF_JOBS'] = config.get_terraform_jobs()


@cli.command()
@click.option(
    '--apply-args',
    default=None,
    help='Additional arguments to pass to terraform apply.')
@click.pass_context
def apply(ctx, apply_args):
    """Run terraform apply."""
    # TODO: add polymorphism to handle this
    parallel.execute(
        ctx.obj['TF_JOBS'],
        'apply',
        apply_args
    )


@cli.command()
@click.option(
    '--plan-args',
    default=None,
    help='Additional arguments to pass to terraform plan.')
@click.pass_context
def plan(ctx, plan_args):
    """Run terraform plan."""
    execute(
        ctx.obj['TF_JOBS'],
        'plan',
        plan_args
    )


@cli.command()
@click.pass_context
def destroy(ctx):
    """Run terraform destroy."""
    execute(
        ctx.obj['TF_JOBS'],
        'destroy',
        None

    )


@cli.command()
@click.option(
    '--init-args',
    default=None,
    help='Additional arguments to pass to terraform init.')
@click.pass_context
def init(ctx, init_args):
    """Run terraform init."""
    execute(
        ctx.obj['TF_JOBS'],
        'init',
        init_args
    )
