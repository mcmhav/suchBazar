tp
==

Data handlers atm

## Useful command line clean-ups

### Remove all non-prod lines

`$ cat sobazar_events_reff_external.tab | awk '{if ($4 ~ /prod/) { print $0; }}' > outputfile.tab`

### Create valid JSON

`sed -e 's/"{/{/g;s/\}"/\}/g;s/\\"/"/g' sobazar_events_reff_external.tab > valid.tab`
