GenThemAll
==========

This is my first open source software project, and it's not complete yet.

Script for generate example::

  #!/usr/bin/env sh

  ### install genthemall
  pip install genthemall

  # generate project config file
  genthemall project myProject ii2d.com

  ### SysUser
  # add a module name sysUser and add field id type int.
  genthemall field sysUser id type=int

  # add field username type string, max length 40, min length 6.
  genthemall field sysUser username type=string max=40 min=6

  # add field password type string, max length 40, min length 8.
  genthemall field sysUser password type=string max=40 min=8

  # add field email type string.
  genthemall field sysUser email type=string

  # add field address type string
  genthemall field sysUser address type=string

  # add field sex type int
  genthemall field sysUser sex type=int

  ### SysRole
  # add a module name sysRole and add field id type int.
  genthemall field sysRole id type=int

  # add field roleName type string.
  genthemall field sysRole roleName type=string



  ### Generate create database sql file
  genthemall generate oracle create_database && cat out/SysUser.sql 

  ### And then see the output. :)

  ### Generate java model file
  genthemall generate java java_base_model && cat out/src/main/java/com/ii2d/model/SysUser.java 

  ### And then see the output. :)
