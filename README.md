# Quarantine-Jira

Version: *1.0*

Fork from: https://github.com/cloudpassage/quarantine.git

## Purpose
This containerized application monitors the /v1/events endpoint in the Halo API,
looking for specific events.  If a targeted event is matched, the tool will
move the workload into the configured quarantine group or create a JIRA ticket with
event information.

## How it works
Targeted events are listed, one per line, in `/conf/target-events`.  Feel free
to alter the file and rebuild the container, or mount in the config file from a
persistent volume.  Event types produced by Halo can be found here:
https://api-doc.cloudpassage.com/help#event-types

When the end of the events stream is reached, this tool continue to query
until more events arrive.  If you do not set the `HALO_EVENTS_START`
environment variable, the tool will start at the beginning of the current day.

## Prerequisites

* You'll need an account with CloudPassage Halo.
* Make sure that your policies are configured to create events on failure.
* You'll need an administrative (read + write) API key for your Halo account.
* You'll need to have Docker installed.
* You'll need a JIRA account
* Create a quarantine group in your Halo account, with the appropriately
restrictive firewall rules.


## Using the tool
Clone the code and build the container:

        git clone https://github.com/mong2/quarantine_jira
        cd quarantine_jira
        docker build -t cloudpassage_quarantine .

Configure your JIRA information in `configs/config.yml`

Set these environment variables:

| Variable            | Purpose                                              |
|---------------------|------------------------------------------------------|
| HALO_API_KEY        | Halo API key ID (administrative privileges required) |
| HALO_API_SECRET_KEY | Halo API key secret                                  |


Optionally, define these as well:

| Variable            | Purpose                                   |
|---------------------|-------------------------------------------|
| HALO_EVENTS_START   | ISO8601 timestamp for starting event      |


To run the container interactively (foreground):

        docker run -it \
        -e HALO_API_KEY=$HALO_API_KEY \
        -e HALO_API_SECRET_KEY=$HALO_API_SECRET_KEY \
        cloudpassage_quarantine


If you want to run quarantine in the background, you can start it like this:

        docker run -d \
        -e HALO_API_KEY=$HALO_API_KEY \
        -e HALO_API_SECRET_KEY=$HALO_API_SECRET_KEY \
        cloudpassage_quarantine


Use `docker ps` to make sure it's running.  The container logs will be updated
with the last event's timestamp after every batch runs, so running
`docker logs -f CONTAINER_NAME` will allow you to watch the quarantine tool's
progress while consuming your events stream.


Optionally, you can add `-v PATH_TO/target-events:/conf/target-events`,
replacing `PATH_TO` with the path to the directory enclosing your customized
`target-events` file.

## Setup Config.yml
| Variable            | Purpose                                                  |
|---------------------|-----------------------------------------    |
| url                 | Jira Cloud url. i.e. https://cloudpassagecs.atlassian.net|
| user                | Jira Username                                                          |
| password            | Jira Password                                                     |
| project_key         | Jira Project Key                                                      |
| issue_name          | Jira Issue Name. i.e. Bug, Improvement                                                     |
| auto_resolved       | Boolean. Auto-resolved ticket based on CloudPassage Scan result                                                     |
| supress_threshold   | Integer. Surppress ticket creation if CVSS score is lower than supress_threshold                                                  |
| sva_severity        | Key-value pair (Priority: CVSS score). Associate CVSS score with your Jira priorities. i.e. Hightest: 9, High: 7, Medium: 4, Low: 2                                                      |
| event_severity      | Key-value pair (Critical: Priority). Associate event criticality with your Jira priorities. i.e. critical: High, non_critical: Low                                                     |
| resolution_workflow | This section is highly customized. Auto-resolved will read this setting and perform based on your project workflow. You will be able to set comment and Jira transition id.                                                     |


<!---
#CPTAGS:community-supported automation
#TBICON:images/python_icon.png
-->
