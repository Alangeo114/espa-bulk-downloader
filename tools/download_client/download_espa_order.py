#!/usr/bin/env python

'''
Author: David Hill
Date: 01/31/2014
Purpose: A simple python client that will download all available (completed)
         scenes for a user order(s).

Requires: Python feedparser and standard Python installation.

Version: 1.0 -- David Hill
    Original Implementation
Version: 1.1 -- Ron Dilley
    Updated for pep8 compliance.
    Updated to support resuming the downloads.
'''

import os
import sys
import shutil
import argparse
import feedparser
import urllib2


def download_the_file(link, target):

    print ("Copying %s to %s" % (link, target))
    req = urllib2.urlopen(link)
    with open(target, 'wb') as target_handle:
        shutil.copyfileobj(req, target_handle)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("-e", "--email", required=True,
                        help=("email address for the user that"
                              " submitted the order"))

    parser.add_argument("-o", "--order", required=True,
                        help=("which order to download"
                              " (use ALL for every order)"))

    parser.add_argument("-d", "--target_directory", required=True,
                        help="where to store the downloaded scenes")

    parser.add_argument("--resume", action='store_true', dest='resume',
                        required=False, default=False,
                        help="resume downloading of files")

    args = parser.parse_args()

    # print args.email
    # print args.order
    # print args.target_directory
    # print args.resume

    # make sure we have a target to land the scenes
    if not os.path.exists(args.target_directory):
        os.makedirs(args.target_directory)
        print ("Created target_directory:%s" % args.target_directory)

    # build the url for the order and get it into a feedparser object
    feed_url = "http://espa.cr.usgs.gov/ordering/status/%s/rss/" % args.email
    feed = feedparser.parse(feed_url)

    # look through all their links and see if its the right order
    target_links = []
    if args.order == "ALL":
        target_links = [entry.link for entry in feed.entries]
    else:
        # user asked for a specific order so go look for it
        target_links = [entry.link for entry in feed.entries
                        if args.order in entry.description]

    # stop if theres nothing to do
    if len(target_links) == 0:
        print("No scenes available to download for %s" % args.order)
        exit()
    else:
        print("Found %i scenes to download in order:%s"
              % (len(target_links), args.order))

    # rip through the links and download them using shutil to control
    # memory usage.
    for link in target_links:
        # name target file same as source file
        parts = link.split('/')
        filename = parts[len(parts) - 1]
        target = os.path.join(args.target_directory, filename)

        if not args.resume:
            download_the_file(link, target)

        elif not os.path.exists(target):
            download_the_file(link, target)

        else:
            req = urllib2.urlopen(link)
            stat_info = os.stat(target)

            source_length = int(req.headers['content-length'])
            target_length = int(stat_info.st_size)

            if target_length == source_length:
                print ("Skipping %s already downloaded" % target)
            else:
                download_the_file(link, target)

    print("Scene downloads complete.")
    sys.exit(0)
