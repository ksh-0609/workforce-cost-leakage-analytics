CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(100)
);

CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    department_id INT REFERENCES departments(department_id),
    location_id INT REFERENCES locations(location_id),
    role VARCHAR(100),
    hourly_rate NUMERIC(6,2) NOT NULL CHECK (hourly_rate > 0),
    hire_date DATE NOT NULL
);
CREATE INDEX idx_employees_department ON employees(department_id);
CREATE INDEX idx_employees_location ON employees(location_id);

CREATE TABLE shifts_scheduled (
    shift_id SERIAL PRIMARY KEY,
    employee_id INT REFERENCES employees(employee_id),
    shift_date DATE NOT NULL,
    scheduled_start TIMESTAMP NOT NULL,
    scheduled_end TIMESTAMP NOT NULL,
    CHECK (scheduled_end > scheduled_start)
);
CREATE INDEX idx_shifts_employee_date ON shifts_scheduled(employee_id, shift_date);

CREATE TABLE time_clock_punches (
    punch_id SERIAL PRIMARY KEY,
    shift_id INT REFERENCES shifts_scheduled(shift_id),
    employee_id INT REFERENCES employees(employee_id),
    clock_in TIMESTAMP NOT NULL,
    clock_out TIMESTAMP,
    break_taken BOOLEAN DEFAULT TRUE,
    CHECK (clock_out IS NULL OR clock_out > clock_in)
);
CREATE INDEX idx_punches_employee_date ON time_clock_punches(employee_id, clock_in);

CREATE TABLE demand_hourly (
    location_id INT REFERENCES locations(location_id),
    department_id INT REFERENCES departments(department_id),
    demand_date DATE NOT NULL,
    hour_of_day INT CHECK (hour_of_day BETWEEN 0 AND 23),
    demand_value NUMERIC(8,2),
    PRIMARY KEY (location_id, department_id, demand_date, hour_of_day)
);

CREATE TABLE shift_swaps (
    swap_id SERIAL PRIMARY KEY,
    original_employee_id INT REFERENCES employees(employee_id),
    covering_employee_id INT REFERENCES employees(employee_id),
    shift_id INT REFERENCES shifts_scheduled(shift_id),
    swap_date DATE NOT NULL,
    manager_approved BOOLEAN DEFAULT FALSE
);

CREATE TABLE leave_absences (
    absence_id SERIAL PRIMARY KEY,
    employee_id INT REFERENCES employees(employee_id),
    absence_date DATE NOT NULL,
    absence_type VARCHAR(50)
);

CREATE TABLE ground_truth_labels (
    label_id SERIAL PRIMARY KEY,
    employee_id INT REFERENCES employees(employee_id),
    label_date DATE NOT NULL,
    anomaly_type VARCHAR(50) NOT NULL,
    injected BOOLEAN DEFAULT TRUE
);