# Barry-the-Browser-Test-Bot

To use:
Configure your favourite Browser test engine and the instance to run against:

    export BROWSER=phantomjs
    export MEDIAWIKI_URL=http://en.m.wikipedia.beta.wmflabs.org/wiki/
    export MEDIAWIKI_API_URL=http://en.wikipedia.beta.wmflabs.org/w/api.php
    export MEDIAWIKI_USER=Selenium_user
    export MEDIAWIKI_PASSWORD=password

Configure Git review

Download the [GerritCommandLinePlugin](https://github.com/jdlrobson/GerritCommandLine)

Enter the browser test directory.
Check out a commit you want to run your browser tests again.
Run:

    ./barrybot.py --project 'mediawiki/extensions/Gather' --core '/Users/jrobson/git/core/' --test /Users/jrobson/git/core/extensions/Gather/ --tag wip --dependencies /Users/jrobson/git/core/extensions/MobileFrontend/

Barry will let you know if he likes it.
