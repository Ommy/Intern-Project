require 'nokogiri'
require 'faraday'
require 'json'
require 'geokit'
require 'mysql2'
require 'active_record'

ActiveRecord::Base.establish_connection(
    :adapter    => "mysql2",
    :host       => "localhost",
    :database   => "intern_project"
)

class Address < ActiveRecord::Base
    self.table_name = 'address'
end

class House < ActiveRecord::Base
    self.table_name = 'housing'
end

# CONSTANTS
LAT_LONG_FILE = "./lat_long"
IMPORT_ADDRESSES = "../data/table_addresses.csv"
IMPORT_HOUSING = "../data/table_housing.csv"
SQL_ADDRESSES_TYPE  = 1
PAD_LISTER_TYPE     = 0
AIRBNB_TYPE         = 1
CRAIGSLIST_TYPE     = 2

# USE RESOURCES
PADLISTER           = "true"
AIRBNB              = "true"
CRAIGSLIST          = "false"
APARTMENTSEARCH     = "false"
RENT_COM            = "false"
APARTMENTFINDER     = "false"
REALTOR_COM         = "false"
OTHER               = "false"

# X-Paths

### PADLISTER ###
PADMAPPER_PADLISTER_XPATH = "/html/body/div[@id='bar']/div[1]/div[@class='sideBarButtonDiv']/a[@class='normalButton whiteButton thumbButton sideBarNavButton'][2]/@href"
PADLISTER_XPATH = "/html/body[@id='listings_show']/div[@id='main_container']/div[@class='wrapper']/div[@id='body_div']/div[@id='left-col']/div[@id='summary']/ul/li"
PADLISTER_PRICE     = 1
PADLISTER_ADDRESS   = 7
###

### AIRBNB ###
AIRBNB_PRICE = "/html/body[@class='no_wiggle_webkit']/div[@id='room']/div[@class='row']/div[@id='right_column']/form[@id='book_it_form']/div[@id='book_it']/div[@class='panel-body panel-dark']/div[@id='pricing']/div[@id='price_amount']"
AIRBNB_ADDRESS = "/html/body[@class='no_wiggle_webkit']/div[@id='room']/div[@class='row row-space-1']/div[@class='col-12']/div[@class='row row-table row-space-1 action-row']/div[@class='col-9 col-top']/div[@class='h4']/span[@id='display-address']"
###

# REGEX

### UNIVERSAL ###
HTML_TAG_REGEX  = /(<[^>]*>)|\n|\t/s
###

#### PADLISTER REGEX ###
PRICE_REGEX     = /(Price|\s|\$)/
ADDRESS_REGEX   = /(Address)/
LEASE_REGEX     = /(Min\.\ Lease|\s)/
###

### AIRBNB REGEX ###
AIRBNB_URL_REGEX       = /(https).*/
URL_STRIP_REGEX = /(\">)/

### CRAIGSLIST ###
CL_URL_REGEX = /(http:\/\/).*/

CITIES = {
"SAN_FRANCISCO" => {
    :elng => "-121.81503295898438",
    :nlat => "37.951684787899445",
    :wlng => "-123.00155639648438",
    :slat => "37.615496567899385"
},
"REDWOOD_CITY" => {
    :elng => "-121.48535190156247",
    :nlat => "37.81817173048233", 
    :wlng => "-122.96850619843747",
    :slat => "37.18162836578623"
},
"PALO_ALTO" => {
    :elng => "-121.7863701562988",
    :nlat => "37.59612129639819",
    :wlng => "-122.5279473047363",
    :slat => "37.27758076928773"
},
"MENLO_PARK" => {
    :elng => "-121.80408077578124",
    :nlat => "37.62213985051201",
    :wlng => "-122.54565792421874",
    :slat => "37.30371033515885"
},
"MOUNTAIN_VIEW" => {
    :elng => "-121.71047842578128",
    :nlat => "37.56315589500217",
    :wlng => "-122.45205557421878",
    :slat => "37.24447481139503"
},
"SAN_JOSE" => {
    :elng => "-120.3342585531249",
    :nlat => "37.935179931509815",
    :wlng => "-123.30056714687498",
    :slat => "36.65864509141163"
},
"SAN_MATEO" => {
    :elng => "-121.96338253359374",
    :nlat => "37.71195871572583",
    :wlng => "-122.70495968203124",
    :slat => "37.393912932677665"
},
"DALY_CITY" => {
    :elng => "-122.10208492617187",
    :nlat => "37.826079374008934",
    :wlng => "-122.84366207460937",
    :slat => "37.50852228212127"
}
}
class Scraper

    def initialize
        @padmapper_url      = "http://www.padmapper.com/"

        @padmapper_place_info = "show.php?id="

        @conn = Faraday.new(:url => @padmapper_url) do |faraday|
            faraday.adapter     Faraday.default_adapter
        end
        @lat_long_map = Hash.new

        @sql = Mysql2::Client.new(:host => 'localhost', :username => 'root')
    end

    def run
        CITIES.each do |city, coords|
            @padmapper_init_lat_long = "reloadMarkersJSON.php?eastLong=#{coords[:elng]}&northLat=#{coords[:nlat]}&westLong=#{coords[:wlng]}&southLat=#{coords[:slat]}&cities=false&showPOI=false&limit=999999&minRent=0&maxRent=6000&searchTerms=Words+Required+In+Listing&maxPricePerBedroom=6000&minBR=0&maxBR=10&minBA=1&maxAge=7&imagesOnly=false&phoneReq=false&cats=false&dogs=false&noFee=false&showSubs=true&showNonSubs=true&showRooms=true&showVac=true&userId=-1&cl=#{CRAIGSLIST}&pl=#{PADLISTER}&aptsrch=#{APARTMENTSEARCH}&rnt=#{RENT_COM}&airbnb=#{AIRBNB}&ood=#{OTHER}&af=#{APARTMENTFINDER}&rltr=#{REALTOR_COM}&zoom=12&favsOnly=false&onlyHQ=true&showHidden=false&am=false&workplaceLat=0&workplaceLong=0&maxTime=0"
            resp = @conn.get(@padmapper_init_lat_long)
            json_string = JSON.parse(resp.body)

            json_string.each do |json|
                if @lat_long_map[json["id"]].nil?
                    @lat_long_map[json["id"]] = {:lat => json["lat"], :lng => json["lng"]}
                end
            end
        end
        get_place_info
    end

    def get_place_info
        link_count = 0
        @lat_long_map.each do |id, coords|
            begin
                resp = @conn.get(@padmapper_place_info + "#{id}")
                if resp.body.include? "META" and resp.body.include? "airbnb"
                    link = resp.body.match(AIRBNB_URL_REGEX).to_s.gsub(URL_STRIP_REGEX, "")

                    resp = Faraday.get(link)
                    html = Nokogiri::HTML(resp.body)

                    listing_price       = html.xpath(AIRBNB_PRICE).to_s.gsub(HTML_TAG_REGEX, "").gsub(/\$/, "").strip
                    listing_address     = html.xpath(AIRBNB_ADDRESS).to_s.gsub(HTML_TAG_REGEX, "").strip
                    listing_price       = (listing_price.to_i * 30).to_s
                    listing_type        = link

                elsif resp.body.include? "META" and resp.body.include? "craigslist"
                    link = resp.body.match(CL_URL_REGEX).to_s.gsub(URL_STRIP_REGEX, "")

                    link = "http://#{link}" if !link.include? "http"
                    resp = Faraday.get(link)
                    html = Nokogiri::HTML(resp.body)

                    puts "#{id} => lat: #{@lat_long_map[id][:lat]}, lng: #{@lat_long_map[id][:lng]}"

                    listing_price      = html.css("h2").text.to_s.gsub("\\n", "").strip.split("\/")[0].gsub("\$","").strip
                    listing_address    = nil
                    listing_type       = CRAIGSLIST_TYPE

                else
                    link = Nokogiri::HTML(resp.body).xpath(PADMAPPER_PADLISTER_XPATH).to_s
                    resp = Faraday.get(link)
                    html = Nokogiri::HTML(resp.body)

                    listing_price       = html.xpath(PADLISTER_XPATH + "[#{PADLISTER_PRICE}]").to_s
                                                                                        .strip.gsub(HTML_TAG_REGEX,"")
                                                                                        .gsub(PRICE_REGEX, "")
                    listing_address     = html.xpath(PADLISTER_XPATH + "[#{PADLISTER_ADDRESS}]").to_s.strip
                                                                                        .gsub(HTML_TAG_REGEX, "")
                                                                                        .gsub(ADDRESS_REGEX, "")
                                                                                        .strip
                    listing_type        = link

                end
                addr_id = generate_addresses_csv id, listing_address, listing_type == CRAIGSLIST_TYPE unless listing_price.empty?
                save_housing_data listing_price, listing_type, addr_id unless listing_price.empty?
            rescue => e
                link_count = link_count + 1
                print "Link count: #{link_count} => "
                puts e
            end
        end
    end

    def save_housing_data(price, house_url, address_id)
        House.create(:address_id => address_id, :price => price, :source => house_url)
    end

    def generate_addresses_csv(id, street_address, is_cl = false)
        address = street_address.split(",") unless street_address.nil? 
        geo = nil

        begin
            geo = Geokit::Geocoders::GoogleGeocoder.geocode("#{@lat_long_map[id][:lat]},#{@lat_long_map[id][:lng]}")
        rescue
        end
        if street_address.nil? and geo.nil?
            raise "Invalid Address: CL => #{is_cl} -- #{geo.full_address unless geo.nil?}"
        end

        if !geo.nil? and !is_cl
            street = (address[0].nil? ? ( geo.full_address.nil? ? "NULL" : geo.full_address.split(",")[0]) : address[0]).strip
            city = (address[1].nil? ? ( geo.city.nil? ? "NULL" : geo.city) : address[1]).strip
            country = (address[3].nil? ? (geo.country.nil? ? "USA" : geo.country) : address[3]).strip
        elsif is_cl and !geo.nil?
            street  = (geo.full_address.nil? ? "NULL" : geo.full_address.split(",")[0]).strip
            city    = (geo.city.nil? ? "NULL" : geo.city).strip
            country = (geo.country.nil? ? "USA" : geo.country).strip
        else
            street  = (address[0].nil? ? "NULL" : address[0]).strip
            city    = (address[1].nil? ? "NULL" : address[1]).strip
            country = (address[3].nil? ? "USA" : address[3]).strip
        end
        csv_string = "#{street}*#{city}*#{country}*#{@lat_long_map[id][:lng]}*#{@lat_long_map[id][:lat]}"
        #puts csv_string
        addr = Address.create(:street_address  => street,
                              :city            => city,
                              :country         => country,
                              :longitude       => @lat_long_map[id][:lng],
                              :latitude        => @lat_long_map[id][:lat])
        return addr.id
    end

    def store_csvs
        File.open(IMPORT_HOUSING, 'w') do |f|
            @housing_array.each do |house|
                f.write house << "\n"
            end
        end
        File.open(IMPORT_ADDRESSES, 'w') do |f|
            @address_array.each do |address|
                f.write address << "\n"
            end
        end
    end
end
# ADDRESSES: 
# CREATE TABLE IF NOT EXISTS `addresses` (
#   `id` int(11) NOT NULL,
#   `street_address` varchar(200) DEFAULT NULL,
#   `city` varchar(100) NOT NULL,
#   `country` varchar(100) NOT NULL,
#   `longitude` decimal(18,12) DEFAULT NULL,
#   `latitude` decimal(18,12) DEFAULT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

# HOUSING:   price, source (0 => padlister, 1 => airbnb)

# CREATE TABLE IF NOT EXISTS `housing` (
#   `id` int(11) NOT NULL,
#   `address_id` int(11) NOT NULL,
#   `price` decimal(10,0) NOT NULL DEFAULT '0',
#   `source` int(3) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

if __FILE__ == $0
    scraper = Scraper.new
    scraper.run
end