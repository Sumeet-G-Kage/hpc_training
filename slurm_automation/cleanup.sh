#!/bin/bash
set -e

echo "Stopping services..."
systemctl stop slurmd 2>/dev/null || true
systemctl stop slurmctld 2>/dev/null || true
systemctl stop slurmdbd 2>/dev/null || true
systemctl stop munge 2>/dev/null || true

echo "Disabling services..."
systemctl disable slurmd slurmctld slurmdbd munge 2>/dev/null || true

echo "Removing systemd service files..."
rm -f /usr/local/lib/systemd/system/slurm*
rm -f /usr/local/lib/systemd/system/munge*
systemctl daemon-reload

echo "Removing binaries..."
rm -rf /usr/local/sbin/slurm*
rm -rf /usr/local/bin/srun
rm -rf /usr/local/bin/sinfo
rm -rf /usr/local/bin/sacct*
rm -rf /usr/local/bin/squeue*
rm -rf /usr/local/lib/slurm*
rm -rf /usr/local/sbin/munge*
rm -rf /usr/local/bin/munge*
rm -rf /usr/local/lib/libmunge*

echo "Removing configuration..."
rm -rf /etc/slurm
rm -rf /etc/munge

echo "Removing runtime & spool..."
rm -rf /var/spool/slurm*
rm -rf /var/log/slurm*
rm -rf /var/lib/munge
rm -rf /var/log/munge
rm -rf /run/munge

echo "Removing users..."
userdel -r slurm 2>/dev/null || true
userdel -r munge 2>/dev/null || true

echo "Dropping database..."
mysql -u root -e "DROP DATABASE IF EXISTS slurm_acct_db;" 2>/dev/null || true
mysql -u root -e "DROP USER IF EXISTS 'slurm'@'localhost';" 2>/dev/null || true

echo "Cleaning source directory..."
rm -rf /opt/src

echo "Cleanup completed successfully."
