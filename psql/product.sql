CREATE TABLE products (
  id varchar(25),
  brandId varchar(25),
  brandName varchar(25),
  title varchar(256),
  description text,
  terms text, 
  imageUrl text,
  oldPrice int,
  newPrice int,
  type int,
  currency varchar(6),
  redirectWebUrl text
);
GRANT ALL PRIVILEGES ON products TO sobazar;
