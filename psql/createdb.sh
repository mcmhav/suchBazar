#!/bin/bash

# Exit on error
set -e

PROGNAME="$(basename $0)";
PROGDIR="$( cd "$( dirname "$0" )" && pwd )";
ROOT="$( dirname "$CWD")";

usage() {
cat <<- EOF
usage: $PROGNAME options

This program adds stuff from event log to a PostgreSQL-DB for easy analytics.

OPTIONS:
  -i event_file.tab             File containing event log
  -h                            Print help dialog (this one)

EXAMPLE:
  $0 -i sobazar_log.tab

PREREQUISITES:
  You need a postgreSQL-DB running, with valid users and so forth.
EOF
exit 1;
}

INFILE=""
SQLFILE=""
CLEAN=0

while getopts ":i:s:c" o; do
  case "${o}" in
    i)
      INFILE="${OPTARG}";
      ;;
    s)
      SQLFILE="${OPTARG}";
      ;;
    c)
      CLEAN=1
      ;;
    *)
      usage
      ;;
  esac
done

if [[ ! -f $INFILE ]]; then
  echo "Event log file not found!";
  exit 1;
fi

if [[ ! -f $SQLFILE ]]; then
  echo "SQL file not found!";
  exit 1;
fi

# Fixing the input
if [ $CLEAN -eq 1 ]; then
  cat $INFILE | awk '{if ($4 ~ /prod/) { print $0; }}' > /tmp/tmp.tab
  sed -e 's/"{/{/g;s/\}"/\}/g;s/\\"/"/g' /tmp/tmp.tab > /tmp/valid.tab
fi

# Postgresql import
if psql -l | grep -q sobazar; then
  echo "Dropping existing database.."
  dropdb sobazar
fi

echo "Creating database..."
createdb sobazar

echo "Importing from SQL-file..."
psql -f $SQLFILE -d sobazar

echo "Giving permissions..."
psql -d sobazar -c "COPY sobazar FROM '/tmp/valid.tab' DELIMITER E'\t';"
psql -d sobazar -c "DROP ROLE IF EXISTS sobazar; CREATE ROLE sobazar WITH LOGIN;"
psql -d sobazar -c "GRANT ALL PRIVILEGES ON sobazar TO sobazar;"

# Clean-up
echo "Cleaning up..."
rm /tmp/valid.tab /tmp/tmp.tab

# Write message to user
echo -e "Successfully imported data. Open the database with:\n$ psql -d sobazar"
