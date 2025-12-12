
CREATE TABLE activity_log (
  id int PRIMARY KEY NOT NULL,
  user_id int KEY NOT NULL,
  action varchar(200) NOT NULL,
  target_list_id int KEY DEFAULT NULL,
  timestamp datetime DEFAULT NULL
);