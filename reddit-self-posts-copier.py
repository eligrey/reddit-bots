#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''Reddit Self Posts Copier.

Copies self posts from one or more subreddit to a target subreddit.'''

# By Eli Grey, http://eligrey.com
# License: The MIT/X11 license (see COPYING.md)

from sys import stdout, stdin
from urllib import request as urlrequest
from urllib import parse as urlparse
from urllib import error as urlerror
from http import cookiejar
from time import sleep
import json
import re

VERSION = '2010-06-09'
APP_TITLE = 'Reddit Self Posts Copier'
USER_AGENT = {'User-agent': APP_TITLE + '/' + VERSION}

def request_json(request):
    try:
        return json.loads(urlrequest.urlopen(request).read().decode('utf-8'))
    except (urlerror.URLError, KeyError, ValueError):
        return None

def unescape_entities(html):
    left_bracket = re.compile('&lt;', re.IGNORECASE)
    right_bracket = re.compile('&gt;', re.IGNORECASE)
    ampersand = re.compile('&amp;', re.IGNORECASE)
    return ampersand.sub('&', right_bracket.sub('>', left_bracket.sub('<', html)))

class Title:
    def set(self, title):
        self.title = title
        stdout.write('\x1b]2;' + title + '\x07')
    
    def get(self):
        return self.title

class RedditInvalidUsernamePasswordException(Exception):
    pass

class SubredditSubmissionsCopier:
    def __init__(self, options, submitted):
        self.options = options
        self.submitted = submitted
        self._maybe_down_message = 'Perhaps the connection was interupted or %s is down.' % self.options.site
        cookie_jar = cookiejar.FileCookieJar()
        urlrequest.install_opener(urlrequest.build_opener(urlrequest.HTTPCookieProcessor(cookie_jar)))
    
    def login(self):
        params = urlparse.urlencode({
            'user': self.options.username,
            'passwd': self.options.password
        })
        
        request = urlrequest.Request(self.options.login_url, params, USER_AGENT)
        
        if self.options.verbose:
            print('Logging in as %s.' % self.options.username)
        
        response = request_json(request)
        
        if response is None or 'invalid password' in str(response):
            raise RedditInvalidUsernamePasswordException('Login failed. Please ensure that your username and password are correct.')
        
        title.set('%s - %s' % (self.options.target, APP_TITLE))
    
    def submit(self, submission, modhash):
        self.submitted.append(submission['id'])
        try:
            open(self.options.save_file, 'a').write('\n' + submission['id'])
        except IOError:
            if self.options.verbose:
                print('Problem saving submission %s.' % submission['id'])
        
        submission_title = unescape_entities(submission['title'])
        
        if self.options.manual:
            normal_title = title.get()
            title.set('[!] ' + normal_title);
            print('Submit %r from %s (Y/N)?' % (submission_title, submission['subreddit']))
            approved = stdin.readline()[0].upper()
            title.set(normal_title)
            if approved != 'Y':
                return
        
        if self.options.verbose:
            print('Submitting %r from %s.\n' % (submission_title, submission['subreddit']))
        
        params = urlparse.urlencode({
            'title': submission_title,
            'text': unescape_entities(submission['selftext']),
            'kind': 'self',
            'sr': self.options.target,
            'uh': modhash
        })
        
        request = urlrequest.Request(self.options.submit_url, params, USER_AGENT)
        response = request_json(request)
        
        if self.options.verbose:
            if '.error.BAD_CAPTCHA.field-captcha' in str(response):
                print('Could not submit the post because a CAPTCHA was required.')
            elif '.error.RATELIMIT.field-ratelimit' in str(response):
                print('Could not submit the post because a submission rate limit was triggered.')
            elif response is None:
                print('Problem submitting the post.' + self._maybe_down_message)
    
    def poll(self):
        if self.options.verbose:
            print('Polling for new submissions.')
        
        request = urlrequest.Request(self.options.poll_url, headers=USER_AGENT)
        submissions = request_json(request)
        
        if submissions is not None:
            modhash = submissions['data']['modhash']
            submissions = submissions['data']['children']
            for submission in submissions:
                if submission['data']['is_self'] and submission['data']['id'] not in submitted:
                    sleep(self.options.submit_rate)
                    self.submit(submission['data'], modhash)

if __name__ == '__main__':
    from optparse import OptionParser
    
    parser = OptionParser(version=APP_TITLE + ' ' + VERSION)
    
    parser.add_option('-u', '--username', dest='username',
                      help='username for bot to login as', metavar='USERNAME')
    parser.add_option('-p', '--password', dest='password',
                      help='password for the username', metavar='PASSWORD')
    parser.add_option('-r', '--subreddit', dest='subreddits',
                      help='subreddits to copy from; can specify multiple',
                      metavar='SUBREDDIT', action='append')
    parser.add_option('-t', '--target', dest='target', metavar='SUBREDDIT',
                      help='target subreddit')
    parser.add_option('-v', '--verbose', dest='verbose', default=True, metavar='VERBOSE',
                      action='store_true', help='show informative messages')
    parser.add_option('-q', '--quiet', dest='verbose', metavar='VERBOSE',
                      action='store_false', help='hide informative messages')
    parser.add_option('-s', '--site', dest='site', metavar='SITE', help='target reddit-powered site',
                      default='http://www.reddit.com/') # yeah, I sold out to reddit.com
    parser.add_option('-f', '--save-file', dest='save_file', metavar='FILE',
                      default='.submitted', help='file to save the submitted posts to')
    parser.add_option('-l', '--limit', dest='limit', metavar='LIMIT', type='int',
                      help='amount of submissions to poll for', default=25)
    parser.add_option('-o', '--poll-rate', dest='poll_rate', default=120, type='float',
                      metavar='POLL_RATE', help='rate in seconds at which to poll for new submissions')
    parser.add_option('-e', '--submit-rate', dest='submit_rate', default=4, type='float',
                      metavar='SUBMIT_RATE', help='rate in seconds at which to post new submissions')
    parser.add_option('-m', '--manual', dest='manual', default=False, action='store_true',
                      metavar='ENABLE_MANUAL', help='enable manual screening of submissions') 
    
    (options, args) = parser.parse_args()
    
    options.poll_url = options.site + 'r/%s/hot.json?limit=%d' % ('+'.join(options.subreddits), options.limit)
    options.login_url = options.site + 'api/login'
    options.submit_url = options.site + 'api/submit'
    
    try:
        submitted = open(options.save_file, 'r').read().split('\n')
        if options.verbose:
            print('Loaded ' + options.save_file)
    except IOError:
        submitted = []
    
    title = Title()
    title.set(APP_TITLE)
    
    copier = SubredditSubmissionsCopier(options, submitted)
    copier.login()
    
    try:
        while True:
            copier.poll()
            sleep(options.poll_rate)
    except KeyboardInterrupt:
        if options.verbose:
            print('Closing %s.' % APP_TITLE)
        quit()

