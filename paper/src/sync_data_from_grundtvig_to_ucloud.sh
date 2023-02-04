# sync data to ucloud using rsync
# this is assumed to be run from  Grundtvig
# It is also assume that you have an rsync server running on ucloud using the rsync app
# with the following mounted folder:
# /conspiracies  (project: pandemic-info-resp)

# --- Environment variables ------------------------------
ucloud_user="ucloud"
ucloud_rsync_ip="130.225.164.149"
ucloud_data_folder="/work/conspiracies/data"
grundtvig_data_path="/data/conspiracies"


# --- Sync to UCloud -------------------------------------
# rsync -avPu {from} {to}
# -a archive mode
# -v verbose
# -P progress
# -u update (only copy files that are newer than the destination)
# -r recursive
rsync -avPur ${grundtvig_data_path}/* ${ucloud_user}@${ucloud_rsync_ip}:${ucloud_data_folder}
# this moves it to a conspiracies folder on ucloud
# so you might need to move it to the right place

# you can also to it the other way around using:
# rsync -avPur ${ucloud_user}@${ucloud_rsync_ip}:${ucloud_data_folder}/* ${grundtvig_data_path} 


