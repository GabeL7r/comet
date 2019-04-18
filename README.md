# Comet
Comet is a CLI to manage multiple Terraform configurations in parallel.

### Features
* Supports use of workspaces
* Filter executions based on job name, region or workspace
* Runs Terraform in parallel
* DRY backend configuration
* Maps workspaces to different accounts

### Limitations
* Cannot initialize new workspace
* Need to run `comet init` anytime changes to Terraform files are made
* Limited debug logging
* Does NOT prompt user to approve apply or destroy
* Only supports local Terraform configurations

## Getting Started
```shell
pip install pycomet

comet --help

Usage: comet [OPTIONS] COMMAND [ARGS]...

  A program to manage and run multiple terraform configurations.

Options:
  -c, --config-file TEXT      Name of comet config file  [default: comet.yml]
  -d, --depends-on TEXT       Run all jobs that have a depency matching a
                              regex.
  --debug TEXT                Enable debug output.
  -j, --jobs TEXT             Filter jobs using a regular expression.
  -m, --max-parallel INTEGER  Maximum number of jobs to run in parallel
                              (cannot be more than number of cores).
  -r, --region TEXT           Filter regions using regex.
  -w, --workspace TEXT        Filter workspaces using regex.
  -v                          Enable debug logging
  --help                      Show this message and exit.

Commands:
  apply    Run terraform apply.
  destroy  Run terraform destroy.
  init     Run terraform init.
  plan     Run terraform plan.
```

### Configuration

The following configuration is found in the examples directory:

```yaml
---
workspaces:
    - name: prod
      account_id: 12345678
      regions:
          - us-east-1
          - us-west-2
    - name: staging
      account_id: 12345678
      regions:
          - us-west-2
    - name: default
      account_id: 12345678
      regions:
          - us-west-2


# TODO: Add support for creating provider and remote state
backend:
    bucket: cs-comet-test-state
    key: "{{job_name}}/{{region}}"
    region: "us-west-2"
    role_arn: "arn:aws:iam::{{account_id}}:role/terraform"

jobs:
  - name: app
    # TODO: Add ability to include other directories as dependencies
    source: app
    # Depends on can be any value you decide, it is a way to identify jobs have a common dependency. 
    # If you have a job that depends on an external module you can give it a name such as modules-null-label
    # running comet -d modules-null-label will trigger every job that has the value in it's depends on list.
    depends_on:
        - users
        - modules-null-label
  - name: users
    source: users
    depends_on:
        - app
  - name: website
    source: website
    depends_on:
        - modules-null-label
```
#### Workspaces
A list of workspaces used by your Terraform configurations. It is recommended to use a different
AWS account for each workspace to isolate your environments.

#### Backend
Specifies backend parameters to be used during terraform init. Comet using pystache to render variable values
from job and workspace configurations.

#### Jobs
Each job must specify a name and source. The field depends_on is used to to filter jobs based on dependencies. However,
depends_on does not make a dependency graph between jobs. From our experience it is not often you want to run through
an entire dependency graph of Terraform configurations, rather you want to run one set that depends on a common value. 
