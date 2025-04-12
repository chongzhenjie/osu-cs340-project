/*
    Group 40 Project Step 5 Portfolio Assignment: DML.sql
    Zhen Jie Chong
    Zhen Kang Chong
*/

-- display table on Service Categories page
SELECT service_category_id, name, description 
FROM ServiceCategories
ORDER BY service_category_id ASC;

-- display table on Services page
SELECT Services.service_id, 
Services.name, 
Services.description, 
ServiceCategories.name, 
MIN(RequestServices.request_service_id) AS request_service_id
FROM Services
LEFT JOIN ServiceCategories ON Services.service_category_id = ServiceCategories.service_category_id
LEFT JOIN RequestServices ON Services.service_id = RequestServices.service_id
GROUP BY Services.service_id
ORDER BY Services.service_id ASC;

-- dropdown on Services page
SELECT service_category_id, name
FROM ServiceCategories
ORDER BY service_category_id ASC;

-- display table on Customers page
SELECT customer_id, first_name, last_name, address, phone, email
FROM Customers
ORDER BY customer_id ASC;

-- display table on Requests page
SELECT Requests.request_id, 
Requests.request_date, 
Requests.completion_date, 
CONCAT(Customers.first_name, ' ', Customers.last_name) AS full_name, 
Payments.date,
MIN(RequestServices.request_service_id) AS request_service_id
FROM Requests
LEFT JOIN Customers ON Requests.customer_id = Customers.customer_id
LEFT JOIN Payments ON Requests.payment_id = Payments.payment_id
LEFT JOIN RequestServices ON Requests.request_id = RequestServices.request_id
GROUP BY Requests.request_id
ORDER BY Requests.request_id ASC;

-- dropdown on Requests page
SELECT customer_id, CONCAT(first_name, ' ', last_name) AS full_name
FROM Customers
ORDER BY customer_id ASC;

-- display table on Requested Services page
SELECT RequestServices.request_service_id,
IFNULL(CONCAT(Requests.request_date, ', ', Customers.first_name, ' ', Customers.last_name), CONCAT(Requests.request_date, ', None')) AS request_info,
Services.name,
RequestServices.quotation_price
FROM RequestServices
LEFT JOIN Requests ON RequestServices.request_id = Requests.request_id
LEFT JOIN Services ON RequestServices.service_id = Services.service_id
LEFT JOIN Customers ON Requests.customer_id = Customers.customer_id
ORDER BY RequestServices.request_service_id ASC;

-- dropdown on Requested Services page
SELECT Requests.request_id,
IFNULL(CONCAT(Requests.request_date, ', ', Customers.first_name, ' ', Customers.last_name), CONCAT(Requests.request_date, ', None')) AS request_info
FROM Requests
LEFT JOIN Customers ON Requests.customer_id = Customers.customer_id
ORDER BY Requests.request_id ASC;

-- another dropdown on Requested Services page
SELECT Services.service_id, Services.name
FROM Services
ORDER BY Services.service_id ASC;

-- display table on Payments page
SELECT Payments.payment_id,
Requests.request_id,
IFNULL(CONCAT(Requests.request_date, ', ', Customers.first_name, ' ', Customers.last_name), CONCAT(Requests.request_date, ', None')) AS request_info, 
Payments.date, 
Payments.amount
FROM Payments
LEFT JOIN Requests ON Payments.payment_id = Requests.payment_id
LEFT JOIN Customers ON Requests.customer_id = Customers.customer_id
ORDER BY Payments.payment_id ASC;

-- dropdown on Payments page
SELECT Requests.request_id,
IFNULL(CONCAT(Requests.request_date, ', ', Customers.first_name, ' ', Customers.last_name), CONCAT(Requests.request_date, ', None')) AS request_info
FROM Requests
LEFT JOIN Customers ON Requests.customer_id = Customers.customer_id
WHERE Requests.completion_date is NOT NULL AND Requests.payment_id is NULL
ORDER BY Requests.request_id ASC;

-- create a service category
INSERT INTO ServiceCategories (name, description)
VALUES (:name_input, :description_input);

-- create a service
INSERT INTO Services (name, description, service_category_id)
VALUES (:name_input, :description_input, :service_category_id_from_dropdown_input);

-- create a customer
INSERT INTO Customers (first_name, last_name, address, phone, email)
VALUES (:first_name_input, :last_name_input, :address_input, :phone_input, :email_input);

-- create a request
INSERT INTO Requests (request_date, completion_date, customer_id)
VALUES (:request_date_input, :completion_date_input, :customer_id_from_dropdown_input);

-- create a requested service
INSERT INTO RequestServices (request_id, service_id, quotation_price)
VALUES (:request_id_from_dropdown_input, :service_id_from_dropdown_input, :quotation_price_input);

-- update payment while creating a requested service
UPDATE Payments
SET amount = (
    SELECT SUM(RequestServices.quotation_price)
    FROM RequestServices
    WHERE RequestServices.request_id = :request_id_from_dropdown_input
    GROUP BY RequestServices.request_id
)
WHERE payment_id = :payment_id_from_dropdown_input;

-- create a payment
INSERT INTO Payments (payment_id, date, amount)
VALUES (:payment_id_from_dropdown_input, :date_input, IFNULL((
        SELECT SUM(RequestServices.quotation_price) AS amount
        FROM RequestServices
        WHERE RequestServices.request_id = :request_id_from_dropdown_input
        GROUP BY RequestServices.request_id
    ), 0.00)
);

-- update request while creating a payment
UPDATE Requests
SET payment_id = :payment_id_from_dropdown_input
WHERE request_id = :request_id_from_dropdown_input;

-- update a service category
UPDATE ServiceCategories
SET description = :description_input
WHERE service_category_id = :service_category_id_from_dropdown_input;

-- update a service
UPDATE Services
SET description = :description_input, service_category_id = :service_category_id_from_dropdown_input
WHERE service_id = :service_id_from_dropdown_input;

-- update a customer
UPDATE Customers
SET address = :address_input, phone = :phone_input, email = :email_input
WHERE customer_id = :customer_id_from_dropdown_input;

-- update a request
UPDATE Requests
SET completion_date = :completion_date_input, customer_id = :customer_id_from_dropdown_input
WHERE request_id = :request_id_from_dropdown_input;

-- update a requested service
UPDATE RequestServices
SET service_id = :service_id_from_dropdown_input, quotation_price = :quotation_price_input
WHERE request_service_id = :request_service_id_from_dropdown_input;

-- update payment while updating a requested service
UPDATE Payments
SET amount = (
    SELECT SUM(RequestServices.quotation_price)
    FROM RequestServices
    WHERE RequestServices.request_id = (SELECT request_id FROM RequestServices WHERE request_service_id = :request_service_id_from_dropdown_input)
    GROUP BY RequestServices.request_id
)
WHERE payment_id = (
    SELECT request_id 
    FROM RequestServices
    WHERE request_service_id = :request_service_id_from_dropdown_input
);

-- update a payment
UPDATE Payments
SET date = :date_input
WHERE payment_id = :payment_id_from_dropdown_input;

-- delete a service category
DELETE FROM ServiceCategories
WHERE service_category_id = :service_category_id_from_delete_button;

-- delete a service
DELETE FROM Services
WHERE service_id = :service_id_from_delete_button;

-- delete a customer
DELETE FROM Customers
WHERE customer_id = :customer_id_from_delete_button;

-- delete a request
DELETE FROM Requests
WHERE request_id = :request_id_from_delete_button;

-- delete a requested service
DELETE FROM RequestServices
WHERE request_service_id = :request_service_id_from_delete_button;

-- update payment while deleting a requested service
UPDATE Payments
SET amount = IFNULL((
    SELECT SUM(RequestServices.quotation_price)
    FROM RequestServices
    WHERE RequestServices.request_id = (SELECT request_id FROM RequestServices WHERE request_service_id = :request_service_id_from_delete_button)
    AND RequestServices.request_service_id != :request_service_id_from_delete_button
    GROUP BY RequestServices.request_id
), 0.00)
WHERE payment_id = (
    SELECT request_id
    FROM RequestServices
    WHERE request_service_id = :request_service_id_from_delete_button
);

-- delete a payment
DELETE FROM Payments
WHERE payment_id = :payment_id_from_delete_button;