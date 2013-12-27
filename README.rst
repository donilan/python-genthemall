GenThemAll
==========

GenThemAll is a Python command-line tool for generate code or other.

Let's try to generate some code for java.

Install
-------
install from pypi::
   pip install genthemall

install from git::
  ## checkout project source
  git clone https://github.com/donilan/python-genthemall genthemall
  ## entry project folder
  cd genthemall
  ## then install from source
  python setup.py install

Create J2EE project
-------------------
Here we need a java tool name Maven. If you don't have it, Then install first::
  ## yum install
  sudo yum install maven -y
  ## apt-get install
  sudo apt-get install maven -y

Now We are going to create a J2EE project with maven::
  mvn archetype:generate -DgroupId=com.ii2d \
  -DartifactId=mywebapp -DarchetypeArtifactId=maven-archetype-webapp

And then we entry project foler and create genthemall project::
  cd mywebapp
  genthemall project MyWebapp ii2d.com 'My genthemall webapp'

We add some modules and module's fields with my project::
  ## module user
  genthemall field user id type=int
  genthemall field user username type=string min=6 max=40
  genthemall field user password type=string min=6 max=40
  genthemall field user firstName type=string required=false
  genthemall field user lastName type=string required=false
  genthemall field user address type=string max=256 required=false

  ## module article
  genthemall field article id type=int
  genthemall field article title type=string
  genthemall field article content type=text
  genthemall field article created type=date
  genthemall field article userId type=int
  
Ok, We can list template by genthemall template command::
  genthenall template list

After we run template command, genthemall will copy default templates to 
current folder name .genthemall folder. And then We can edit some templates, if
you want. Before edit must be set a envionment variable name EDITOR, like
this::
  export EDITOR='emacs -nw'

  ## edit template command
  genthemall template edit java.model

  ## or you can edit with anther way
  emacs -nw .genthemall/java.model.gt



