#!/bin/bash

# Must be run as root or with sudo privileges



export VER="24.11.1"

export MUNGE_VER="0.5.16"

export HWLOC_VER="2.11.2"



user_home_dir="/root"



SLURM_CONF="/etc/slurm/slurm.conf"

CGROUP_CONF="/etc/slurm/cgroup.conf"

SLURMDBD_CONF="/etc/slurm/slurmdbd.conf"



# --- OS DETECTION ---

if [ -f /etc/os-release ]; then

. /etc/os-release

OS_FAMILY=${ID_LIKE:-$ID}

OS_ID=$ID

else

echo "Cannot detect Linux distribution. Exiting."

exit 1

fi





update_and_install_packages() {



echo "--> Installing dependencies for OS Family: $OS_FAMILY"



if [[ "$OS_FAMILY" == *"debian"* ]] || [[ "$OS_ID" == "ubuntu" ]]; then



sudo apt-get update -y

sudo apt-get install -y build-essential libssl-dev \

libglib2.0-dev libgtk2.0-dev libgtk2.0-doc devhelp libdbus-1-dev \

mysql-server libmysqlclient-dev mysql-common mysql-server-core-* mysql-client-core-* \

wget tar bzip2 xz-utils pkg-config



sudo systemctl enable --now mysql



elif [[ "$OS_FAMILY" == *"rhel"* ]] || [[ "$OS_FAMILY" == *"fedora"* ]] || [[ "$OS_ID" == *"rocky"* ]] || [[ "$OS_ID" == *"almalinux"* ]]; then



if [[ "$OS_ID" != "fedora" ]]; then

sudo dnf install -y epel-release

fi



sudo dnf groupinstall -y "Development Tools"

sudo dnf install -y openssl-devel glib2-devel gtk2-devel dbus-devel \

mariadb-server mariadb-devel wget tar bzip2 xz pkgconf perl



sudo systemctl enable --now mariadb



else

echo "Unsupported distribution for automatic dependency installation."

exit 1

fi

}





download_files() {



echo "--> Checking source files"



# remove old wget logs if they exist

rm -f wget-log*



if [ ! -f "$user_home_dir/slurm-$VER.tar.bz2" ]; then

echo "--> Downloading Slurm $VER"

sudo wget -q -nc -P $user_home_dir https://download.schedmd.com/slurm/slurm-$VER.tar.bz2

else

echo "--> Slurm source already downloaded"

fi



if [ ! -f "$user_home_dir/munge-$MUNGE_VER.tar.xz" ]; then

echo "--> Downloading Munge $MUNGE_VER"

sudo wget -q -nc -P $user_home_dir https://github.com/dun/munge/releases/download/munge-$MUNGE_VER/munge-$MUNGE_VER.tar.xz

else

echo "--> Munge source already downloaded"

fi



if [ ! -f "$user_home_dir/hwloc-$HWLOC_VER.tar.bz2" ]; then

echo "--> Downloading HWLOC $HWLOC_VER"

sudo wget -q -nc -P $user_home_dir https://download.open-mpi.org/release/hwloc/v2.11/hwloc-$HWLOC_VER.tar.bz2

else

echo "--> HWLOC source already downloaded"

fi

}





create_munge_user() {

id -u munge &>/dev/null || sudo useradd -m -d /etc/munge munge

}





build_munge() {



echo "--> Building Munge"



if [ ! -d "$user_home_dir/munge-$MUNGE_VER" ]; then

tar -xvf $user_home_dir/munge-$MUNGE_VER.tar.xz -C $user_home_dir

fi



cd $user_home_dir/munge-$MUNGE_VER



sudo ./configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var --libdir=/usr/lib

sudo make -j $(nproc)

sudo make install

}





create_munge_key() {



if [ -f /usr/sbin/mungekey ]; then

sudo /usr/sbin/mungekey

else

sudo /usr/local/sbin/mungekey

fi

}





set_munge_permissions() {



echo "--> Setting Munge permissions"



sudo chown -R munge: /etc/munge/

sudo mkdir -p /var/log/munge /var/run/munge



sudo chmod 0700 /etc/munge/ /var/log/munge

sudo chmod 0755 /var/run/munge



sudo chown -R munge:munge /var/log/munge /var/run/munge



sudo mkdir -p /run/munge

sudo chown munge:munge /run/munge



if [ ! -S /run/munge/munge.socket.2 ]; then

sudo ln -sf /var/run/munge/munge.socket.2 /run/munge/munge.socket.2 2>/dev/null || true

fi

}





start_munge_service() {



echo "--> Starting Munge"



if ! systemctl list-unit-files | grep -q munge.service; then



sudo bash -c 'cat > /etc/systemd/system/munge.service << EOF

[Unit]

Description=MUNGE authentication service

After=network.target



[Service]

Type=forking

ExecStart=/usr/sbin/munged

PIDFile=/var/run/munge/munged.pid

User=munge

Group=munge

Restart=on-abort



[Install]

WantedBy=multi-user.target

EOF'



sudo systemctl daemon-reload

fi



sudo systemctl enable --now munge

sleep 2

}





create_slurm_user() {

id -u slurm &>/dev/null || sudo useradd -m -d /etc/slurm slurm

}





build_slurm() {



echo "--> Building HWLOC and Slurm"



if [ ! -d "$user_home_dir/hwloc-$HWLOC_VER" ]; then

tar -xvf $user_home_dir/hwloc-$HWLOC_VER.tar.bz2 -C $user_home_dir

fi



cd $user_home_dir/hwloc-$HWLOC_VER



sudo ./configure

sudo make -j $(nproc)

sudo make install





sudo mkdir -p /etc/slurm

sudo chown slurm:slurm /etc/slurm





if [ ! -d "$user_home_dir/slurm-$VER" ]; then

tar -xvf $user_home_dir/slurm-$VER.tar.bz2 -C $user_home_dir

fi



cd $user_home_dir/slurm-$VER



sudo ./configure --sysconfdir=/etc/slurm --with-munge=/usr --with-hwloc=/usr/local/

sudo make -j $(nproc)

sudo make install

}





create_slurm_conf() {



echo "--> Configuring slurm.conf"



cat > $user_home_dir/slurm.conf << EOF

ClusterName=HPC

SlurmctldHost=$HOSTNAME

MpiDefault=none

ProctrackType=proctrack/cgroup

SlurmctldPidFile=/var/run/slurmctld.pid

SlurmctldPort=6817

SlurmdPidFile=/var/run/slurmd.pid

SlurmdPort=6818

SlurmdSpoolDir=/var/spool/slurmd

SlurmUser=slurm

StateSaveLocation=/var/spool/slurmctld

SwitchType=switch/none

TaskPlugin=task/affinity

AuthType=auth/munge

SlurmctldTimeout=120

SlurmdTimeout=300

SchedulerType=sched/backfill

SelectType=select/cons_tres

AccountingStorageType=accounting_storage/slurmdbd

JobCompType=jobcomp/none

JobAcctGatherFrequency=30

JobAcctGatherType=jobacct_gather/none

SlurmctldDebug=info

SlurmctldLogFile=/var/log/slurm/slurmctld.log

SlurmdDebug=info

SlurmdLogFile=/var/log/slurm/slurmd.log

EOF

}





add_additional_configurations() {



slurmd -C | head -n1 >> $user_home_dir/slurm.conf



LINE="PartitionName=caribou_node Nodes=ALL Default=YES MaxTime=INFINITE State=UP"

echo "$LINE" >> $user_home_dir/slurm.conf



sudo cp $user_home_dir/slurm.conf $SLURM_CONF

}





create_cgroup_conf() {



cat > $user_home_dir/cgroup.conf << EOF

ConstrainCores=yes

ConstrainDevices=yes

ConstrainRAMSpace=yes

ConstrainSwapSpace=yes

EOF



sudo cp $user_home_dir/cgroup.conf $CGROUP_CONF

}





configure_slurm_database() {



echo "--> Configuring Slurm Database"



sudo mysql -u root -e "CREATE USER IF NOT EXISTS 'slurm'@'localhost';"

sudo mysql -u root -e "CREATE DATABASE IF NOT EXISTS slurm_acct_db;"

sudo mysql -u root -e "GRANT ALL PRIVILEGES ON slurm_acct_db.* TO 'slurm'@'localhost';"



cat > $user_home_dir/slurmdbd.conf << EOF

AuthType=auth/munge

DbdHost=localhost

SlurmUser=slurm

DebugLevel=verbose

LogFile=/var/log/slurm/slurmdbd.log

PidFile=/var/run/slurmdbd.pid

StorageType=accounting_storage/mysql

StorageLoc=slurm_acct_db

EOF



sudo cp $user_home_dir/slurmdbd.conf $SLURMDBD_CONF

}





set_slurm_permissions() {



sudo mkdir -p /var/log/slurm /var/spool/slurmctld /var/spool/slurmd

sudo touch /var/log/slurm/slurmctld.log /var/log/slurm/slurmdbd.log



sudo chown -R slurm:slurm /etc/slurm

sudo chown -R slurm:slurm /var/log/slurm

sudo chown -R slurm:slurm /var/spool/slurmctld /var/spool/slurmd



sudo chmod 600 $SLURMDBD_CONF

}





start_slurm_services() {



echo "--> Starting Slurm Services"



sudo cp -avr $user_home_dir/slurm-$VER/etc/*.service /etc/systemd/system/



sudo systemctl daemon-reload

sudo systemctl enable slurmdbd slurmctld slurmd



sudo systemctl start slurmdbd



while ! systemctl is-active --quiet slurmdbd; do sleep 1; done



echo "--> Slurmdbd is active. Waiting 5s for DB..."

sleep 5





sudo systemctl start slurmctld



echo "--> Waiting for slurmctld to respond..."



until scontrol ping | grep -q "UP"; do

sleep 2

echo "--> Controller still initializing..."

done





sudo systemctl start slurmd



while ! systemctl is-active --quiet slurmd; do sleep 1; done





echo "--> Cluster is ready!"



sleep 2

sinfo



sudo scontrol update node=$HOSTNAME state=idle

}





main() {



update_and_install_packages

download_files

create_munge_user

build_munge

create_munge_key

set_munge_permissions

start_munge_service

create_slurm_user

build_slurm

create_slurm_conf

add_additional_configurations

create_cgroup_conf

configure_slurm_database

set_slurm_permissions

start_slurm_services

}



main
