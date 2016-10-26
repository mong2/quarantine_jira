#Quarantine script

Version: *2.0*

Author: *Apurv Singh* - *apurva@cloudpassage.com*

Updates (v2): *Ash Wilson* - *awilson@cloudpassage.com*

##Purpose

This containerized application monitors the /v1/events endpoint in the Halo API,
looking for specific events.  If a targeted event is matched, the tool will
move the workload into the configured quarantine group.

##How it works
Targeted events are listed, one per line, in `/conf/target-events`.  Feel free
to alter the file and rebuild the container, or mount in the config file from a
persistent volume.

When the end of the events stream is reached, this tool continue to query
until more events arrive.  If you do not set the `HALO_EVENTS_START`
environment variable, the tool will start at the beginning of the current day.

The quarantine group is defined with the `$QUARANTINE_GROUP_NAME` environment
variable.  If you don't define this environment variable, it is assumed to be
"Quarantine". You should configure the group in your Halo account before you run
this tool.  We recommend applying a firewall policy to the group that restricts
all outbound traffic, and only allows inbound traffic from Ghostports users.

##Running the tool
Clone the code and build the container:

        git clone https://github.com/cloudpassage/quarantine
        cd quarantine
        docker build -t cloudpassage_quarantine .

Set these environment variables:

| Variable            | Purpose                                              |
|---------------------|------------------------------------------------------|
| HALO_API_KEY        | Halo API key ID (administrative privileges required) |
| HALO_API_SECRET_KEY | Halo API key secret                                  |
| HALO_QUARANTINE_GRP | Halo quarantine group name                           |


Optionally, define these as well:

| Variable            | Purpose                                   |
|---------------------|-------------------------------------------|
| HALO_EVENTS_START   | ISO8601 timestamp for starting event      |

Run the container:

        docker run -d \
        -e HALO_API_KEY=$HALO_API_KEY \
        -e HALO_API_SECRET_KEY=$HALO_API_SECRET_KEY \
        -e HALO_QUARANTINE_GROUP=$HALO_QUARANTINE_GROUP \
        cloudpassage_quarantine

Optionally, you can add `-v PATH_TO/target-events:/conf/target-events`,
replacing `PATH_TO` with the path to the directory enclosing your customized
`target-events` file.


<!---
#CPTAGS:community-supported automation
#TBICON:images/python_icon.png
-->
