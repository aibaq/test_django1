from . import common
from . import install

from fabric.state import env

env.repository = "https://github.com/aibaq/test_django1.git"
env.repository_ssh = "git@github.com:aibaq/test_django1.git"
env.repo_name = "test_django1"
env.user = "ubuntu"
env.key_filename = "~/test_django1.pem"
env.hosts = [""]
