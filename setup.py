"""
The setup script for scripty bot, running this
gets the requirements and installs them as needed.

Note: This assumes you have python3 installed
"""
from setuptools import setup

print('Setting up scripty bot ...')

setup(name='discord_scripty_bot',
      version='1.0.0',
      description='',
      author='Noah Dueck',
      author_email='duecknoah@gmail.com',
      install_requires=[
          'discord.py', 'aioconsole'
      ],
      zip_safe=False)

print('**************************************\n'
      'Setup done!\n'
      'To start the script, run the appropriate script:\n'
      'WINDOWS:\tstart.bat\n'
      'LINUX or MAC:\tstart.sh\n'
      '**************************************\n'
      )