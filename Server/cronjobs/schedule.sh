# Determining path of script
MY_PATH=$(dirname "$0")            # relative
MY_PATH=$(cd "$MY_PATH" && pwd)    # absolutized and normalized
if [[ -z "$MY_PATH" ]] ; then
  # error; for some reason, the path is not accessible
  # to the script (e.g. permissions re-evaled after suid)
  exit 1  # fail
fi

# Saving all Cronjobs in file
crontab -l > cronjobs

# Adding cronjobs
echo "30 11 * * * python3 $MY_PATH/jobs/archiveMetrics.py" >> cronjobs

crontab cronjobs
rm cronjobs