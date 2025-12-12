
CREATE TABLE shared_lists (
  user_id int NOT NULL,
  list_id int NOT NULL
);

ALTER TABLE shared_lists
  ADD PRIMARY KEY (user_id, list_id),
  ADD KEY list_id (list_id);