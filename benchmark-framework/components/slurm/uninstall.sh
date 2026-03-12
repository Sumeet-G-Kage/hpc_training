#!/bin/bash

export VER="24.11.1"
export MUNGE_VER="0.5.16"
export HWLOC_VER="2.11.2"
user_home_dir="/root"

echo "--> Handling MySQL/MariaDB to drop Slurm database..."
# Ensure the service is running so we can drop the DB
if systemctl list-unit-files | grep -qE "mysql|mariadb"; then
    sudo systemctl start mysql 2>/dev/null || sudo systemctl start mariadb 2>/dev/null
    sleep 2
    sudo mysql -u root -e "DROP DATABASE IF EXISTS slurm_acct_db;" 2>/dev/null
    sudo mysql -u root -e "DROP USER IF EXISTS 'slurm'@'localhost';" 2>/dev/null
    echo "--> Slurm database and user dropped."
    # Optional: stop it again if you don't need it
    sudo systemctl stop mysql 2>/dev/null || sudo systemctl stop mariadb 2>/dev/null
fi

echo "--> Stopping and disabling all related services..."
sudo systemctl stop slurmd slurmctld slurmdbd munge 2>/dev/null
sudo systemctl disable slurmd slurmctld slurmdbd munge 2>/dev/null

echo "--> Removing systemd service files (including /usr/lib ghosts)..."
sudo rm -f /etc/systemd/system/slurm*.service
sudo rm -f /etc/systemd/system/munge.service
sudo rm -f /usr/lib/systemd/system/munge.service
sudo rm -f /lib/systemd/system/munge.service
sudo systemctl daemon-reload

echo "--> Removing Slurm and Munge binaries..."
sudo rm -rf /usr/local/bin/s* /usr/local/sbin/s*
sudo rm -rf /usr/local/bin/munge* /usr/local/sbin/munge*
sudo rm -rf /usr/local/lib/libslurm* /usr/local/lib/slurm/
sudo rm -rf /usr/local/include/slurm/
sudo rm -rf /usr/sbin/munged /usr/sbin/mungekey /usr/bin/munge
sudo rm -rf /usr/lib/munge/

echo "--> Cleaning up configuration, logs, and spool directories..."
sudo rm -rf /etc/slurm /etc/munge
sudo rm -rf /var/log/slurm /var/log/munge
sudo rm -rf /var/spool/slurmctld /var/spool/slurmd
sudo rm -rf /var/run/munge /run/munge
sudo rm -f /var/run/slurm*.pid

echo "--> Removing users and groups..."
sudo userdel -r slurm 2>/dev/null
sudo userdel -r munge 2>/dev/null
sudo groupdel slurm 2>/dev/null
sudo groupdel munge 2>/dev/null

echo "--> Removing source files and build artifacts..."
sudo rm -rf $user_home_dir/slurm-$VER*
sudo rm -rf $user_home_dir/munge-$MUNGE_VER*
sudo rm -rf $user_home_dir/hwloc-$HWLOC_VER*
sudo rm -f $user_home_dir/slurm.conf $user_home_dir/cgroup.conf $user_home_dir/slurmdbd.conf

echo "--> Finalizing cleanup..."
sudo systemctl reset-failed
echo "--> Cleanup complete. Your system should now be Slurm-free."
