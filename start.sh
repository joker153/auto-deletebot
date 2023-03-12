if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone  
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /
fi
cd /Evamari12
pip freeze > requirements.txt
echo "Starting Bot...."
python3 bot.py
