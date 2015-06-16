bundle install > tmp
msg=$(bundle exec cucumber features/mainmenu.feature --tags @wip)
# Run GerritCommandLine script with score and message
if [ $? -ne 0 ]; then
  echo "Browserbot sad :-("
  gerrit.py --review -1 --message ""$msg""
else
  echo "Browserbot happy!"
  gerrit.py --review +1 --message "$msg"
fi
