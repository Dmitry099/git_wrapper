import argparse
import logging
import os
import shutil
import subprocess
import sys


class GitLogger:
    """Logger for git commands CLI."""

    def __init__(self):
        """Initialize."""
        self.logger = logging.getLogger('__name__')
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )
        self.logger.addHandler(handler)

    def log(self, message: str):
        """Log message.

        :param message: message to log.
        """
        self.logger.info(message)


def clone_repo(repo_url: str) -> str:
    """Clones the repo from repository link.

    :param repo_url: repository link
    :return: path to copy directory
    """

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
    process = subprocess.Popen(['git', 'clone', repo_url, copy_directory],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if error and 'fatal: ' in error.decode('utf-8'):
        print(error.decode('utf-8'))
        sys.exit()
    return copy_directory


def checkout_branch(branch_name: str, copy_directory: str):
    """Checkout to branch.

    :param branch_name: name of the checkout branch
    :param copy_directory: path to copy directory
    """
    os.chdir(copy_directory)
    error_string = (
        "pathspec '%s' did not match any file(s) known to git" % (
            branch_name
        )
    )
    process = subprocess.Popen(
        ['git', 'checkout', branch_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output, error = process.communicate()

    if error and bytes(error_string, 'utf-8') in error:
        subprocess.call(
            ['git', 'checkout', '-b', branch_name],
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            'Command line interface to clone the repository and switch '
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
    git_logger = GitLogger()
    copy_directory = clone_repo(args.repository)
    git_logger.log(
        'Repository with name {} has been cloned to path {}!'.format(
            args.repository, copy_directory
        )
    )
    checkout_branch(args.branch, copy_directory)
    git_logger.log(
        'Branch with name "{}" has been selected!'.format(args.branch)
    )
