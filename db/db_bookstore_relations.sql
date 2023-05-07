use db_bookstore;

ALTER TABLE print
ADD FOREIGN KEY (tran_id) REFERENCES transactions(id);

ALTER TABLE takeaway
ADD FOREIGN KEY (tran_id) REFERENCES transactions(id);

ALTER TABLE indoor
ADD FOREIGN KEY (tran_id) REFERENCES transactions(id);

ALTER TABLE indoor_detail
ADD FOREIGN KEY (tran_id) REFERENCES transactions(id);

ALTER TABLE indoor
ADD FOREIGN KEY (item_id) REFERENCES items(id);

ALTER TABLE takeaway
ADD FOREIGN KEY (item_id) REFERENCES items(id);
