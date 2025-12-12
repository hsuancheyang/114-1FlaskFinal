CREATE TABLE task (
  id int(11) PRIMARY KEY NOT NULL,
  list_id int(11) KEY NOT NULL,
  content varchar(200) NOT NULL,
  due_date datetime DEFAULT NULL,
  is_completed tinyint(1) DEFAULT NULL,
  created_at datetime DEFAULT NULL
);