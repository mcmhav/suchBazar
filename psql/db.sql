CREATE TABLE sobazar (
service_id varchar(25), -- SOBAZAR
event_id varchar(64),
event_data json,
server_time_stamp timestamp,
client_time_stamp varchar(64),
user_agent varchar(256),
storefront_position varchar(64),
tag_id varchar(64),
storefront_name varchar(64),
country_id varchar(64),
price varchar(64),
product_type varchar(64),
product_id varchar(64),
origin_ui varchar(64),
tag_position varchar(64),
gender_target varchar(64),
user_id varchar(64),
tag_name varchar(64),
login_type varchar(64),
server_environment varchar(64),
currency varchar(64),
age_target varchar(64),
time_stamp varchar(64),
storefront_id varchar(64),
platform varchar(64),
country_name varchar(64),
event_location varchar(64),
retailer_brand varchar(64),
app_version varchar(64),
product_name varchar(256),
transaction_id varchar(64),
event_json json,
hr smallint, -- 12
ts varchar(64), --1377864663008
epoch_day smallint, -- 15947
epoch_week smallint, -- 2278
yr smallint, -- 2013
mo smallint, -- 09
dy smallint -- 01
);
