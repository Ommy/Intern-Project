require 'active_record'

ActiveRecord::Base.establish_connection(
	:adapter 	=> "mysql2",
	:host	 	=> "localhost",
	:database 	=> "intern_project"
	)

class HouseToCrime < ActiveRecord::Base
	self.table_name = 'house_to_crime'
end

class Housing < ActiveRecord::Base
	self.table_name = 'housing'
end

class Crime < ActiveRecord::Base
	self.table_name = 'crime'
end

class Address < ActiveRecord::Base
	self.table_name = 'address'
end

def haversine(lat1, long1, lat2, long2)  
  radius_of_earth = 6378.14 
  rlat1, rlong1, rlat2, rlong2 = [lat1, long1, lat2, long2].map { |d| as_radians(d)}
 
  dlon = rlong1 - rlong2
  dlat = rlat1 - rlat2
 
  a = power(Math::sin(dlat/2), 2) + Math::cos(rlat1) * Math::cos(rlat2) * power(Math::sin(dlon/2), 2)
  great_circle_distance = 2 * Math::atan2(Math::sqrt(a), Math::sqrt(1-a))
  radius_of_earth * great_circle_distance
end
 
def as_radians(degrees)
  degrees * Math::PI/180
end
 
def power(num, pow)
  num ** pow
end

def run
	housing = Housing.all
	crimes = Crime.all
	housing.each do |house|
		house_address = Address.find(house.address_id)
		crimes.each do |crime|
			crime_address = Address.find(crime.address_id)
			distance = haversine(house_address.latitude.to_s.to_f,
								 house_address.longitude.to_s.to_f,
								 crime_address.latitude.to_s.to_f,
								 crime_address.longitude.to_s.to_f)
			HouseToCrime.create(:house_id => house.id, :crime_id => crime.id, :distance => distance)
		end
	end
end

if __FILE__ == $0
	run
end
