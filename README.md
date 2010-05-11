Reddit Bots
===========

A collection of various reddit bots.


Reddit Feeds Auto-Poster
------------------------

Reddit Feeds Auto-Poster is a Python script that automatically posts new entries from
feeds to a subreddit.

Coming soon! (read: sometime in 2010)


Reddit Self Posts Copier
------------------------

Reddit Self Posts Copier is a Python script that copies self posts from one or more
subreddit to a target subreddit.

### Usage

    reddit-self-posts-copier.py [options]


### Options

<dl>
  <dt><code>--version</code></dt>
  <dd>show program's version number and exit</dd>
  
  <dt><code>-h</code>, <code>--help</code></dt>
  <dd>show this help message and exit</dd>
  
  <dt><code>-u USERNAME</code>, <code>--username=USERNAME</code></dt>
  <dd>username for bot to login as</dd>
  
  <dt><code>-p PASSWORD</code>, <code>--password=PASSWORD</code></dt>
  <dd>password for the username</dd>
  
  <dt><code>-r SUBREDDIT</code>, <code>--subreddit=SUBREDDIT</code></dt>
  <dd>subreddits to copy from; can specify multiple</dd>
  
  <dt><code>-t SUBREDDIT</code>, <code>--target=SUBREDDIT</code></dd>
  <dd>target subreddit</dd>
  
  <dt><code>-v</code>, <code>--verbose</code> (on by default)</dt>
  <dd>show informative messages</dt>

  <dt><code>-q</code>, <code> --quiet</code></dt>
  <dd>hide informative messages</dd>
  
  <dt><code>-s SITE</code>, <code>--site=SITE</code> (defaults to <code>http://www.reddit.com/</code>)</dt>
  <dd>target reddit-powered site</dd>
  
  <dt><code>-f FILE</code>, <code>--save-file=FILE</code> (defaults to <code>.submitted</code>)</dt>
  <dd>file to save the submitted posts to</dd>
  
  <dt><code>-l LIMIT</code>, <code>--limit=LIMIT</code> (defaults to <code>25</code>)</dt>
  <dd>amount of submissions to poll for</dd>
  
  <dt><code>-o POLL_RATE</code>, <code>--poll-rate=POLL_RATE</code> (defaults to <code>120</code>)</dt>
  <dd>rate in seconds at which to poll for new submissions</dd>
</dl>


![Tracking image](//in.getclicky.com/212712ns.gif =1x1)
