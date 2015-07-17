#!/usr/bin/env python

'''
Copyright [2013] [Jon Robson]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

See the License for the specific language governing permissions and
limitations under the License.
'''
import urllib2
import json
import subprocess
import argparse
import sys

def run_shell_command( args, pre_pipe_args=None, verbose = False ):
    """
    run_shell_command(['echo', 'hi']) runs 'echo hi'
    run_shell_command(['grep', 'hi'], ['cat', 'hi.txt']) runs 'cat hi.txt | grep hi'
    """
    cmd = " ".join( args )
    if pre_pipe_args:
        pre_pipe = subprocess.Popen(pre_pipe_args, stdout=subprocess.PIPE)
        process = subprocess.Popen(args, stdin=pre_pipe.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        process = subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True )
    if verbose:
        print "Running `%s`" %cmd
    out, err = process.communicate()
    return out, process.returncode > 0

def run_maintenance_scripts( mediawikipath, verbose = False ):
    args = ['cd', mediawikipath, '&&',
        'php', 'maintenance/update.php' ]
    output, error = run_shell_command( args, verbose=verbose )
    if verbose:
        print output

def update_code_to_master( paths, verbose = False ):
    print "Updating to latest code..."
    for path in paths:
        args = ['cd', path, '&&',
            # Stuff might be dirty
            'git', 'stash', '&&',
            'git', 'checkout', 'master', '&&',
            # Update code
            'git', 'pull', 'origin', 'master' ]
        output, error = run_shell_command( args, verbose=verbose )
        if verbose:
            print output

def get_pending_changes( project, user, verbose = False ):
    url = "https://gerrit.wikimedia.org/r/changes/?q=project:%s+(label:Verified>=0)+AND+status:open+AND+NOT+reviewer:\"%s\"&O=1"%(project,user)
    if verbose:
        print "Request %s"%url
    req = urllib2.Request(url)
    req.add_header('Accept',
                   'application/json,application/json,application/jsonrequest')
    req.add_header('Content-Type', "application/json; charset=UTF-8")
    resp, data = urllib2.urlopen(req)
    data = json.loads(data)
    return data

def checkout_commit( path, changeid, verbose = False ):
    print "Preparing to test change %s..." % changeid
    args = ["cd", path, "&&",
        # might be in a dirty state
        'git', 'stash', '&&',
        'git', 'checkout', 'master', '&&',
        "git", "review", "-d", changeid
     ]
    output, error = run_shell_command( args, verbose=verbose )
    if verbose:
        print output
    # get the latest commit
    args = [ "cd", path, "&&",  "git", "rev-parse", "HEAD" ]
    output, error = run_shell_command( args, verbose=verbose )
    if verbose:
        print output
    commit = output.strip()
    return commit

def bundle_install( path, verbose = False ):
    print 'Running bundle install'
    args = ['cd', path, '&&',
        'cd', 'tests/browser/', '&&',
        'bundle', 'install' ]
    output, error = run_shell_command( args, verbose=verbose )
    if verbose:
        print output

def run_browser_tests( path, tag = None, verbose = False, dry_run = False ):
    print 'Running browser tests...'
    args = ['cd', path, '&&',
        'cd', 'tests/browser/', '&&',
        'bundle', 'exec', 'cucumber', 'features/',
    ]
    if dry_run:
        args.extend( [ '--format', 'rerun' ] )
    if tag:
        if tag[0] != '@' and tag[0]  != '~':
            tag = '@' + tag
        args.extend( [ '--tags', tag ] )

    output, error = run_shell_command( args, verbose=verbose )
    if verbose:
        print output

    if error:
       is_good = False
    else:
        is_good = True
        output = 'Barry says good job. Keep it up.'
    return is_good, output

def do_review( pathtotest, commit, is_good, msg, action, verbose = False ):
    print "Posting to Gerrit..."
    args = [ 'cd', pathtotest, '&&',
        'ssh', '-p 29418',
        'gerrit.wikimedia.org', 'gerrit', 'review' ]
    if action == 'verified':
        if is_good:
            score = '+2'
        else:
            score = '-2'
        args.extend( ['--' + action, score ] )
    else:
        if is_good:
            score = '0'
        else:
            score = '-1'
        args.extend( ['--' + action, score ] )

    if msg:
        args.extend( [ '--message', "\"'" + msg.replace( '"', '' ).replace( "'", '' ) + "'\"" ] )
    args.append( commit )
    # Turn on when you trust it.
    output, error = run_shell_command( args, verbose=verbose )
    if verbose:
        print output


def get_parser_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', help='Name of project e.g. mediawiki/extension/Gather', type=str)
    parser.add_argument('--core', help='Absolute path to core e.g /git/core', type=str)
    parser.add_argument('--test', help='Absolute path that corresponds to project to be tested. e.g /git/core', type=str)
    parser.add_argument('--dependencies', help='Absolute path to a dependency e.g /git/core/extensions/MobileFrontend', type=str, nargs='+')
    parser.add_argument('--tag', help='A tag to run a subset of tests. e.g. `wip`', type=str)
    parser.add_argument('--noupdates', help='This will do no review but will tell you what it is about to review', type=bool)
    parser.add_argument('--review', help='This will post actual reviews to Gerrit. Only use when you are sure Barry is working.', type=bool)
    parser.add_argument('--verify', help='This will post actual reviews to Gerrit. Only use when you are sure Barry is working.', type=bool)
    parser.add_argument('--verbose', help='Advanced debugging.', type=bool)
    parser.add_argument('--user', help='The username of the bot which will do the review.', type=str, default='BarryTheBrowserTestBot')
    parser.add_argument('--paste', help='This will post failed test results to phabricator and share the url in the posted review.', type=bool)
    return parser

def get_paste_url(text):
    """ paste text into Phabricator
    Return paste URL
    """
    output, error = run_shell_command(['arc', 'paste'], ['echo', text])
    # output looks something like "P899: https://phabricator.wikimedia.org/P899"
    return output.split(': ')[1].strip()

def watch( project, user, mediawikipath, pathtotest, tag = None, dependencies=[], noupdates = False, paste=False, action = None, verbose = False ):
    paths = [ mediawikipath, pathtotest ]
    paths.extend( dependencies )
    print "Searching for patches to review..."
    changes = get_pending_changes( project, user )
    if len( changes ) == 0:
        print "No changes."

    for change in changes:
        print "Testing %s..."%change['subject']
        if not noupdates:
            update_code_to_master( paths, verbose )
            run_maintenance_scripts( mediawikipath, verbose )
        commit = checkout_commit( pathtotest, str( change["_number"] ), verbose )
        if not noupdates:
            bundle_install( pathtotest, verbose )
        is_good, output = run_browser_tests( pathtotest, tag, verbose, not paste )
        print output
        if paste:
            print 'Pasting commit %s with (is good = %s)..' %(commit, is_good)
            if not is_good:
                output = get_paste_url(output)
        if action:
            print 'Reviewing commit %s with (is good = %s)..' %( commit, is_good )
            do_review( pathtotest, commit, is_good, output, action, verbose )

if __name__ == '__main__':
    parser = get_parser_arguments()
    args = parser.parse_args()
    if not args.project or not args.core or not args.test:
        print 'Project, core and test are needed.'
        sys.exit(1)
    if args.dependencies:
        deps = args.dependencies
    else:
        deps = []
    if args.review:
        action = 'code-review'
    else:
        action = 'verified'

    watch(
        args.project,
        args.user,
        args.core,
        args.test,
        args.tag,
        deps,
        args.noupdates,
        args.paste,
        action,
        args.verbose
    )

