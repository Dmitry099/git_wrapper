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


def clone_repo(repo_url: str) -> str:
    """Clones the repo from repository link.

    :param repo_url: repository link
    :return: path to copy directory
    """

    if re.match(GIT_URL_REGEXP, repo_url) is None:
        raise IncorrectRepoLinkException(repo_url)

    url_to_find_repo_name = repo_url[:-1] if repo_url[-1] == '/' else repo_url
    repo_directory_name = os.path.splitext(os.path.basename(
        url_to_find_repo_name
    ))[0]
    # For task purpose the path to copied directory
    # is stable, but we can make it like argument for CLI
    # if it will be needed.
    copy_directory = os.path.join(os.getcwd(), repo_directory_name)

    if os.path.exists(copy_directory) and os.path.isdir(copy_directory):
        shutil.rmtree(copy_directory)
    process = subprocess.Popen(['git', 'clone', repo_url, copy_directory])
    process.wait()
    return copy_directory


def checkout_branch(branch_name: str, copy_directory: str):
    """Checkout to branch.

    :param branch_name: name of the checkout branch
    :param copy_directory: path to copy directory
    """
    os.chdir(copy_directory)
    error_string = (
        "error: pathspec '%s' did not match any file(s) known to git\n" % (
            branch_name
        )
    )
    process = subprocess.Popen(
        ['git', 'checkout', branch_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output, error = process.communicate()

    if error and error == bytes(error_string, 'utf-8'):
        process = subprocess.Popen(
            ['git', 'checkout', '-b', branch_name],
        )
        process.wait()
    else:
        print('Output: {}\nError: {}\n'.format(output, error))


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


if __name__ == "__main__":
    args = parser.parse_args()
    copy_directory = clone_repo(args.repository)
    checkout_branch(args.branch, copy_directory)
