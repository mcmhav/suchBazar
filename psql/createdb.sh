#/bin/sh
if [ "$#" -ne 3 ]; then
  echo -e "Usage:\n$ createdb.sh data.tab db.sql"
  exit 0
fi

# Exit on error
set -e

# Fixing the input
cat $1 | awk '{if ($4 ~ /prod/) { print $0; }}' > /tmp/tmp.tab
sed -e 's/"{/{/g;s/\}"/\}/g;s/\\"/"/g' /tmp/tmp.tab > /tmp/valid.tab

# Postgresql import
if psql -l | grep -q sobazar; then
  dropdb sobazar
fi
createdb sobazar
psql -f $2 -d sobazar
psql -d sobazar -c "COPY sobazar FROM '/tmp/valid.tab' DELIMITER E'\t';"

# Clean-up
rm /tmp/valid.tab /tmp/tmp.tab

# Write message to user
echo -e "Successfully imported data. Open the database with:\n$ psql -d sobazar"
