tp
==

Data handlers atm

## Useful command line clean-ups

### Remove all non-prod lines

    $ cat sobazar_events_reff_external.tab | awk '{if ($20 ~ /prod/) { print $0; }}' > outputfile.tab

### Create valid JSON

    sed -e 's/"{/{/g;s/\}"/\}/g;s/\\"/"/g' sobazar_events_reff_external.tab > valid.tab

### Rename new events to old format

    $ sed -e 's/content:interact:product_wanted/product_wanted/g;s/content:interact:product_clicked/product_detail_clicked/g;s/purchase:buy_clicked/product_purchase_intended/g;s/content:interact:product_detail_viewed/product_detail_clicked/g' in.tab > out.tab

### All events after 1st of November

    cat sobazar_events_prod_cleaned_formatted.tab | awk -F'\t' '{ if($34 > 1383264000000) { print; }}' > sobazar_events_prod_cleaned_recent.tab
