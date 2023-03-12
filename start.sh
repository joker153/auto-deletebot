if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone  https://github.com/joker153/auto-deletebot.git
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /auto-deletebot
fi
cd /auto-deletebot
pip freeze > requirements.txt
echo "Starting Bot...."
python3 bot.py
