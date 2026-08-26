create table orders (
  id varchar(64) primary key,
  customer_id varchar(64) not null,
  status varchar(32) not null,
  total_amount decimal(12,2) not null
);
