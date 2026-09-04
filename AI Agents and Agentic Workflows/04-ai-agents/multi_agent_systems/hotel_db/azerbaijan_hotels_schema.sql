-- Azerbaijan Hotels SQLite Schema and Sample Data

CREATE TABLE IF NOT EXISTS hotels (
    hotel_id INTEGER PRIMARY KEY AUTOINCREMENT,
    hotel_name TEXT NOT NULL,
    town TEXT NOT NULL,
    address TEXT NOT NULL,
    rating REAL NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS hotel_room_offers (
    offer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    hotel_id INTEGER NOT NULL,
    available_rooms INTEGER NOT NULL,
    price_single REAL NOT NULL,
    price_double REAL NOT NULL,
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id)
);

-- Pre-populate Azerbaijani hotels. Room prices are in AZN.
INSERT INTO hotels (hotel_name, town, address, rating, description) VALUES
('Caspian View Hotel', 'Baku', '1 Neftchilar Avenue, Baku', 4.5, 'A modern hotel overlooking the Caspian Sea.'),
('Sheki Caravan Inn', 'Sheki', '12 Mirza Fatali Akhundov Street, Sheki', 4.6, 'A traditional stay near Sheki''s historic centre.'),
('Ganja Garden Hotel', 'Ganja', '5 Nizami Ganjavi Avenue, Ganja', 4.2, 'A comfortable hotel close to Ganja''s main attractions.'),
('Quba Mountain Retreat', 'Quba', '8 Heydar Aliyev Avenue, Quba', 4.4, 'A peaceful base for exploring the Greater Caucasus.'),
('Gabala Peaks Resort', 'Gabala', '3 Tufandag Road, Gabala', 4.7, 'A mountain resort near hiking trails and ski facilities.'),
('Lankaran Springs Hotel', 'Lankaran', '10 Khanbulan Road, Lankaran', 4.3, 'A relaxing hotel near forests, springs, and the Caspian coast.'),
('Shamakhi Heritage Inn', 'Shamakhi', '7 Shahriyar Street, Shamakhi', 4.1, 'A welcoming inn near Shamakhi''s historic landmarks.'),
('Nakhchivan Palace Hotel', 'Nakhchivan', '15 Heydar Aliyev Avenue, Nakhchivan', 4.5, 'A central hotel with convenient access to the old city.'),
('Naftalan Wellness Lodge', 'Naftalan', '4 Shirvan Avenue, Naftalan', 4.4, 'A wellness-focused stay in Azerbaijan''s spa destination.'),
('Goygol Lake Resort', 'Goygol', '9 Goygol National Park Road, Goygol', 4.6, 'A scenic retreat near forests, mountains, and Lake Goygol.');

-- Pre-populate hotel room offers. Prices are in AZN.
INSERT INTO hotel_room_offers (hotel_id, available_rooms, price_single, price_double) VALUES
(1, 5, 180.00, 260.00),
(2, 4, 90.00, 140.00),
(3, 6, 100.00, 155.00),
(4, 5, 120.00, 180.00),
(5, 3, 160.00, 240.00),
(6, 7, 95.00, 145.00),
(7, 4, 110.00, 165.00),
(8, 5, 125.00, 185.00),
(9, 6, 140.00, 210.00),
(10, 4, 115.00, 175.00);
