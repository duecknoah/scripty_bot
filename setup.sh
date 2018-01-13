echo "Setting up scripty-bot ..."

cd src
sudo apt-get install python3
sudo apt-get install python3-pip
sudo -H python3 -m pip install -U setuptools
sudo -H python3 -m pip install -U discord.py
sudo -H python3 -m pip install -U aioconsole

echo "*************************************************************
Setup complete, you can now run the bot by running start.sh
*************************************************************"
