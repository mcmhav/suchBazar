cd ../generators;
python makeWALSRatingMatrix.py;
./split.sh ratings/No.csv
mv training.txt ratings/no1.train
mv validation.txt ratings/no1.validate
cp ratings/no1.validate ratings/no1.predict
