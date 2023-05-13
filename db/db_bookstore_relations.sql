Use db_bookstore;

ALTER TABLE instore ADD FOREIGN KEY (tran_id) REFERENCES transactions(id) ON DELETE SET NULL;
ALTER TABLE order_group ADD FOREIGN KEY (tran_id) REFERENCES transactions(id) ON DELETE SET NULL;
ALTER TABLE order_group ADD FOREIGN KEY (item_id) REFERENCES item(id) ON DELETE SET NULL;
ALTER TABLE print_stock ADD FOREIGN KEY (tran_id) REFERENCES transactions(id) ON DELETE SET NULL;
