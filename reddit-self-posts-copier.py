#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''Reddit Self Posts Copier.

Copies self posts from one or more subreddit to a target subreddit.'''

# Copyright (c) 2010 Eli Grey; http://eligrey.com
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

from urllib import request as urlrequest
from urllib import parse as urlparse
from urllib import error as urlerror
from http import cookiejar
from time import sleep
import json

VERSION = 1.0
USER_AGENT = {'User-agent': 'Reddit Self Posts Copier/%s' % VERSION}

class RedditInvalidUsernamePasswordException(Exception):
    pass

class SubredditSubmissionsCopier:
    def __init__(self, options):
        self.username = options.username
        self.password = options.password
        self.verbose = options.verbose
        self.target = options.target
        self.poll_url = '%sr/%s/hot.json?limit=%d' % (options.site, '+'.join(options.subreddits), options.limit)
        self.login_url = '%sapi/login' % options.site
        self.submit_url = '%sapi/submit' % options.site
        cookie_jar = cookiejar.FileCookieJar()
        urlrequest.install_opener(urlrequest.build_opener(urlrequest.HTTPCookieProcessor(cookie_jar)))
    
    def _request_json(self, request):
        try:
            return json.loads(urlrequest.urlopen(request).read().decode('utf-8'))
        except urlerror.URLError:
            if self.verbose:
                print('Problem requesting %r' % request)
            return None
        except (KeyError, ValueError):
            if self.verbose:
                print('The JSON returned was incomplete. Perhaps the connection was interupted or reddit is down.')
            return None
    
    def login(self):
        params = urlparse.urlencode({
            'user': self.username,
            'passwd': self.password
        })
        
        request = urlrequest.Request(self.login_url, params, USER_AGENT)
        
        if self.verbose:
            print('Logging in.')
        response = self._request_json(request)
        
        if response is None or 'invalid password' in str(response):
            raise RedditInvalidUsernamePasswordException('Login failed. Please ensure that your username and password are correct.')
    
    def submit(self, submission, modhash):
        newly_submitted.append(submission['id'])
        if self.verbose:
            print('\nSubmitting %r from %s.' % (submission['title'], submission['subreddit']))
        
        params = urlparse.urlencode({
            'title': submission['title'],
            'text': submission['selftext'],
            'kind': 'self',
            'sr': self.target,
            'uh': modhash
        })
        
        request = urlrequest.Request(self.submit_url, params, USER_AGENT)
        response = self._request_json(request)
        
        if self.verbose:
            if '.error.BAD_CAPTCHA.field-captcha' in str(response):
                print('Could not submit the post because a CAPTCHA was required.')
            elif response is None:
                print('Problem submitting the post. Perhaps the connection was interupted or reddit is down.')
    
    def poll(self):
        if self.verbose:
            print('Polling for new submissions.')
        
        request = urlrequest.Request(self.poll_url, headers=USER_AGENT)
        submissions = self._request_json(request)
        
        if submissions is not None:
            modhash = submissions['data']['modhash']
            submissions = submissions['data']['children']
            for submission in submissions:
                if submission['data']['is_self'] and \
                   submission['data']['id'] not in newly_submitted and \
                   submission['data']['id'] not in submitted:
                    self.submit(submission['data'], modhash)
                    sleep(4)

if __name__ == '__main__':
    from optparse import OptionParser
    
    parser = OptionParser(version='Reddit Self Posts Copier %s' % VERSION)
    
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
                      default='http://www.reddit.com/') # yeah, I sold out
    parser.add_option('-f', '--save-file', dest='save_file', metavar='FILE',
                      default='.submitted', help='file to save the submitted posts to')
    parser.add_option('-l', '--limit', dest='limit', metavar='LIMIT', type='int',
                      help='amount of submissions to poll for', default=25)
    parser.add_option('-o', '--poll-rate', dest='poll_rate', default=120, type='float',
                      help='rate in seconds at which to poll for new submissions')
    
    (options, args) = parser.parse_args()
    
    try:
        if options.verbose:
            print('Loading submitted posts file.')
        submitted = open(options.save_file, 'r').read().split('\n')
    except IOError:
        submitted = []
    
    newly_submitted = []
    copier = SubredditSubmissionsCopier(options)
    copier.login()
    
    try:
        while True:
            copier.poll()
            sleep(options.poll_rate)
    except KeyboardInterrupt:
        if options.verbose:
            print('\nSaving submitted posts file.')
        
        open(options.save_file, 'a').write('\n' + '\n'.join(newly_submitted))
        quit()

