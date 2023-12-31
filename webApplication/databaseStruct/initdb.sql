CREATE TABLE parking_bay_detail(
    PARKING_BAY_NAME TEXT NOT NULL,
    PARKING_BAY_STATUS INT NOT NULL
);

CREATE TABLE parking_bay_timestamp(
    PARKING_BAY_ID INT NOT NULL,
    PARKING_BAY_ENTRY_TIME DATETIME NOT NULL,
    PARKING_BAY_EXIT_TIME DATETIME,
    PARKING_BAY_TOTAL_MINUTES INT
);

CREATE TABLE booking_parking_bay(
    PARKING_BAY_ID INT NOT NULL,
    FULL_NAME TEXT NOT NULL,
    EMAIL TEXT NOT NULL,
    PHONE_NUMBER TEXT NOT NULL,
    PLATE_NUMBER TEXT NOT NULL,
    BOOKING_ENTRY_TIME DATETIME NOT NULL,
    BOOKING_EXIT_TIME DATETIME NOT NULL,
    IS_EXPIRED NUMBER NOT NULL
);