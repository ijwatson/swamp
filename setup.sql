create table users(id integer unique primary key, name string);
create table measures(id integer unique primary key, userId integer, startTime time, endTime time);
create table current(userId integer, measureTime integer, status bool, startTime time);
