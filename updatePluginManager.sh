#!/usr/bin/env bash

rm -rf pluginManager*
cp ~chris/pluginManager.zip .
unzip pluginManager.zip
rm -rf /usr/local/CyberCP/public/static/*
/usr/local/CyberCP/bin/python manage.py collectstatic --noinput
cp -R  /usr/local/CyberCP/static/* /usr/local/CyberCP/public/static/
systemctl restart lscpd