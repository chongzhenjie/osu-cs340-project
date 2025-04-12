/*
    Group 40 Project Step 5 Portfolio Assignment: DDL.sql
    Zhen Jie Chong
    Zhen Kang Chong

    Note: Do not use semicolons for commenting in this file
*/

-- disable foreign key checks and commits
SET FOREIGN_KEY_CHECKS = 0;
SET AUTOCOMMIT = 0;

-- drop tables if they exist to minimize import errors
DROP TABLE IF EXISTS RequestServices;
DROP TABLE IF EXISTS Payments;
DROP TABLE IF EXISTS Requests;
DROP TABLE IF EXISTS Customers;
DROP TABLE IF EXISTS Services;
DROP TABLE IF EXISTS ServiceCategories;

-- create Customers table
CREATE TABLE Customers (
    customer_id INT AUTO_INCREMENT UNIQUE NOT NULL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    address VARCHAR(200) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL
);

-- create Services table
CREATE TABLE Services (
    service_id INT AUTO_INCREMENT UNIQUE NOT NULL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(200) NOT NULL,
    service_category_id INT,
    FOREIGN KEY (service_category_id) REFERENCES ServiceCategories(service_category_id) ON DELETE SET NULL
);

-- create ServiceCategories table
CREATE TABLE ServiceCategories (
    service_category_id INT AUTO_INCREMENT UNIQUE NOT NULL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(200) NOT NULL
);

-- create Requests table
CREATE TABLE Requests (
    request_id INT AUTO_INCREMENT UNIQUE NOT NULL PRIMARY KEY,
    request_date DATETIME UNIQUE NOT NULL,
    completion_date DATETIME,
    customer_id INT,
    payment_id INT,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON DELETE SET NULL,
    FOREIGN KEY (payment_id) REFERENCES Payments(payment_id) ON DELETE SET NULL
);

-- create Payments table
CREATE TABLE Payments (
    payment_id INT UNIQUE NOT NULL PRIMARY KEY,
    date DATETIME UNIQUE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL
);

-- create RequestServices table (intersection table)
CREATE TABLE RequestServices (
    request_service_id INT AUTO_INCREMENT UNIQUE NOT NULL PRIMARY KEY,
    request_id INT NOT NULL,
    service_id INT NOT NULL,
    quotation_price DECIMAL(10, 2) NOT NULL,
    UNIQUE (request_id, service_id),
    FOREIGN KEY (request_id) REFERENCES Requests(request_id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES Services(service_id) ON DELETE CASCADE
);

-- insert example data for ServiceCategories
INSERT INTO ServiceCategories (name, description) VALUES 
('Artificial Intelligence', 'Advanced AI solutions for businesses'),
('Software Development', 'Custom software development services'),
('Cybersecurity', 'Security solutions and services');

-- insert example data for Services
INSERT INTO Services (name, description, service_category_id) VALUES
(
    'AI Chatbot Development',
    'Develop AI-powered chatbots for customer support', 
    (SELECT service_category_id FROM ServiceCategories WHERE name = 'Artificial Intelligence')
),
(
    'Web Application Development', 
    'Build custom web applications tailored to client needs', 
    (SELECT service_category_id FROM ServiceCategories WHERE name = 'Software Development')
),
(
    'Network Security Audit', 
    'Conduct audits to assess network security vulnerabilities', 
    (SELECT service_category_id FROM ServiceCategories WHERE name = 'Cybersecurity')
);

-- insert sample data for Customers
INSERT INTO Customers (first_name, last_name, address, phone, email) VALUES
('James', 'Wheels', '123 Main St, Atown, USA', '555-1234', 'james.wheels@gmail.com'),
('Sam', 'Smith', '456 Elm St, Btown, USA', '555-5678', 'sam.smith@gmail.com'),
('Wendy', 'Button', '789 Oak St, Ctown, USA', '555-9012', 'wendy.button@gmail.com');

-- insert example data for Requests
INSERT INTO Requests (request_date, completion_date, customer_id, payment_id) VALUES
(
    '2024-06-15 10:20:00', 
    '2024-06-17 12:45:30', 
    (SELECT customer_id FROM Customers WHERE email = 'james.wheels@gmail.com'), -- email is unique, name may not be
    1 -- payment_id matches request_id by design, subqueries will be used for Payments PK instead
),
(
    '2024-07-15 10:00:00', 
    '2024-07-18 13:00:00', 
    (SELECT customer_id FROM Customers WHERE email = 'james.wheels@gmail.com'),
    2
),
(
    '2024-07-16 09:30:00', 
    '2024-07-23 15:00:00', 
    (SELECT customer_id FROM Customers WHERE email = 'sam.smith@gmail.com'),
    3
),
(
    '2024-07-17 11:45:00', 
    NULL,
    (SELECT customer_id FROM Customers WHERE email = 'wendy.button@gmail.com'),
    NULL -- this will be NULL as payment has yet to be made
);

-- insert example data for Payments
INSERT INTO Payments (payment_id, date, amount) VALUES
(
    (SELECT request_id FROM Requests WHERE request_date='2024-06-15 10:20:00'), -- payment_id matches request_id by design, request_date is assumed to be unique
    '2024-06-19 18:23:56', 
    780.25
),
(
    (SELECT request_id FROM Requests WHERE request_date='2024-07-15 10:00:00'),
    '2024-07-19 11:30:00', 
    1000.75
),
(
    (SELECT request_id FROM Requests WHERE request_date='2024-07-16 09:30:00'),
    '2024-07-24 14:00:00',
     2300.50
);

-- insert example data for RequestServices (intersection table)
INSERT INTO RequestServices (request_id, service_id, quotation_price) VALUES
(
    (SELECT request_id FROM Requests WHERE request_date='2024-06-15 10:20:00'), 
    (SELECT service_id FROM Services WHERE name = 'Web Application Development'),
    780.25
),  -- James Wheels's request for Web Application Development
(
    (SELECT request_id FROM Requests WHERE request_date='2024-07-15 10:00:00'), 
    (SELECT service_id FROM Services WHERE name = 'AI Chatbot Development'), 
    1000.75
),  -- James Wheels's request for AI Chatbot Development
(
    (SELECT request_id FROM Requests WHERE request_date='2024-07-16 09:30:00'), 
    (SELECT service_id FROM Services WHERE name = 'Web Application Development'), 
    1500.00
),  -- Sam Smith's request for Web Application Development
(
    (SELECT request_id FROM Requests WHERE request_date='2024-07-16 09:30:00'), 
    (SELECT service_id FROM Services WHERE name = 'Network Security Audit'), 
    800.50
),   -- Sam Smith's request for Network Security Audit
(
    (SELECT request_id FROM Requests WHERE request_date='2024-07-17 11:45:00'), 
    (SELECT service_id FROM Services WHERE name = 'Network Security Audit'),  
    1200.00
);  -- Wendy Button's request for Network Security Audit

-- enable foreign key checks and commit changes
SET FOREIGN_KEY_CHECKS=1;
COMMIT;