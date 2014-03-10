#!/bin/bash
if [ $# -ne 1 ]; then
  echo "Need to specify file with product ids.";
  exit 2;
fi

i=0;
tot=`wc -l product_ids.txt | cut -d ' ' -f 5`
while read p; do
  curl -u goodiez:goodiez https://goodiez-staging.appspot.com/api/goodiez/offer/v10/$p -w '\n' -s >>  products.txt;
  let i++;
  perc=`echo "scale=2;($i*100/$tot)"|bc -l`;
  echo -ne "\r$i/$tot $perc%";
done < $1;
echo ""
