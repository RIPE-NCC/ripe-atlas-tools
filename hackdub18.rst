Dublin Hackathon 2018
===================


* Document how to use atlas tools in a hurry, NOC people in panic
* Make the three step pocess into a 1 step - run now process
* awlx has a use-case with country select probes in region in as

API key, beginning:
11febf03-5190-47e5-882a-.........


Get started
===========

Install Python Pip, then:

git clone https://github.com/kramse/ripe-atlas-tools/
cd ripe-atlas-tools

pip install pipenv
pipenv --python 3
pipenv install -e .


When this is done, you can do
pipenv shell

That activates the environment, and is the command to use when doing work on this project.

Original Project idea and description
===================================

 Project_Name_1

realtime ripe-atlas traceroute commandline: hack together a ripe-atlas commandline that is as smooth to use as possible.
Currently in the commandline you need 3 steps, and in an 'the customer is screaming on the phone'-situation where traceroutes can narrow down a problem, you probably want
to minimise the amount of thinking you need to do to maximise the result of measuring.
 - a single command to do all steps (select right probes for your use case, do the measurement, print relevant results)
 - make it as real-time as possible
   - oversubscribe probes slightly for one-offs
   - tweak measurement parameters for fast results (1 probing per hop, reduce timeout vals?)
   - commandline results that are 'enriched' (show ASN, location, weirdnesses, nice short asn-names)
   - steal good parts from https://github.com/emileaben/eyeballtrace ? / use/extend bleau? https://labs.ripe.net/Members/stephane_bortzmeyer/creating-ripe-atlas-one-off-measurements-with-blaeu


Already existing stuff
======================
- https://labs.ripe.net/Members/annika_wickert/using-ripe-atlas-to-monitor-game-service-connectivity
- https://github.com/RIPE-Atlas-Community/ripe-atlas-community-contrib
- https://github.com/emileaben/eyeballtrace
- https://framagit.org/bortzmeyer/blaeu
