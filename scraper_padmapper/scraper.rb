require 'nokogiri'
require 'faraday'
require 'json'
require 'geokit'


# CONSTANTS
LAT_LONG_FILE = "./lat_long"
IMPORT_ADDRESSES = "../data/addresses.csv"
IMPORT_HOUSING = "../data/housing.csv"
SQL_ADDRESSES_TYPE = 1
PAD_LISTER_TYPE = 0
AIRBNB_TYPE = 1

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
URL_REGEX       = /(https).*/
URL_STRIP_REGEX = /(\">)/

class Scraper

    def initialize
        @padmapper_url = "http://www.padmapper.com/"
        @padmapper_init_lat_long = "reloadMarkersJSON.php?eastLong=-121.81503295898438&northLat=37.951684787899445&westLong=-123.00155639648438&southLat=37.615496567899385&cities=false&showPOI=false&limit=999999&minRent=0&maxRent=6000&searchTerms=Words+Required+In+Listing&maxPricePerBedroom=6000&minBR=0&maxBR=10&minBA=1&maxAge=7&imagesOnly=false&phoneReq=false&cats=false&dogs=false&noFee=false&showSubs=true&showNonSubs=true&showRooms=true&showVac=true&userId=-1&cl=true&pl=true&aptsrch=true&rnt=true&airbnb=true&ood=true&af=true&rltr=true&zoom=12&favsOnly=false&onlyHQ=true&showHidden=false&am=false&workplaceLat=0&workplaceLong=0&maxTime=0"
        @padmapper_place_info = "show.php?id="

        @conn = Faraday.new(:url => @padmapper_url) do |faraday|
            faraday.adapter     Faraday.default_adapter
        end
        @lat_long_map = Hash.new

        @housing_array = []
        @address_array = []
    end

    def get_lat_longs
        resp = @conn.get(@padmapper_init_lat_long)
        json_string = JSON.parse(resp.body)

        json_string.each do |json|
            @lat_long_map[json["id"]] = {:lat => json["lat"], :lng => json["lng"]}
        end
        return json_string
    end

    def get_place_info(id)
        begin
            @lat_long_map[id] = {:lat => "37.7019", :lng => "-121.929"}
            resp = @conn.get(@padmapper_place_info + "#{id}")
            if resp.body.include? "META"
                link = resp.body.match(URL_REGEX).to_s.gsub(URL_STRIP_REGEX, "")
                resp = Faraday.get(link)
                html = Nokogiri::HTML(resp.body)

                listing_price       = html.xpath(AIRBNB_PRICE).to_s.gsub(HTML_TAG_REGEX, "").gsub(/\$/, "").strip
                listing_address     = html.xpath(AIRBNB_ADDRESS).to_s.gsub(HTML_TAG_REGEX, "").strip
                listing_price       = (listing_price.to_i * 30).to_s
                listing_type        = AIRBNB_TYPE
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
                listing_type        = PAD_LISTER_TYPE
            end
            generate_housing_csv listing_price, listing_type unless listing_price.empty?
            generate_addresses_csv id, listing_address unless listing_price.empty?
        rescue => e
            puts e
        end
    end

    def generate_housing_csv(price, source)
        csv_string = "#{price}*#{source}"
        @housing_array << csv_string
    end

    def generate_addresses_csv(id, street_address)
        address = street_address.split(",")
        geo = Geokit::Geocoders::GoogleGeocoder.geocode("#{@lat_long_map[id][:lat]},#{@lat_long_map[id][:lng]}")
        street = (address[0].nil? ? ( geo.full_address.nil? ? "NULL" : geo.full_address.split(",")[0]) : address[0]).strip
        city = (address[1].nil? ? ( geo.city.nil? ? "NULL" : geo.city) : address[1]).strip
        country = (address[3].nil? ? (geo.country.nil? ? "NULL" : geo.country) : address[3]).strip
        csv_string = "#{street}*#{city}*#{country}*#{@lat_long_map[id][:lng]}*#{@lat_long_map[id][:lat]}"
        @address_array << csv_string
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
# ADDRESSES: street_address, city, country, longitude, latitude
# HOUSING:   price, source (0 => padlister, 1 => airbnb)

if __FILE__ == $0
    scraper = Scraper.new
    lat_long = scraper.get_lat_longs # JSON of all the ID's of places
    #sample_json = "{\"id\": \"186788778\", \"lng\": \"-121.929\", \"lat\": \"37.7019\", \"type\": \"2\"}"
    #json = JSON.parse(sample_json)
    # http://www.padmapper.com/show.php?id=186788778
    lat_long.each do |json|
        scraper.get_place_info json["id"]
    end
    #scraper.get_place_info json["id"]
    scraper.store_csvs
end