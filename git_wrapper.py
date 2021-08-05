import argparse
import os
import re
import shutil
import subprocess

GIT_URL_REGEXP = (
    r'((git|ssh|http(s)?)|(git@[\w\.]+))(:(//)?)([\w\.@\:/\-~]+)(\.git)(/)?'
)


class IncorrectRepoLinkException(Exception):
    """Exception raised when repository link is not correct."""
    def __init__(self, link_name: str):
        self.link_name = link_name

    def __str__(self):
        return (
            'Link {} is not match with git url regular expression {}'.format(
                self.link_name, GIT_URL_REGEXP
            )
        )


def clone_repo(repo_url: str):
    """Clones the repo from repository link."""

    if re.match(GIT_URL_REGEXP, repo_url) is None:
        raise IncorrectRepoLinkException(repo_url)

    url_to_find_repo_name = repo_url[:-1] if repo_url[-1] == '/' else repo_url
    repo_directory_name = os.path.splitext(os.path.basename(
        url_to_find_repo_name
    ))[0]
    # For task purpose the path to copied directory
    # is stable, but we can make it like argument for CLI
    # if it will be needed.
    copy_directory = os.path.join(os.path.dirname(os.getcwd()),
                                  repo_directory_name)

    if os.path.exists(copy_directory) and os.path.isdir(copy_directory):
        shutil.rmtree(copy_directory)
    process = subprocess.Popen(['git', 'clone', repo_url, copy_directory])
    process.wait()
    # change directory for future command to make a checkout
    os.chdir(copy_directory)


def checkout_branch(branch_name: str):
    """Checkout to branch."""
    process = subprocess.Popen(['git', 'checkout', '-B', branch_name])
    process.wait()

parser = argparse.ArgumentParser(
    description=('Command line interface to clone the repository and switch '
                 'to the branch.')
)

parser.add_argument(
    '-c',
    type=str,
    dest='repository',
    required=True,
    help='repository link'
)
parser.add_argument(
    '-b',
    type=str,
    dest='branch',
    required=True,
    help='branch name'
)

args = parser.parse_args()
clone_repo(args.repository)
checkout_branch(args.branch)
