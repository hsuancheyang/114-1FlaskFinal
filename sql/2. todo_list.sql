CREATE TABLE todo_list (
  id int PRIMARY KEY NOT NULL,
  title varchar(100) NOT NULL,
  owner_id int KEY NOT NULL,
  created_at datetime DEFAULT NULL
);
