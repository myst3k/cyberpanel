#!/bin/sh

OUTPUT=$(cat /etc/*release)
if echo "$OUTPUT" | grep -q "CentOS Linux 7"; then
  printf "Checking and installing curl and wget\n"
  yum install curl wget -y 1>/dev/null
  yum update curl wget ca-certificates -y 1>/dev/null
  SERVER_OS="CentOS"
elif echo "$OUTPUT" | grep -q "CentOS Linux 8"; then
  printf "\nDetecting Centos 8...\n"
  SERVER_OS="CentOS8"
  yum install curl wget -y 1>/dev/null
  yum update curl wget ca-certificates -y 1>/dev/null
elif echo "$OUTPUT" | grep -q "CloudLinux 7"; then
  printf "Checking and installing curl and wget\n"
  yum install curl wget -y 1>/dev/null
  yum update curl wget ca-certificates -y 1>/dev/null
  SERVER_OS="CloudLinux"
elif echo "$OUTPUT" | grep -q "Ubuntu 18.04"; then
  apt install -y -qq wget curl
  SERVER_OS="Ubuntu"
elif echo "$OUTPUT" | grep -q "Ubuntu 20.04"; then
  apt install -y -qq wget curl
  SERVER_OS="Ubuntu"
else
  printf "\nUnable to detect your OS...\n"
  printf "\nCyberPanel is supported on Ubuntu 18.04, CentOS 7.x and CloudLinux 7.x...\n"
  exit 1
fi

rm -f cyberpanel.sh
rm -f install.tar.gz
curl --silent -o cyberpanel.sh "https://cyberpanel.sh/?dl&$SERVER_OS" 2>/dev/null
chmod +x cyberpanel.sh
./cyberpanel.sh "$@"
