CREATE DATABASE mydb;

create table user {
    id int not null auto_increment primary key,
    name varchar(255) not null,
    email varchar(255) unique not null,
    password varchar(255) not null,
    role varchar(255) not null,
}

CREATE TABLE score{
    test1 int,
    test2 int,
    test3 int,
    test4 int,
    test5 int,
    test6 int,
    test7 int,
    user_id int ,
    FOREIGN KEY (user_id) REFERENCES users (id) 
}


