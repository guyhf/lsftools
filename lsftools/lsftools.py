import itertools
from multiprocessing import Pool
import os
import re
import subprocess
import time
from collections import Counter
import numpy as np


def bjobs_re_match(regex, ngroup, user=None):
    re_obj = re.compile(regex)
    if user == None:
        user = os.getlogin()
    results = subprocess.check_output(["bjobs","-w", "-u", user])
    lines = results.split("\n")[1:]

    results = list()
    for line in lines:
        match = re_obj.match(line)
        if match:
            results.append(match.group(ngroup))
    return results


def get_job_counts():
    results = subprocess.check_output(["bjobs","-u","all"])
    lines = results.split("\n")[1:]
    job_counts = Counter()

    for line in lines:
        line = re.sub("\s+", " ", line)
        if len(line) <= 0:
            continue
        user = line.split(" ")[1]
        job_counts[user] += 1

    total = sum(job_counts.values())
    job_counts['total'] = total

    return job_counts


def run_commands(commands, filenames, test=False, verbose=False):
    for command, filename in itertools.izip(commands, filenames):
        if os.path.exists(filename):
            try:
                os.unlink(filename)
            except:
                pass
        cmd_list = command.split(" ")
        try:
            if test:
                print "would run command: %s" % command
            else:
                if verbose:
                    print "running command: %s" % command
                subprocess.check_output(cmd_list)
        except:
            print "could not run process: " + " ".join(cmd_list)
            raise

    if verbose or test:
        print "ran %d jobs" % len(commands)

    return len(commands)


def run_command(args):
    command, filename, test, verbose = args
    if os.path.exists(filename):
        try:
            if not test:
                os.unlink(filename)
        except:
            pass
    cmd_list = command.split(" ")
    try:
        if test:
            print "would run command: %s" % command
        else:
            if verbose:
                print "running command: %s" % command
            subprocess.check_output(cmd_list)
    except:
        print "could not run process: " + " ".join(cmd_list)
        return False

    return True


def run_commands_async(commands, filenames, pool_size=20, test=False, verbose=False):
    args_lists = itertools.izip(commands, filenames, itertools.repeat(test, len(commands)), itertools.repeat(verbose, len(commands)))
    pool = Pool(pool_size)
    async_result = pool.map_async(run_command, args_lists)
    results = async_result.get()
    return np.all(np.array(results))


def add_jobs(commands, filenames, memlimit=12, test=False, verbose=False, group=None):
    """
    Take 2 lists of equal length and bsub jobs for each command, directing
    output to the correspinding filename.  Commands are strings.  Returns
    number of jobs submitted
    """
    for command, filename in itertools.izip(commands, filenames):
        if os.path.exists(filename):
            try:
                os.unlink(filename)
            except:
                pass
        cmd_list = command.split(" ")
        bsub_list = ["/opt/lsf/8.3/linux2.6-glibc2.3-x86_64/bin/bsub", "-v", "%d" % memlimit, "-M", "%d" % memlimit, "-o", filename]
        if group is not None:
            bsub_list.extend(["-g", group])
        bsub_list.extend(cmd_list)
        try:
            if test:
                print "would run command: %s" % " ".join(bsub_list)
            else:
                subprocess.check_output(bsub_list)
        except:
            print "could not run process: " + " ".join(bsub_list)
            raise

    if test:
        print "would have submitted %d jobs" % len(commands)

    if verbose and not test:
        print "submitted %d jobs" % len(commands)

    return len(commands)

    
def keep_jobs_running(commands, filenames, max_jobs, user=None, wait=300, verbose=False):

    total = len(commands)

    if user == None:
        user = os.getlogin()

    jobs_submitted = 0

    while len(commands) > 0:
        job_counts = get_job_counts()
        if job_counts[user] < max_jobs:
            to_add = max_jobs - job_counts[user]
            to_add = min(to_add, len(commands))

            commands_add = commands[:to_add]
            filenames_add = filenames[:to_add]

            commands = commands[to_add:]
            filenames = filenames[to_add:]

            add_jobs(commands_add, filenames_add, memlimit=27, verbose=verbose)

            jobs_submitted += to_add

            if verbose:
                print "%d/%d jobs submitted" % (jobs_submitted, total)
        time.sleep(wait)  # wait in seconds
    return jobs_submitted