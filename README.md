# Barry-the-Browser-Test-Bot

## To use:
### Configure your favourite Browser test engine and the instance to run against:

    export BROWSER=phantomjs
    export MEDIAWIKI_URL=http://en.m.wikipedia.beta.wmflabs.org/wiki/
    export MEDIAWIKI_API_URL=http://en.wikipedia.beta.wmflabs.org/w/api.php
    export MEDIAWIKI_USER=Selenium_user
    export MEDIAWIKI_PASSWORD=password

### Configure Git review
Download the [GerritCommandLinePlugin](https://github.com/jdlrobson/GerritCommandLine)

### Install and configure arcanist for pasting failed test results to Phabricator
#### Install
For full instructions see https://secure.phabricator.com/book/phabricator/article/arcanist_quick_start/
```
cd /opt
git clone https://github.com/phacility/arcanist.git
cd /opt/arcanist/externals/includes/
git clone https://github.com/phacility/libphutil.git
```
Edit `/etc/profile` and add the following line: `PATH="$PATH:/opt/:/opt/arcanist/bin/"` before `export PATH`

```source /etc/profile```

#### Configure
* Visit https://phabricator.wikimedia.org/conduit/login/ to get the API Token and paste it after running the command below:
`arc --conduit-uri=https://phabricator.wikimedia.org install-certificate`
* Copy the config file somewhere where arcanist can find it when run by any user: `sudo cp ~/.arcrc /etc/arcconfig`
* Make it readable: `sudo chmod a+rx /etc/arcconfig`
* Edit `/etc/arcconfig` and add the following key value pair: `"phabricator.uri" : "https://phabricator.wikimedia.org"`


### Run
Enter the browser test directory.
Check out a commit you want to run your browser tests again.
Run:
    ./barrybot.py --project 'mediawiki/extensions/Gather' --core '/Users/jrobson/git/core/' --test /Users/jrobson/git/core/extensions/Gather/ --tag wip --dependencies /Users/jrobson/git/core/extensions/MobileFrontend/

Barry will let you know if he likes it.
